# backend/routers/admin/analytics.py
from collections import Counter
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from db.database import SessionLocal
from model.report import Report, KanbanStage
from model.users import User
from model.user_profile import UserProfile
from model.routing_table import RoutingTable
from utils.rbac import require_roles

router = APIRouter(prefix="/admin/analytics", tags=["Admin Analytics"])

ALL_ADMIN = require_roles("super_admin", "city_admin", "dept_officer")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _to_utc(dt):
    if dt is None:
        return None
    return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt


def _apply_scope(q, scope: str, scope_id: str, current_user: User, db: Session):
    """
    Row-level filter based on scope param.
    scope=city_dept  scope_id="lahore_lmc"   -> city + dept filter
    scope=city       scope_id="lahore"        -> city filter only
    scope=national                            -> no filter (super_admin only)
    Role is always the ceiling.
    """
    role = (current_user.role or "").lower()

    if scope == "national" and role == "super_admin":
        return q

    if scope == "city":
        city = scope_id or (current_user.city if role == "city_admin" else None)
        if city:
            q = q.filter(Report.assigned_city == city)
        return q

    if scope == "city_dept":
        parts = (scope_id or "").split("_", 1)
        city  = parts[0] if len(parts) > 0 else None
        dept  = parts[1] if len(parts) > 1 else None
        if city:
            q = q.filter(Report.assigned_city == city)
        if dept:
            q = q.filter(Report.assigned_department == dept)
        return q

    # Fallback: role-based default scoping
    if role == "dept_officer":
        routing = db.query(RoutingTable).filter_by(
            officer_id=current_user.id, is_active=True
        ).first()
        if routing:
            q = q.filter(
                Report.assigned_city == routing.city,
                Report.assigned_department == routing.department,
            )
    elif role == "city_admin" and current_user.city:
        q = q.filter(Report.assigned_city == current_user.city)

    return q


def _signal(metric: str, value: float) -> str:
    if metric == "total_reports":
        return "red" if value > 20 else "amber" if value > 10 else "green"
    if metric == "avg_resolution":
        return "red" if value > 5 else "amber" if value > 3 else "green"
    if metric == "re_report_rate":
        return "red" if value > 25 else "amber" if value > 15 else "green"
    if metric == "community_score":
        return "red" if value < 40 else "amber" if value < 60 else "green"
    return "green"


# ---------------------------------------------------------------------------
# MODULE 1 — KPI endpoint
# ---------------------------------------------------------------------------
@router.get("/kpi")
def get_kpi(
    scope:    str = Query("city_dept"),
    scope_id: str = Query(""),
    days:     int = Query(30, ge=7, le=365),
    current_user: User = Depends(ALL_ADMIN),
    db: Session = Depends(get_db),
):
    now           = datetime.now(timezone.utc)
    current_start = now - timedelta(days=days)
    prev_start    = now - timedelta(days=days * 2)

    base    = _apply_scope(db.query(Report), scope, scope_id, current_user, db)
    current = base.filter(Report.created_at >= current_start).all()
    prev    = base.filter(Report.created_at >= prev_start,
                          Report.created_at <  current_start).all()

    # Total Reports
    total      = len(current)
    total_prev = len(prev)
    delta_pct  = round((total - total_prev) / total_prev * 100, 1) if total_prev else 0.0

    # Avg Resolution Time
    def avg_res(reports):
        durations = []
        for r in reports:
            if r.kanban_stage == KanbanStage.RESOLVED and r.created_at and r.updated_at:
                d = (_to_utc(r.updated_at) - _to_utc(r.created_at)).total_seconds() / 86400
                if 0 < d < 365:
                    durations.append(d)
        return round(sum(durations) / len(durations), 1) if durations else 0.0

    res_days  = avg_res(current)
    res_prev  = avg_res(prev)
    res_delta = round(res_days - res_prev, 1)

    # Re-report Rate
    re_count     = sum(1 for r in current if r.duplicate_of_id)
    re_rate      = round(re_count / total * 100, 1) if total else 0.0
    re_prev_cnt  = sum(1 for r in prev if r.duplicate_of_id)
    re_rate_prev = round(re_prev_cnt / len(prev) * 100, 1) if prev else 0.0
    re_delta     = round(re_rate - re_rate_prev, 1)

    # Community Score
    scores      = [r.community_score for r in current if r.community_score is not None]
    comm_score  = round(sum(scores) / len(scores), 1) if scores else None
    scores_prev = [r.community_score for r in prev if r.community_score is not None]
    comm_prev   = round(sum(scores_prev) / len(scores_prev), 1) if scores_prev else None
    comm_delta  = round(comm_score - comm_prev, 1) if (comm_score and comm_prev) else None

    return {
        "total_reports": {
            "value":     total,
            "delta_pct": delta_pct,
            "signal":    _signal("total_reports", delta_pct),
        },
        "avg_resolution_time": {
            "value_days": res_days,
            "delta_days": res_delta,
            "signal":     _signal("avg_resolution", res_days),
        },
        "re_report_rate": {
            "value_pct": re_rate,
            "delta_pp":  re_delta,
            "signal":    _signal("re_report_rate", re_rate),
        },
        "community_score": {
            "value":  comm_score,
            "delta":  comm_delta,
            "signal": _signal("community_score", comm_score or 100),
        },
    }


