# -*- coding: utf-8 -*-
"""
DECISIO PDF Generator V14 — ReportLab pur
==========================================
• Zéro dépendance système (pas de cairo/pango/gobject)
• 100% Python — fonctionne sur Railway, Heroku, partout
• UTF-8 complet : é è à ê ç ™ € · tous préservés
• Page de garde navy/doré niveau cabinet conseil
• Header/footer sur chaque page de contenu
• Pages séparatrices D3 entre chaque partie
• Tableaux protégés contre coupure
• Scores visuels en barres de progression
• Graphique financier natif
"""

import re
from datetime import datetime
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate, Frame, HRFlowable, Image, NextPageTemplate,
    PageBreak, PageTemplate, Paragraph, Spacer, Table, TableStyle,
    KeepTogether
)
from reportlab.platypus.flowables import Flowable
from reportlab.lib.colors import HexColor

# ── Palette ──────────────────────────────────────────────────
NAVY       = HexColor('#1C2B4A')
GOLD       = HexColor('#C9A84C')
LIGHT_BG   = HexColor('#F7F8FA')
BORDER_C   = HexColor('#E2E5EB')
TEXT_C     = HexColor('#1A1A2E')
MUTED_C    = HexColor('#6B7280')
RED_ACC    = HexColor('#C0392B')
GREEN_ACC  = HexColor('#1A7A45')
BLUE_ACC   = HexColor('#2563A8')
ORANGE_C   = HexColor('#C4621A')
WHITE_C    = colors.white
BLACK_C    = colors.black

PW, PH = A4  # 595.28 x 841.89 points
ML, MR, MT, MB = 26*mm, 26*mm, 24*mm, 22*mm
CW = PW - ML - MR  # content width

MODE_LABELS = {
    'flash':          'AUDIT FLASH · 490 €',
    'premium':        'AUDIT STRATÉGIQUE PREMIUM · 2 490 €',
    'transformation': 'AUDIT TRANSFORMATION · 6 900 €',
    'redressement':   'AUDIT REDRESSEMENT · 9 900 €',
    'diagnostic':     'DIAGNOSTIC GRATUIT',
}
PRICE_MAP = {
    'flash':          '490 €',
    'premium':        '2 490 €',
    'transformation': '6 900 €',
    'redressement':   '9 900 €',
    'diagnostic':     'Gratuit',
}


# ── Utilitaires texte ────────────────────────────────────────

def clean(s):
    s = str(s)
    s = s.replace('\u2014', ' — ').replace('\u2013', ' – ')
    s = s.replace('\u2018', '\u2019').replace('\u201c', '«').replace('\u201d', '»')
    s = re.sub(
        r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF'
        r'\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF'
        r'\U00002702-\U000027B0\U000024C2-\U0001F251]+',
        '', s)
    return s.strip()


def rl_escape(s):
    """Échappe les caractères spéciaux ReportLab."""
    s = clean(s)
    s = s.replace('&', '&amp;').replace('<', '&lt;').replace('>','&gt;')
    return s


def md_to_rl(s):
    """Convertit markdown basique en markup ReportLab."""
    s = rl_escape(s)
    s = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s)
    s = re.sub(r'\*(.+?)\*',     r'<i>\1</i>', s)
    return s


# ── Styles ───────────────────────────────────────────────────

def make_styles():
    base = getSampleStyleSheet()

    def S(name, **kw):
        return ParagraphStyle(name, **kw)

    return {
        'body': S('body',
            fontName='Helvetica', fontSize=10.5, leading=17,
            textColor=TEXT_C, alignment=TA_JUSTIFY,
            spaceAfter=4*mm),

        'h2': S('h2',
            fontName='Helvetica-Bold', fontSize=10, leading=14,
            textColor=WHITE_C, spaceAfter=4*mm, spaceBefore=9*mm),

        'h3': S('h3',
            fontName='Helvetica-Bold', fontSize=10.5, leading=14,
            textColor=NAVY, spaceAfter=2.5*mm, spaceBefore=7*mm),

        'h4': S('h4',
            fontName='Helvetica-Bold', fontSize=10, leading=13,
            textColor=NAVY, spaceAfter=2*mm, spaceBefore=5*mm),

        'bullet': S('bullet',
            fontName='Helvetica', fontSize=10.5, leading=17,
            textColor=TEXT_C, leftIndent=5*mm, spaceAfter=2.5*mm),

        'kv_key': S('kv_key',
            fontName='Helvetica-Bold', fontSize=9, leading=13,
            textColor=NAVY),

        'kv_val': S('kv_val',
            fontName='Helvetica', fontSize=9.5, leading=14,
            textColor=TEXT_C),

        'table_h': S('table_h',
            fontName='Helvetica-Bold', fontSize=9, leading=12,
            textColor=WHITE_C),

        'table_c': S('table_c',
            fontName='Helvetica', fontSize=9, leading=13,
            textColor=TEXT_C),

        'caption': S('caption',
            fontName='Helvetica', fontSize=7.5, leading=10,
            textColor=MUTED_C, alignment=TA_CENTER),

        'quote': S('quote',
            fontName='Helvetica-Oblique', fontSize=10, leading=15,
            textColor=HexColor('#334466'), leftIndent=4*mm,
            spaceAfter=3*mm),

        'verite': S('verite',
            fontName='Helvetica-BoldOblique', fontSize=11, leading=17,
            textColor=WHITE_C, spaceAfter=0),

        'footer': S('footer',
            fontName='Helvetica', fontSize=7.5, leading=10,
            textColor=MUTED_C, alignment=TA_CENTER),

        'option_title': S('option_title',
            fontName='Helvetica-Bold', fontSize=10, leading=13,
            textColor=NAVY),

        'option_detail': S('option_detail',
            fontName='Helvetica', fontSize=8.5, leading=12,
            textColor=MUTED_C),
    }


