"""PDF export for scoped municipal analytics (ASCII-safe for core PDF fonts + colour sections)."""
from __future__ import annotations

from typing import Any


def _txt(s: Any) -> str:
    if s is None:
        return ""
    t = str(s)
    return t.encode("latin-1", "replace").decode("latin-1")


def render_analytics_pdf(summary: dict) -> bytes:
    from fpdf import FPDF
    from fpdf.enums import XPos, YPos

    ORANGE = (232, 97, 45)
    SLATE = (55, 65, 81)
    GREEN = (34, 197, 94)
    AMBER = (217, 119, 6)
    BLUE = (59, 130, 246)
    RED_PRI = (220, 38, 38)

    class PDF(FPDF):
        def footer(self) -> None:
            self.set_y(-12)
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(100, 100, 100)
            self.cell(0, 8, _txt(f"Page {self.page_no()}"), align="C")

    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=16)
    pdf.add_page()

    def mc(text: str, h: float = 5) -> None:
        pdf.multi_cell(
            pdf.epw,
            h,
            _txt(text),
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
        )

    def band(title: str, rgb: tuple[int, int, int]) -> None:
        pdf.set_fill_color(*rgb)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(pdf.epw, 7, _txt(title), new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True)
        pdf.set_text_color(33, 37, 41)
        pdf.ln(1)

    # ── Title ribbon ───────────────────────────────────────────────────────────
    pdf.set_fill_color(*ORANGE)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 15)
    pdf.cell(pdf.epw, 11, _txt("StreetLight — Municipal Analytics Report"), align="C",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True)
    pdf.set_text_color(66, 66, 66)
    pdf.set_font("Helvetica", size=9)
    mc(summary.get("subtitle") or "", h=5)
    pdf.ln(3)

    # ── Key numbers table ──────────────────────────────────────────────────────
    band("Key numbers", ORANGE)
    rows = summary.get("stats_table") or []
    w_k = pdf.epw * 0.58
    w_v = pdf.epw * 0.42
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(243, 244, 246)
    pdf.cell(w_k, 6, _txt("Metric"), border=1, fill=True)
    pdf.cell(w_v, 6, _txt("Value"), border=1, fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Helvetica", size=9)
    for i, row in enumerate(rows):
        zebra = (i % 2) == 1
        pdf.set_fill_color(249, 250, 251) if zebra else pdf.set_fill_color(255, 255, 255)
        pdf.cell(w_k, 6, _txt(row.get("label", "")), border=1, fill=True)
        pdf.cell(w_v, 6, _txt(row.get("value", "")), border=1, fill=True,
                 new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(3)

    # ── Complaints by type (counts + %) + coloured bars ─────────────────────────
    band("Complaints by type", SLATE)
    cats = summary.get("categories") or []
    label_w = 48
    cnt_w = 14
    pct_w = 16
    bar_slot = pdf.epw - label_w - cnt_w - pct_w
    pdf.set_font("Helvetica", "", 8)
    for c in cats:
        name = c.get("name", "")
        cnt = c.get("count", 0)
        pct = float(c.get("pct") or 0)
        line_top = pdf.get_y()
        pdf.set_x(pdf.l_margin)
        pdf.cell(label_w, 6, _txt(str(name)), border=0)
        pdf.cell(cnt_w, 6, _txt(str(cnt)), border=0)
        pdf.cell(pct_w, 6, _txt(f"{pct}%"), border=0)
        bx = pdf.get_x()
        bw = max(bar_slot * (pct / 100.0), 1.2 if pct > 0 else 0)
        if "Garbage" in name or "waste" in name.lower():
            pdf.set_fill_color(*AMBER)
        else:
            pdf.set_fill_color(*GREEN)
        pdf.rect(bx, line_top + 1.4, min(bw, bar_slot), 3.8, style="F")
        pdf.set_xy(pdf.l_margin, line_top + 6.5)
    pdf.ln(2)

    # ── Pipeline stages ──────────────────────────────────────────────────────────
    band("Pipeline — complaints per stage", BLUE)
    stages = summary.get("stage_rows") or []
    w_s = pdf.epw * 0.42
    w_n = pdf.epw * 0.58
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(239, 246, 255)
    pdf.cell(w_s, 6, _txt("Stage"), border=1, fill=True)
    pdf.cell(w_n, 6, _txt("Count"), border=1, fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Helvetica", size=9)
    for i, srow in enumerate(stages):
        zebra = (i % 2) == 1
        pdf.set_fill_color(249, 250, 251) if zebra else pdf.set_fill_color(255, 255, 255)
        pdf.cell(w_s, 6, _txt(str(srow.get("label", srow.get("key", "")))), border=1, fill=True)
        pdf.cell(w_n, 6, _txt(str(srow.get("count", 0))), border=1, fill=True,
                 new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(3)

    # ── Alerts ─────────────────────────────────────────────────────────────────
    band("Alerts — plain reading of your complaint numbers", ORANGE)
    pdf.set_font("Helvetica", size=9)
    pdf.set_text_color(55, 65, 81)
    for line in summary.get("alert_lines") or []:
        mc(f"* {line}", h=5)
    pdf.set_text_color(33, 37, 41)
    pdf.ln(2)

    # ── Recommendations (colour by priority) ─────────────────────────────────
    band("Recommendations — tied to those same counts", GREEN)
    pdf.set_font("Helvetica", size=9)
    pri_rgb = {"high": RED_PRI, "medium": AMBER, "low": SLATE}
    tag_txt = {"high": "DO FIRST", "medium": "DO SOON", "low": "NOTE"}
    for r in summary.get("recommendations") or []:
        pri = (r.get("priority") or "low").lower()
        rgb = pri_rgb.get(pri, SLATE)
        pdf.set_fill_color(*rgb)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 9)
        title = str(r.get("title") or "")
        pdf.cell(
            pdf.epw,
            6,
            _txt(f"{tag_txt.get(pri, 'NOTE')}: {title}"),
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
            fill=True,
        )
        pdf.set_text_color(33, 37, 41)
        pdf.set_font("Helvetica", "", 9)
        mc(str(r.get("detail") or ""), h=5)
        pdf.ln(1)

    pdf.ln(2)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(120, 120, 120)
    mc(
        "Note: Coloured charts summarise complaint data for this scope and period only. "
        "They support decisions — they do not replace site visits or weather services.",
        h=4,
    )

    raw = pdf.output(dest="S")
    return bytes(raw)