# ---------------------------------------------------------------------------
# MODULE 2 — Issue breakdown (donut chart)
# ---------------------------------------------------------------------------
@router.get("/issue-breakdown")
def get_issue_breakdown(
    scope:    str = Query("city_dept"),
    scope_id: str = Query(""),
    days:     int = Query(30, ge=7, le=365),
    current_user: User = Depends(ALL_ADMIN),
    db: Session = Depends(get_db),
):
    now   = datetime.now(timezone.utc)
    since = now - timedelta(days=days)

    reports = _apply_scope(
        db.query(Report), scope, scope_id, current_user, db
    ).filter(Report.created_at >= since).all()

    total  = len(reports)
    counts = Counter(
        r.category.value if r.category else "UNKNOWN" for r in reports
    )

    breakdown = [
        {
            "category": cat,
            "count":    cnt,
            "pct":      round(cnt / total * 100, 1) if total else 0.0,
        }
        for cat, cnt in sorted(counts.items(), key=lambda x: -x[1])
    ]

    return {"breakdown": breakdown, "total": total}


# ---------------------------------------------------------------------------
# MODULE 2 — Pipeline stage distribution (funnel)
# ---------------------------------------------------------------------------
STAGE_ORDER = [
    ("NEW",                  "New"),
    ("PENDING_VERIFICATION", "Pending Verification"),
    ("VERIFIED",             "Verified"),
    ("IN_PROGRESS",          "In Progress"),
    ("AWAITING_FEEDBACK",    "Awaiting Feedback"),
    ("RESOLVED",             "Resolved"),
]


