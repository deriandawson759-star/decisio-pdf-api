"""
DECISIO — Email Notifications
Alerte équipe lors d'un nouveau prospect (via SMTP ou SendGrid).
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


TEAM_EMAIL = os.environ.get('DECISIO_TEAM_EMAIL', '')
SMTP_HOST  = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT  = int(os.environ.get('SMTP_PORT', '587'))
SMTP_USER  = os.environ.get('SMTP_USER', '')
SMTP_PASS  = os.environ.get('SMTP_PASS', '')


def notify_new_prospect(client_data: dict, scores: dict) -> bool:
    """
    Envoie un email d'alerte à l'équipe DECISIO pour un nouveau prospect.
    Retourne True si envoyé avec succès.
    """
    if not all([TEAM_EMAIL, SMTP_USER, SMTP_PASS]):
        # Variables SMTP non configurées — silencieux
        return False

    nom     = client_data.get('nom', 'Client')
    secteur = client_data.get('secteur', '')
    mode    = client_data.get('mode', 'premium')
    score   = scores.get('global_score', 'N/A')
    maturite = scores.get('maturity_level', '')

    prix_map = {
        'flash':          '490€',
        'premium':        '2 490€',
        'transformation': '6 900€',
        'redressement':   '9 900€',
    }
    prix = prix_map.get(mode.lower(), mode)

    subject = f"[DECISIO] Nouveau prospect — {nom} ({secteur})"

    body = f"""
<h2 style="color:#0B2B4E;">Nouveau prospect DECISIO</h2>
<table style="font-family:sans-serif;font-size:14px;border-collapse:collapse;">
  <tr><td style="padding:6px 16px 6px 0;color:#666;">Nom</td>
      <td style="padding:6px 0;font-weight:bold;">{nom}</td></tr>
  <tr><td style="padding:6px 16px 6px 0;color:#666;">Secteur</td>
      <td style="padding:6px 0;">{secteur}</td></tr>
  <tr><td style="padding:6px 16px 6px 0;color:#666;">Offre</td>
      <td style="padding:6px 0;font-weight:bold;color:#C9A84C;">{mode.upper()} — {prix}</td></tr>
  <tr><td style="padding:6px 16px 6px 0;color:#666;">Score global</td>
      <td style="padding:6px 0;">{score}/10 — {maturite}</td></tr>
</table>
<p style="font-family:sans-serif;font-size:13px;color:#888;margin-top:16px;">
  Connectez-vous au dashboard DECISIO pour voir l'analyse complète.
</p>
""".strip()

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From']    = SMTP_USER
    msg['To']      = TEAM_EMAIL
    msg.attach(MIMEText(body, 'html'))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, TEAM_EMAIL, msg.as_string())
        print(f"[Notify] Email envoyé à {TEAM_EMAIL} pour {nom}")
        return True
    except Exception as e:
        print(f"[Notify] Erreur envoi email: {e}")
        return False
