"""
DECISIO PDF Generator V9 — DocRaptor
HTML/CSS → PDF niveau cabinet conseil premium.
"""
import re
import requests
import base64
from datetime import datetime

NAVY      = '#1C2B4A'
GOLD      = '#C9A84C'
LIGHT_BG  = '#F7F8FA'
BORDER    = '#E2E5EB'
TEXT      = '#1A1A2E'
MUTED     = '#6B7280'
WHITE     = '#FFFFFF'
RED_ACC   = '#C0392B'
GREEN_ACC = '#1A7A45'
BLUE_ACC  = '#2563A8'
ORANGE    = '#C4621A'

DOCRAPTOR_API_KEY = 'xwOLiOzjmLgknBf9eA8H'

MODE_LABELS = {
    'flash':          'AUDIT FLASH  ·  490 €',
    'premium':        'AUDIT STRATÉGIQUE PREMIUM  ·  2 490 €',
    'transformation': 'AUDIT TRANSFORMATION  ·  6 900 €',
    'redressement':   'AUDIT REDRESSEMENT  ·  9 900 €',
    'diagnostic':     'DIAGNOSTIC GRATUIT',
}

PRICE_MAP = {
    'flash': '490 €', 'premium': '2 490 €',
    'transformation': '6 900 €', 'redressement': '9 900 €',
    'diagnostic': 'Gratuit',
}

EMOJI_MAP = {
    '🏆':'', '⚡':'', '🔴':'●', '🟡':'●', '🟢':'●', '🎯':'',
    '✅':'✓', '🛑':'■', '🔄':'↺', '→':'→', '←':'←', '↑':'↑', '↓':'↓',
    '\u2014':' – ', '\u2013':' – ', '\u2026':'...', '\u00d7':'x',
}

def clean(s):
    s = str(s)
    for k, v in EMOJI_MAP.items():
        s = s.replace(k, v)
    return s

def clean_html(s):
    s = clean(s)
    s = s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'\*(.+?)\*', r'<em>\1</em>', s)
    s = s.replace('&lt;strong&gt;','<strong>').replace('&lt;/strong&gt;','</strong>')
    s = s.replace('&lt;em&gt;','<em>').replace('&lt;/em&gt;','</em>')
    return s

def _section_color(txt):
    t = txt.upper()
    if any(x in t for x in ['EXEC','SYNTH','EXECUTIV']): return GOLD
    if any(x in t for x in ['QUICK','WIN','48H']):        return GREEN_ACC
    if any(x in t for x in ['DIAG','PARTIE 1','1 —']):   return RED_ACC
    if any(x in t for x in ['DECIS','PARTIE 2','2 —']):  return ORANGE
    if any(x in t for x in ['DEPLOY','PARTIE 3','3 —']): return GREEN_ACC
    if any(x in t for x in ['LOIN','COMPLEM','SUITE']):  return '#5B3FA6'
    return NAVY

def _render_chart(data):
    max_v = max(v for _, a, b in data for v in (a, b)) * 1.15
    bars = ''
    for label, current, projected in data:
        pct_cur = round(current / max_v * 100, 1)
        pct_pro = round(projected / max_v * 100, 1)
        bars += f'''
<div class="chart-group">
  <div class="chart-bars">
    <div class="bar-wrap">
      <div class="bar-val">{current:,}&nbsp;€</div>
      <div class="bar bar-current" style="height:{pct_cur}%"></div>
    </div>
    <div class="bar-wrap">
      <div class="bar-val projected">{projected:,}&nbsp;€</div>
      <div class="bar bar-projected" style="height:{pct_pro}%"></div>
    </div>
  </div>
  <div class="chart-label">{label}</div>
</div>'''
    return f'''<div class="chart-container">
  <div class="chart-inner">{bars}</div>
  <div class="chart-legend">
    <span class="legend-item"><span class="legend-dot current"></span>CA actuel</span>
    <span class="legend-item"><span class="legend-dot projected"></span>Objectif projeté</span>
  </div>
</div>'''