@router.get("/pipeline")
def get_pipeline(
    scope:    str = Query("city_dept"),
    scope_id: str = Query(""),
    days:     int = Query(30, ge=7, le=365),
    current_user: User = Depends(ALL_ADMIN),
    db: Session = Depends(get_db),
):
    now   = datetime.now(timezone.utc)
    since = now - timedelta(days=days)

    reports = _apply_scope(
        db.query(Report), scope, scope_id, current_user, db
    ).filter(Report.created_at >= since).all()

    total  = len(reports)
    counts = Counter(
        r.kanban_stage.value if r.kanban_stage else "NEW" for r in reports
    )

    # Avg days per stage:
    # RESOLVED  → avg(updated_at - created_at) for resolved reports
    # Active    → avg(now - updated_at) as proxy for time stuck in current stage
    stage_durations: dict[str, list[float]] = {key: [] for key, _ in STAGE_ORDER}
    for r in reports:
        stage = r.kanban_stage.value if r.kanban_stage else "NEW"
        if stage == "RESOLVED" and r.created_at and r.updated_at:
            d = (_to_utc(r.updated_at) - _to_utc(r.created_at)).total_seconds() / 86400
            if 0 < d < 365:
                stage_durations["RESOLVED"].append(d)
        elif r.updated_at:
            d = (now - _to_utc(r.updated_at)).total_seconds() / 86400
            if 0 <= d < 365:
                stage_durations[stage].append(d)

    def _avg_days(lst):
        return round(sum(lst) / len(lst), 1) if lst else 0.0

    stages = [
        {
            "stage":    key,
            "label":    label,
            "count":    counts.get(key, 0),
            "avg_days": _avg_days(stage_durations.get(key, [])),
        }
        for key, label in STAGE_ORDER
    ]

    # Bottleneck = non-RESOLVED stage with highest count
    non_resolved = [s for s in stages if s["stage"] != "RESOLVED"]
    bottleneck   = (
        max(non_resolved, key=lambda s: s["count"])["stage"]
        if any(s["count"] > 0 for s in non_resolved) else None
    )

    return {"stages": stages, "total": total, "bottleneck_stage": bottleneck}


# ---------------------------------------------------------------------------
# MODULE 3 — AI Insight Cards (Forecast · Bottleneck · Health Index)
# ---------------------------------------------------------------------------
_STAGE_LABELS = {
    "NEW":                  "New",
    "PENDING_VERIFICATION": "Pending Verification",
    "VERIFIED":             "Verified",
    "IN_PROGRESS":          "In Progress",
    "AWAITING_FEEDBACK":    "Awaiting Feedback",
    "RESOLVED":             "Resolved",
}


@router.get("/insights")
def get_insights(
    scope:    str = Query("city_dept"),
    scope_id: str = Query(""),
    days:     int = Query(30, ge=7, le=365),
    current_user: User = Depends(ALL_ADMIN),
    db: Session = Depends(get_db),
):
    now   = datetime.now(timezone.utc)
    since = now - timedelta(days=days)

    base    = _apply_scope(db.query(Report), scope, scope_id, current_user, db)
    current = base.filter(Report.created_at >= since).all()
    total   = len(current)

    # ── Forecast ──────────────────────────────────────────────────────────────
    # Split the window into two halves; compare averages to get direction + delta
    half       = days // 2
    mid        = now - timedelta(days=half)
    recent_cnt = sum(1 for r in current if _to_utc(r.created_at) >= mid)
    prior_cnt  = sum(1 for r in current if _to_utc(r.created_at) <  mid)

    recent_rate = recent_cnt / half   # reports per day
    prior_rate  = prior_cnt  / half

    forecast_delta = round((recent_rate - prior_rate) * days)
    if prior_rate == 0:
        direction = "stable"
    elif recent_rate > prior_rate * 1.10:
        direction = "up"
    elif recent_rate < prior_rate * 0.90:
        direction = "down"
    else:
        direction = "stable"

    # ── Bottleneck ────────────────────────────────────────────────────────────
    from collections import Counter as _Counter
    stage_counts = _Counter(
        r.kanban_stage.value if r.kanban_stage else "NEW" for r in current
    )
    non_resolved = {k: v for k, v in stage_counts.items() if k != "RESOLVED"}
    if non_resolved:
        bn_stage = max(non_resolved, key=non_resolved.get)
        bn_count = non_resolved[bn_stage]
        bn_pct   = round(bn_count / total * 100, 1) if total else 0.0
    else:
        bn_stage = None
        bn_count = 0
        bn_pct   = 0.0

    # ── Health Index ──────────────────────────────────────────────────────────
    resolved_cnt  = stage_counts.get("RESOLVED", 0)
    resolved_pct  = (resolved_cnt / total * 100) if total else 0.0
    re_rate       = (sum(1 for r in current if r.duplicate_of_id) / total * 100) if total else 0.0
    confidences   = [r.ai_confidence for r in current if r.ai_confidence is not None]
    avg_conf      = (sum(confidences) / len(confidences)) if confidences else 0.5

    health = round(
        resolved_pct * 0.5 + (100 - re_rate) * 0.3 + avg_conf * 100 * 0.2, 1
    )
    health = max(0.0, min(100.0, health))
    health_label = "Healthy" if health >= 70 else "At Risk" if health >= 40 else "Critical"

    return {
        "forecast": {
            "delta":     forecast_delta,
            "direction": direction,
        },
        "bottleneck": {
            "stage":  bn_stage,
            "label":  _STAGE_LABELS.get(bn_stage, bn_stage) if bn_stage else None,
            "count":  bn_count,
            "pct":    bn_pct,
        },
        "health": {
            "index": health,
            "label": health_label,
        },
    }


