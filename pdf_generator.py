"""
DECISIO PDF Generator V3 — Style McKinsey/BCG Authentique
Georgia serif + Helvetica | Bleu marine | Structure Pyramid Principle
"""
import re
from datetime import datetime
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether
)
from reportlab.platypus.flowables import Flowable
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pypdf import PdfReader, PdfWriter

# ═══ ENREGISTREMENT POLICES TTF (Liberation Sans = Arial + accents complets) ═══
_FONTS_REGISTERED = False
def register_fonts():
    global _FONTS_REGISTERED
    if _FONTS_REGISTERED:
        return
    import os
    # Chercher d'abord dans fonts/ à côté du fichier (déploiement Railway)
    here = os.path.dirname(os.path.abspath(__file__))
    local = os.path.join(here, 'fonts')
    system = '/usr/share/fonts/truetype/liberation'
    base = local if os.path.isdir(local) else system
    pdfmetrics.registerFont(TTFont('LS',            os.path.join(base, 'LiberationSans-Regular.ttf')))
    pdfmetrics.registerFont(TTFont('LS-Bold',       os.path.join(base, 'LiberationSans-Bold.ttf')))
    pdfmetrics.registerFont(TTFont('LS-Italic',     os.path.join(base, 'LiberationSans-Italic.ttf')))
    pdfmetrics.registerFont(TTFont('LS-BoldItalic', os.path.join(base, 'LiberationSans-BoldItalic.ttf')))
    from reportlab.pdfbase.pdfmetrics import registerFontFamily
    registerFontFamily('LS', normal='LS', bold='LS-Bold',
                       italic='LS-Italic', boldItalic='LS-BoldItalic')
    _FONTS_REGISTERED = True

W, H = A4
ML = 21*mm
MR = 21*mm
CW = W - ML - MR

# ═══ PALETTE McKINSEY/BCG AUTHENTIQUE ═══════════════════════
NAVY        = colors.HexColor('#1C2B4A')   # Bleu marine McKinsey
NAVY2       = colors.HexColor('#243656')   # Variante plus claire
BLUE_ACC    = colors.HexColor('#2563A8')   # Bleu accent liens/soulignements
TEAL        = colors.HexColor('#0D6E6E')   # Teal section Deploy/Green
RED_ACC     = colors.HexColor('#B83232')   # Rouge section Diagnostic
ORANGE_ACC  = colors.HexColor('#C4621A')   # Orange section Decision
GREEN_ACC   = colors.HexColor('#1A7A45')   # Vert section Deploy
GOLD_ACC    = colors.HexColor('#B8860B')   # Or section Executive
PURPLE_ACC  = colors.HexColor('#5B3FA6')   # Violet section Pour aller loin

BLACK       = colors.HexColor('#1A1A1A')
CHARCOAL    = colors.HexColor('#2D2D2D')
DARK_GREY   = colors.HexColor('#404040')
MID_GREY    = colors.HexColor('#666666')
LIGHT_GREY  = colors.HexColor('#999999')
RULE        = colors.HexColor('#DDDDDD')
BG_STRIP    = colors.HexColor('#F5F6F8')   # Fond alternance tableau
BG_CALLOUT  = colors.HexColor('#F0F4FB')   # Fond callout bleu très pâle
BG_WARNING  = colors.HexColor('#FDF5F0')   # Fond warning orangé très pâle
BG_SUCCESS  = colors.HexColor('#F0FAF4')   # Fond success vert très pâle
BG_GOLD     = colors.HexColor('#FDFAF0')   # Fond gold très pâle
WHITE       = colors.white

# ═══ HELPERS ════════════════════════════════════════════════
EMOJI_CLEAN = {
    # Emojis → supprimer
    '🏆':'', '⚡':'', '🔴':'', '🟡':'', '🟢':'', '🎯':'',
    '🛑':'STOP', '🔄':'PIVOT', '✅':'OK',
    # Flèches → ASCII
    '→':'->', '←':'<-', '↑':'^', '↓':'v',
    # Typographie — conserver le sens
    '\u2212':'-',    # − signe moins mathématique
    '\u2013':'-',    # – tiret demi-cadratin
    '\u2014':' - ',  # — tiret cadratin
    '\u2026':'...',  # … points de suspension
    '\u2018':"'",    # ' guillemet gauche
    '\u2019':"'",    # ' guillemet droit
    '\u201c':'"',    # " guillemet gauche double
    '\u201d':'"',    # " guillemet droit double
    '\u00d7':'x',    # × multiplication
    '\u00f7':'/',    # ÷ division
    '\u2264':'<=',   # ≤
    '\u2265':'>=',   # ≥
    # GARDER les accents français — Liberation Sans les supporte
    # GARDER € et ™ — Liberation Sans les supporte
}

def clean(s):
    """Nettoyer le texte en préservant accents, € et ™."""
    s = str(s)
    for k, v in EMOJI_CLEAN.items():
        s = s.replace(k, v)
    result = []
    for ch in s:
        cp = ord(ch)
        # Garder : ASCII imprimable
        if 0x20 <= cp <= 0x7E:
            result.append(ch)
        # Garder : Latin étendu complet (accents français)
        elif 0x00C0 <= cp <= 0x024F:
            result.append(ch)
        # Garder : € (euro)
        elif cp == 0x20AC:
            result.append('€')
        # Garder : ™ (trademark)
        elif cp == 0x2122:
            result.append('\u2122')  # ™ direct
        # Garder : ® (registered)
        elif cp == 0x00AE:
            result.append('\u00AE')
        # Garder : guillemets typographiques → neutres
        elif cp == 0x00AB:
            result.append('"')
        elif cp == 0x00BB:
            result.append('"')
        # Garder : bullet → *
        elif cp == 0x2022:
            result.append('*')
        elif cp == 0x00B7:
            result.append('*')
        # Newlines et tabs
        elif ch in ('\n', '\t'):
            result.append(ch)
        # Ignorer le reste (emojis, CJK, etc.)
    return ''.join(result)

