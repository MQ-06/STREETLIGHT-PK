"""
Transactional email: Mailjet (HTTPS), Brevo (HTTPS), or Gmail SMTP (TLS).

Mailjet (API key + secret — works well on PaaS without SMTP egress issues):
    MAILJET_API_KEY     = public API key (Mailjet → Account → API Keys)
    MAILJET_SECRET_KEY  = secret key (same screen)
    EMAIL_FROM          = verified sender address (must match Mailjet sender)

Brevo:
    BREVO_API_KEY       = xkeysib-...
    BREVO_SENDER_EMAIL  = verified sender in Brevo

Gmail SMTP (fallback):
    SMTP_USER, SMTP_PASSWORD (App Password)

Shared optional:
    SMTP_FROM_NAME      = display name (default "StreetLight")
    ADMIN_BASE_URL      = admin SPA origin for links

Order when sending: Mailjet → Brevo → SMTP (first success wins).
"""
from __future__ import annotations

import logging
import os
import smtplib
import socket
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

SMTP_HOST         = "smtp.gmail.com"
SMTP_PORT         = 587
BREVO_API_URL     = "https://api.brevo.com/v3/smtp/email"
MAILJET_SEND_URL  = "https://api.mailjet.com/v3.1/send"


class _SMTPIPv4(smtplib.SMTP):
    """
    Connect via IPv4 only. Many PaaS hosts (e.g. Render) have no IPv6 egress;
    getaddrinfo() may return AAAA first → connect raises Errno 101 ENETUNREACH.
    """

    def _get_socket(self, host, port, timeout):  # type: ignore[override]
        last_exc: Optional[OSError] = None
        for res in socket.getaddrinfo(host, port, socket.AF_INET, socket.SOCK_STREAM):
            af, socktype, proto, _canon, sa = res
            sock = socket.socket(af, socktype, proto)
            sock.settimeout(timeout)
            try:
                sock.connect(sa)
                return sock
            except OSError as exc:
                last_exc = exc
                sock.close()
        if last_exc:
            raise last_exc
        raise OSError(f"No IPv4 route to {host!r} port {port}")


def _brevo_configured() -> bool:
    return bool(
        os.getenv("BREVO_API_KEY", "").strip()
        and os.getenv("BREVO_SENDER_EMAIL", "").strip()
    )


def _mailjet_configured() -> bool:
    return bool(
        os.getenv("MAILJET_API_KEY", "").strip()
        and os.getenv("MAILJET_SECRET_KEY", "").strip()
        and os.getenv("EMAIL_FROM", "").strip()
    )


def _any_provider_configured() -> bool:
    return _mailjet_configured() or _brevo_configured() or _smtp_configured()


def _from_email_for_header() -> str:
    """MIME From address when using Mailjet/Brevo/Gmail-only setups."""
    return (
        os.getenv("SMTP_USER", "").strip()
        or os.getenv("BREVO_SENDER_EMAIL", "").strip()
        or os.getenv("EMAIL_FROM", "").strip()
    )


def _smtp_configured() -> bool:
    return bool(os.getenv("SMTP_USER", "").strip() and os.getenv("SMTP_PASSWORD", "").strip())


def _send_html_via_brevo(
    *,
    to_email: str,
    subject: str,
    html: str,
    from_name: str,
    sender_email: str,
    api_key: str,
) -> bool:
    try:
        r = httpx.post(
            BREVO_API_URL,
            headers={
                "accept": "application/json",
                "api-key": api_key,
                "content-type": "application/json",
            },
            json={
                "sender": {"name": from_name, "email": sender_email},
                "to": [{"email": to_email}],
                "subject": subject,
                "htmlContent": html,
            },
            timeout=30.0,
        )
        if r.is_success:
            return True
        logger.warning(
            "Brevo HTTP %s: %s",
            r.status_code,
            (r.text or "")[:500],
        )
        return False
    except Exception as exc:
        logger.warning("Brevo request failed: %s", exc)
        return False


def _send_html_via_mailjet(
    *,
    to_email: str,
    subject: str,
    html: str,
    from_name: str,
    sender_email: str,
    api_key: str,
    secret_key: str,
) -> bool:
    """Mailjet REST v3.1 — Basic auth (API key + secret)."""
    try:
        r = httpx.post(
            MAILJET_SEND_URL,
            auth=(api_key, secret_key),
            headers={"Content-Type": "application/json"},
            json={
                "Messages": [
                    {
                        "From": {
                            "Email": sender_email,
                            "Name": from_name,
                        },
                        "To": [{"Email": to_email}],
                        "Subject": subject,
                        "HTMLPart": html,
                    }
                ]
            },
            timeout=30.0,
        )
        if r.is_success:
            return True
        logger.warning(
            "Mailjet HTTP %s: %s",
            r.status_code,
            (r.text or "")[:500],
        )
        return False
    except Exception as exc:
        logger.warning("Mailjet request failed: %s", exc)
        return False


