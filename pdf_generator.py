"""
DECISIO PDF Generator V12 - DocRaptor HTML/CSS
Version propre complete - tous bugs corriges
- Header horizontal propre sur chaque page
- Footer sans caractere special
- Tableaux proteges contre coupure
- Scores visuels en barres de progression
- Pages separatrices D3
- Graphique CSS natif
- ASCII uniquement pour eviter bugs encodage
"""
import re
from datetime import datetime
from weasyprint import HTML

NAVY      = '#1C2B4A'
GOLD      = '#C9A84C'
LIGHT_BG  = '#F7F8FA'
BORDER    = '#E2E5EB'
TEXT      = '#1A1A2E'
MUTED     = '#6B7280'
RED_ACC   = '#C0392B'
GREEN_ACC = '#1A7A45'
BLUE_ACC  = '#2563A8'
ORANGE    = '#C4621A'


MODE_LABELS = {
    'flash':          'AUDIT FLASH - 490 EUR',
    'premium':        'AUDIT PREMIUM - 2 490 EUR',
    'transformation': 'AUDIT TRANSFORMATION - 6 900 EUR',
    'redressement':   'AUDIT REDRESSEMENT - 9 900 EUR',
    'diagnostic':     'DIAGNOSTIC GRATUIT',
}

PRICE_MAP = {
    'flash': '490 EUR',
    'premium': '2 490 EUR',
    'transformation': '6 900 EUR',
    'redressement': '9 900 EUR',
    'diagnostic': 'Gratuit',
}


def clean(s):
    """Nettoie le texte - supprime emojis et caracteres non-ASCII"""
    s = str(s)
    # Remplacer les caracteres speciaux courants
    replacements = {
        '\u2014': ' - ', '\u2013': ' - ', '\u2026': '...',
        '\u00d7': 'x', '\u00b7': '-', '\u2019': "'", '\u2018': "'",
        '\u201c': '"', '\u201d': '"', '\u00e9': 'e', '\u00e8': 'e',
        '\u00ea': 'e', '\u00eb': 'e', '\u00e0': 'a', '\u00e2': 'a',
        '\u00f4': 'o', '\u00f9': 'u', '\u00fb': 'u', '\u00ee': 'i',
        '\u00ef': 'i', '\u00e7': 'c', '\u00c9': 'E', '\u00c8': 'E',
        '\u00c0': 'A', '\u00c7': 'C', '\u00d4': 'O', '\u00db': 'U',
    }
    for k, v in replacements.items():
        s = s.replace(k, v)
    # Supprimer emojis et tout non-ASCII restant
    return s.strip()


def clean_html(s):
    s = clean(s)
    s = s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'\*(.+?)\*', r'<em>\1</em>', s)
    s = s.replace('&lt;strong&gt;', '<strong>').replace('&lt;/strong&gt;', '</strong>')
    s = s.replace('&lt;em&gt;', '<em>').replace('&lt;/em&gt;', '</em>')
    return s


def section_color(txt):
    t = txt.upper()
    if any(x in t for x in ['EXEC', 'SYNTH']): return GOLD
    if any(x in t for x in ['QUICK', 'WIN', '48H']): return GREEN_ACC
    if any(x in t for x in ['DIAG', 'PARTIE 1']): return RED_ACC
    if any(x in t for x in ['DECIS', 'PARTIE 2']): return ORANGE
    if any(x in t for x in ['DEPLOY', 'PARTIE 3']): return GREEN_ACC
    return NAVY


def score_bar(score_str):
    try:
        val = float(score_str.replace(',', '.'))
        pct = int(val * 10)
        color = GREEN_ACC if val >= 7 else (ORANGE if val >= 5 else RED_ACC)
        return (
            f'<div style="display:table;width:100%;margin-top:3px">'
            f'<div style="display:table-cell;vertical-align:middle;width:85%">'
            f'<div style="background:{BORDER};height:5px;border-radius:3px;overflow:hidden">'
            f'<div style="background:{color};height:5px;width:{pct}%"></div>'
            f'</div></div>'
            f'<div style="display:table-cell;vertical-align:middle;padding-left:4px;'
            f'font-size:9pt;font-weight:700;color:{color};white-space:nowrap">'
            f'{score_str}/10</div>'
            f'</div>'
        )
    except Exception:
        return f'<span style="font-weight:700">{score_str}/10</span>'