ST = make_styles()


# ── Flowables personnalisés ──────────────────────────────────

class ColorRect(Flowable):
    """Rectangle coloré pleine largeur."""
    def __init__(self, width, height, fill, radius=0):
        super().__init__()
        self.width  = width
        self.height = height
        self.fill   = fill
        self.radius = radius

    def draw(self):
        self.canv.setFillColor(self.fill)
        self.canv.roundRect(0, 0, self.width, self.height,
                            self.radius, fill=1, stroke=0)


class SectionHeader(Flowable):
    """Bandeau de section coloré avec filet gauche."""
    def __init__(self, text, color, width):
        super().__init__()
        self.text   = text
        self.color  = color
        self.width  = width
        self.height = 10*mm

    def draw(self):
        c = self.canv
        # Fond
        c.setFillColor(LIGHT_BG)
        c.rect(0, 0, self.width, self.height, fill=1, stroke=0)
        # Filet gauche
        c.setFillColor(self.color)
        c.rect(0, 0, 5, self.height, fill=1, stroke=0)
        # Texte
        c.setFillColor(self.color)
        c.setFont('Helvetica-Bold', 10)
        c.drawString(8*mm, 3.5*mm, self.text.upper())

    def wrap(self, aw, ah):
        return self.width, self.height


class ScoreBar(Flowable):
    """Barre de progression pour les scores."""
    def __init__(self, label, score, width, color=None):
        super().__init__()
        self.label  = label
        self.score  = score
        self.width  = width
        self.height = 8*mm
        if color:
            self.color = color
        elif score >= 7:
            self.color = GREEN_ACC
        elif score >= 5:
            self.color = ORANGE_C
        else:
            self.color = RED_ACC

    def draw(self):
        c    = self.canv
        pct  = self.score / 10
        bw   = self.width * 0.6
        bx   = self.width * 0.35
        by   = 1.5*mm
        bh   = 4*mm

        # Label
        c.setFillColor(TEXT_C)
        c.setFont('Helvetica', 9)
        c.drawString(0, by + 0.5*mm, self.label[:40])

        # Track
        c.setFillColor(BORDER_C)
        c.roundRect(bx, by, bw, bh, 2, fill=1, stroke=0)

        # Fill
        c.setFillColor(self.color)
        c.roundRect(bx, by, bw * pct, bh, 2, fill=1, stroke=0)

        # Valeur
        c.setFillColor(self.color)
        c.setFont('Helvetica-Bold', 9)
        c.drawRightString(self.width, by + 0.5*mm, f'{self.score}/10')

    def wrap(self, aw, ah):
        return self.width, self.height


class BarChart(Flowable):
    """Graphique barres financier navy/doré."""
    def __init__(self, data, width):
        super().__init__()
        self.data   = data   # [(label, current, projected)]
        self.width  = width
        self.height = 55*mm

    def draw(self):
        c     = self.canv
        n     = len(self.data)
        max_v = max(v for _, a, b in self.data for v in (a, b)) * 1.15
        max_h = 35*mm
        col_w = self.width / n
        bar_w = col_w * 0.25
        base_y = 12*mm

        for i, (label, current, projected) in enumerate(self.data):
            cx = col_w * i + col_w * 0.15
            px = col_w * i + col_w * 0.55

            h_c = (current   / max_v) * max_h
            h_p = (projected / max_v) * max_h

            # Barre actuel
            c.setFillColor(NAVY)
            c.roundRect(cx, base_y, bar_w, h_c, 1, fill=1, stroke=0)
            c.setFillColor(NAVY)
            c.setFont('Helvetica-Bold', 6)
            c.drawCentredString(cx + bar_w/2, base_y + h_c + 1*mm,
                                f'{current:,} €')

            # Barre projection
            c.setFillColor(GOLD)
            c.roundRect(px, base_y, bar_w, h_p, 1, fill=1, stroke=0)
            c.setFillColor(HexColor('#7A6020'))
            c.setFont('Helvetica-Bold', 6)
            c.drawCentredString(px + bar_w/2, base_y + h_p + 1*mm,
                                f'{projected:,} €')

            # Label période
            c.setFillColor(MUTED_C)
            c.setFont('Helvetica-Bold', 8)
            c.drawCentredString(col_w * i + col_w/2, 6*mm, label)

        # Ligne de base
        c.setStrokeColor(NAVY)
        c.setLineWidth(1.5)
        c.line(0, base_y, self.width, base_y)

        # Légende
        ly = 1*mm
        c.setFillColor(NAVY)
        c.roundRect(self.width/2 - 30*mm, ly, 4*mm, 3*mm, 1, fill=1, stroke=0)
        c.setFillColor(TEXT_C)
        c.setFont('Helvetica', 7.5)
        c.drawString(self.width/2 - 24*mm, ly + 0.5*mm, "Aujourd'hui")

        c.setFillColor(GOLD)
        c.roundRect(self.width/2 + 5*mm, ly, 4*mm, 3*mm, 1, fill=1, stroke=0)
        c.setFillColor(TEXT_C)
        c.setFont('Helvetica', 7.5)
        c.drawString(self.width/2 + 11*mm, ly + 0.5*mm, 'Projection')

    def wrap(self, aw, ah):
        return self.width, self.height