def _send_mime_via_smtp(
    *,
    to_email: str,
    msg: MIMEMultipart,
    smtp_user: str,
    smtp_pass: str,
) -> bool:
    try:
        with _SMTPIPv4(SMTP_HOST, SMTP_PORT, timeout=15) as server:
            server.ehlo()
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, [to_email], msg.as_string())
        return True
    except Exception as exc:
        logger.warning("SMTP send failed: %s", exc)
        return False


def _send_html_email(
    *,
    to_email: str,
    subject: str,
    html: str,
    from_name: str,
    smtp_msg: MIMEMultipart,
    smtp_user: str,
    smtp_pass: str,
    ok_log: str,
    fail_log: str,
) -> bool:
    """
    Mailjet → Brevo → Gmail SMTP. First success wins; HTTP APIs tried before SMTP.
    """
    mj_key = os.getenv("MAILJET_API_KEY", "").strip()
    mj_secret = os.getenv("MAILJET_SECRET_KEY", "").strip()
    mj_from = os.getenv("EMAIL_FROM", "").strip()

    if mj_key and mj_secret and mj_from:
        if _send_html_via_mailjet(
            to_email=to_email,
            subject=subject,
            html=html,
            from_name=from_name,
            sender_email=mj_from,
            api_key=mj_key,
            secret_key=mj_secret,
        ):
            logger.info(ok_log)
            return True
        logger.warning("Mailjet failed for %s; trying next provider.", to_email)

    api_key = os.getenv("BREVO_API_KEY", "").strip()
    sender_email = os.getenv("BREVO_SENDER_EMAIL", "").strip()

    if api_key and sender_email:
        if _send_html_via_brevo(
            to_email=to_email,
            subject=subject,
            html=html,
            from_name=from_name,
            sender_email=sender_email,
            api_key=api_key,
        ):
            logger.info(ok_log)
            return True
        if smtp_user and smtp_pass:
            logger.warning("Brevo failed for %s; trying SMTP fallback.", to_email)

    if smtp_user and smtp_pass:
        if _send_mime_via_smtp(
            to_email=to_email,
            msg=smtp_msg,
            smtp_user=smtp_user,
            smtp_pass=smtp_pass,
        ):
            logger.info(ok_log)
            return True

    logger.warning(fail_log)
    return False