def strip_md(s):
    s = clean(s)
    s = re.sub(r'\*\*(.*?)\*\*', r'\1', s)
    s = re.sub(r'\*(.*?)\*', r'\1', s)
    s = re.sub(r'^#{1,4}\s+', '', s)
    s = re.sub(r'^[-*>]+\s*', '', s)  # retire prefixes markdown
    # Nettoyer les caracteres de controle restants
    s = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', s)
    return s.strip()

def rich(s, style):
    """Markdown basique → ReportLab XML"""
    s = clean(s)
    s = re.sub(r'\*\*(.*?)\*\*',r'<b>\1</b>',s)
    s = re.sub(r'\*(.*?)\*',r'<i>\1</i>',s)
    s = s.replace('&','&amp;')
    for tag in ['b','i','b/','i/']: 
        s = s.replace(f'&lt;{tag}&gt;',f'<{tag}>')
    # Protéger les vraies balises
    s = s.replace('<b>','\x00b').replace('</b>','\x00/b')
    s = s.replace('<i>','\x00i').replace('</i>','\x00/i')
    s = s.replace('<','&lt;').replace('>','&gt;')
    s = s.replace('\x00b','<b>').replace('\x00/b','</b>')
    s = s.replace('\x00i','<i>').replace('\x00/i','</i>')
    try:    return Paragraph(s, style)
    except: return Paragraph(strip_md(s), style)

def sec_accent(text):
    t = text.upper()
    if any(x in t for x in ['EXEC','SYNTH','EXECUTIV']): return GOLD_ACC
    if any(x in t for x in ['QUICK','WIN','48H','48 H']): return GREEN_ACC
    if any(x in t for x in ['DIAG','PARTIE 1','PART 1']): return RED_ACC
    if any(x in t for x in ['DECIS','PARTIE 2','PART 2']): return ORANGE_ACC
    if any(x in t for x in ['DEPLOY','PARTIE 3','PART 3']): return GREEN_ACC
    if any(x in t for x in ['LOIN','COMPLEM','SUITE']): return PURPLE_ACC
    return BLUE_ACC

# ═══ STYLES TYPOGRAPHIQUES ══════════════════════════════════
def styles():
    return {
        # Corps principal — Helvetica 10pt justifié, leading généreux
        'body': ParagraphStyle('body',
            fontName='LS', fontSize=10, textColor=CHARCOAL,
            leading=16, spaceAfter=5, alignment=TA_JUSTIFY),
        # Labels clés — bold NAVY
        'label': ParagraphStyle('label',
            fontName='LS-Bold', fontSize=9.5, textColor=NAVY,
            leading=14, spaceAfter=2),
        # Valeur associée
        'value': ParagraphStyle('value',
            fontName='LS', fontSize=9.5, textColor=CHARCOAL,
            leading=14, spaceAfter=2),
        # Note de bas / muted
        'muted': ParagraphStyle('muted',
            fontName='LS-Italic', fontSize=8.5, textColor=MID_GREY,
            leading=12, spaceAfter=3),
        # Bullet
        'bullet': ParagraphStyle('bullet',
            fontName='LS', fontSize=10, textColor=CHARCOAL,
            leading=15, spaceAfter=4, leftIndent=16, firstLineIndent=0),
        # H4 inline
        'h4': ParagraphStyle('h4',
            fontName='LS-Bold', fontSize=10.5, textColor=NAVY,
            leading=15, spaceBefore=6, spaceAfter=3),
        # Tableau header
        'th': ParagraphStyle('th',
            fontName='LS-Bold', fontSize=8.5, textColor=WHITE,
            leading=12, alignment=TA_LEFT),
        # Tableau cellule
        'td': ParagraphStyle('td',
            fontName='LS', fontSize=8.5, textColor=CHARCOAL,
            leading=12),
        # Headline statement (résumé message clé en haut de section — style McKinsey)
        'headline': ParagraphStyle('headline',
            fontName='LS-BoldItalic', fontSize=10.5, textColor=NAVY,
            leading=16, spaceAfter=6, leftIndent=6),
        # Footer
        'footer': ParagraphStyle('footer',
            fontName='LS', fontSize=7, textColor=LIGHT_GREY,
            leading=10, alignment=TA_CENTER),
        # Message script
        'script': ParagraphStyle('script',
            fontName='LS-Italic', fontSize=9.5, textColor=DARK_GREY,
            leading=15, spaceAfter=3),
    }

# ═══ FLOWABLES CUSTOM ═══════════════════════════════════════

class SectionHeader(Flowable):
    """
    Header H2 McKinsey : barre pleine couleur a gauche (5px),
    texte MAJUSCULE propre, fond legerement teinte, ligne couleur bas
    """
    def __init__(self, text, accent, width=CW):
        self.text = strip_md(text).upper()
        self.accent = accent
        self.w = width
        Flowable.__init__(self)

    def draw(self):
        c = self.canv
        c.setFillColor(BG_STRIP)
        c.rect(0, 0, self.w, 11*mm, fill=1, stroke=0)
        c.setFillColor(self.accent)
        c.rect(0, 0, 5, 11*mm, fill=1, stroke=0)
        c.setFillColor(self.accent)
        c.rect(0, 0, self.w, 1.5, fill=1, stroke=0)
        c.setFillColor(NAVY)
        c.setFont('LS-Bold', 11)
        txt = self.text[:70]
        c.drawString(11, 11*mm/2 - 3.5, txt)

    def wrap(self, aW, aH): return (aW, 11*mm)


class SubHeader(Flowable):
    """H3 sobre : numéro + titre, ligne accent en dessous"""
    def __init__(self, text, accent, width=CW):
        self.text = strip_md(text)
        self.accent = accent
        self.w = width
        Flowable.__init__(self)

    def draw(self):
        c = self.canv
        c.setFillColor(self.accent)
        c.setFont('LS-Bold', 10.5)
        c.drawString(0, 6, self.text[:80])
        # Ligne accent sous le titre
        text_w = min(len(self.text) * 5.5, self.w * 0.75)
        c.setFillColor(self.accent)
        c.rect(0, 2, text_w, 2, fill=1, stroke=0)

    def wrap(self, aW, aH): return (aW, 10*mm)