class VeriteFondamentale(Flowable):
    """Encadré vérité fondamentale navy/doré."""
    def __init__(self, text, width):
        super().__init__()
        self.text   = text
        self.width  = width
        self.height = 28*mm

    def draw(self):
        c = self.canv
        # Fond navy
        c.setFillColor(NAVY)
        c.roundRect(0, 0, self.width, self.height, 2, fill=1, stroke=0)
        # Filet doré gauche
        c.setFillColor(GOLD)
        c.rect(0, 0, 5, self.height, fill=1, stroke=0)
        # Label
        c.setFillColor(GOLD)
        c.setFont('Helvetica-Bold', 6.5)
        c.drawString(8*mm, self.height - 7*mm, 'VÉRITÉ FONDAMENTALE')
        # Texte
        c.setFillColor(WHITE_C)
        c.setFont('Helvetica-BoldOblique', 10.5)
        # Wrap manuel
        words = self.text.split()
        line, lines_out = '', []
        for w in words:
            test = line + ' ' + w if line else w
            if c.stringWidth(test, 'Helvetica-BoldOblique', 10.5) < self.width - 16*mm:
                line = test
            else:
                lines_out.append(line)
                line = w
        if line:
            lines_out.append(line)
        y = self.height - 14*mm
        for l in lines_out[:3]:
            c.drawString(8*mm, y, l)
            y -= 5.5*mm

    def wrap(self, aw, ah):
        return self.width, self.height


class OptionBlock(Flowable):
    """Bloc option A/B/C avec barre de score."""
    def __init__(self, letter, title, detail, score, color, width):
        super().__init__()
        self.letter = letter
        self.title  = title
        self.detail = detail
        self.score  = score
        self.color  = color
        self.width  = width
        self.height = 24*mm

    def draw(self):
        c = self.canv
        h = self.height
        # Fond
        c.setFillColor(LIGHT_BG)
        c.roundRect(0, 0, self.width, h, 2, fill=1, stroke=0)
        # Bordure gauche colorée
        c.setFillColor(self.color)
        c.roundRect(0, 0, 14*mm, h, 2, fill=1, stroke=0)
        c.rect(6*mm, 0, 8*mm, h, fill=1, stroke=0)
        # Lettre
        c.setFillColor(WHITE_C)
        c.setFont('Helvetica-Bold', 14)
        c.drawCentredString(7*mm, h/2 - 2.5*mm, self.letter)
        # Titre
        c.setFillColor(NAVY)
        c.setFont('Helvetica-Bold', 10)
        c.drawString(16*mm, h - 8*mm, self.title[:55])
        # Détail
        c.setFillColor(MUTED_C)
        c.setFont('Helvetica', 8.5)
        c.drawString(16*mm, h - 13.5*mm, self.detail[:70])
        # Barre score
        bx = 16*mm
        by = 3*mm
        bw = self.width - 22*mm
        bh = 4*mm
        pct = min(self.score / 10, 1.0)
        c.setFillColor(BORDER_C)
        c.roundRect(bx, by, bw, bh, 2, fill=1, stroke=0)
        c.setFillColor(self.color)
        c.roundRect(bx, by, bw * pct, bh, 2, fill=1, stroke=0)
        # Score texte
        c.setFillColor(self.color)
        c.setFont('Helvetica-Bold', 9)
        c.drawRightString(self.width - 2*mm, by + 0.5*mm,
                          f'{self.score}/10')

    def wrap(self, aw, ah):
        return self.width, self.height


# ── Page de garde ────────────────────────────────────────────