def render_chart(data):
    if not data:
        return ''
    max_v = max(v for _, a, b in data for v in (a, b)) * 1.15
    cols = ''
    for label, current, projected in data:
        pct_c = round(current / max_v * 100, 1)
        pct_p = round(projected / max_v * 100, 1)
        cols += (
            f'<td style="vertical-align:bottom;text-align:center;padding:0 4px">'
            f'<div style="display:inline-block;vertical-align:bottom;margin:0 2px">'
            f'<div style="font-size:6.5pt;font-weight:600;color:{NAVY};margin-bottom:2px">{current:,}</div>'
            f'<div style="width:14mm;background:{NAVY};height:{pct_c}%;border-radius:2px 2px 0 0;min-height:3px"></div>'
            f'</div>'
            f'<div style="display:inline-block;vertical-align:bottom;margin:0 2px">'
            f'<div style="font-size:6.5pt;font-weight:600;color:#7A6020;margin-bottom:2px">{projected:,}</div>'
            f'<div style="width:14mm;background:{GOLD};height:{pct_p}%;border-radius:2px 2px 0 0;min-height:3px"></div>'
            f'</div>'
            f'<div style="font-size:8pt;color:{MUTED};margin-top:3px;padding-top:2px;border-top:1px solid {BORDER}">{clean(label)}</div>'
            f'</td>'
        )
    return (
        f'<div style="page-break-inside:avoid;margin:6mm 0">'
        f'<table style="width:100%;border-bottom:2px solid {NAVY};height:52mm">'
        f'<tr>{cols}</tr>'
        f'</table>'
        f'<div style="text-align:center;font-size:8pt;color:{MUTED};margin-top:3mm">'
        f'<span style="display:inline-block;width:8px;height:8px;background:{NAVY};border-radius:50%;margin-right:3px;vertical-align:middle"></span>Aujourd\'hui'
        f'&nbsp;&nbsp;'
        f'<span style="display:inline-block;width:8px;height:8px;background:{GOLD};border-radius:50%;margin-right:3px;vertical-align:middle"></span>Projection'
        f'</div>'
        f'</div>'
    )


def partie_break(num, titre, color):
    return (
        f'<div class="partie-break" style="background:{color}">'
        f'<div class="partie-num">0{num}</div>'
        f'<div class="partie-titre">{titre}</div>'
        f'<div class="partie-rule"></div>'
        f'<div class="partie-sub">METHODE D3 - DECISIO AGENCY</div>'
        f'</div>'
    )