def parse_report(text):
    lines = text.split('\n')
    output = []
    i = 0
    def add(h): output.append(h)

    while i < len(lines):
        raw = lines[i]
        line = raw.strip()

        if not line: i += 1; continue

        if line == '---':
            add('<hr class="section-rule">'); i += 1; continue

        m = re.match(r'^#{1}\s+(.+)', line)
        if m:
            add(f'<h1 class="h1">{clean(m.group(1))}</h1>'); i += 1; continue

        m = re.match(r'^#{2}\s+(.+)', line)
        if m:
            txt = clean(m.group(1).upper())
            color = _section_color(txt)
            add(f'<div class="section-header" style="border-left-color:{color}"><span class="section-label" style="color:{color}">{txt}</span></div>')
            i += 1; continue

        m = re.match(r'^#{3}\s+(.+)', line)
        if m:
            add(f'<h3 class="h3">{clean(m.group(1))}</h3>'); i += 1; continue

        m = re.match(r'^#{4}\s+(.+)', line)
        if m:
            add(f'<h4 class="h4">{clean_html(m.group(1))}</h4>'); i += 1; continue

        if re.search(r'v[eé]rit[eé]\s+fondamentale', line, re.I):
            txt = re.sub(r'.*?v[eé]rit[eé]\s+fondamentale\s*:?\s*', '', line, flags=re.I)
            txt = re.sub(r'^[#*>\[\]! ]+', '', txt).strip()
            if not txt and i+1 < len(lines):
                i += 1; txt = lines[i].strip()
            add(f'<div class="verite-block"><div class="verite-label">VÉRITÉ FONDAMENTALE</div><div class="verite-text">{clean(txt)}</div></div>')
            i += 1; continue

        kv = re.match(r'\*\*(.+?)\*\*\s*::\s*(.*)', line)
        if kv:
            add(f'<div class="kv-row"><span class="kv-label">{clean(kv.group(1))}</span><span class="kv-value">{clean(kv.group(2))}</span></div>')
            i += 1; continue

        if line.startswith('>') or line.startswith('->'):
            txt = re.sub(r'^-?>?\s*', '', line).strip()
            add(f'<blockquote class="bq">{clean(txt)}</blockquote>')
            i += 1; continue

        opt = re.match(r'^OPTION\s+([A-C])\s*[-—]?\s*(.{5,})', line, re.I)
        if opt:
            letter = opt.group(1)
            title = clean(opt.group(2).strip()[:80])
            score = '?'; detail = ''
            j = i + 1
            while j < len(lines) and j < i + 5:
                nl = lines[j].strip()
                sm = re.search(r'Score\s*:\s*([\d,.]+)', nl, re.I)
                if sm:
                    score = sm.group(1)
                    detail = re.sub(r'Score\s*:.*', '', nl).strip()
                    break
                if nl: detail += clean(nl[:80]) + ' '
                j += 1
            try:
                sv = float(score.replace(',','.'))
                sc = GREEN_ACC if sv >= 7 else (ORANGE if sv >= 5 else RED_ACC)
            except:
                sc = NAVY
            color = _section_color('DECISION')
            add(f'''<div class="option-card" style="border-left-color:{color}">
  <div class="option-letter" style="background:{color}">{letter}</div>
  <div class="option-body"><div class="option-title">{title}</div><div class="option-detail">{detail.strip()}</div></div>
  <div class="option-score" style="color:{sc}"><span class="score-num">{score}</span><span class="score-denom">/10</span></div>
</div>''')
            i += 1; continue

        mm = re.match(r'^(Message\s+\d[^:]*)', line, re.I)
        if mm:
            label = clean(mm.group(1))
            rest = line[len(mm.group(0)):].lstrip(': ').strip()
            if not rest and i+1 < len(lines):
                i += 1; rest = lines[i].strip()
            add(f'<div class="message-card"><div class="message-label">{label}</div><div class="message-text">"{clean(rest)}"</div></div>')
            i += 1; continue

        if line.startswith('CHART_BAR:'):
            raw_data = line[len('CHART_BAR:'):]
            chart_rows = []
            for seg in raw_data.split('|'):
                parts = seg.split(':')
                if len(parts) == 3:
                    try: chart_rows.append((parts[0], int(parts[1]), int(parts[2])))
                    except: pass
            if chart_rows: add(_render_chart(chart_rows))
            i += 1; continue

        if re.match(r'^[-*•·]\s', line) or re.match(r'^\s{2,}[-*•·]\s', raw):
            items = []
            while i < len(lines):
                l = lines[i].strip()
                if re.match(r'^[-*•·]\s', l):
                    items.append(re.sub(r'^[-*•·]\s', '', l)); i += 1
                else: break
            add('<ul class="report-list">' + ''.join(f'<li>{clean_html(it)}</li>' for it in items) + '</ul>')
            continue

        if re.match(r'^\d+\.\s', line):
            items = []
            while i < len(lines):
                l = lines[i].strip()
                if re.match(r'^\d+\.\s', l):
                    items.append(re.sub(r'^\d+\.\s', '', l)); i += 1
                else: break
            add('<ol class="report-list">' + ''.join(f'<li>{clean_html(it)}</li>' for it in items) + '</ol>')
            continue

        if line.startswith('|') and i+1 < len(lines):
            rows = []
            is_hdr = True
            while i < len(lines) and lines[i].strip().startswith('|'):
                row_line = lines[i].strip()
                if re.match(r'^\|[-| :]+\|$', row_line):
                    is_hdr = False; i += 1; continue
                cells = [c.strip() for c in row_line.strip('|').split('|')]
                rows.append((cells, is_hdr and len(rows) == 0)); i += 1
            html_rows = ''
            for cells, header in rows:
                tag = 'th' if header else 'td'
                html_rows += '<tr>' + ''.join(f'<{tag}>{clean_html(c)}</{tag}>' for c in cells) + '</tr>'
            add(f'<table class="report-table">{html_rows}</table>')
            continue

        add(f'<p class="body">{clean_html(line)}</p>')
        i += 1

    return '\n'.join(output)