# ---------------------------------------------------------------------------
# MODULE 4 — Predictive Alerts Feed (5 rule-based alert types)
# ---------------------------------------------------------------------------
_CATEGORY_LABEL = {"POTHOLE": "Pothole", "TRASH": "Garbage"}


@router.get("/alerts")
def get_alerts(
    scope:    str = Query("city_dept"),
    scope_id: str = Query(""),
    days:     int = Query(30, ge=7, le=365),
    current_user: User = Depends(ALL_ADMIN),
    db: Session = Depends(get_db),
):
    """
    5 rule-based alert types — no ML, no extra table:
      area_warning       • re-report rate > 30%                      (red)
      resource_suggest   • pending > 50 and forecast rising           (blue)
      seasonal           • within 21 days of monsoon peak (Jul 1)    (amber)
      dept_nudge         • any category avg resolution > 10 days     (orange)
      anomaly            • today's volume > 3× 30-day daily average  (red_bold)
    """
    now   = datetime.now(timezone.utc)
    since = now - timedelta(days=days)

    base    = _apply_scope(db.query(Report), scope, scope_id, current_user, db)
    current = base.filter(Report.created_at >= since).all()
    total   = len(current)

    alerts = []

    # ── 1. Area Warning — re-report rate > 30% ───────────────────────────────
    re_count = sum(1 for r in current if r.duplicate_of_id)
    re_rate  = round(re_count / total * 100, 1) if total else 0.0
    if re_rate > 30:
        alerts.append({
            "type":    "area_warning",
            "message": f"Re-report rate {re_rate}% — field verification recommended",
        })

    # ── 2. Resource Suggestion — pending > 50 and forecast rising ────────────
    pending_count = sum(
        1 for r in current if r.kanban_stage != KanbanStage.RESOLVED
    )
    half       = days // 2
    mid        = now - timedelta(days=half)
    recent_cnt = sum(1 for r in current if _to_utc(r.created_at) >= mid)
    prior_cnt  = total - recent_cnt
    trending_up = recent_cnt > prior_cnt * 1.10

    if pending_count > 50 and trending_up:
        extra = max(1, round((pending_count - 50) / 25))
        alerts.append({
            "type":    "resource_suggest",
            "message": f"Assign {extra} extra field worker{'s' if extra > 1 else ''} this week",
        })

    # ── 3. Seasonal Prediction — within 90 days of monsoon (Jul 1) ───────────
    monsoon = now.replace(month=7, day=1, hour=0, minute=0, second=0, microsecond=0)
    if now >= monsoon:
        monsoon = monsoon.replace(year=monsoon.year + 1)
    if (monsoon - now).days <= 90:
        alerts.append({
            "type":    "seasonal",
            "message": "Pothole spike expected — monsoon approaching",
        })

    # ── 4. Department Nudge — any category avg resolution > 10 days ──────────
    cat_durations: dict = {}
    for r in current:
        if r.kanban_stage == KanbanStage.RESOLVED and r.created_at and r.updated_at:
            d = (_to_utc(r.updated_at) - _to_utc(r.created_at)).total_seconds() / 86400
            if 0 < d < 365:
                cat = r.category.value if r.category else "UNKNOWN"
                cat_durations.setdefault(cat, []).append(d)

    for cat, durations in cat_durations.items():
        avg_d = round(sum(durations) / len(durations), 1)
        if avg_d > 10:
            label = _CATEGORY_LABEL.get(cat, cat)
            alerts.append({
                "type":    "dept_nudge",
                "message": f"{label} avg {avg_d}d — target is 5d",
            })

    # ── 5. Anomaly Alert — today's volume > 3× daily average ─────────────────
    daily_avg   = total / days if days else 0
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_count = sum(1 for r in current if _to_utc(r.created_at) >= today_start)

    if daily_avg > 0 and today_count >= daily_avg * 3:
        area = scope_id.split("_")[0].title() if scope_id else "This area"
        alerts.append({
            "type":    "anomaly",
            "message": f"{area} volume spiked 3× today — investigate",
        })

    # ── All clear ─────────────────────────────────────────────────────────────
    if not alerts:
        alerts.append({
            "type":    "ok",
            "message": "All metrics within normal range — no active alerts.",
        })

    return {"alerts": alerts, "total": len(alerts)}