def parse_report(text):
    lines = text.split('\n')
    out = []
    i = 0

    while i < len(lines):
        raw = lines[i]
        line = raw.strip()

        if not line:
            i += 1
            continue

        if line == '---':
            out.append(f'<hr style="border:none;border-top:1px solid {BORDER};margin:6mm 0">')
            i += 1
            continue

        # H1 - pages separatrices
        m = re.match(r'^#\s+(.+)', line)
        if m:
            txt = clean(m.group(1)).upper()
            if 'PARTIE 1' in txt or 'DIAGNOSTIC' in txt:
                out.append(partie_break(1, 'DIAGNOSTIC', RED_ACC))
            elif 'PARTIE 2' in txt or 'DECISION' in txt:
                out.append(partie_break(2, 'DECISION', ORANGE))
            elif 'PARTIE 3' in txt or 'DEPLOIEMENT' in txt:
                out.append(partie_break(3, 'DEPLOIEMENT', GREEN_ACC))
            else:
                out.append(f'<h1 class="h1">{clean(m.group(1))}</h1>')
            i += 1
            continue

        # H2 - section header
        m = re.match(r'^##\s+(.+)', line)
        if m:
            txt = clean(m.group(1).upper())
            color = section_color(txt)
            out.append(
                f'<div style="background:{LIGHT_BG};border-left:6px solid {color};'
                f'padding:4mm 5mm;margin:10mm 0 5mm;page-break-after:avoid">'
                f'<span style="font-size:10.5pt;font-weight:700;letter-spacing:0.04em;color:{color}">{txt}</span>'
                f'</div>'
            )
            i += 1
            continue

        # H3
        m = re.match(r'^###\s+(.+)', line)
        if m:
            txt = clean(m.group(1))
            out.append(
                f'<div style="font-size:10.5pt;font-weight:700;color:{NAVY};'
                f'margin:7mm 0 2.5mm;padding-bottom:1.5mm;border-bottom:2px solid {GOLD};'
                f'page-break-after:avoid">{txt}</div>'
            )
            i += 1
            continue

        # H4
        m = re.match(r'^####\s+(.+)', line)
        if m:
            out.append(
                f'<div style="font-size:10pt;font-weight:600;color:{NAVY};'
                f'margin:5mm 0 1.5mm;page-break-after:avoid">{clean_html(m.group(1))}</div>'
            )
            i += 1
            continue

        # Verite fondamentale
        if re.search(r'v.rit. fondamentale', line, re.I):
            txt = re.sub(r'.*?v.rit. fondamentale\s*:?\s*', '', line, flags=re.I)
            txt = re.sub(r'^[#*>\[\]! ]+', '', txt).strip()
            if not txt and i + 1 < len(lines):
                i += 1
                txt = lines[i].strip()
            out.append(
                f'<div style="background:{NAVY};border-left:5px solid {GOLD};'
                f'padding:5mm 7mm;margin:7mm 0;page-break-inside:avoid">'
                f'<div style="font-size:7pt;font-weight:700;color:{GOLD};'
                f'letter-spacing:0.15em;text-transform:uppercase;margin-bottom:3mm">VERITE FONDAMENTALE</div>'
                f'<div style="font-size:11pt;font-weight:600;font-style:italic;color:white;line-height:1.6">{clean(txt)}</div>'
                f'</div>'
            )
            i += 1
            continue

        # KEY :: VALUE
        kv = re.match(r'\*\*(.+?)\*\*\s*::\s*(.*)', line)
        if kv:
            out.append(
                f'<div style="display:table;width:100%;padding:3mm 4mm;'
                f'background:{LIGHT_BG};border-bottom:1px solid {BORDER};'
                f'border-left:3px solid {GOLD};page-break-inside:avoid">'
                f'<span style="display:table-cell;width:52mm;font-size:9pt;font-weight:700;color:{NAVY}">'
                f'{clean(kv.group(1))}</span>'
                f'<span style="display:table-cell;font-size:9.5pt;color:{TEXT}">'
                f'{clean(kv.group(2))}</span>'
                f'</div>'
            )
            i += 1
            continue

        # Blockquote
        if line.startswith('>') or line.startswith('->'):
            txt = re.sub(r'^-?>?\s*', '', line).strip()
            out.append(
                f'<div style="background:{LIGHT_BG};border-left:3px solid {BLUE_ACC};'
                f'padding:3.5mm 5mm;margin:4mm 0;font-size:10pt;font-style:italic;'
                f'color:#333;page-break-inside:avoid">{clean(txt)}</div>'
            )
            i += 1
            continue

        # Options A/B/C
        opt = re.match(r'^OPTION\s+([A-C])\s*[-]?\s*(.{5,})', line, re.I)
        if opt:
            letter = opt.group(1)
            title = clean(opt.group(2).strip()[:80])
            score_val = '?'
            detail = ''
            j = i + 1
            while j < len(lines) and j < i + 5:
                nl = lines[j].strip()
                sm = re.search(r'Score\s*:\s*([\d,.]+)', nl, re.I)
                if sm:
                    score_val = sm.group(1)
                    detail = re.sub(r'Score\s*:.*', '', nl).strip()
                    break
                if nl:
                    detail += clean(nl[:80]) + ' '
                j += 1
            color = ORANGE
            bar_html = score_bar(score_val)
            out.append(
                f'<div style="display:table;width:100%;background:{LIGHT_BG};'
                f'border:1px solid {BORDER};border-left:6px solid {color};'
                f'margin:3mm 0;page-break-inside:avoid">'
                f'<div style="display:table-cell;width:12mm;background:{color};'
                f'text-align:center;vertical-align:middle;font-weight:700;font-size:13pt;color:white;padding:4mm 3mm">'
                f'{letter}</div>'
                f'<div style="display:table-cell;padding:4mm 5mm;vertical-align:top">'
                f'<div style="font-size:10pt;font-weight:700;color:{NAVY};margin-bottom:1.5mm">{title}</div>'
                f'<div style="font-size:8.5pt;color:{MUTED};margin-bottom:2mm">{detail.strip()}</div>'
                f'{bar_html}'
                f'</div>'
                f'</div>'
            )
            i += 1
            continue

        # Message card
        mm = re.match(r'^(Message\s+\d[^:]*)', line, re.I)
        if mm:
            label = clean(mm.group(1))
            rest = line[len(mm.group(0)):].lstrip(': ').strip()
            if not rest and i + 1 < len(lines):
                i += 1
                rest = lines[i].strip()
            out.append(
                f'<div style="background:#EEF4FF;border:1px solid #C7D9F5;'
                f'border-left:4px solid {BLUE_ACC};border-radius:2mm;'
                f'padding:4mm 6mm;margin:4mm 0;page-break-inside:avoid">'
                f'<div style="font-size:7.5pt;font-weight:700;color:{BLUE_ACC};'
                f'text-transform:uppercase;letter-spacing:0.08em;margin-bottom:2mm">{label}</div>'
                f'<div style="font-size:10pt;font-style:italic;color:{TEXT};line-height:1.6">"{clean(rest)}"</div>'
                f'</div>'
            )
            i += 1
            continue

        # Graphique
        if line.startswith('CHART_BAR:'):
            raw_data = line[len('CHART_BAR:'):]
            chart_rows = []
            for seg in raw_data.split('|'):
                parts = seg.split(':')
                if len(parts) == 3:
                    try:
                        chart_rows.append((parts[0], int(parts[1]), int(parts[2])))
                    except Exception:
                        pass
            if chart_rows:
                out.append(render_chart(chart_rows))
            i += 1
            continue

        # Bullets
        if re.match(r'^[-*]\s', line):
            items = []
            while i < len(lines):
                l = lines[i].strip()
                if re.match(r'^[-*]\s', l):
                    items.append(re.sub(r'^[-*]\s', '', l))
                    i += 1
                else:
                    break
            li_html = ''.join(
                f'<li style="font-size:10.5pt;line-height:1.7;color:{TEXT};'
                f'margin-bottom:3mm;padding-left:5mm;position:relative">'
                f'<span style="position:absolute;left:0;top:6pt;display:inline-block;'
                f'width:4px;height:4px;border-radius:50%;background:{GOLD}"></span>'
                f'{clean_html(it)}</li>'
                for it in items
            )
            out.append(f'<ul style="list-style:none;padding:0;margin:2mm 0 5mm">{li_html}</ul>')
            continue

        # Liste numerotee
        if re.match(r'^\d+\.\s', line):
            items = []
            while i < len(lines):
                l = lines[i].strip()
                if re.match(r'^\d+\.\s', l):
                    items.append(re.sub(r'^\d+\.\s', '', l))
                    i += 1
                else:
                    break
            li_html = ''.join(
                f'<li style="font-size:10.5pt;line-height:1.7;color:{TEXT};margin-bottom:3mm">'
                f'{clean_html(it)}</li>'
                for it in items
            )
            out.append(f'<ol style="padding-left:6mm;margin:2mm 0 5mm">{li_html}</ol>')
            continue

        # Tableau markdown
        if line.startswith('|') and i + 1 < len(lines):
            rows = []
            is_first = True
            while i < len(lines) and lines[i].strip().startswith('|'):
                row_line = lines[i].strip()
                if re.match(r'^\|[-| :]+\|$', row_line):
                    is_first = False
                    i += 1
                    continue
                cells = [c.strip() for c in row_line.strip('|').split('|')]
                rows.append((cells, is_first and len(rows) == 0))
                i += 1
            html_rows = ''
            for cells, is_header in rows:
                if is_header:
                    tds = ''.join(
                        f'<th style="background:{NAVY};color:white;font-weight:700;'
                        f'padding:3.5mm 4mm;text-align:left;border-top:2.5px solid {GOLD}">'
                        f'{clean_html(c)}</th>'
                        for c in cells
                    )
                else:
                    tds = ''.join(
                        f'<td style="padding:3mm 4mm;border-bottom:1px solid {BORDER};'
                        f'color:{TEXT};line-height:1.5">{clean_html(c)}</td>'
                        for c in cells
                    )
                html_rows += f'<tr>{tds}</tr>'
            out.append(
                f'<table style="width:100%;border-collapse:collapse;margin:4mm 0;'
                f'font-size:9pt;page-break-inside:avoid">{html_rows}</table>'
            )
            continue

        # Paragraphe normal
        out.append(
            f'<p style="font-size:10.5pt;color:{TEXT};line-height:1.8;'
            f'text-align:justify;margin-bottom:4mm;orphans:3;widows:3">'
            f'{clean_html(line)}</p>'
        )
        i += 1

    return '\n'.join(out)