def draw_cover(canvas, nom, secteur, mode, date_str, price):
    canvas.saveState()
    w, h = A4

    # Colonne gauche navy
    canvas.setFillColor(NAVY)
    canvas.rect(0, 0, w * 0.42, h, fill=1, stroke=0)

    # Filet doré vertical
    canvas.setFillColor(GOLD)
    canvas.rect(w * 0.42, 0, 4, h, fill=1, stroke=0)

    # Logo DECISIO
    canvas.setFillColor(WHITE_C)
    canvas.setFont('Helvetica-Bold', 30)
    canvas.drawString(11*mm, h - 45*mm, 'DECISIO')

    canvas.setFillColor(GOLD)
    canvas.setFont('Helvetica-Bold', 6.5)
    canvas.drawString(11*mm, h - 52*mm, 'MÉTHODE D3™')

    canvas.setFillColor(HexColor('#FFFFFF55') if False else WHITE_C)
    canvas.setFillColorRGB(1, 1, 1, 0.35)
    canvas.setFont('Helvetica', 6)
    canvas.drawString(11*mm, h - 57*mm, 'FIRST PRINCIPLES · AI-POWERED 48H')

    # Étapes D3
    steps = [('01', 'DIAGNOSTIC', 'Analyse complète'),
             ('02', 'DÉCISION', 'Options scorées'),
             ('03', 'DÉPLOIEMENT', "Plan d'action")]
    y_step = 90*mm
    for num, lbl, sub in steps:
        # Cercle doré
        canvas.setFillColor(GOLD)
        canvas.circle(16*mm, y_step, 4.5*mm, fill=1, stroke=0)
        canvas.setFillColor(NAVY)
        canvas.setFont('Helvetica-Bold', 6.5)
        canvas.drawCentredString(16*mm, y_step - 1.5*mm, num)
        # Texte
        canvas.setFillColor(WHITE_C)
        canvas.setFont('Helvetica-Bold', 8.5)
        canvas.drawString(22*mm, y_step + 1*mm, lbl)
        canvas.setFillColor(GOLD)
        canvas.setFont('Helvetica', 7)
        canvas.drawString(22*mm, y_step - 4.5*mm, sub)
        y_step -= 17*mm

    # Contact
    canvas.setFillColorRGB(1, 1, 1, 0.28)
    canvas.setFont('Helvetica', 6)
    canvas.drawString(11*mm, 12*mm, 'decisio.agency · contact@decisio.agency')

    # ── Colonne droite ──
    rx = w * 0.42 + 10*mm
    rw = w - rx - 9*mm

    # Badge mode
    badge_text = clean(MODE_LABELS.get(mode, 'AUDIT PREMIUM'))
    canvas.setFillColor(NAVY)
    bw = canvas.stringWidth(badge_text, 'Helvetica-Bold', 6.5) + 10*mm
    canvas.roundRect(w - bw - 9*mm, h - 22*mm, bw, 7*mm, 1.5, fill=1, stroke=0)
    canvas.setFillColor(GOLD)
    canvas.setFont('Helvetica-Bold', 6.5)
    canvas.drawString(w - bw - 4*mm, h - 17.5*mm, badge_text)

    # Nom client
    canvas.setFillColor(NAVY)
    canvas.setFont('Helvetica-Bold', 26)
    nom_c = clean(nom)
    # Réduire taille si trop long
    fs = 26
    while canvas.stringWidth(nom_c, 'Helvetica-Bold', fs) > rw and fs > 14:
        fs -= 1
    canvas.setFont('Helvetica-Bold', fs)
    canvas.drawString(rx, h - 65*mm, nom_c)

    # Filet doré
    canvas.setFillColor(GOLD)
    canvas.rect(rx, h - 70*mm, 22*mm, 2.5, fill=1, stroke=0)

    # Secteur
    canvas.setFillColor(HexColor('#444444'))
    canvas.setFont('Helvetica', 13)
    canvas.drawString(rx, h - 79*mm, clean(secteur))

    # Date
    canvas.setFillColor(MUTED_C)
    canvas.setFont('Helvetica', 9)
    canvas.drawString(rx, h - 86*mm, clean(date_str))

    # Séparateur
    canvas.setStrokeColor(BORDER_C)
    canvas.setLineWidth(0.5)
    canvas.line(rx, h - 93*mm, w - 9*mm, h - 93*mm)

    # Encadré prix
    box_y = 52*mm
    box_h = 32*mm
    canvas.setFillColor(LIGHT_BG)
    canvas.roundRect(rx, box_y, rw, box_h, 2, fill=1, stroke=0)
    canvas.setStrokeColor(BORDER_C)
    canvas.setLineWidth(0.5)
    canvas.roundRect(rx, box_y, rw, box_h, 2, fill=0, stroke=1)
    canvas.setFillColor(GOLD)
    canvas.rect(rx, box_y, 3, box_h, fill=1, stroke=0)

    canvas.setFillColor(NAVY)
    canvas.setFont('Helvetica-Bold', 7)
    canvas.drawString(rx + 5*mm, box_y + box_h - 7*mm, 'AUDIT STRATÉGIQUE')

    canvas.setFont('Helvetica-Bold', 24)
    canvas.drawString(rx + 5*mm, box_y + box_h - 18*mm, clean(price))

    canvas.setFillColor(MUTED_C)
    canvas.setFont('Helvetica', 7.5)
    canvas.drawString(rx + 5*mm, box_y + 5*mm,
                      'Livraison 48h · Méthode D3™ · Confidentiel')

    # Confidentialité
    canvas.setFillColor(MUTED_C)
    canvas.setFont('Helvetica', 6.5)
    conf_text = ('Ce rapport est strictement confidentiel et destiné au seul usage '
                 'du client désigné ci-dessus.')
    canvas.drawString(rx, 32*mm, conf_text)
    canvas.drawString(rx, 27*mm,
                      'Toute reproduction est interdite sans autorisation écrite de DECISIO AGENCY.')

    canvas.restoreState()