def build_html(report_text, nom, secteur, mode, date_str):
    mode_label = MODE_LABELS.get(mode, MODE_LABELS['premium'])
    price = PRICE_MAP.get(mode, '2 490 €')
    content_html = parse_report(report_text)

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>DECISIO — Audit {clean(nom)}</title>
<style>
@page {{
  size: A4;
  margin: 20mm 28mm 20mm 28mm;
}}
@page cover {{
  size: A4;
  margin: 0;
}}
@page content {{
  size: A4;
  margin: 20mm 28mm 20mm 28mm;
  @bottom-left {{
    content: "CONFIDENTIEL  ·  DECISIO AGENCY  ·  MÉTHODE D3™";
    font-family: 'Helvetica Neue', Arial, sans-serif;
    font-size: 7pt; color: {MUTED}; letter-spacing: 0.05em;
  }}
  @bottom-right {{
    content: counter(page);
    font-family: 'Helvetica Neue', Arial, sans-serif;
    font-size: 8pt; font-weight: 700; color: {NAVY};
  }}
  @top-left {{
    content: "DECISIO  ·  MÉTHODE D3™";
    font-family: 'Helvetica Neue', Arial, sans-serif;
    font-size: 7.5pt; font-weight: 700; color: {NAVY};
  }}
  @top-right {{
    content: "{clean(nom)}  ·  {clean(secteur)}";
    font-family: 'Helvetica Neue', Arial, sans-serif;
    font-size: 7pt; color: {MUTED};
  }}
}}

*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ font-family: 'Helvetica Neue', Arial, sans-serif; font-size: 10.5pt; color: {TEXT}; line-height: 1.75; background: white; }}