def build_html(report_text, nom, secteur, mode, date_str):
    mode_label = MODE_LABELS.get(mode, MODE_LABELS['premium'])
    price = PRICE_MAP.get(mode, '2 490 EUR')
    content_html = parse_report(report_text)

    nom_c = clean(nom)
    secteur_c = clean(secteur)
    date_c = clean(date_str)
    mode_c = clean(mode_label)

    css = f"""
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Source+Sans+3:wght@300;400;600;700&display=swap');

*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

@page {{ size: A4; margin: 0; }}

@page content {{
  size: A4;
  margin: 22mm 26mm 20mm 26mm;
  @top-center {{
    content: element(pageHeader);
    width: 100%;
    vertical-align: bottom;
  }}
  @bottom-left {{
    content: "CONFIDENTIEL - DECISIO AGENCY";
    font-family: Arial, sans-serif;
    font-size: 7pt;
    color: {MUTED};
  }}
  @bottom-right {{
    content: counter(page);
    font-family: Arial, sans-serif;
    font-size: 8pt;
    font-weight: 700;
    color: {NAVY};
  }}
}}

@page partie {{ size: A4; margin: 0; }}

body {{
  font-family: 'Source Sans 3', Arial, sans-serif;
  font-size: 10.5pt;
  color: {TEXT};
  line-height: 1.75;
  background: white;
}}

.cover {{
  page: cover;
  width: 210mm; height: 297mm;
  display: flex;
  page-break-after: always;
}}
.cover-left {{
  width: 42%; background: {NAVY};
  padding: 14mm 8mm 10mm 10mm;
  display: flex; flex-direction: column;
  justify-content: space-between;
  position: relative;
}}
.cover-left::after {{
  content: '';
  position: absolute; right: 0; top: 0; bottom: 0;
  width: 4px; background: {GOLD};
}}
.cover-right {{
  flex: 1; padding: 12mm 9mm 10mm 11mm;
  display: flex; flex-direction: column;
}}

.partie-break {{
  page: partie;
  width: 210mm; height: 297mm;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  page-break-before: always;
  page-break-after: always;
}}
.partie-num {{
  font-family: 'Playfair Display', Georgia, serif;
  font-size: 80pt; font-weight: 900;
  color: rgba(255,255,255,0.12); line-height: 1;
}}
.partie-titre {{
  font-family: 'Playfair Display', Georgia, serif;
  font-size: 32pt; font-weight: 700;
  color: white; letter-spacing: 0.05em;
  margin-top: -10mm;
}}
.partie-rule {{
  width: 20mm; height: 3px;
  background: rgba(255,255,255,0.4);
  margin: 6mm 0;
}}
.partie-sub {{
  font-size: 8pt; font-weight: 600;
  color: rgba(255,255,255,0.4);
  letter-spacing: 0.15em;
}}

.content {{ page: content; }}

.page-header {{
  position: running(pageHeader);
  display: table;
  width: 100%;
  border-bottom: 1.5px solid {NAVY};
  padding-bottom: 2.5mm;
}}
.page-header-left {{
  display: table-cell;
  font-family: Arial, sans-serif;
  font-size: 7.5pt; font-weight: 700;
  color: {NAVY}; letter-spacing: 0.06em;
}}
.page-header-right {{
  display: table-cell;
  text-align: right;
  font-family: Arial, sans-serif;
  font-size: 7pt; color: {MUTED};
}}

h1.h1 {{
  font-family: 'Playfair Display', Georgia, serif;
  font-size: 15pt; font-weight: 700; color: {NAVY};
  margin: 9mm 0 4mm; page-break-after: avoid;
}}
"""

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>DECISIO - Audit {nom_c}</title>
<style>{css}</style>
</head>
<body>