# ── Page séparatrice ─────────────────────────────────────────

def draw_partie(canvas, num, titre, color):
    canvas.saveState()
    w, h = A4
    # Fond coloré
    canvas.setFillColor(color)
    canvas.rect(0, 0, w, h, fill=1, stroke=0)
    # Numéro grand
    canvas.setFillColorRGB(1, 1, 1, 0.10)
    canvas.setFont('Helvetica-Bold', 100)
    canvas.drawCentredString(w/2, h/2 + 10*mm, f'0{num}')
    # Titre
    canvas.setFillColor(WHITE_C)
    canvas.setFont('Helvetica-Bold', 30)
    canvas.drawCentredString(w/2, h/2 - 5*mm, titre.upper())
    # Filet
    canvas.setFillColor(HexColor('#FFFFFF66'))
    canvas.rect(w/2 - 12*mm, h/2 - 12*mm, 24*mm, 2.5, fill=1, stroke=0)
    # Sous-titre
    canvas.setFillColorRGB(1, 1, 1, 0.40)
    canvas.setFont('Helvetica-Bold', 7.5)
    canvas.drawCentredString(w/2, h/2 - 19*mm, 'MÉTHODE D3™ · DECISIO AGENCY')
    canvas.restoreState()


# ── Header/Footer ────────────────────────────────────────────

def make_header_footer(nom, secteur):
    def on_page(canvas, doc):
        canvas.saveState()
        w = A4[0]
        # Header — ligne navy + texte
        y_h = A4[1] - MT + 5*mm
        canvas.setStrokeColor(NAVY)
        canvas.setLineWidth(1.5)
        canvas.line(ML, y_h - 3*mm, w - MR, y_h - 3*mm)
        canvas.setFillColor(NAVY)
        canvas.setFont('Helvetica-Bold', 7.5)
        canvas.drawString(ML, y_h, 'DECISIO · MÉTHODE D3™')
        canvas.setFillColor(MUTED_C)
        canvas.setFont('Helvetica', 7)
        right_text = f'{clean(nom)} · {clean(secteur)}'
        canvas.drawRightString(w - MR, y_h, right_text)
        # Footer
        y_f = MB - 5*mm
        canvas.setStrokeColor(BORDER_C)
        canvas.setLineWidth(0.5)
        canvas.line(ML, y_f + 3*mm, w - MR, y_f + 3*mm)
        canvas.setFillColor(MUTED_C)
        canvas.setFont('Helvetica', 6.5)
        canvas.drawString(ML, y_f,
                          'CONFIDENTIEL · DECISIO AGENCY · MÉTHODE D3™')
        canvas.setFillColor(NAVY)
        canvas.setFont('Helvetica-Bold', 8)
        canvas.drawRightString(w - MR, y_f, str(doc.page))
        canvas.restoreState()
    return on_page


# ── Parser Markdown → Flowables ──────────────────────────────

def section_color(txt):
    t = txt.upper()
    if any(x in t for x in ['EXEC', 'SYNTH']):                     return GOLD
    if any(x in t for x in ['QUICK', 'WIN', '48H']):               return GREEN_ACC
    if any(x in t for x in ['DIAG', 'PARTIE 1']):                  return RED_ACC
    if any(x in t for x in ['DÉCIS', 'DECIS', 'PARTIE 2']):        return ORANGE_C
    if any(x in t for x in ['DÉPLOI', 'DEPLOY', 'PARTIE 3']):      return GREEN_ACC
    if any(x in t for x in ['ALLER', 'PLUS LOIN']):                return BLUE_ACC
    return NAVY