class KeyInsight(Flowable):
    """
    Encadré insight clé McKinsey :
    Barre gauche couleur + fond très pâle + texte italic NAVY
    """
    def __init__(self, label, text, accent=NAVY, bg=BG_CALLOUT, width=CW):
        self.label = clean(label)
        self.text = strip_md(text)
        self.accent = accent
        self.bg = bg
        self.w = width
        Flowable.__init__(self)
        cpl = int((width - 26) / 5.0)
        n = max(1, -(-len(self.text) // max(cpl, 1)))
        self.h = n * 14 + 30

    def draw(self):
        c = self.canv
        h = self.h
        # Fond
        c.setFillColor(self.bg)
        c.rect(0, 0, self.w, h, fill=1, stroke=0)
        # Barre gauche
        c.setFillColor(self.accent)
        c.rect(0, 0, 4, h, fill=1, stroke=0)
        # Label
        c.setFillColor(self.accent)
        c.setFont('LS-Bold', 7.5)
        c.drawString(11, h - 13, self.label.upper())
        # Texte
        c.setFillColor(CHARCOAL)
        c.setFont('LS-Italic', 9.5)
        words = self.text.split()
        line = ''; y = h - 25
        cpl = int((self.w - 22) / 5.0)
        for word in words:
            if len(line + word) < cpl: line += word + ' '
            else:
                c.drawString(11, y, line.strip()); y -= 14; line = word + ' '
        if line: c.drawString(11, y, line.strip())

    def wrap(self, aW, aH): return (aW, self.h + 3*mm)


class VeritefBlock(Flowable):
    """
    Vérité fondamentale McKinsey-style :
    Fond or très pâle, barre or, label small caps, texte bold italic
    """
    def __init__(self, text, width=CW):
        self.text = strip_md(text)
        self.w = width
        Flowable.__init__(self)
        cpl = int((width - 26) / 5.2)
        n = max(1, -(-len(self.text) // max(cpl, 1)))
        self.h = n * 15 + 34

    def draw(self):
        c = self.canv
        h = self.h
        # Fond navy plein — style McKinsey statement box
        c.setFillColor(NAVY)
        c.rect(0, 0, self.w, h, fill=1, stroke=0)
        # Barre or gauche épaisse
        c.setFillColor(GOLD_ACC)
        c.rect(0, 0, 5, h, fill=1, stroke=0)
        # Ligne or top
        c.setFillColor(GOLD_ACC)
        c.rect(0, h-2.5, self.w, 2.5, fill=1, stroke=0)
        # Label
        c.setFillColor(GOLD_ACC)
        c.setFont('LS-Bold', 7)
        c.drawString(13, h - 14, 'VÉRITÉ FONDAMENTALE')
        # Texte
        c.setFillColor(WHITE)
        c.setFont('LS-BoldItalic', 10)
        words = self.text.split()
        line = ''; y = h - 28
        cpl = int((self.w - 24) / 5.1)
        for word in words:
            if len(line + word) < cpl: line += word + ' '
            else:
                c.drawString(12, y, line.strip()); y -= 15; line = word + ' '
        if line: c.drawString(12, y, line.strip())

    def wrap(self, aW, aH): return (aW, self.h + 3*mm)


class MessageCard(Flowable):
    """Script de message — fond légèrement bleuté, guillemets visuels"""
    def __init__(self, label, text, width=CW):
        self.label = clean(label)
        self.text = clean(text)
        self.w = width
        Flowable.__init__(self)
        cpl = int((width - 28) / 5.0)
        n = max(2, -(-len(self.text) // max(cpl, 1)))
        self.h = n * 13 + 36

    def draw(self):
        c = self.canv
        h = self.h
        c.setFillColor(BG_CALLOUT)
        c.roundRect(0, 0, self.w, h, 2*mm, fill=1, stroke=0)
        c.setStrokeColor(RULE)
        c.setLineWidth(0.6)
        c.roundRect(0, 0, self.w, h, 2*mm, fill=0, stroke=1)
        # Guillemet décoratif
        c.setFillColor(BLUE_ACC)
        c.setFont('LS-Bold', 28)
        c.drawString(8, h - 22, '"')
        # Label
        c.setFillColor(BLUE_ACC)
        c.setFont('LS-Bold', 8)
        c.drawString(24, h - 14, self.label)
        # Texte
        c.setFillColor(CHARCOAL)
        c.setFont('LS-Italic', 9)
        words = self.text.split(); line = ''; y = h - 28
        cpl = int((self.w - 24) / 4.9)
        for word in words:
            if len(line + word) < cpl: line += word + ' '
            else:
                c.drawString(12, y, line.strip()); y -= 13; line = word + ' '
        if line: c.drawString(12, y, line.strip())

    def wrap(self, aW, aH): return (aW, self.h + 3*mm)


class ScoreCard(Flowable):
    """Option avec score — card sobre style BCG"""
    def __init__(self, letter, title, detail, score, accent=NAVY, width=CW):
        self.letter = clean(letter)
        self.title = clean(title)
        self.detail = clean(detail)
        self.score = clean(score)
        self.accent = accent
        self.w = width
        Flowable.__init__(self)
        cpl = int((width - 80) / 4.9)
        n = max(1, -(-len(self.detail) // max(cpl, 1)))
        self.h = max(22*mm, n * 12 + 30)

    def draw(self):
        c = self.canv
        h = self.h
        bw = 18*mm
        # Fond
        c.setFillColor(BG_STRIP)
        c.roundRect(0, 0, self.w, h, 2*mm, fill=1, stroke=0)
        c.setStrokeColor(RULE)
        c.setLineWidth(0.5)
        c.roundRect(0, 0, self.w, h, 2*mm, fill=0, stroke=1)
        # Barre gauche couleur
        c.setFillColor(self.accent)
        c.roundRect(0, 0, 8, h, 2*mm, fill=1, stroke=0)
        c.rect(4, 0, 4, h, fill=1, stroke=0)
        # Lettre option
        c.setFillColor(WHITE)
        c.setFont('LS-Bold', 13)
        c.drawCentredString(4, h/2 - 4, self.letter)
        # Badge score (droite)
        c.setFillColor(NAVY)
        c.roundRect(self.w - bw - 6, h/2 - 9*mm, bw, 18*mm, 2*mm, fill=1, stroke=0)
        c.setFillColor(GOLD_ACC)
        c.setFont('LS-Bold', 18)
        score_display = self.score if '/' not in self.score else self.score.split('/')[0]
        c.drawCentredString(self.w - bw/2 - 6, h/2 - 2, score_display)
        c.setFillColor(LIGHT_GREY)
        c.setFont('LS', 7)
        c.drawCentredString(self.w - bw/2 - 6, h/2 - 9, '/10')
        # Titre
        c.setFillColor(NAVY)
        c.setFont('LS-Bold', 10)
        c.drawString(16, h - 12, self.title[:60])
        # Detail
        c.setFillColor(MID_GREY)
        c.setFont('LS', 8.5)
        words = self.detail.split(); line = ''; y = h - 24
        cpl = int((self.w - bw - 28) / 4.8)
        for word in words:
            if len(line + word) < cpl: line += word + ' '
            else:
                c.drawString(16, y, line.strip()); y -= 12; line = word + ' '
        if line: c.drawString(16, y, line.strip())

    def wrap(self, aW, aH): return (aW, self.h + 3*mm)



class FinancialBarChart(Flowable):
    """Graphique barres M+1/M+3/M+6 style McKinsey — aujourd'hui vs projection"""
    def __init__(self, data, width=CW):
        # data = [(label, current, projected), ...]
        self.data = data
        self.w = width
        self.h = 52*mm
        Flowable.__init__(self)

    def draw(self):
        c = self.canv
        w, h = self.w, self.h
        pad_l, pad_r, pad_b, pad_t = 14*mm, 8*mm, 12*mm, 8*mm
        chart_w = w - pad_l - pad_r
        chart_h = h - pad_b - pad_t
        n = len(self.data)
        if n == 0: return

        all_vals = [v for _, a, b in self.data for v in (a, b)]
        max_val = max(all_vals) * 1.18
        bar_group_w = chart_w / n
        bar_w = bar_group_w * 0.28
        gap = bar_group_w * 0.07

        def vy(v): return pad_b + (v / max_val) * chart_h

        # Grille horizontale légère
        c.setStrokeColor(colors.HexColor('#EEEEEE'))
        c.setLineWidth(0.4)
        for step in [0.25, 0.5, 0.75, 1.0]:
            y = pad_b + step * chart_h
            c.line(pad_l, y, pad_l + chart_w, y)

        # Axe Y label
        c.setFillColor(LIGHT_GREY)
        c.setFont('LS', 6)
        for step in [0, 0.5, 1.0]:
            val = int(max_val * step)
            c.drawRightString(pad_l - 2, pad_b + step * chart_h - 2, f'{val:,}€'.replace(',', ' '))

        # Barres
        for i, (label, current, projected) in enumerate(self.data):
            cx = pad_l + i * bar_group_w + bar_group_w * 0.18

            # Barre Aujourd'hui (gris)
            bh_curr = vy(current) - pad_b
            c.setFillColor(colors.HexColor('#C8D0DC'))
            c.roundRect(cx, pad_b, bar_w, bh_curr, 1, fill=1, stroke=0)

            # Barre Projection (navy)
            bh_proj = vy(projected) - pad_b
            c.setFillColor(NAVY)
            c.roundRect(cx + bar_w + gap, pad_b, bar_w, bh_proj, 1, fill=1, stroke=0)

            # Valeur au dessus barres
            c.setFont('LS-Bold', 6.5)
            c.setFillColor(MID_GREY)
            c.drawCentredString(cx + bar_w/2, pad_b + bh_curr + 2, f'{current:,}€'.replace(',', ' '))
            c.setFillColor(GOLD_ACC)
            c.drawCentredString(cx + bar_w + gap + bar_w/2, pad_b + bh_proj + 2, f'{projected:,}€'.replace(',', ' '))

            # Gain +X€
            gain = projected - current
            c.setFillColor(GREEN_ACC)
            c.setFont('LS-Bold', 6)
            c.drawCentredString(cx + bar_w + gap/2 + bar_w/2, vy(projected) + 7, f'+{gain}€')

            # Label axe X
            c.setFillColor(CHARCOAL)
            c.setFont('LS-Bold', 7.5)
            c.drawCentredString(cx + bar_w + gap/2 + bar_w/2, pad_b - 8, label)

        # Légende
        leg_x = pad_l + chart_w * 0.62
        leg_y = pad_b + chart_h + 2
        c.setFillColor(colors.HexColor('#C8D0DC'))
        c.rect(leg_x, leg_y, 8, 6, fill=1, stroke=0)
        c.setFillColor(CHARCOAL)
        c.setFont('LS', 6.5)
        c.drawString(leg_x + 10, leg_y, "Aujourd'hui")
        c.setFillColor(NAVY)
        c.rect(leg_x + 52, leg_y, 8, 6, fill=1, stroke=0)
        c.setFillColor(CHARCOAL)
        c.drawString(leg_x + 62, leg_y, "Projection")

        # Ligne axe bas
        c.setStrokeColor(NAVY)
        c.setLineWidth(1)
        c.line(pad_l, pad_b, pad_l + chart_w, pad_b)
        c.line(pad_l, pad_b, pad_l, pad_b + chart_h)

    def wrap(self, aW, aH): return (aW, self.h)

# ═══ TABLE PRO ═══════════════════════════════════════════════
def pro_table(headers, rows, ratios=None):
    n = len(headers)
    col_ws = [CW * r for r in ratios] if ratios else [CW / n] * n
    S = styles()

    def cell_color(txt):
        t = txt.upper()
        if any(x in t for x in ['STOP','ELEVE','CRITIQU','ROUGE','HAUT']): return RED_ACC
        if any(x in t for x in ['OK','VERT','FAIBLE','CONTINUER','BON','SUCCES']): return GREEN_ACC
        if any(x in t for x in ['PIVOT','MOYEN','MODERE','PARTIEL']): return ORANGE_ACC
        return CHARCOAL

    hrow = [Paragraph(f'<b>{clean(h)}</b>', S['th']) for h in headers]
    data = [hrow]
    for row in rows:
        dr = []
        for cell in row:
            txt = strip_md(str(cell))
            col = cell_color(txt)
            bold = col != CHARCOAL
            ps = ParagraphStyle('tdc', fontName='LS-Bold' if bold else 'Helvetica',
                fontSize=8.5, textColor=col, leading=12)
            dr.append(Paragraph(txt, ps))
        data.append(dr)

    t = Table(data, colWidths=col_ws, repeatRows=1)
    rn = len(data)
    row_bgs = [('BACKGROUND', (0, ri), (-1, ri), BG_STRIP if ri % 2 == 0 else WHITE)
               for ri in range(1, rn)]
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), NAVY),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.3, RULE),
        ('LINEABOVE', (0, 0), (-1, 0), 2.5, GOLD_ACC),
        ('LINEBELOW', (0, -1), (-1, -1), 2, NAVY),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        *row_bgs,
    ]))
    return t


# ═══ COUVERTURE ═════════════════════════════════════════════
def build_cover(c, nom, secteur, mode_label, date_str):
    """Couverture McKinsey/BCG niveau — layout colonne gauche navy."""
    # ── FOND BLANC TOTAL ──────────────────────────────────────
    c.setFillColor(WHITE)
    c.rect(0, 0, W, H, fill=1, stroke=0)

    # ── BANDE GAUCHE NAVY PLEINE HAUTEUR ──────────────────────
    side_w = W * 0.40
    c.setFillColor(NAVY)
    c.rect(0, 0, side_w, H, fill=1, stroke=0)

    # Accent or vertical bord droit de la bande
    c.setFillColor(GOLD_ACC)
    c.rect(side_w, 0, 3, H, fill=1, stroke=0)

    # ── LOGO DECISIO (bande gauche, haut) ─────────────────────
    c.setFillColor(WHITE)
    c.setFont('LS-Bold', 38)
    c.drawString(ML, H - 30*mm, 'DECISIO')

    c.setFillColor(WHITE)
    c.setFillAlpha(0.2)
    c.rect(ML, H - 34*mm, side_w - ML*2, 0.8, fill=1, stroke=0)
    c.setFillAlpha(1.0)

    c.setFillColor(GOLD_ACC)
    c.setFont('LS-Bold', 7)
    c.drawString(ML, H - 40*mm, 'M\u00c9THODE D3\u2122')
    c.setFillColor(WHITE)
    c.setFillAlpha(0.55)
    c.setFont('LS', 6.5)
    c.drawString(ML, H - 47*mm, 'FIRST PRINCIPLES  \u2022  AI-POWERED 48H')
    c.setFillAlpha(1.0)

    # ── 3 PILIERS D3 (bande gauche, milieu) ───────────────────
    piliers = [
        ('01', 'DIAGNOSTIC',     'Analyse compl\u00e8te'),
        ('02', 'D\u00c9CISION',      'Options scor\u00e9es'),
        ('03', 'D\u00c9PLOIEMENT',   'Plan d\'action'),
    ]
    py_start = H * 0.50
    pill_h = 26*mm
    for i, (num, titre, desc) in enumerate(piliers):
        py = py_start - i * pill_h
        # Cercle doré
        c.setFillColor(GOLD_ACC)
        c.circle(ML + 4.5*mm, py + 2.5*mm, 4.5*mm, fill=1, stroke=0)
        # Numéro dans cercle
        c.setFillColor(NAVY)
        c.setFont('LS-Bold', 7.5)
        c.drawCentredString(ML + 4.5*mm, py + 0.5*mm, num)
        # Titre
        c.setFillColor(WHITE)
        c.setFont('LS-Bold', 9.5)
        c.drawString(ML + 13*mm, py + 3.5*mm, titre)
        # Description
        c.setFillColor(GOLD_ACC)
        c.setFillAlpha(0.75)
        c.setFont('LS', 7.5)
        c.drawString(ML + 13*mm, py - 3*mm, desc)
        c.setFillAlpha(1.0)

    # ── FOOTER BANDE GAUCHE ────────────────────────────────────
    c.setFillColor(WHITE)
    c.setFillAlpha(0.15)
    c.rect(0, 0, side_w, 20*mm, fill=1, stroke=0)
    c.setFillAlpha(1.0)
    c.setFillColor(GOLD_ACC)
    c.setFont('LS-Bold', 7.5)
    c.drawString(ML, 8*mm, 'decisio.agency')
    c.setFillColor(WHITE)
    c.setFillAlpha(0.55)
    c.setFont('LS', 6.5)
    c.drawString(ML, 3*mm, 'contact@decisio.agency')
    c.setFillAlpha(1.0)

    # ── ZONE DROITE ───────────────────────────────────────────
    rx = side_w + 10*mm
    rw = W - rx - MR

    # Badge mode/prix (haut droite)
    badge_w = 55*mm
    badge_x = W - MR - badge_w
    c.setFillColor(NAVY)
    c.roundRect(badge_x, H - 22*mm, badge_w, 10*mm, 2*mm, fill=1, stroke=0)
    c.setFillColor(GOLD_ACC)
    c.setFont('LS-Bold', 7)
    c.drawCentredString(badge_x + badge_w/2, H - 18.5*mm, clean(mode_label).upper())

    # Nom client — grand
    c.setFillColor(NAVY)
    c.setFont('LS-Bold', 32)
    nom_txt = clean(nom)
    while c.stringWidth(nom_txt, 'LS-Bold', 32) > rw and len(nom_txt) > 5:
        nom_txt = nom_txt[:-1]
    c.drawString(rx, H - 52*mm, nom_txt)

    # Trait accent or sous le nom
    c.setFillColor(GOLD_ACC)
    c.rect(rx, H - 56*mm, 22*mm, 2.5, fill=1, stroke=0)

    # Secteur
    c.setFillColor(colors.HexColor('#444444'))
    c.setFont('LS', 13)
    c.drawString(rx, H - 65*mm, clean(secteur))

    # Date
    c.setFillColor(LIGHT_GREY)
    c.setFont('LS', 10)
    c.drawString(rx, H - 74*mm, clean(date_str))

    # Ligne séparatrice légère
    c.setStrokeColor(colors.HexColor('#DEDEDE'))
    c.setLineWidth(0.7)
    c.line(rx, H - 81*mm, W - MR, H - 81*mm)

    # ── BLOC DESCRIPTIF AUDIT (centre droite) ─────────────────
    bloc_y = H * 0.30
    bloc_h = H * 0.30
    c.setFillColor(colors.HexColor('#F5F7FA'))
    c.roundRect(rx, bloc_y, rw, bloc_h, 3*mm, fill=1, stroke=0)
    c.setStrokeColor(colors.HexColor('#DDE2EA'))
    c.setLineWidth(0.6)
    c.roundRect(rx, bloc_y, rw, bloc_h, 3*mm, fill=0, stroke=1)

    # Trait or gauche du bloc
    c.setFillColor(GOLD_ACC)
    c.rect(rx, bloc_y, 3, bloc_h, fill=1, stroke=0)

    # Titre du bloc
    c.setFillColor(NAVY)
    c.setFont('LS-Bold', 10.5)
    c.drawString(rx + 8*mm, bloc_y + bloc_h - 11*mm, 'AUDIT STRAT\u00c9GIQUE PREMIUM')

    # Trait sous titre
    c.setFillColor(GOLD_ACC)
    c.rect(rx + 8*mm, bloc_y + bloc_h - 14.5*mm, 28*mm, 1.5, fill=1, stroke=0)

    # Prix grand
    c.setFillColor(NAVY)
    c.setFont('LS-Bold', 30)
    c.drawString(rx + 8*mm, bloc_y + bloc_h - 32*mm, '2 490 \u20ac')

    # Tagline sous prix
    c.setFillColor(colors.HexColor('#555555'))
    c.setFont('LS', 8)
    c.drawString(rx + 8*mm, bloc_y + bloc_h - 40*mm,
        'Livraison 48h  \u2022  M\u00e9thode D3\u2122  \u2022  Confidentiel')

    # ── NOTE CONFIDENTIELLE (bas droite) ──────────────────────
    cy = H * 0.26
    c.setFillColor(LIGHT_GREY)
    c.setFont('LS', 7)
    c.drawString(rx, cy,
        'Ce rapport est strictement confidentiel et destin\u00e9 au seul usage du client d\u00e9sign\u00e9 ci-dessus.')
    c.drawString(rx, cy - 9,
        'Toute reproduction ou diffusion est interdite sans autorisation \u00e9crite de DECISIO AGENCY.')


# ═══ PAGE CHROME (header/footer sur toutes pages) ════════════
class DecisioTemplate(SimpleDocTemplate):
    def __init__(self, buf, nom, secteur, **kw):
        self.nom = clean(nom)
        self.secteur = clean(secteur)
        self._pn = 1
        super().__init__(buf, **kw)

    def handle_pageBegin(self):
        super().handle_pageBegin()
        if self._pn > 1:
            self._header()

    def handle_pageEnd(self):
        if self._pn > 1:
            self._footer()
        self._pn += 1
        super().handle_pageEnd()

    def _header(self):
        c = self.canv
        # Bande navy fine
        c.setFillColor(NAVY)
        c.rect(0, H - 13*mm, W, 13*mm, fill=1, stroke=0)
        # Accent or
        c.setFillColor(GOLD_ACC)
        c.rect(0, H - 13*mm, W, 1.5, fill=1, stroke=0)
        # Logo
        c.setFillColor(WHITE)
        c.setFont('LS-Bold', 10.5)
        c.drawString(ML, H - 8.5*mm, 'DECISIO')
        # Séparateur
        c.setFillColor(WHITE)
        c.setFillAlpha(0.3)
        c.rect(ML + 21*mm, H - 11*mm, 0.5, 7*mm, fill=1, stroke=0)
        c.setFillAlpha(1.0)
        # Méthode
        c.setFillColor(GOLD_ACC)
        c.setFont('LS', 7.5)
        c.drawString(ML + 24*mm, H - 8.5*mm, 'M\u00c9THODE D3\u2122')
        # Client (droite)
        c.setFillColor(colors.HexColor('#AAAAAA'))
        c.setFont('LS', 7)
        c.drawRightString(W - MR, H - 8.5*mm, f'{self.nom}  |  {self.secteur}'[:65])

    def _footer(self):
        c = self.canv
        # Bande navy footer
        c.setFillColor(NAVY)
        c.rect(0, 0, W, 11*mm, fill=1, stroke=0)
        # Accent or haut
        c.setFillColor(GOLD_ACC)
        c.rect(0, 11*mm, W, 1.5, fill=1, stroke=0)
        # Logo DECISIO gauche
        c.setFillColor(WHITE)
        c.setFont('LS-Bold', 8)
        c.drawString(ML, 4*mm, 'DECISIO')
        # Séparateur
        c.setFillColor(GOLD_ACC)
        c.setFillAlpha(0.6)
        c.rect(ML + 19*mm, 3*mm, 0.5, 5*mm, fill=1, stroke=0)
        c.setFillAlpha(1.0)
        # Confidentiel centre
        c.setFillColor(colors.HexColor('#AAAAAA'))
        c.setFont('LS', 6.5)
        c.drawCentredString(W/2, 4*mm, 'CONFIDENTIEL  \u2022  DECISIO AGENCY  \u2022  M\u00e9thode D3\u2122')
        # Numéro page — cercle or droite
        pn = self._pn
        cx = W - MR - 5*mm
        cy = 5.5*mm
        c.setFillColor(GOLD_ACC)
        c.circle(cx, cy, 4.5*mm, fill=1, stroke=0)
        c.setFillColor(NAVY)
        c.setFont('LS-Bold', 8)
        c.drawCentredString(cx, cy - 2.5, str(pn))


# ═══ PARSER MARKDOWN → FLOWABLES ════════════════════════════
def parse(text, ST):
    lines = text.split('\n')
    story = []
    i = 0

    def sp(h=2): story.append(Spacer(1, h * mm))
    def hr(color=RULE, w=0.5):
        story.append(HRFlowable(width=CW, thickness=w, color=color,
                                spaceAfter=4, spaceBefore=4))

    while i < len(lines):
        raw = lines[i]
        line = raw.strip()

        # Vide
        if not line:
            sp(2); i += 1; continue

        # Séparateur
        if line == '---':
            hr(); i += 1; continue

        # ── TABLE ──
        if line.startswith('|'):
            tl = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                if '---' not in lines[i]:
                    cells = [c.strip() for c in lines[i].strip().split('|')][1:-1]
                    tl.append(cells)
                i += 1
            if len(tl) >= 2:
                n = len(tl[0])
                story.append(pro_table(tl[0], tl[1:], [1/n]*n))
                sp(3)
            continue

        # ── H1 ──
        if raw.startswith('# '):
            txt = strip_md(line[2:])
            sp(3)
            t = Table([[Paragraph(f'<b>{txt}</b>',
                ParagraphStyle('h1r', fontName='LS-Bold', fontSize=14,
                    textColor=WHITE, leading=20))]],
                colWidths=[CW])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), NAVY),
                ('LEFTPADDING', (0, 0), (-1, -1), 12),
                ('TOPPADDING', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 9),
                ('LINEABOVE', (0, 0), (-1, 0), 3, GOLD_ACC),
            ]))
            story.append(t)
            sp(3)
            i += 1; continue

        # ── H2 ──
        if raw.startswith('## '):
            txt = strip_md(line[3:])
            acc = sec_accent(txt)
            sp(3)
            story.append(KeepTogether([
                SectionHeader(txt, acc),
                Spacer(1, 4*mm)
            ]))
            i += 1; continue

        # ── H3 ──
        if raw.startswith('### '):
            txt = strip_md(line[4:])
            acc = sec_accent(txt)
            sp(3)
            story.append(KeepTogether([
                SubHeader(txt, acc),
                Spacer(1, 3*mm)
            ]))
            i += 1; continue

        # ── H4 ──
        if raw.startswith('#### '):
            txt = strip_md(line[5:])
            sp(2)
            story.append(Paragraph(f'<b>{clean(txt)}</b>', ST['h4']))
            i += 1; continue

        # ── VÉRITÉ FONDAMENTALE ──
        if re.search(r'v[eé]rit[eé]\s+fondamentale', line, re.I) or \
           ('[!]' in line and 'rit' in line.lower()):
            vtext = re.sub(r'.*?v[eé]rit[eé]\s+fondamentale\s*:?\s*', '', line, flags=re.I)
            vtext = re.sub(r'^[🎯\[\]! >*#+]+', '', vtext).strip()
            if not vtext and i + 1 < len(lines):
                i += 1
                vtext = strip_md(lines[i])
            sp(2)
            story.append(KeepTogether([VeritefBlock(vtext, CW), Spacer(1, 3*mm)]))
            i += 1; continue

        # ── GRAPHIQUE FINANCIER ──
        if line.startswith('CHART_BAR:'):
            raw_data = line[len('CHART_BAR:'):]
            chart_data = []
            for seg in raw_data.split('|'):
                parts = seg.split(':')
                if len(parts) == 3:
                    try:
                        chart_data.append((parts[0], int(parts[1]), int(parts[2])))
                    except: pass
            if chart_data:
                sp(2)
                story.append(KeepTogether([FinancialBarChart(chart_data, CW), Spacer(1, 3*mm)]))
            i += 1; continue

                # ── BLOCKQUOTE (Pourquoi) ──
        if line.startswith('>') or line.startswith('->'):
            # Enlever le prefixe > ou ->
            if line.startswith('->'):
                txt = strip_md(line[2:].strip())
            else:
                txt = strip_md(line[1:].strip())
            is_pourquoi = 'pourquoi' in txt.lower() or 'pourquoi' in line.lower()
            t = Table([[Paragraph(txt,
                ParagraphStyle('bq',
                    fontName='LS-BoldItalic' if is_pourquoi else 'Helvetica-Oblique',
                    fontSize=9.5, textColor=CHARCOAL, leading=14))]],
                colWidths=[CW - 6*mm])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), BG_STRIP),
                ('LEFTPADDING', (0, 0), (-1, -1), 12),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('LINEBEFORE', (0, 0), (0, -1), 3, BLUE_ACC),
                ('LINEBELOW', (0, -1), (-1, -1), 0.3, RULE),
            ]))
            story.append(t)
            sp(1); i += 1; continue

        # ── BULLET ──
        if re.match(r'^[-*•·]\s', line) or re.match(r'^\s{2,}[-*•·]\s', raw):
            txt = strip_md(re.sub(r'^[-*•·]\s', '', line))
            story.append(Paragraph(
                f'<bullet><font color="#B8860B" size="11">&#x25CF;</font></bullet>{clean(txt)}',
                ST['bullet']))
            i += 1; continue

        # ── MESSAGE CARD ──
        mm_m = re.match(r'^(Message\s+\d[^:]*)', line, re.I)
        if mm_m:
            label = mm_m.group(1)
            rest = line[len(mm_m.group(0)):].lstrip(': ').strip()
            if not rest and i + 1 < len(lines):
                i += 1; rest = strip_md(lines[i])
            sp(2)
            story.append(KeepTogether([MessageCard(label, rest, CW), Spacer(1, 2*mm)]))
            i += 1; continue

        # ── OPTION A/B/C SCORE ──
        opt_m = re.match(r'^OPTION\s+([A-C])\s*[-—]?\s*(.{5,})', line, re.I)
        if opt_m:
            letter = opt_m.group(1)
            title = opt_m.group(2).strip()[:55]
            detail = ''; score = '?'
            j = i + 1
            while j < len(lines) and j < i + 4:
                nl = lines[j].strip()
                sm = re.search(r'Score\s*:\s*([\d,.]+)', nl, re.I)
                if sm: score = sm.group(1); detail = strip_md(nl[:90]); break
                if nl: detail += strip_md(nl[:60]) + ' '
                j += 1
            acc = sec_accent('DECISION')
            sp(2)
            story.append(KeepTogether([
                ScoreCard(letter, title, detail.strip(), score, acc, CW),
                Spacer(1, 2*mm)
            ]))
            i += 1; continue

        # ── KEY::VALUE ──
        kv = re.match(r'\*\*(.+?)\*\*\s*::\s*(.*)', line)
        if kv:
            lbl = clean(kv.group(1))
            val = strip_md(kv.group(2))
            t = Table([
                [Paragraph(f'<b>{lbl}</b>', ST['label']),
                 Paragraph(clean(val), ST['value'])]
            ], colWidths=[55*mm, CW - 55*mm])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), BG_STRIP),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('LINEBELOW', (0, -1), (-1, -1), 0.4, RULE),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LINEBEFORE', (0, 0), (0, -1), 2.5, GOLD_ACC),
            ]))
            story.append(t)
            i += 1; continue

        # ── LIGNE NORMALE ──
        story.append(rich(line, ST['body']))
        sp(1)
        i += 1

    return story