# ---------------------------------------------------------------------------
# MODULE 5 — Available scopes (powers the ScopeTabStrip)
# ---------------------------------------------------------------------------
@router.get("/scopes")
def get_scopes(
    current_user: User = Depends(ALL_ADMIN),
    db: Session = Depends(get_db),
):
    """
    Returns the cities and departments the current user can filter by.
    dept_officer  → their single city+dept (no switching)
    city_admin    → their city + all its departments
    super_admin   → all cities + all their departments
    """
    role = (current_user.role or "").lower()

    if role == "dept_officer":
        routing = db.query(RoutingTable).filter_by(
            officer_id=current_user.id, is_active=True
        ).first()
        if routing:
            return {
                "cities": [{"id": routing.city, "label": routing.city.title()}],
                "departments": {
                    routing.city: [{"id": routing.department, "label": routing.department_name}]
                },
            }
        return {"cities": [], "departments": {}}

    if role == "city_admin":
        city = current_user.city or ""
        rows = db.query(RoutingTable).filter_by(city=city, is_active=True).all()
        depts = [{"id": r.department, "label": r.department_name} for r in rows]
        return {
            "cities": [{"id": city, "label": city.title()}],
            "departments": {city: depts},
        }

    # super_admin — everything
    rows = db.query(RoutingTable).filter_by(is_active=True).all()
    city_map: dict = {}
    for r in rows:
        if r.city not in city_map:
            city_map[r.city] = []
        city_map[r.city].append({"id": r.department, "label": r.department_name})

    return {
        "cities": [{"id": c, "label": c.title()} for c in sorted(city_map)],
        "departments": {c: depts for c, depts in city_map.items()},
    }


# ---------------------------------------------------------------------------
# MODULE 6 — City overview cards (super_admin only)
# ---------------------------------------------------------------------------
SUPER_ADMIN_ONLY = require_roles("super_admin")


def _risk_level(re_rate: float, avg_res: float) -> str:
    if re_rate > 25 or avg_res > 7:
        return "HIGH"
    if re_rate > 12 or avg_res > 4:
        return "MED"
    return "LOW"