def parse_report(text, cw):
    lines   = text.split('\n')
    story   = []
    i       = 0

    while i < len(lines):
        line = lines[i].strip()

        if not line:
            i += 1
            continue

        if line == '---':
            story.append(HRFlowable(width=cw, color=BORDER_C, thickness=0.5,
                                    spaceAfter=4*mm))
            i += 1
            continue

        # H1 → séparatrice (# PARTIE, ■ PARTIE, PARTIE X)
        _h1 = re.match(r'^#\s+(.+)', line)
        _p2 = re.match(r'^[■●▶•]+\s*(PARTIE\s+[123].+)', line, re.I)
        _p3 = None
        if not line.startswith('|') and not _h1 and not _p2:
            _p3 = re.match(r'^(PARTIE\s+[123]\b.+)', line, re.I)
        m = _h1 or _p2 or _p3
        if m:
            t = clean(_h1.group(1) if _h1 else (_p2.group(1) if _p2 else _p3.group(1))).upper()
            if 'PARTIE 1' in t or 'DIAGNOSTIC' in t:
                story += [NextPageTemplate('partie'),
                          PageBreak(),
                          _PartieFlowable(1, 'Diagnostic', RED_ACC),
                          NextPageTemplate('content'),
                          PageBreak()]
            elif 'PARTIE 2' in t or 'DÉCISION' in t or 'DECISION' in t:
                story += [NextPageTemplate('partie'),
                          PageBreak(),
                          _PartieFlowable(2, 'Décision', ORANGE_C),
                          NextPageTemplate('content'),
                          PageBreak()]
            elif 'PARTIE 3' in t or 'DÉPLOIEMENT' in t or 'DEPLOIEMENT' in t:
                story += [NextPageTemplate('partie'),
                          PageBreak(),
                          _PartieFlowable(3, 'Déploiement', GREEN_ACC),
                          NextPageTemplate('content'),
                          PageBreak()]
            else:
                story.append(Paragraph(md_to_rl(t.title()),
                    ParagraphStyle('h1x', fontName='Helvetica-Bold', fontSize=14,
                                   leading=20, textColor=NAVY, spaceAfter=4*mm)))
            i += 1
            continue

        # H2
        m = re.match(r'^##\s+(.+)', line)
        if m:
            txt   = clean(m.group(1))
            color = section_color(txt)
            story.append(KeepTogether([
                SectionHeader(txt, color, cw),
                Spacer(1, 1*mm)
            ]))
            i += 1
            continue

        # H3
        m = re.match(r'^###\s+(.+)', line)
        if m:
            txt = clean(m.group(1))
            story.append(KeepTogether([
                Spacer(1, 2*mm),
                HRFlowable(width=cw, color=GOLD, thickness=2,
                           spaceAfter=1.5*mm),
                Paragraph(md_to_rl(txt), ST['h3']),
            ]))
            i += 1
            continue

        # H4
        m = re.match(r'^####\s+(.+)', line)
        if m:
            story.append(Paragraph(md_to_rl(m.group(1)), ST['h4']))
            i += 1
            continue

        # Vérité fondamentale
        if re.search(r'v[eé]rit[eé]\s+fondamentale', line, re.I):
            txt = re.sub(r'.*?v[eé]rit[eé]\s+fondamentale\s*:?\s*',
                         '', line, flags=re.I)
            txt = re.sub(r'^[#*>\[\]! ]+', '', txt).strip()
            if not txt and i + 1 < len(lines):
                i += 1
                txt = lines[i].strip()
            story.append(Spacer(1, 2*mm))
            story.append(VeriteFondamentale(clean(txt), cw))
            story.append(Spacer(1, 4*mm))
            i += 1
            continue

        # KEY :: VALUE
        kv = re.match(r'\*\*(.+?)\*\*\s*::\s*(.*)', line)
        if kv:
            tbl = Table(
                [[Paragraph(md_to_rl(kv.group(1)), ST['kv_key']),
                  Paragraph(md_to_rl(kv.group(2)), ST['kv_val'])]],
                colWidths=[52*mm, cw - 52*mm]
            )
            tbl.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), LIGHT_BG),
                ('LEFTPADDING',  (0,0), (0,-1), 4*mm),
                ('LEFTPADDING',  (1,0), (1,-1), 3*mm),
                ('RIGHTPADDING', (0,0), (-1,-1), 3*mm),
                ('TOPPADDING',   (0,0), (-1,-1), 3*mm),
                ('BOTTOMPADDING',(0,0), (-1,-1), 3*mm),
                ('LINEBELOW',    (0,0), (-1,-1), 0.5, BORDER_C),
                ('LINEBEFORE',   (0,0), (0,-1), 3, GOLD),
            ]))
            story.append(tbl)
            i += 1
            continue

        # Blockquote
        if line.startswith('>') or re.match(r'^-+>\s*', line):
            txt = re.sub(r'^-*>\s*', '', line).strip()
            story.append(Paragraph(md_to_rl(txt), ST['quote']))
            i += 1
            continue

        # Options A/B/C
        opt = re.match(r'^OPTION\s+([A-C])\s*[-–—]?\s*(.{5,})', line, re.I)
        if opt:
            letter    = opt.group(1).upper()
            title     = clean(opt.group(2).strip()[:70])
            score_val = 5.0
            detail    = ''
            j = i + 1
            while j < len(lines) and j < i + 6:
                nl = lines[j].strip()
                sm = re.search(r'Score\s*:\s*([\d,.]+)', nl, re.I)
                if sm:
                    try:
                        score_val = float(sm.group(1).replace(',', '.'))
                    except Exception:
                        pass
                    detail = re.sub(r'Score\s*:.*', '', nl).strip()
                    break
                if nl:
                    detail += clean(nl[:70]) + ' '
                j += 1
            col_map = {'A': GREEN_ACC, 'B': ORANGE_C, 'C': RED_ACC}
            col = col_map.get(letter, NAVY)
            lp = Paragraph(
                '<font color="white" size="14"><b>' + letter + '</b></font>',
                ParagraphStyle('ol', alignment=1, leading=20))
            bp = [
                Paragraph('<font size="10"><b>' + rl_escape(title) + '</b></font>',
                          ParagraphStyle('ot', leading=14, textColor=NAVY, spaceAfter=2*mm)),
                Paragraph('<font size="8">' + rl_escape(detail.strip()) + '</font>',
                          ParagraphStyle('od', leading=12, textColor=MUTED_C, spaceAfter=2*mm)),
                Paragraph('<font size="9"><b>' + str(score_val) + '/10</b></font>',
                          ParagraphStyle('os', leading=11, textColor=col)),
            ]
            opt_tbl = Table([[lp, bp]], colWidths=[14*mm, cw - 14*mm])
            opt_tbl.setStyle(TableStyle([
                ('BACKGROUND',    (0, 0), (0, -1), col),
                ('BACKGROUND',    (1, 0), (1, -1), LIGHT_BG),
                ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING',   (0, 0), (0, -1), 3*mm),
                ('LEFTPADDING',   (1, 0), (1, -1), 4*mm),
                ('TOPPADDING',    (0, 0), (-1, -1), 3*mm),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3*mm),
            ]))
            story.append(KeepTogether([opt_tbl]))
            story.append(Spacer(1, 2*mm))
            i += 1
            continue

        # Message card
        mm_m = re.match(r'^(Message\s+\d[^:]*)', line, re.I)
        if mm_m:
            label = clean(mm_m.group(1))
            rest  = line[len(mm_m.group(0)):].lstrip(': ').strip()
            if not rest and i + 1 < len(lines):
                i += 1
                rest = lines[i].strip()
            tbl = Table(
                [[Paragraph(f'<font color="{BLUE_ACC.hexval()}" size="7">'
                            f'<b>{rl_escape(label).upper()}</b></font>',
                            ST['caption']),],
                 [Paragraph(f'<i>« {md_to_rl(rest)} »</i>', ST['body'])]],
                colWidths=[cw]
            )
            tbl.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), HexColor('#EEF4FF')),
                ('LINEBEFORE',  (0,0), (0,-1), 4, BLUE_ACC),
                ('LEFTPADDING', (0,0), (-1,-1), 5*mm),
                ('TOPPADDING',  (0,0), (-1,0), 3*mm),
                ('BOTTOMPADDING',(0,-1),(-1,-1), 3*mm),
                ('ROUNDEDCORNERS', [2]),
            ]))
            story.append(tbl)
            story.append(Spacer(1, 3*mm))
            i += 1
            continue

        # Graphique
        if line.startswith('CHART_BAR:'):
            chart_rows = []
            for seg in line[len('CHART_BAR:'):].split('|'):
                parts = seg.strip().split(':')
                if len(parts) == 3:
                    try:
                        chart_rows.append((parts[0].strip(),
                                           int(parts[1]),
                                           int(parts[2])))
                    except Exception:
                        pass
            if chart_rows:
                story.append(Spacer(1, 3*mm))
                story.append(BarChart(chart_rows, cw))
                story.append(Spacer(1, 3*mm))
            i += 1
            continue

        # Bullets
        if re.match(r'^[-*•]\s', line):
            items = []
            while i < len(lines):
                l = lines[i].strip()
                if re.match(r'^[-*•]\s', l):
                    items.append(re.sub(r'^[-*•]\s+', '', l))
                    i += 1
                else:
                    break
            for it in items:
                p = Paragraph(
                    f'<bullet color="{GOLD.hexval()}">●</bullet> {md_to_rl(it)}',
                    ST['bullet']
                )
                story.append(p)
            story.append(Spacer(1, 1*mm))
            continue

        # Liste numérotée
        if re.match(r'^\d+[.)]\s', line):
            items = []
            while i < len(lines):
                l = lines[i].strip()
                if re.match(r'^\d+[.)]\s', l):
                    items.append(re.sub(r'^\d+[.)]\s+', '', l))
                    i += 1
                else:
                    break
            for n, it in enumerate(items, 1):
                p = Paragraph(f'{n}. {md_to_rl(it)}', ST['bullet'])
                story.append(p)
            story.append(Spacer(1, 1*mm))
            continue

        # Tableau Markdown
        if line.startswith('|'):
            rows        = []
            header_done = False
            while i < len(lines) and lines[i].strip().startswith('|'):
                row_line = lines[i].strip()
                if re.match(r'^\|[\s\-:|]+\|$', row_line):
                    header_done = True
                    i += 1
                    continue
                cells = [c.strip() for c in row_line.strip('|').split('|')]
                rows.append((cells, not header_done and len(rows) == 0))
                i += 1

            if rows:
                # Calculer largeurs colonnes équilibrées
                n_cols = max(len(r) for r, _ in rows)
                col_w  = [cw / n_cols] * n_cols

                tbl_data = []
                for cells, is_hdr in rows:
                    # Padding si moins de colonnes
                    while len(cells) < n_cols:
                        cells.append('')
                    style = ST['table_h'] if is_hdr else ST['table_c']
                    tbl_data.append([Paragraph(md_to_rl(c), style)
                                     for c in cells])

                tbl = Table(tbl_data, colWidths=col_w, repeatRows=1)
                ts  = TableStyle([
                    ('BACKGROUND',   (0,0), (-1,0),  NAVY),
                    ('LINEABOVE',    (0,0), (-1,0),  2.5, GOLD),
                    ('ROWBACKGROUNDS', (0,1), (-1,-1),
                     [WHITE_C, LIGHT_BG]),
                    ('LINEBELOW',    (0,1), (-1,-1), 0.3, BORDER_C),
                    ('LEFTPADDING',  (0,0), (-1,-1), 4*mm),
                    ('RIGHTPADDING', (0,0), (-1,-1), 3*mm),
                    ('TOPPADDING',   (0,0), (-1,-1), 3*mm),
                    ('BOTTOMPADDING',(0,0), (-1,-1), 3*mm),
                    ('VALIGN',       (0,0), (-1,-1), 'TOP'),
                ])
                tbl.setStyle(ts)
                story.append(KeepTogether([tbl]))
                story.append(Spacer(1, 3*mm))
                _chart = []
                for _c2, _h2 in rows:
                    if _h2 or not _c2:
                        continue
                    if re.match(r'M\+[136]', _c2[0].strip()):
                        try:
                            def _pn(s):
                                s = re.sub(r'[€\s+,]', '', str(s).strip())
                                return int(float(re.sub(r'[^0-9.]', '', s) or '0'))
                            if len(_c2) >= 3:
                                _chart.append((_c2[0].strip(), _pn(_c2[1]), _pn(_c2[2])))
                        except Exception:
                            pass
                if len(_chart) >= 2:
                    story.append(Spacer(1, 2*mm))
                    story.append(BarChart(_chart, cw))
                    story.append(Spacer(1, 3*mm))
            continue

        # Paragraphe normal
        story.append(Paragraph(md_to_rl(line), ST['body']))
        i += 1

    return story