def _build_html(
    *,
    report_id: int,
    display_id: str,
    category: str,
    severity: str,
    city: str,
    department: str,
    officer_name: str,
    description: Optional[str],
    lat: float,
    lng: float,
    admin_url: str,
) -> str:
    desc_block = (
        f'<p style="margin:0 0 8px 0;color:#374151;font-size:14px;">'
        f'<strong>Description:</strong> {description}</p>'
    ) if description else ""

    severity_color = {
        "high":   "#EF4444",
        "medium": "#F97316",
        "low":    "#22C55E",
    }.get((severity or "").lower(), "#6B7280")

    category_display = (category or "").replace("_", " ").title()
    city_display     = (city or "").capitalize()
    dept_display     = (department or "").upper()

    return f"""
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#F7F6E8;font-family:'Segoe UI',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#F7F6E8;padding:32px 0;">
    <tr><td align="center">
      <table width="560" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,0.08);">

        <!-- Header -->
        <tr>
          <td style="background:#B85C2E;padding:28px 32px;">
            <h1 style="margin:0;color:#ffffff;font-size:22px;font-weight:800;letter-spacing:-0.5px;">
              🔔 New Report Assigned
            </h1>
            <p style="margin:6px 0 0 0;color:#f5ddd1;font-size:13px;">
              StreetLight Municipal Platform
            </p>
          </td>
        </tr>

        <!-- Body -->
        <tr>
          <td style="padding:28px 32px;">
            <p style="margin:0 0 20px 0;color:#111827;font-size:15px;">
              Dear <strong>{officer_name}</strong>,
            </p>
            <p style="margin:0 0 20px 0;color:#374151;font-size:14px;line-height:1.6;">
              A new civic issue has been reported in your area and automatically assigned
              to your department (<strong>{dept_display}</strong>, {city_display}).
              Please review it at your earliest convenience.
            </p>

            <!-- Report card -->
            <table width="100%" cellpadding="0" cellspacing="0"
                   style="background:#F7F6E8;border-radius:12px;border:1px solid #EDE8DC;margin-bottom:24px;">
              <tr>
                <td style="padding:20px 24px;">
                  <p style="margin:0 0 12px 0;font-size:11px;font-weight:700;letter-spacing:2px;color:#9CA3AF;text-transform:uppercase;">Report Details</p>

                  <table width="100%" cellpadding="0" cellspacing="0">
                    <tr>
                      <td style="padding:5px 0;">
                        <span style="font-size:13px;color:#6B7280;width:130px;display:inline-block;">Report ID</span>
                        <span style="font-size:13px;font-weight:700;color:#111827;">{display_id}</span>
                      </td>
                    </tr>
                    <tr>
                      <td style="padding:5px 0;">
                        <span style="font-size:13px;color:#6B7280;width:130px;display:inline-block;">Category</span>
                        <span style="font-size:13px;font-weight:600;color:#111827;">{category_display}</span>
                      </td>
                    </tr>
                    <tr>
                      <td style="padding:5px 0;">
                        <span style="font-size:13px;color:#6B7280;width:130px;display:inline-block;">Severity</span>
                        <span style="font-size:13px;font-weight:700;color:{severity_color};">{(severity or 'Unknown').upper()}</span>
                      </td>
                    </tr>
                    <tr>
                      <td style="padding:5px 0;">
                        <span style="font-size:13px;color:#6B7280;width:130px;display:inline-block;">City / Dept</span>
                        <span style="font-size:13px;font-weight:600;color:#111827;">{city_display} — {dept_display}</span>
                      </td>
                    </tr>
                    <tr>
                      <td style="padding:5px 0;">
                        <span style="font-size:13px;color:#6B7280;width:130px;display:inline-block;">GPS</span>
                        <span style="font-size:13px;color:#111827;">{lat:.5f}, {lng:.5f}</span>
                      </td>
                    </tr>
                  </table>

                  {desc_block}
                </td>
              </tr>
            </table>

            <!-- CTA button -->
            <table cellpadding="0" cellspacing="0" style="margin-bottom:24px;">
              <tr>
                <td style="background:#B85C2E;border-radius:10px;">
                  <a href="{admin_url}/complaint-detail/{report_id}"
                     style="display:inline-block;padding:12px 28px;color:#ffffff;font-size:14px;font-weight:700;text-decoration:none;">
                    View Report in Dashboard →
                  </a>
                </td>
              </tr>
            </table>

            <p style="margin:0;color:#9CA3AF;font-size:12px;line-height:1.6;">
              You are receiving this because you are the assigned officer for
              <strong>{dept_display}</strong> in <strong>{city_display}</strong>.
              Log in to the StreetLight Admin Portal to update the report status.
            </p>
          </td>
        </tr>

        <!-- Footer -->
        <tr>
          <td style="background:#F7F6E8;border-top:1px solid #EDE8DC;padding:16px 32px;">
            <p style="margin:0;color:#9CA3AF;font-size:11px;text-align:center;">
              StreetLight — AI-Powered Civic Issue Reporting System &nbsp;|&nbsp; Do not reply to this email.
            </p>
          </td>
        </tr>

      </table>
    </td></tr>
  </table>
</body>
</html>
"""