@router.get("/city-overview")
def get_city_overview(
    days: int = Query(30, ge=7, le=365),
    current_user: User = Depends(SUPER_ADMIN_ONLY),
    db: Session = Depends(get_db),
):
    """
    Rich per-city stats for the super_admin unified dashboard.
    Includes: risk level, admin name, civic score, bottleneck + avg days, 30d forecast.
    """
    now   = datetime.now(timezone.utc)
    since = now - timedelta(days=days)
    mid   = now - timedelta(days=days // 2)   # for forecast split

    reports = db.query(Report).filter(Report.created_at >= since).all()

    # First active officer per city (for admin name)
    routing_rows = db.query(RoutingTable).filter_by(is_active=True).all()
    city_officer: dict = {}
    for row in routing_rows:
        if row.city not in city_officer and row.officer:
            city_officer[row.city] = (
                f"{row.officer.first_name} {row.officer.last_name}"
            )

    # Group by city
    city_map: dict = {}
    for r in reports:
        city = (r.assigned_city or "unassigned").lower()
        city_map.setdefault(city, []).append(r)

    def _stats(reps):
        total    = len(reps)
        resolved = sum(1 for r in reps if r.kanban_stage == KanbanStage.RESOLVED)
        re_count = sum(1 for r in reps if r.duplicate_of_id)
        re_rate  = round(re_count / total * 100, 1) if total else 0.0

        # Avg resolution (RESOLVED reports only)
        durations = []
        for r in reps:
            if r.kanban_stage == KanbanStage.RESOLVED and r.created_at and r.updated_at:
                d = (_to_utc(r.updated_at) - _to_utc(r.created_at)).total_seconds() / 86400
                if 0 < d < 365:
                    durations.append(d)
        avg_res = round(sum(durations) / len(durations), 1) if durations else 0.0

        # Civic score (avg community_score)
        scores      = [r.community_score for r in reps if r.community_score is not None]
        civic_score = round(sum(scores) / len(scores)) if scores else None

        # Top category with percentage
        cat_counts   = Counter(r.category.value if r.category else "UNKNOWN" for r in reps)
        top_cat      = max(cat_counts, key=cat_counts.get) if cat_counts else None
        top_cat_pct  = round(cat_counts[top_cat] / total * 100) if top_cat and total else 0

        # Bottleneck stage (non-RESOLVED with most reports)
        stage_counts = Counter(
            r.kanban_stage.value if r.kanban_stage else "NEW" for r in reps
        )
        non_res      = {k: v for k, v in stage_counts.items() if k != "RESOLVED"}
        bn_stage     = max(non_res, key=non_res.get) if non_res else None

        # Bottleneck avg days: use (now - updated_at) for reports stuck in that stage
        bn_avg_days = None
        if bn_stage:
            bn_reps  = [r for r in reps if r.kanban_stage and r.kanban_stage.value == bn_stage]
            bn_times = []
            for r in bn_reps:
                if r.updated_at:
                    d = (now - _to_utc(r.updated_at)).total_seconds() / 86400
                    if 0 <= d < 365:
                        bn_times.append(d)
            if bn_times:
                bn_avg_days = round(sum(bn_times) / len(bn_times), 1)

        # 30d forecast: compare recent half vs prior half
        recent = sum(1 for r in reps if _to_utc(r.created_at) >= mid)
        prior  = total - recent
        rate_r = recent / (days / 2)
        rate_p = prior  / (days / 2)
        forecast_delta = round((rate_r - rate_p) * days)

        return {
            "total":         total,
            "pending":       total - resolved,
            "resolved":      resolved,
            "resolved_pct":  round(resolved / total * 100, 1) if total else 0.0,
            "re_rate":       re_rate,
            "avg_res_days":  avg_res,
            "civic_score":   civic_score,
            "top_category":  _CATEGORY_LABEL.get(top_cat, top_cat) if top_cat else None,
            "top_cat_pct":   top_cat_pct,
            "bottleneck":    _STAGE_LABELS.get(bn_stage, bn_stage) if bn_stage else None,
            "bn_avg_days":   bn_avg_days,
            "forecast_delta": forecast_delta,
            "risk":          _risk_level(re_rate, avg_res),
        }

    cities = []
    for city, reps in sorted(city_map.items()):
        s = _stats(reps)
        cities.append({
            "city":       city,
            "label":      city.title(),
            "admin_name": city_officer.get(city),
            **s,
        })

    agg = _stats(reports) if reports else {}

    return {"cities": cities, "aggregate": agg}