class _PartieFlowable(Flowable):
    """Flowable qui déclenche le dessin d'une page séparatrice."""
    def __init__(self, num, titre, color):
        super().__init__()
        self.num   = num
        self.titre = titre
        self.color = color
        self.width  = A4[0]
        self.height = A4[1]

    def draw(self):
        draw_partie(self.canv, self.num, self.titre, self.color)

    def wrap(self, aw, ah):
        return A4


# ── Constructeur principal ───────────────────────────────────

def generate_pdf(report_text, nom, secteur, mode='premium', date_str=None):
    if not date_str:
        date_str = datetime.now().strftime('%d %B %Y')

    price = PRICE_MAP.get(mode, '2 490 €')
    buf   = BytesIO()
    on_page = make_header_footer(nom, secteur)

    # Templates de pages
    cover_frame   = Frame(0, 0, PW, PH, leftPadding=0, rightPadding=0,
                          topPadding=0, bottomPadding=0)
    partie_frame  = Frame(0, 0, PW, PH, leftPadding=0, rightPadding=0,
                          topPadding=0, bottomPadding=0)
    content_frame = Frame(ML, MB, CW, PH - MT - MB,
                          leftPadding=0, rightPadding=0,
                          topPadding=0, bottomPadding=0)

    def cover_bg(canvas, doc):
        draw_cover(canvas, nom, secteur, mode, date_str, price)

    def partie_bg(canvas, doc):
        pass  # Dessiné par _PartieFlowable

    doc = BaseDocTemplate(
        buf, pagesize=A4,
        leftMargin=ML, rightMargin=MR,
        topMargin=MT, bottomMargin=MB,
    )
    doc.addPageTemplates([
        PageTemplate(id='cover',   frames=[cover_frame],
                     onPage=cover_bg),
        PageTemplate(id='partie',  frames=[partie_frame],
                     onPage=partie_bg),
        PageTemplate(id='content', frames=[content_frame],
                     onPage=on_page),
    ])

    # Story
    story = [NextPageTemplate('content'), PageBreak()]

    # En-tête du rapport
    story += [
        Paragraph(
            f'RAPPORT D\'AUDIT STRATÉGIQUE — MÉTHODE D3™',
            ParagraphStyle('rh',
                fontName='Helvetica-Bold', fontSize=17, leading=22,
                textColor=NAVY, alignment=TA_CENTER, spaceAfter=3*mm)
        ),
        Paragraph(
            f'{clean(nom)} · {clean(secteur)} · {clean(date_str)}',
            ParagraphStyle('rs',
                fontName='Helvetica', fontSize=9, leading=12,
                textColor=MUTED_C, alignment=TA_CENTER, spaceAfter=3*mm)
        ),
        HRFlowable(width=CW, color=NAVY, thickness=2.5, spaceAfter=1.5*mm),
        HRFlowable(width=CW, color=GOLD, thickness=1, spaceAfter=9*mm),
    ]

    # Contenu parsé
    story += parse_report(report_text, CW)

    # Footer rapport
    story += [
        Spacer(1, 10*mm),
        HRFlowable(width=CW, color=NAVY, thickness=2, spaceAfter=3*mm),
        Paragraph(
            'Rapport strictement confidentiel — DECISIO AGENCY · '
            'Méthode D3™ · contact@decisio.agency',
            ST['footer']
        ),
    ]

    doc.build(story)
    return buf.getvalue()