def send_resolved_notification(
    *,
    to_email: str,
    citizen_name: str,
    report_id: int,
    display_id: str,
    category: str,
    city: str,
    department: str,
    admin_url: Optional[str] = None,
) -> bool:
    """Send a 'your report has been resolved' email to the citizen."""
    smtp_user = os.getenv("SMTP_USER", "").strip()
    smtp_pass = os.getenv("SMTP_PASSWORD", "").strip()
    from_name = os.getenv("SMTP_FROM_NAME", "StreetLight")
    base_url  = admin_url or os.getenv("ADMIN_BASE_URL", "http://localhost:5173").rstrip("/")

    if not _any_provider_configured():
        logger.warning(
            "Resolved email skipped: set MAILJET_* + EMAIL_FROM "
            "and/or BREVO_* and/or SMTP_USER + SMTP_PASSWORD"
        )
        return False
    if not to_email or "@" not in to_email:
        return False

    category_display = (category or "").replace("_", " ").title()
    city_display     = (city or "").capitalize()
    dept_display     = (department or "").upper()
    subject          = f"[StreetLight] Your Report Has Been Resolved — {display_id}"

    html = f"""
<!DOCTYPE html>
<html><head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#F7F6E8;font-family:'Segoe UI',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#F7F6E8;padding:32px 0;">
    <tr><td align="center">
      <table width="560" cellpadding="0" cellspacing="0" style="background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,0.08);">
        <tr>
          <td style="background:#22C55E;padding:28px 32px;">
            <h1 style="margin:0;color:#fff;font-size:22px;font-weight:800;">✅ Issue Resolved!</h1>
            <p style="margin:6px 0 0 0;color:#dcfce7;font-size:13px;">StreetLight Municipal Platform</p>
          </td>
        </tr>
        <tr>
          <td style="padding:28px 32px;">
            <p style="margin:0 0 16px 0;color:#111827;font-size:15px;">Dear <strong>{citizen_name}</strong>,</p>
            <p style="margin:0 0 20px 0;color:#374151;font-size:14px;line-height:1.6;">
              Great news! The civic issue you reported has been resolved by the
              <strong>{dept_display}</strong> department in <strong>{city_display}</strong>.
              Thank you for helping improve your city.
            </p>
            <table width="100%" cellpadding="0" cellspacing="0"
                   style="background:#F7F6E8;border-radius:12px;border:1px solid #EDE8DC;margin-bottom:24px;">
              <tr><td style="padding:20px 24px;">
                <p style="margin:0 0 12px 0;font-size:11px;font-weight:700;letter-spacing:2px;color:#9CA3AF;text-transform:uppercase;">Report Details</p>
                <p style="margin:0 0 8px 0;font-size:13px;color:#374151;"><span style="color:#6B7280;display:inline-block;width:120px;">Report ID</span><strong>{display_id}</strong></p>
                <p style="margin:0 0 8px 0;font-size:13px;color:#374151;"><span style="color:#6B7280;display:inline-block;width:120px;">Category</span>{category_display}</p>
                <p style="margin:0;font-size:13px;color:#374151;"><span style="color:#6B7280;display:inline-block;width:120px;">Resolved by</span>{dept_display}, {city_display}</p>
              </td></tr>
            </table>
            <p style="margin:0;color:#9CA3AF;font-size:12px;line-height:1.6;">
              If the issue persists, please submit a new report via the StreetLight app.
            </p>
          </td>
        </tr>
        <tr>
          <td style="background:#F7F6E8;border-top:1px solid #EDE8DC;padding:16px 32px;">
            <p style="margin:0;color:#9CA3AF;font-size:11px;text-align:center;">StreetLight — AI-Powered Civic Issue Reporting System</p>
          </td>
        </tr>
      </table>
    </td></tr>
  </table>
</body></html>
"""

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = f"{from_name} <{_from_email_for_header()}>"
    msg["To"]      = to_email
    msg.attach(MIMEText(html, "html"))

    return _send_html_email(
        to_email=to_email,
        subject=subject,
        html=html,
        from_name=from_name,
        smtp_msg=msg,
        smtp_user=smtp_user,
        smtp_pass=smtp_pass,
        ok_log=f"✅ Resolved email sent → {to_email} for report {display_id}",
        fail_log=f"⚠️ Resolved email failed → {to_email} (Mailjet / Brevo / SMTP exhausted)",
    )


def send_new_report_notification(
    *,
    to_email: str,
    officer_name: str,
    report_id: int,
    display_id: str,
    category: str,
    severity: str,
    city: str,
    department: str,
    description: Optional[str],
    lat: float,
    lng: float,
) -> bool:
    """
    Send a 'new report assigned' email to a dept officer.
    Returns True if sent, False if skipped/failed (non-blocking).
    """
    smtp_user = os.getenv("SMTP_USER", "").strip()
    smtp_pass = os.getenv("SMTP_PASSWORD", "").strip()
    from_name = os.getenv("SMTP_FROM_NAME", "StreetLight")
    admin_url = os.getenv("ADMIN_BASE_URL", "http://localhost:5173").rstrip("/")

    if not _any_provider_configured():
        logger.warning(
            "Email skipped: set MAILJET_* + EMAIL_FROM "
            "and/or BREVO_* and/or SMTP_USER + SMTP_PASSWORD"
        )
        return False

    if not to_email or "@" not in to_email:
        logger.warning(f"Email skipped: invalid notification_email '{to_email}'")
        return False

    subject = f"[StreetLight] New Report Assigned — {display_id} ({(category or '').replace('_',' ').title()})"

    html_body = _build_html(
        report_id    = report_id,
        display_id   = display_id,
        category     = category,
        severity     = severity,
        city         = city,
        department   = department,
        officer_name = officer_name,
        description  = description,
        lat          = lat,
        lng          = lng,
        admin_url    = admin_url,
    )

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = f"{from_name} <{_from_email_for_header()}>"
    msg["To"]      = to_email
    msg.attach(MIMEText(html_body, "html"))

    return _send_html_email(
        to_email=to_email,
        subject=subject,
        html=html_body,
        from_name=from_name,
        smtp_msg=msg,
        smtp_user=smtp_user,
        smtp_pass=smtp_pass,
        ok_log=f"✅ Email sent → {to_email} for report {display_id}",
        fail_log=f"⚠️ Email failed → {to_email} (Mailjet / Brevo / SMTP exhausted)",
    )