# ═══ GENERATE ════════════════════════════════════════════════
def generate_pdf(report_text, nom, secteur, mode, date_str=None):
    register_fonts()
    if not date_str:
        date_str = datetime.now().strftime('%d %B %Y')
    labels = {
        'flash': 'AUDIT FLASH  |  490 EUR',
        'premium': 'AUDIT STRATÉGIQUE PREMIUM  •  2 490 €',
        'transformation': 'AUDIT TRANSFORMATION  |  6 900 EUR',
        'diagnostic': 'DIAGNOSTIC GRATUIT',
    }
    mode_label = labels.get(mode, 'AUDIT STRATÉGIQUE PREMIUM  •  2 490 €')

    # ── COUVERTURE ──
    register_fonts()  # Assurer polices dispo pour canvas
    buf_cover = BytesIO()
    c = pdf_canvas.Canvas(buf_cover, pagesize=A4)
    build_cover(c, nom, secteur, mode_label, date_str)
    c.showPage(); c.save()

    # ── CONTENU ──
    ST = styles()
    story = []

    # Titre rapport (page 2)
    story.append(Spacer(1, 5*mm))
    story.append(Paragraph(
        'RAPPORT D\'AUDIT STRATÉGIQUE — MÉTHODE D3™',
        ParagraphStyle('rt', fontName='LS-Bold', fontSize=13,
            textColor=NAVY, leading=18, alignment=TA_CENTER)))
    story.append(Paragraph(
        f'{clean(nom)}  |  {clean(secteur)}  |  {clean(date_str)}',
        ParagraphStyle('rs', fontName='LS', fontSize=9,
            textColor=MID_GREY, leading=13, alignment=TA_CENTER, spaceAfter=3)))
    story.append(HRFlowable(width=CW, thickness=2.5, color=NAVY,
                             spaceBefore=3, spaceAfter=3))
    story.append(HRFlowable(width=CW, thickness=1, color=GOLD_ACC,
                             spaceAfter=8))

    story += parse(report_text, ST)

    story.append(Spacer(1, 5*mm))
    story.append(HRFlowable(width=CW, thickness=1.5, color=NAVY))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph(
        'Rapport strictement confidentiel — DECISIO AGENCY  |  Méthode D3™  |  contact@decisio.agency',
        ParagraphStyle('fin', fontName='LS-Italic', fontSize=7.5,
            textColor=LIGHT_GREY, alignment=TA_CENTER)))

    buf_content = BytesIO()
    tpl = DecisioTemplate(
        buf_content, nom, secteur,
        pagesize=A4,
        leftMargin=ML, rightMargin=MR,
        topMargin=13*mm, bottomMargin=15*mm,
    )
    tpl.build(story)

    # ── MERGE ──
    writer = PdfWriter()
    for p in PdfReader(BytesIO(buf_cover.getvalue())).pages:
        writer.add_page(p)
    for p in PdfReader(BytesIO(buf_content.getvalue())).pages:
        writer.add_page(p)
    out = BytesIO(); writer.write(out)
    return out.getvalue()


# ═══ TEST ════════════════════════════════════════════════════
if __name__ == '__main__':
    SAMPLE = open('/home/claude/sample_report_v2.txt').read()
    pdf = generate_pdf(SAMPLE, 'Lucas Bernard', 'Electricien independant', 'premium', '11 mars 2026')
    with open('/mnt/user-data/outputs/DECISIO_McKINSEY_V7.pdf', 'wb') as f:
        f.write(pdf)
    print(f'OK — {len(pdf)//1024} KB — {len(open("/mnt/user-data/outputs/DECISIO_McKINSEY_V3.pdf","rb").read())//1024} KB')