/* COUVERTURE */
.cover {{ page: cover; width: 210mm; height: 297mm; display: flex; page-break-after: always; }}
.cover-left {{ width: 40%; background: {NAVY}; padding: 14mm 9mm 10mm 10mm; display: flex; flex-direction: column; justify-content: space-between; position: relative; }}
.cover-left::after {{ content: ''; position: absolute; right: 0; top: 0; bottom: 0; width: 3.5px; background: {GOLD}; }}
.cover-logo {{ font-family: Georgia, serif; font-size: 30pt; font-weight: 900; color: white; letter-spacing: -0.5px; line-height: 1; }}
.cover-method {{ font-size: 6.5pt; font-weight: 700; color: {GOLD}; letter-spacing: 0.18em; text-transform: uppercase; margin-top: 3mm; }}
.cover-tagline {{ font-size: 6.5pt; color: rgba(255,255,255,0.4); letter-spacing: 0.07em; margin-top: 2mm; }}
.cover-pillars {{ margin-top: auto; padding-top: 8mm; }}
.pillar {{ display: flex; align-items: flex-start; gap: 4mm; margin-bottom: 6mm; }}
.pillar-num {{ width: 8mm; height: 8mm; border-radius: 50%; background: {GOLD}; display: flex; align-items: center; justify-content: center; font-size: 6.5pt; font-weight: 700; color: {NAVY}; flex-shrink: 0; }}
.pillar-title {{ font-size: 8.5pt; font-weight: 700; color: white; line-height: 1.2; }}
.pillar-desc {{ font-size: 7pt; color: {GOLD}; opacity: 0.8; }}
.cover-footer {{ font-size: 6.5pt; color: rgba(255,255,255,0.3); }}
.cover-right {{ flex: 1; padding: 12mm 9mm 10mm 11mm; display: flex; flex-direction: column; }}
.cover-badge {{ align-self: flex-end; background: {NAVY}; color: {GOLD}; font-size: 6.5pt; font-weight: 700; letter-spacing: 0.1em; padding: 2.5mm 5mm; border-radius: 1.5mm; }}
.cover-client-name {{ font-family: Georgia, serif; font-size: 26pt; font-weight: 700; color: {NAVY}; line-height: 1.1; margin-top: 16mm; }}
.cover-gold-rule {{ width: 20mm; height: 2.5px; background: {GOLD}; margin: 4mm 0; }}
.cover-sector {{ font-size: 13pt; color: #444; font-weight: 300; }}
.cover-date {{ font-size: 9pt; color: {MUTED}; margin-top: 2mm; }}
.cover-sep {{ border: none; border-top: 1px solid {BORDER}; margin: 7mm 0; }}
.cover-info-box {{ background: {LIGHT_BG}; border: 1px solid {BORDER}; border-left: 3px solid {GOLD}; border-radius: 3mm; padding: 6mm 7mm; margin-top: auto; }}
.cover-info-title {{ font-size: 7.5pt; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; color: {NAVY}; margin-bottom: 3mm; }}
.cover-price {{ font-family: Georgia, serif; font-size: 24pt; font-weight: 700; color: {NAVY}; line-height: 1; }}
.cover-delivery {{ font-size: 7.5pt; color: {MUTED}; margin-top: 2mm; }}
.cover-confidential {{ font-size: 6.5pt; color: {MUTED}; margin-top: 7mm; line-height: 1.6; }}

/* CONTENU */
.content {{ page: content; }}
.report-title {{ font-family: Georgia, serif; font-size: 18pt; font-weight: 700; color: {NAVY}; text-align: center; line-height: 1.25; margin-bottom: 3mm; }}
.report-subtitle {{ font-size: 9pt; color: {MUTED}; text-align: center; margin-bottom: 3mm; }}
.title-rule-navy {{ border: none; border-top: 2.5px solid {NAVY}; margin: 3mm 0 1.5mm; }}
.title-rule-gold {{ border: none; border-top: 1px solid {GOLD}; margin-bottom: 9mm; }}

.h1 {{ font-family: Georgia, serif; font-size: 15pt; font-weight: 700; color: {NAVY}; margin: 9mm 0 4mm; }}
.section-header {{ background: {LIGHT_BG}; border-left: 6px solid {NAVY}; padding: 4.5mm 5mm; margin: 11mm 0 5mm; }}
.section-label {{ font-size: 10.5pt; font-weight: 700; letter-spacing: 0.04em; }}
.h3 {{ font-size: 10.5pt; font-weight: 700; color: {NAVY}; margin: 7mm 0 2.5mm; padding-bottom: 1.5mm; border-bottom: 2px solid {GOLD}; display: inline-block; padding-right: 8mm; }}
.h4 {{ font-size: 10pt; font-weight: 600; color: {NAVY}; margin: 5mm 0 1.5mm; }}
.body {{ font-size: 10.5pt; color: {TEXT}; line-height: 1.8; text-align: justify; margin-bottom: 4.5mm; orphans: 3; widows: 3; }}

.report-list {{ margin: 2mm 0 5mm 4mm; padding-left: 5mm; }}
.report-list li {{ font-size: 10.5pt; line-height: 1.7; color: {TEXT}; margin-bottom: 3mm; }}
ul.report-list {{ list-style: none; padding-left: 0; }}
ul.report-list li::before {{ content: '●'; color: {GOLD}; font-size: 7pt; margin-right: 3mm; vertical-align: middle; }}

.kv-row {{ display: flex; align-items: baseline; gap: 3mm; padding: 3mm 4mm; background: {LIGHT_BG}; border-bottom: 1px solid {BORDER}; border-left: 3px solid {GOLD}; }}
.kv-label {{ font-size: 9pt; font-weight: 700; color: {NAVY}; min-width: 52mm; flex-shrink: 0; }}
.kv-value {{ font-size: 9.5pt; color: {TEXT}; }}

.verite-block {{ background: {NAVY}; border-left: 5px solid {GOLD}; padding: 5mm 7mm; margin: 7mm 0; }}
.verite-label {{ font-size: 7pt; font-weight: 700; color: {GOLD}; letter-spacing: 0.15em; text-transform: uppercase; margin-bottom: 3mm; }}
.verite-text {{ font-size: 11pt; font-weight: 600; font-style: italic; color: white; line-height: 1.6; }}

.bq {{ background: {LIGHT_BG}; border-left: 3px solid {BLUE_ACC}; padding: 3.5mm 5mm; margin: 4mm 0; font-size: 10pt; font-style: italic; color: #333; }}

.option-card {{ display: flex; align-items: center; gap: 4mm; background: {LIGHT_BG}; border: 1px solid {BORDER}; border-left: 6px solid; border-radius: 2mm; padding: 4mm 5mm; margin: 3mm 0; }}
.option-letter {{ width: 10mm; height: 10mm; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 11pt; color: white; flex-shrink: 0; }}
.option-body {{ flex: 1; }}
.option-title {{ font-size: 10pt; font-weight: 700; color: {NAVY}; margin-bottom: 1mm; }}
.option-detail {{ font-size: 8.5pt; color: {MUTED}; }}
.option-score {{ text-align: center; flex-shrink: 0; min-width: 18mm; }}
.score-num {{ display: block; font-family: Georgia, serif; font-size: 22pt; font-weight: 700; line-height: 1; }}
.score-denom {{ font-size: 8pt; color: {MUTED}; }}

.message-card {{ background: #EEF4FF; border: 1px solid #C7D9F5; border-radius: 2mm; padding: 4mm 6mm; margin: 4mm 0; }}
.message-label {{ font-size: 7.5pt; font-weight: 700; color: {BLUE_ACC}; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 2mm; }}
.message-text {{ font-size: 10pt; font-style: italic; color: {TEXT}; line-height: 1.6; }}

.report-table {{ width: 100%; border-collapse: collapse; margin: 4mm 0; font-size: 9pt; }}
.report-table th {{ background: {NAVY}; color: white; font-weight: 700; padding: 3.5mm 4mm; text-align: left; border-top: 2.5px solid {GOLD}; }}
.report-table td {{ padding: 3mm 4mm; border-bottom: 1px solid {BORDER}; color: {TEXT}; line-height: 1.5; }}
.report-table tr:nth-child(even) td {{ background: {LIGHT_BG}; }}
.report-table tr:last-child td {{ border-bottom: 2px solid {NAVY}; }}

.chart-container {{ margin: 5mm 0; }}
.chart-inner {{ display: flex; align-items: flex-end; gap: 6mm; height: 52mm; padding: 0 4mm; border-bottom: 2px solid {NAVY}; }}
.chart-group {{ flex: 1; display: flex; flex-direction: column; align-items: center; height: 100%; justify-content: flex-end; }}
.chart-bars {{ display: flex; align-items: flex-end; gap: 2mm; height: 44mm; width: 100%; justify-content: center; }}
.bar-wrap {{ display: flex; flex-direction: column; align-items: center; justify-content: flex-end; height: 100%; min-width: 13mm; }}
.bar {{ width: 13mm; border-radius: 1.5mm 1.5mm 0 0; min-height: 3mm; }}
.bar-current {{ background: {NAVY}; }}
.bar-projected {{ background: {GOLD}; }}
.bar-val {{ font-size: 6.5pt; font-weight: 600; color: {NAVY}; text-align: center; margin-bottom: 1mm; }}
.bar-val.projected {{ color: #7A6020; }}
.chart-label {{ font-size: 8pt; font-weight: 600; color: {MUTED}; text-align: center; margin-top: 2.5mm; padding-top: 2mm; border-top: 1px solid {BORDER}; width: 100%; }}
.chart-legend {{ display: flex; gap: 6mm; justify-content: center; margin-top: 3mm; font-size: 8pt; color: {MUTED}; }}
.legend-item {{ display: flex; align-items: center; gap: 2mm; }}
.legend-dot {{ width: 3mm; height: 3mm; border-radius: 50%; display: inline-block; }}
.legend-dot.current {{ background: {NAVY}; }}
.legend-dot.projected {{ background: {GOLD}; }}

.section-rule {{ border: none; border-top: 1px solid {BORDER}; margin: 6mm 0; }}
.report-footer {{ margin-top: 12mm; padding-top: 4mm; border-top: 2px solid {NAVY}; font-size: 8pt; color: {MUTED}; text-align: center; line-height: 1.6; }}
</style>
</head>
<body>

<div class="cover">
  <div class="cover-left">
    <div>
      <div class="cover-logo">DECISIO</div>
      <div class="cover-method">MÉTHODE D3™</div>
      <div class="cover-tagline">FIRST PRINCIPLES · AI-POWERED 48H</div>
    </div>
    <div class="cover-pillars">
      <div class="pillar"><div class="pillar-num">01</div><div><div class="pillar-title">DIAGNOSTIC</div><div class="pillar-desc">Analyse complète</div></div></div>
      <div class="pillar"><div class="pillar-num">02</div><div><div class="pillar-title">DÉCISION</div><div class="pillar-desc">Options scorées</div></div></div>
      <div class="pillar"><div class="pillar-num">03</div><div><div class="pillar-title">DÉPLOIEMENT</div><div class="pillar-desc">Plan d'action</div></div></div>
    </div>
    <div class="cover-footer">decisio.agency · contact@decisio.agency</div>
  </div>
  <div class="cover-right">
    <div class="cover-badge">{clean(mode_label)}</div>
    <div class="cover-client-name">{clean(nom)}</div>
    <div class="cover-gold-rule"></div>
    <div class="cover-sector">{clean(secteur)}</div>
    <div class="cover-date">{clean(date_str)}</div>
    <hr class="cover-sep">
    <div class="cover-info-box">
      <div class="cover-info-title">Audit Stratégique Premium</div>
      <div class="cover-price">{price}</div>
      <div class="cover-delivery">Livraison 48h · Méthode D3™ · Confidentiel</div>
    </div>
    <div class="cover-confidential">
      Ce rapport est strictement confidentiel et destiné au seul usage du client désigné ci-dessus.<br>
      Toute reproduction est interdite sans autorisation écrite de DECISIO AGENCY.
    </div>
  </div>
</div>

<div class="content">
  <h2 class="report-title">RAPPORT D'AUDIT STRATÉGIQUE — MÉTHODE D3™</h2>
  <p class="report-subtitle">{clean(nom)} &nbsp;·&nbsp; {clean(secteur)} &nbsp;·&nbsp; {clean(date_str)}</p>
  <hr class="title-rule-navy">
  <hr class="title-rule-gold">
  {content_html}
  <div class="report-footer">
    Rapport strictement confidentiel — DECISIO AGENCY &nbsp;·&nbsp; Méthode D3™ &nbsp;·&nbsp; contact@decisio.agency
  </div>
</div>

</body>
</html>"""


def generate_pdf(report_text, nom, secteur, mode, date_str=None):
    if not date_str:
        date_str = datetime.now().strftime('%d %B %Y')

    html_content = build_html(report_text, nom, secteur, mode, date_str)

    response = requests.post(
        'https://docraptor.com/docs',
        auth=(DOCRAPTOR_API_KEY, ''),
        json={
            'doc': {
                'document_content': html_content,
                'document_type': 'pdf',
                'test': False,
                'prince_options': {
                    'media': 'print',
                    'baseurl': 'https://decisio.agency',
                }
            }
        },
        timeout=60
    )

    response.raise_for_status()
    return response.content