<div class="cover">
  <div class="cover-left">
    <div>
      <div style="font-family:'Playfair Display',Georgia,serif;font-size:30pt;font-weight:900;color:white;line-height:1">DECISIO</div>
      <div style="font-size:6.5pt;font-weight:700;color:{GOLD};letter-spacing:0.18em;text-transform:uppercase;margin-top:3mm">METHODE D3</div>
      <div style="font-size:6pt;color:rgba(255,255,255,0.35);letter-spacing:0.07em;margin-top:2mm">FIRST PRINCIPLES - AI-POWERED 48H</div>
    </div>
    <div style="margin-top:auto;padding-top:8mm">
      <div style="display:flex;align-items:flex-start;gap:4mm;margin-bottom:6mm">
        <div style="width:8mm;height:8mm;border-radius:50%;background:{GOLD};display:flex;align-items:center;justify-content:center;font-size:6.5pt;font-weight:700;color:{NAVY};flex-shrink:0">01</div>
        <div><div style="font-size:8.5pt;font-weight:700;color:white">DIAGNOSTIC</div><div style="font-size:7pt;color:{GOLD};opacity:0.8">Analyse complete</div></div>
      </div>
      <div style="display:flex;align-items:flex-start;gap:4mm;margin-bottom:6mm">
        <div style="width:8mm;height:8mm;border-radius:50%;background:{GOLD};display:flex;align-items:center;justify-content:center;font-size:6.5pt;font-weight:700;color:{NAVY};flex-shrink:0">02</div>
        <div><div style="font-size:8.5pt;font-weight:700;color:white">DECISION</div><div style="font-size:7pt;color:{GOLD};opacity:0.8">Options scorees</div></div>
      </div>
      <div style="display:flex;align-items:flex-start;gap:4mm;margin-bottom:6mm">
        <div style="width:8mm;height:8mm;border-radius:50%;background:{GOLD};display:flex;align-items:center;justify-content:center;font-size:6.5pt;font-weight:700;color:{NAVY};flex-shrink:0">03</div>
        <div><div style="font-size:8.5pt;font-weight:700;color:white">DEPLOIEMENT</div><div style="font-size:7pt;color:{GOLD};opacity:0.8">Plan d'action</div></div>
      </div>
    </div>
    <div style="font-size:6.5pt;color:rgba(255,255,255,0.3)">decisio.agency - contact@decisio.agency</div>
  </div>
  <div class="cover-right">
    <div style="align-self:flex-end;background:{NAVY};color:{GOLD};font-size:6.5pt;font-weight:700;letter-spacing:0.1em;padding:2.5mm 5mm;border-radius:1.5mm">{mode_c}</div>
    <div style="font-family:'Playfair Display',Georgia,serif;font-size:26pt;font-weight:700;color:{NAVY};line-height:1.1;margin-top:16mm">{nom_c}</div>
    <div style="width:20mm;height:2.5px;background:{GOLD};margin:4mm 0"></div>
    <div style="font-size:13pt;color:#444;font-weight:300">{secteur_c}</div>
    <div style="font-size:9pt;color:{MUTED};margin-top:2mm">{date_c}</div>
    <hr style="border:none;border-top:1px solid {BORDER};margin:7mm 0">
    <div style="background:{LIGHT_BG};border:1px solid {BORDER};border-left:3px solid {GOLD};border-radius:3mm;padding:6mm 7mm;margin-top:auto">
      <div style="font-size:7.5pt;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;color:{NAVY};margin-bottom:3mm">Audit Strategique</div>
      <div style="font-family:'Playfair Display',Georgia,serif;font-size:24pt;font-weight:700;color:{NAVY};line-height:1">{price}</div>
      <div style="font-size:7.5pt;color:{MUTED};margin-top:2mm">Livraison 48h - Methode D3 - Confidentiel</div>
    </div>
    <div style="font-size:6.5pt;color:{MUTED};margin-top:7mm;line-height:1.6">
      Ce rapport est strictement confidentiel et destine au seul usage du client designe ci-dessus.
      Toute reproduction est interdite sans autorisation ecrite de DECISIO AGENCY.
    </div>
  </div>
</div>

<div class="content">

  <div class="page-header">
    <span class="page-header-left">DECISIO - METHODE D3</span>
    <span class="page-header-right">{nom_c} - {secteur_c}</span>
  </div>

  <div style="font-family:'Playfair Display',Georgia,serif;font-size:18pt;font-weight:700;color:{NAVY};text-align:center;line-height:1.25;margin-bottom:3mm">RAPPORT D'AUDIT STRATEGIQUE - METHODE D3</div>
  <div style="font-size:9pt;color:{MUTED};text-align:center;margin-bottom:3mm">{nom_c} - {secteur_c} - {date_c}</div>
  <hr style="border:none;border-top:2.5px solid {NAVY};margin:3mm 0 1.5mm">
  <hr style="border:none;border-top:1px solid {GOLD};margin-bottom:9mm">

  {content_html}

  <div style="margin-top:12mm;padding-top:4mm;border-top:2px solid {NAVY};font-size:8pt;color:{MUTED};text-align:center;line-height:1.6">
    Rapport strictement confidentiel - DECISIO AGENCY - Methode D3 - contact@decisio.agency
  </div>

</div>

</body>
</html>"""


def generate_pdf(report_text, nom, secteur, mode, date_str=None):
    if not date_str:
        date_str = datetime.now().strftime('%d %B %Y')
    html_content = build_html(report_text, nom, secteur, mode, date_str)
    return HTML(string=html_content, base_url='.').write_pdf()
