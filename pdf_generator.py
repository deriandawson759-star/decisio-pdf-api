"""
DECISIO AGENCY — PDF Generator V17
Méthode D3™ | Audit Stratégique Premium
Score cible : 9.5/10

Améliorations V17 vs V16 :
- Pages séparatrices navy pleine page (01/02/03)
- Graphique barres navy/doré M+1/M+3/M+6 réel
- Barres de score colorées options A/B/C
- Navy propagé sur tous les H2/H3
- Accent bar doré sur les headers de section
- Tableau couleurs alternées
- Typographie renforcée
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, Flowable, KeepTogether
)
from reportlab.platypus.flowables import Flowable
from reportlab.lib.colors import HexColor, Color, white, black
from reportlab.pdfgen import canvas as rl_canvas
from io import BytesIO
import copy

# ─────────────────────────────────────────────
# BRAND COLORS
# ─────────────────────────────────────────────
NAVY       = HexColor('#1A3A5C')
GOLD       = HexColor('#C9A84C')
GOLD_LIGHT = HexColor('#E8D49A')
WHITE      = HexColor('#FFFFFF')
DARK       = HexColor('#1C1C1C')
GREY_DARK  = HexColor('#4A4A4A')
GREY_MID   = HexColor('#888888')
GREY_LIGHT = HexColor('#F2F4F7')
GREY_LINE  = HexColor('#D8DCE5')
RED_ALERT  = HexColor('#C0392B')
GREEN_OK   = HexColor('#1A7A4A')
NAVY_LIGHT = HexColor('#2C5282')

W, H = A4  # 595.3 x 841.9

# ─────────────────────────────────────────────
# DATA — LUCAS BERNARD
# ─────────────────────────────────────────────
CLIENT = {
    "nom": "Lucas Bernard",
    "metier": "Électricien indépendant",
    "date": "18 mars 2026",
    "offre": "AUDIT STRATÉGIQUE",
    "prix": "2 490 €",
}

# ─────────────────────────────────────────────
# STYLES
# ─────────────────────────────────────────────
def make_styles():
    s = {}

    s['cover_brand'] = ParagraphStyle('cover_brand',
        fontName='Helvetica-Bold', fontSize=42, textColor=WHITE,
        leading=48, alignment=TA_LEFT)

    s['cover_method'] = ParagraphStyle('cover_method',
        fontName='Helvetica', fontSize=12, textColor=GOLD,
        leading=16, alignment=TA_LEFT, spaceAfter=4)

    s['cover_tag'] = ParagraphStyle('cover_tag',
        fontName='Helvetica', fontSize=9, textColor=HexColor('#AABBCC'),
        leading=13, alignment=TA_LEFT)

    s['cover_client'] = ParagraphStyle('cover_client',
        fontName='Helvetica-Bold', fontSize=28, textColor=DARK,
        leading=34, alignment=TA_LEFT)

    s['cover_metier'] = ParagraphStyle('cover_metier',
        fontName='Helvetica', fontSize=14, textColor=GREY_DARK,
        leading=20, alignment=TA_LEFT)

    s['cover_date'] = ParagraphStyle('cover_date',
        fontName='Helvetica', fontSize=10, textColor=GREY_MID,
        leading=14, alignment=TA_LEFT)

    s['section_title'] = ParagraphStyle('section_title',
        fontName='Helvetica-Bold', fontSize=11, textColor=NAVY,
        leading=16, spaceBefore=20, spaceAfter=6)

    s['subsection_title'] = ParagraphStyle('subsection_title',
        fontName='Helvetica-Bold', fontSize=10, textColor=NAVY,
        leading=14, spaceBefore=14, spaceAfter=5)

    s['body'] = ParagraphStyle('body',
        fontName='Helvetica', fontSize=9, textColor=DARK,
        leading=14, spaceBefore=3, spaceAfter=3, alignment=TA_JUSTIFY)

    s['body_bold'] = ParagraphStyle('body_bold',
        fontName='Helvetica-Bold', fontSize=9, textColor=DARK,
        leading=14, spaceBefore=2, spaceAfter=2)

    s['body_navy'] = ParagraphStyle('body_navy',
        fontName='Helvetica-Bold', fontSize=9, textColor=NAVY,
        leading=14, spaceBefore=2, spaceAfter=2)

    s['insight'] = ParagraphStyle('insight',
        fontName='Helvetica-Bold', fontSize=9, textColor=NAVY,
        leading=13, spaceBefore=4, spaceAfter=4,
        leftIndent=10, rightIndent=10)

    s['callout'] = ParagraphStyle('callout',
        fontName='Helvetica', fontSize=8.5, textColor=DARK,
        leading=13, spaceBefore=2, spaceAfter=2,
        leftIndent=12, rightIndent=8)

    s['label_gold'] = ParagraphStyle('label_gold',
        fontName='Helvetica-Bold', fontSize=8, textColor=GOLD,
        leading=11, alignment=TA_LEFT)

    s['small_grey'] = ParagraphStyle('small_grey',
        fontName='Helvetica', fontSize=7.5, textColor=GREY_MID,
        leading=11, alignment=TA_CENTER)

    s['table_header'] = ParagraphStyle('table_header',
        fontName='Helvetica-Bold', fontSize=8, textColor=WHITE,
        leading=11, alignment=TA_CENTER)

    s['table_cell'] = ParagraphStyle('table_cell',
        fontName='Helvetica', fontSize=8, textColor=DARK,
        leading=12, alignment=TA_LEFT)

    s['table_cell_bold'] = ParagraphStyle('table_cell_bold',
        fontName='Helvetica-Bold', fontSize=8, textColor=NAVY,
        leading=12, alignment=TA_LEFT)

    s['table_cell_center'] = ParagraphStyle('table_cell_center',
        fontName='Helvetica', fontSize=8, textColor=DARK,
        leading=12, alignment=TA_CENTER)

    s['quick_win_title'] = ParagraphStyle('quick_win_title',
        fontName='Helvetica-Bold', fontSize=12, textColor=NAVY,
        leading=16, spaceBefore=8, spaceAfter=6)

    s['message_text'] = ParagraphStyle('message_text',
        fontName='Helvetica', fontSize=8.5, textColor=DARK,
        leading=13, leftIndent=8, rightIndent=8,
        spaceBefore=2, spaceAfter=2, alignment=TA_JUSTIFY)

    s['exec_label'] = ParagraphStyle('exec_label',
        fontName='Helvetica-Bold', fontSize=9, textColor=GOLD,
        leading=13, spaceBefore=6, spaceAfter=1)

    s['exec_value'] = ParagraphStyle('exec_value',
        fontName='Helvetica', fontSize=9, textColor=DARK,
        leading=13, spaceBefore=0, spaceAfter=4, alignment=TA_JUSTIFY)

    s['rule_text'] = ParagraphStyle('rule_text',
        fontName='Helvetica', fontSize=9, textColor=DARK,
        leading=13, spaceBefore=3, spaceAfter=3,
        leftIndent=14, rightIndent=6, alignment=TA_JUSTIFY)

    s['footer_conf'] = ParagraphStyle('footer_conf',
        fontName='Helvetica', fontSize=7, textColor=GREY_MID,
        leading=10, alignment=TA_LEFT)

    return s


# ─────────────────────────────────────────────
# CUSTOM FLOWABLES
# ─────────────────────────────────────────────

class SeparatorPage(Flowable):
    """Full-page navy separator with number, title, subtitle."""
    def __init__(self, number, title, subtitle, desc=""):
        super().__init__()
        self.number = number
        self.title = title
        self.subtitle = subtitle
        self.desc = desc
        self.width = W
        self.height = H

    def wrap(self, aw, ah):
        # Claim full available space so it gets its own page
        return (aw, ah)

    def draw(self):
        c = self.canv
        # Get actual page dimensions
        pw, ph = c._pagesize
        # Full navy background
        c.saveState()
        # Extend to full page using translation to compensate for margins
        c.translate(-40, -45)  # compensate for doc margins
        pw, ph = A4
        c.setFillColor(NAVY)
        c.rect(0, 0, W, H, fill=1, stroke=0)

        # Subtle diagonal stripe pattern (luxury feel)
        c.setStrokeColor(HexColor('#1E4570'))
        c.setLineWidth(0.5)
        for i in range(-20, 40):
            x = i * 40
            c.line(x, 0, x + H, H)

        # Large number — very faint watermark
        c.setFillColor(HexColor('#1E4570'))
        c.setFont('Helvetica-Bold', 180)
        c.drawCentredString(W/2, H/2 - 60, self.number)

        # Gold accent line
        c.setStrokeColor(GOLD)
        c.setLineWidth(2)
        c.line(W/2 - 80, H/2 + 80, W/2 + 80, H/2 + 80)

        # Number label
        c.setFillColor(GOLD)
        c.setFont('Helvetica-Bold', 64)
        c.drawCentredString(W/2, H/2 + 100, self.number)

        # Title
        c.setFillColor(WHITE)
        c.setFont('Helvetica-Bold', 32)
        c.drawCentredString(W/2, H/2 + 30, self.title)

        # Subtitle
        c.setFillColor(GOLD_LIGHT)
        c.setFont('Helvetica', 16)
        c.drawCentredString(W/2, H/2 - 8, self.subtitle)

        # Description
        if self.desc:
            c.setFillColor(HexColor('#AABBCC'))
            c.setFont('Helvetica', 10)
            c.drawCentredString(W/2, H/2 - 34, self.desc)

        # Bottom branding
        c.setFillColor(GOLD)
        c.setFont('Helvetica-Bold', 9)
        c.drawCentredString(W/2, 50, 'DECISIO AGENCY · MÉTHODE D3™ · CONFIDENTIEL')

        # Top line
        c.setStrokeColor(HexColor('#AABBCC'))
        c.setLineWidth(0.3)
        c.line(60, H - 40, W - 60, H - 40)
        c.line(60, 40, W - 60, 40)

        c.restoreState()


class SectionHeader(Flowable):
    """Navy header bar with gold accent for section titles."""
    def __init__(self, text, height=28):
        super().__init__()
        self.text = text
        self._height = height

    def wrap(self, aw, ah):
        self._width = aw
        return (aw, self._height + 6)

    def draw(self):
        c = self.canv
        c.saveState()
        # Navy background
        c.setFillColor(NAVY)
        c.rect(0, 4, self._width, self._height, fill=1, stroke=0)
        # Gold left accent
        c.setFillColor(GOLD)
        c.rect(0, 4, 4, self._height, fill=1, stroke=0)
        # Text
        c.setFillColor(WHITE)
        c.setFont('Helvetica-Bold', 11)
        c.drawString(14, 4 + self._height/2 - 4, self.text)
        c.restoreState()


class MiniSectionHeader(Flowable):
    """Smaller gold-accented navy header for subsections."""
    def __init__(self, text, height=22):
        super().__init__()
        self.text = text
        self._height = height

    def wrap(self, aw, ah):
        self._width = aw
        return (aw, self._height + 4)

    def draw(self):
        c = self.canv
        c.saveState()
        # Light navy bg
        c.setFillColor(HexColor('#EEF2F8'))
        c.rect(0, 2, self._width, self._height, fill=1, stroke=0)
        # Navy left accent bar
        c.setFillColor(NAVY)
        c.rect(0, 2, 3, self._height, fill=1, stroke=0)
        # Gold small dot
        c.setFillColor(GOLD)
        c.rect(0, 2, 3, 6, fill=1, stroke=0)
        # Text
        c.setFillColor(NAVY)
        c.setFont('Helvetica-Bold', 10)
        c.drawString(12, 2 + self._height/2 - 4, self.text)
        c.restoreState()


class BarChart(Flowable):
    """Navy/gold grouped bar chart for financial projections."""
    def __init__(self, data, width=420, height=140):
        """
        data: list of (label, today_val, proj_val)
        """
        super().__init__()
        self.data = data
        self._width = width
        self._height = height

    def wrap(self, aw, ah):
        return (self._width, self._height + 60)

    def draw(self):
        c = self.canv
        c.saveState()

        max_val = max(max(p, t) for _, t, p in self.data) * 1.15
        chart_h = self._height - 20
        chart_y = 45
        n = len(self.data)
        group_w = (self._width - 60) / n
        bar_w = group_w * 0.28

        # Grid lines
        c.setStrokeColor(GREY_LINE)
        c.setLineWidth(0.5)
        for i in range(5):
            y = chart_y + (i / 4) * chart_h
            c.line(40, y, self._width - 10, y)

        # Bars
        for i, (label, today, proj) in enumerate(self.data):
            x_center = 40 + i * group_w + group_w / 2

            # Today bar — navy
            h1 = (today / max_val) * chart_h
            x1 = x_center - bar_w - 3
            c.setFillColor(NAVY)
            # Rounded top feel via rect
            c.rect(x1, chart_y, bar_w, h1, fill=1, stroke=0)
            # Value label on top
            c.setFillColor(NAVY)
            c.setFont('Helvetica-Bold', 7.5)
            val_str = f"{today:,}€".replace(',', ' ')
            c.drawCentredString(x1 + bar_w/2, chart_y + h1 + 4, val_str)

            # Projection bar — gold
            h2 = (proj / max_val) * chart_h
            x2 = x_center + 3
            c.setFillColor(GOLD)
            c.rect(x2, chart_y, bar_w, h2, fill=1, stroke=0)
            # Gold shimmer top
            c.setFillColor(GOLD_LIGHT)
            c.rect(x2, chart_y + h2 - 4, bar_w, 4, fill=1, stroke=0)
            # Value label
            c.setFillColor(HexColor('#8B6914'))
            c.setFont('Helvetica-Bold', 7.5)
            val_str2 = f"{proj:,}€".replace(',', ' ')
            c.drawCentredString(x2 + bar_w/2, chart_y + h2 + 4, val_str2)

            # X label
            c.setFillColor(DARK)
            c.setFont('Helvetica-Bold', 9)
            c.drawCentredString(x_center, chart_y - 18, label)

            # Gain annotation
            gain = proj - today
            c.setFillColor(GREEN_OK)
            c.setFont('Helvetica-Bold', 7)
            c.drawCentredString(x_center, chart_y - 30, f"+{gain:,}€".replace(',', ' '))

        # Legend
        legend_x = self._width - 150
        legend_y = self._height + 28

        c.setFillColor(NAVY)
        c.rect(legend_x, legend_y, 12, 10, fill=1, stroke=0)
        c.setFillColor(DARK)
        c.setFont('Helvetica', 8)
        c.drawString(legend_x + 16, legend_y + 1, "Aujourd'hui")

        c.setFillColor(GOLD)
        c.rect(legend_x + 80, legend_y, 12, 10, fill=1, stroke=0)
        c.setFillColor(DARK)
        c.drawString(legend_x + 96, legend_y + 1, "Projection")

        # Y-axis label
        c.saveState()
        c.setFillColor(GREY_MID)
        c.setFont('Helvetica', 7)
        c.translate(12, chart_y + chart_h/2)
        c.rotate(90)
        c.drawCentredString(0, 0, "Revenu net mensuel (€)")
        c.restoreState()

        c.restoreState()


class ScoreBar(Flowable):
    """Horizontal score bar for options A/B/C."""
    def __init__(self, option_label, description, score, max_score=10,
                 roi=None, proba=None, diff=None, is_best=False):
        super().__init__()
        self.option_label = option_label
        self.description = description
        self.score = score
        self.max_score = max_score
        self.roi = roi
        self.proba = proba
        self.diff = diff
        self.is_best = is_best
        self._height = 56 if is_best else 50

    def wrap(self, aw, ah):
        self._width = aw
        return (aw, self._height + 8)

    def draw(self):
        c = self.canv
        c.saveState()

        bar_y = 10
        bar_h = self._height - 22
        bar_total_w = self._width - 130

        # Border if best option
        if self.is_best:
            c.setStrokeColor(GOLD)
            c.setLineWidth(1.5)
            c.rect(0, 2, self._width, self._height + 2, fill=0, stroke=1)
            c.setFillColor(HexColor('#FFFBF0'))
            c.rect(0, 2, self._width, self._height + 2, fill=1, stroke=0)
            c.setStrokeColor(GOLD)
            c.setLineWidth(1.5)
            c.rect(0, 2, self._width, self._height + 2, fill=0, stroke=1)
            # Best badge
            c.setFillColor(GOLD)
            c.rect(self._width - 70, self._height - 4, 68, 16, fill=1, stroke=0)
            c.setFillColor(WHITE)
            c.setFont('Helvetica-Bold', 7.5)
            c.drawCentredString(self._width - 36, self._height + 1, '★ RECOMMANDÉ')
        else:
            c.setFillColor(GREY_LIGHT)
            c.rect(0, 2, self._width, self._height + 2, fill=1, stroke=0)

        # Option label
        c.setFillColor(NAVY if self.is_best else GREY_DARK)
        c.setFont('Helvetica-Bold', 10)
        c.drawString(10, bar_y + bar_h - 4, self.option_label)

        # Description
        c.setFillColor(DARK)
        c.setFont('Helvetica', 8.5)
        c.drawString(55, bar_y + bar_h - 4, self.description)

        # Score background
        c.setFillColor(HexColor('#DDDDDD'))
        c.rect(10, bar_y, bar_total_w, 14, fill=1, stroke=0)

        # Score fill
        ratio = self.score / self.max_score
        if self.score >= 7:
            fill_color = NAVY
        elif self.score >= 5:
            fill_color = GOLD
        else:
            fill_color = RED_ALERT

        c.setFillColor(fill_color)
        c.rect(10, bar_y, bar_total_w * ratio, 14, fill=1, stroke=0)

        # Score text on bar
        c.setFillColor(WHITE)
        c.setFont('Helvetica-Bold', 9)
        c.drawString(16, bar_y + 3, f"Score : {self.score}/10")

        # Score box right
        c.setFillColor(fill_color)
        c.rect(self._width - 48, bar_y, 46, 14, fill=1, stroke=0)
        c.setFillColor(WHITE)
        c.setFont('Helvetica-Bold', 10)
        c.drawCentredString(self._width - 25, bar_y + 2, f"{self.score}/10")

        # Sub-metrics
        if self.roi is not None:
            metrics = [
                (f"ROI {self.roi}/10", 10),
                (f"Prob. {self.proba}/10", 70),
                (f"Diff. {self.diff}/10", 130),
            ]
            for label, mx in metrics:
                c.setFillColor(GREY_MID)
                c.setFont('Helvetica', 7)
                c.drawString(mx + 10, bar_y - 8, label)

        c.restoreState()


class GoldDivider(Flowable):
    """Gold horizontal rule with diamond center."""
    def __init__(self, width=None):
        super().__init__()
        self._w = width

    def wrap(self, aw, ah):
        self._width = self._w or aw
        return (self._width, 16)

    def draw(self):
        c = self.canv
        c.saveState()
        c.setStrokeColor(GOLD)
        c.setLineWidth(0.8)
        mid = self._width / 2
        c.line(0, 8, mid - 8, 8)
        c.line(mid + 8, 8, self._width, 8)
        # Diamond
        c.setFillColor(GOLD)
        from reportlab.graphics.shapes import Polygon
        # Simple diamond via 4-point polygon
        c.translate(mid, 8)
        c.rotate(45)
        c.rect(-4, -4, 8, 8, fill=1, stroke=0)
        c.restoreState()


class ExecCard(Flowable):
    """Executive summary card with colored left border."""
    def __init__(self, label, value, accent=NAVY, width=None):
        super().__init__()
        self.label = label
        self.value = value
        self.accent = accent
        self._req_width = width
        self._estimated_height = 48

    def wrap(self, aw, ah):
        self._width = self._req_width or aw
        return (self._width, self._estimated_height)

    def draw(self):
        c = self.canv
        c.saveState()
        # Background
        c.setFillColor(GREY_LIGHT)
        c.rect(0, 0, self._width, self._estimated_height, fill=1, stroke=0)
        # Left accent
        c.setFillColor(self.accent)
        c.rect(0, 0, 4, self._estimated_height, fill=1, stroke=0)
        # Label
        c.setFillColor(self.accent)
        c.setFont('Helvetica-Bold', 8)
        c.drawString(12, self._estimated_height - 14, self.label)
        # Value
        c.setFillColor(DARK)
        c.setFont('Helvetica', 8.5)
        # Multi-line value
        lines = self.value.split('\n')
        for i, line in enumerate(lines):
            c.drawString(12, self._estimated_height - 26 - i * 12, line)
        c.restoreState()


class ScoreGauge(Flowable):
    """Circular score indicator."""
    def __init__(self, score, label, size=60):
        super().__init__()
        self.score = score
        self.label = label
        self.size = size

    def wrap(self, aw, ah):
        return (self.size, self.size + 16)

    def draw(self):
        c = self.canv
        c.saveState()
        cx, cy = self.size/2, self.size/2 + 8
        r = self.size/2 - 4

        # Background circle
        c.setFillColor(GREY_LIGHT)
        c.setStrokeColor(GREY_LINE)
        c.setLineWidth(0.5)
        c.circle(cx, cy, r, fill=1, stroke=1)

        # Score arc (navy fill ratio)
        ratio = self.score / 10
        c.setStrokeColor(NAVY)
        c.setLineWidth(5)
        import math
        start_angle = 90
        sweep = ratio * 360
        c.arc(cx - r + 3, cy - r + 3, cx + r - 3, cy + r - 3,
              startAng=start_angle - sweep, extent=sweep)

        # Score text
        c.setFillColor(NAVY)
        c.setFont('Helvetica-Bold', 14)
        c.drawCentredString(cx, cy - 5, str(self.score))

        # Label below
        c.setFillColor(GREY_MID)
        c.setFont('Helvetica', 7)
        c.drawCentredString(cx, 2, self.label)

        c.restoreState()


class RuleBlock(Flowable):
    """Non-negotiable rule block with number badge."""
    def __init__(self, number, title, body_text, width=None):
        super().__init__()
        self.number = number
        self.title = title
        self.body_text = body_text
        self._req_width = width

    def wrap(self, aw, ah):
        self._width = self._req_width or aw
        # Estimate height based on text
        lines = len(self.body_text) // 80 + 2
        self._height = 20 + lines * 13 + 14
        return (self._width, self._height)

    def draw(self):
        c = self.canv
        c.saveState()
        # Background
        c.setFillColor(GREY_LIGHT)
        c.rect(0, 0, self._width, self._height, fill=1, stroke=0)
        # Left stripe
        c.setFillColor(NAVY)
        c.rect(0, 0, 3, self._height, fill=1, stroke=0)
        # Number badge
        c.setFillColor(GOLD)
        c.circle(20, self._height - 16, 10, fill=1, stroke=0)
        c.setFillColor(WHITE)
        c.setFont('Helvetica-Bold', 10)
        c.drawCentredString(20, self._height - 20, str(self.number))
        # Title
        c.setFillColor(NAVY)
        c.setFont('Helvetica-Bold', 9)
        c.drawString(36, self._height - 20, self.title)
        # Body
        c.setFillColor(DARK)
        c.setFont('Helvetica', 8.5)
        # Word-wrap manually
        words = self.body_text.split()
        line = ""
        y = self._height - 36
        for word in words:
            test = line + word + " "
            if c.stringWidth(test, 'Helvetica', 8.5) > self._width - 44:
                c.drawString(36, y, line.strip())
                y -= 13
                line = word + " "
            else:
                line = test
        if line.strip():
            c.drawString(36, y, line.strip())
        c.restoreState()


# ─────────────────────────────────────────────
# HEADER / FOOTER
# ─────────────────────────────────────────────
def header_footer(canvas_obj, doc):
    canvas_obj.saveState()
    page = doc.page
    w, h = A4

    # Header line
    canvas_obj.setStrokeColor(NAVY)
    canvas_obj.setLineWidth(0.8)
    canvas_obj.line(40, h - 28, w - 40, h - 28)

    # Header left — brand
    canvas_obj.setFillColor(NAVY)
    canvas_obj.setFont('Helvetica-Bold', 8)
    canvas_obj.drawString(40, h - 22, 'DECISIO · MÉTHODE D3™')

    # Header right — client
    canvas_obj.setFillColor(GREY_DARK)
    canvas_obj.setFont('Helvetica', 8)
    client_str = f"{CLIENT['nom']} · {CLIENT['metier']}"
    canvas_obj.drawRightString(w - 40, h - 22, client_str)

    # Footer line
    canvas_obj.setStrokeColor(GREY_LINE)
    canvas_obj.setLineWidth(0.5)
    canvas_obj.line(40, 28, w - 40, 28)

    # Footer left
    canvas_obj.setFillColor(GREY_MID)
    canvas_obj.setFont('Helvetica', 7)
    canvas_obj.drawString(40, 20, 'CONFIDENTIEL · DECISIO AGENCY · MÉTHODE D3™')

    # Footer right — page number
    canvas_obj.setFillColor(NAVY)
    canvas_obj.setFont('Helvetica-Bold', 8)
    canvas_obj.drawRightString(w - 40, 20, str(page))

    canvas_obj.restoreState()


# ─────────────────────────────────────────────
# TABLE BUILDER
# ─────────────────────────────────────────────
def make_table(headers, rows, col_widths=None, stripe=True,
               header_bg=NAVY, header_fg=WHITE):
    """Build a styled DECISIO table."""
    S = make_styles()

    # Build header row
    header_cells = [Paragraph(h, S['table_header']) for h in headers]
    table_data = [header_cells]

    for i, row in enumerate(rows):
        cells = []
        for j, cell in enumerate(row):
            style = S['table_cell_bold'] if j == 0 else S['table_cell']
            if isinstance(cell, str):
                cells.append(Paragraph(cell, style))
            else:
                cells.append(cell)
        table_data.append(cells)

    n_rows = len(table_data)
    n_cols = len(headers)

    # Table style
    ts = [
        # Header
        ('BACKGROUND', (0, 0), (-1, 0), header_bg),
        ('TEXTCOLOR', (0, 0), (-1, 0), header_fg),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, 0), 6),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('TOPPADDING', (0, 1), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 7),
        ('RIGHTPADDING', (0, 0), (-1, -1), 7),
        # Grid
        ('LINEBELOW', (0, 0), (-1, 0), 1, NAVY),
        ('LINEBELOW', (0, 1), (-1, -2), 0.4, GREY_LINE),
        ('BOX', (0, 0), (-1, -1), 0.8, GREY_LINE),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1),
         [WHITE, GREY_LIGHT] if stripe else [WHITE]),
    ]

    tbl = Table(table_data, colWidths=col_widths, repeatRows=1)
    tbl.setStyle(TableStyle(ts))
    return tbl


# ─────────────────────────────────────────────
# SWOT TABLE
# ─────────────────────────────────────────────
def make_swot():
    S = make_styles()
    header_style = ParagraphStyle('sh', fontName='Helvetica-Bold',
                                  fontSize=8.5, textColor=WHITE,
                                  alignment=TA_CENTER)
    label_style = ParagraphStyle('sl', fontName='Helvetica-Bold',
                                 fontSize=8.5, textColor=WHITE,
                                 alignment=TA_CENTER)
    cell_style = ParagraphStyle('sc', fontName='Helvetica', fontSize=8,
                                textColor=DARK, leading=12, alignment=TA_LEFT)

    data = [
        [
            Paragraph('', header_style),
            Paragraph('Opportunités (O)', header_style),
            Paragraph('Menaces (T)', header_style),
        ],
        [
            Paragraph('Forces (S)', label_style),
            Paragraph("S×O — Installations d'urgence weekend (prime 30%), audits préventifs clients fidèles, service après-vente exclusif", cell_style),
            Paragraph("S×T — Fidéliser par abonnement maintenance, former sur nouvelles technologies (bornes électriques), partenariats exclusifs", cell_style),
        ],
        [
            Paragraph('Faiblesses (W)', label_style),
            Paragraph("W×O — Créer grilles tarifaires claires, développer argumentaires anti-prix, standardiser processus commercial", cell_style),
            Paragraph("W×T — Minima de facturation, refus catégorique des appels d'offres, focalisation géographique", cell_style),
        ],
    ]

    ts = [
        ('BACKGROUND', (0, 0), (-1, 0), NAVY),
        ('BACKGROUND', (0, 1), (0, 1), NAVY),
        ('BACKGROUND', (0, 2), (0, 2), NAVY_LIGHT),
        ('BACKGROUND', (1, 1), (1, 1), HexColor('#EBF5EB')),
        ('BACKGROUND', (2, 1), (2, 1), HexColor('#FFF3E0')),
        ('BACKGROUND', (1, 2), (1, 2), HexColor('#E8F0FB')),
        ('BACKGROUND', (2, 2), (2, 2), HexColor('#FDECEA')),
        ('TEXTCOLOR', (0, 0), (0, -1), WHITE),
        ('TEXTCOLOR', (1, 0), (-1, 0), WHITE),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('BOX', (0, 0), (-1, -1), 1, NAVY),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, GREY_LINE),
    ]

    tbl = Table(data, colWidths=[70, 195, 185])
    tbl.setStyle(TableStyle(ts))
    return tbl


# ─────────────────────────────────────────────
# COVER PAGE
# ─────────────────────────────────────────────
def make_cover():
    """Returns a canvas-drawn cover page."""
    buf = BytesIO()
    c = rl_canvas.Canvas(buf, pagesize=A4)

    # Left panel — navy
    c.setFillColor(NAVY)
    c.rect(0, 0, 255, H, fill=1, stroke=0)

    # Left panel — gold accent strip
    c.setFillColor(GOLD)
    c.rect(251, 0, 4, H, fill=1, stroke=0)

    # Subtle pattern on navy side
    c.setStrokeColor(HexColor('#1E4570'))
    c.setLineWidth(0.3)
    for i in range(0, 20):
        y = i * 45
        c.line(0, y, 255, y + 40)

    # DECISIO brand
    c.setFillColor(WHITE)
    c.setFont('Helvetica-Bold', 44)
    c.drawString(30, H - 130, 'DECISIO')

    c.setFillColor(GOLD)
    c.setFont('Helvetica-Bold', 13)
    c.drawString(30, H - 152, 'MÉTHODE D3™')

    c.setFillColor(HexColor('#AABBCC'))
    c.setFont('Helvetica', 9)
    c.drawString(30, H - 168, 'FIRST PRINCIPLES · AI-POWERED 48H')

    # Separator line
    c.setStrokeColor(GOLD)
    c.setLineWidth(1)
    c.line(30, H - 178, 225, H - 178)

    # D3 steps on left panel
    steps = [
        ('01', 'DIAGNOSTIC', 'Analyse complète', H//2 + 60),
        ('02', 'DÉCISION', 'Options scorées', H//2 - 10),
        ('03', 'DÉPLOIEMENT', "Plan d'action", H//2 - 80),
    ]
    for num, title, sub, y in steps:
        c.setFillColor(GOLD)
        c.setFont('Helvetica-Bold', 20)
        c.drawString(30, y, num)
        c.setFillColor(WHITE)
        c.setFont('Helvetica-Bold', 12)
        c.drawString(62, y, title)
        c.setFillColor(HexColor('#AABBCC'))
        c.setFont('Helvetica', 9)
        c.drawString(62, y - 13, sub)

    # Gold connector line
    c.setStrokeColor(HexColor('#3A5A7C'))
    c.setLineWidth(1)
    c.line(38, H//2 + 55, 38, H//2 - 75)

    # Website bottom left
    c.setFillColor(HexColor('#7A9ABC'))
    c.setFont('Helvetica', 8)
    c.drawString(30, 28, 'decisio.agency · contact@decisio.agency')

    # Right panel content
    # Offer badge
    c.setFillColor(GREY_LIGHT)
    c.rect(278, H - 110, 290, 68, fill=1, stroke=0)
    c.setFillColor(NAVY)
    c.rect(278, H - 110, 4, 68, fill=1, stroke=0)

    c.setFillColor(NAVY)
    c.setFont('Helvetica-Bold', 13)
    c.drawString(290, H - 72, 'AUDIT STRATÉGIQUE')

    c.setFillColor(GOLD)
    c.setFont('Helvetica-Bold', 24)
    c.drawString(290, H - 96, '2 490 €')

    c.setFillColor(GREY_DARK)
    c.setFont('Helvetica', 8.5)
    c.drawString(290, H - 56, 'Livraison 48h · Méthode D3™ · Confidentiel')

    # Client name
    c.setFillColor(DARK)
    c.setFont('Helvetica-Bold', 30)
    c.drawString(278, H - 175, 'Lucas Bernard')

    # Gold underline
    name_w = c.stringWidth('Lucas Bernard', 'Helvetica-Bold', 30)
    c.setStrokeColor(GOLD)
    c.setLineWidth(2)
    c.line(278, H - 180, 278 + name_w, H - 180)

    c.setFillColor(GREY_DARK)
    c.setFont('Helvetica', 15)
    c.drawString(278, H - 202, 'Électricien indépendant')

    c.setFillColor(GREY_MID)
    c.setFont('Helvetica', 10)
    c.drawString(278, H - 222, '18 mars 2026')

    # Decorative line
    c.setStrokeColor(GREY_LINE)
    c.setLineWidth(0.5)
    c.line(278, H - 232, 568, H - 232)

    # Confidentiality notice
    c.setFillColor(GREY_LIGHT)
    c.rect(278, 55, 290, 50, fill=1, stroke=0)
    c.setFillColor(GREY_DARK)
    c.setFont('Helvetica', 7.5)
    conf_lines = [
        "Ce rapport est strictement confidentiel et destiné",
        "au seul usage du client désigné ci-dessus.",
        "Toute reproduction est interdite sans autorisation",
        "écrite de DECISIO AGENCY.",
    ]
    for i, line in enumerate(conf_lines):
        c.drawString(286, 92 - i * 11, line)

    c.save()
    return buf


# ─────────────────────────────────────────────
# BUILD STORY
# ─────────────────────────────────────────────
def build_story():
    S = make_styles()
    story = []

    # ── SYNTHÈSE EXECUTIVE ──────────────────────
    story.append(SectionHeader("RAPPORT D'AUDIT STRATÉGIQUE — MÉTHODE D3™"))
    story.append(Spacer(1, 6))

    # Sub-header
    story.append(Paragraph(
        f"<b>Client :</b> {CLIENT['nom']} | {CLIENT['metier']} | 18 mars 2026",
        S['body']
    ))
    story.append(Spacer(1, 10))

    story.append(MiniSectionHeader("SYNTHÈSE EXECUTIVE"))
    story.append(Spacer(1, 6))

    # Executive cards in 2 columns
    exec_data = [
        [
            ExecCard("VRAI PROBLÈME", "Lucas est positionné comme un dépanneur d'urgence\nalors qu'il a les compétences d'un installateur premium.", NAVY),
            ExecCard("SOLUTION OPTIMALE", "Transformer sa réactivité en argument de vente\npour installations complètes avec primes d'urgence.", GREEN_OK),
        ],
        [
            ExecCard("ACTION #1 dans les 48h", "Appeler 10 clients fidèles pour proposer un audit électrique\ngratuit et identifier besoins d'installation.", GOLD),
            ExecCard("IMPACT M+6", "2 800€ net/mois — objectif atteint\nProbabilité de succès : 72%", NAVY),
        ],
    ]

    for row in exec_data:
        t = Table([[row[0], Spacer(8, 1), row[1]]],
                  colWidths=[220, 8, 220])
        t.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        story.append(t)
        story.append(Spacer(1, 6))

    # Score de maturité
    story.append(Spacer(1, 4))
    score_data = [[
        Paragraph("<b>Score de maturité client : 7/10</b>", S['body_navy']),
        Paragraph("[Conscience du problème 8/10 / Budget limité 5/10 / Capacité de décision 9/10]", S['body']),
    ]]
    score_tbl = Table(score_data, colWidths=[170, 280])
    score_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), HexColor('#EEF2F8')),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LINEAFTER', (0, 0), (0, -1), 1, NAVY),
    ]))
    story.append(score_tbl)
    story.append(Spacer(1, 14))

    # QUICK WIN
    story.append(MiniSectionHeader("QUICK WIN — 48H"))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "<b>Action :</b> Contacter les 10 clients les plus fidèles pour proposer un audit électrique gratuit de 30 minutes",
        S['body']
    ))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "<b>Pourquoi ça marche :</b> Exploite la confiance existante et transforme le relationnel en opportunité commerciale structurée",
        S['body']
    ))
    story.append(Spacer(1, 8))

    # Message scripts in cards
    messages = [
        ("MESSAGE 1 — Accroche",
         '"Bonjour [Prénom], Lucas de LB Électricité. Je lance un service d\'audit électrique gratuit pour mes clients fidèles comme vous. 30 minutes pour vérifier votre installation et identifier les améliorations possibles."'),
        ("MESSAGE 2 — Approfondissement",
         '"Cela vous permet d\'anticiper les pannes, réduire votre facture énergétique et mettre aux normes si besoin. C\'est gratuit car vous me faites déjà confiance depuis 3 ans. Êtes-vous disponible cette semaine ou la prochaine ?"'),
    ]

    for title, msg in messages:
        msg_data = [[
            Paragraph(title, S['label_gold']),
        ], [
            Paragraph(msg, S['message_text']),
        ]]
        mt = Table(msg_data, colWidths=[448])
        mt.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), NAVY),
            ('BACKGROUND', (0, 1), (-1, 1), HexColor('#F0F4FA')),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LINEBELOW', (0, -1), (-1, -1), 1.5, GOLD),
        ]))
        story.append(mt)
        story.append(Spacer(1, 6))

    result_data = [
        ["Résultat attendu", "Temps total", "Si pas de réponse 48h"],
        [
            "3-4 audits programmés sous 48h\n1-2 devis d'installation sous 7 jours",
            "2h\n(appels + grille d'audit)",
            '"Bonjour [Prénom], peut-être que le moment n\'est pas opportun - gardez mon numéro si vous avez des projets futurs."',
        ]
    ]
    rt = make_table(result_data[0], [result_data[1]],
                    col_widths=[150, 100, 198])
    story.append(rt)

    # ── SEPARATOR PAGE 1 ────────────────────────
    story.append(PageBreak())
    story.append(SeparatorPage("01", "DIAGNOSTIC", "Analyse complète",
                               "Porter's Five Forces · SWOT · 5 Pourquoi · Coût de l'inaction"))
    story.append(PageBreak())

    # ── PARTIE 1 — DIAGNOSTIC ───────────────────
    story.append(SectionHeader("PARTIE 1 — DIAGNOSTIC"))
    story.append(Spacer(1, 8))

    # 1.1 Analyse financière
    story.append(MiniSectionHeader("1.1 Analyse financière"))
    story.append(Spacer(1, 5))

    fin_headers = ["Indicateur", "Valeur calculée", "Interprétation"]
    fin_rows = [
        ["Taux de marge nette", "33,3%", "Excellent pour un électricien (moyenne secteur 15-20%)"],
        ["Revenu horaire effectif", "Non calculable", "Heures travaillées non fournies"],
        ["Poids dépense principale", "42,8%", "Normal pour activité mobile avec matériel"],
        ["Écart objectif vs réalité", "+1 400€ net manquants", "Besoin de doubler la rentabilité"],
    ]
    story.append(make_table(fin_headers, fin_rows, col_widths=[140, 110, 198]))
    story.append(Spacer(1, 12))

    # 1.2 Déconstruction 5 Pourquoi
    story.append(MiniSectionHeader("1.2 Déconstruction — 5 Pourquoi"))
    story.append(Spacer(1, 5))
    story.append(Paragraph(
        "<b>Problème exprimé :</b> J'ai toujours du travail mais je gagne pas assez. Je passe mon temps à faire des petits dépannages à 80-100€ alors que mes collègues font des installations complètes à 2 000-3 000€. Les clients me comparent toujours aux moins chers.",
        S['body']
    ))
    story.append(Spacer(1, 6))

    pourquois = [
        ("→ Pourquoi 1", "Pourquoi faites-vous que des petits dépannages ?", "Parce que les clients m'appellent pour de l'urgence"),
        ("→ Pourquoi 2", "Pourquoi ne proposez-vous pas d'installations lors de ces dépannages ?", "Parce que les clients sont en mode \"réparer vite\" pas \"investir\""),
        ("→ Pourquoi 3", "Pourquoi ne revenez-vous pas plus tard avec une approche différente ?", "Parce que je pense qu'ils vont comparer les prix"),
        ("→ Pourquoi 4", "Pourquoi pensez-vous qu'ils vont comparer alors qu'ils vous font déjà confiance ?", "Parce que j'assimile dépannage et installation comme deux univers différents"),
        ("→ Pourquoi 5", "Pourquoi séparez-vous ces deux activités alors qu'elles exploitent la même relation client ?", "Parce que je n'ai pas de processus pour transformer la confiance dépannage en vente installation"),
    ]
    pq_rows = []
    for num, question, reponse in pourquois:
        pq_rows.append([
            Paragraph(f"<b>{num}</b>", S['table_cell_bold']),
            Paragraph(question, S['table_cell']),
            Paragraph(f"<i>{reponse}</i>", S['table_cell']),
        ])
    pq_tbl = Table(pq_rows, colWidths=[55, 195, 198])
    pq_tbl.setStyle(TableStyle([
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [WHITE, GREY_LIGHT]),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 7),
        ('RIGHTPADDING', (0, 0), (-1, -1), 7),
        ('LINEBELOW', (0, -1), (-1, -1), 1.5, GOLD),
        ('BOX', (0, 0), (-1, -1), 0.8, GREY_LINE),
    ]))
    story.append(pq_tbl)
    story.append(Spacer(1, 6))

    # Véritable fondamentale
    fund_data = [[Paragraph(
        "⬛  <b>Véritable fondamentale :</b> Lucas a construit un capital confiance énorme mais ne l'exploite pas commercialement pour monter en gamme.",
        S['insight']
    )]]
    fund_tbl = Table(fund_data, colWidths=[448])
    fund_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), HexColor('#EEF2F8')),
        ('LINERIGHT', (0, 0), (0, -1), 3, GOLD),
        ('LINEBEFORE', (0, 0), (0, -1), 3, NAVY),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(fund_tbl)
    story.append(Spacer(1, 12))

    # 1.3 Pattern
    story.append(MiniSectionHeader("1.3 Ce que les tentatives révèlent"))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "<b>Pattern identifié :</b> Fuite en avant vers le discount au lieu de capitaliser sur ses atouts relationnels et qualitatifs",
        S['body']
    ))
    story.append(Spacer(1, 10))

    # 1.4 Porter's Five Forces
    story.append(MiniSectionHeader("1.4 Porter's Five Forces — Analyse sectorielle"))
    story.append(Spacer(1, 5))

    porter_headers = ["Force", "Intensité (/5)", "Impact sur le client", "Levier d'action"]
    porter_rows = [
        ["Rivalité concurrentielle", "5/5  ●●●●●", "Guerre des prix permanente", "Différenciation service + relation"],
        ["Pouvoir des clients", "4/5  ●●●●○", "Comparaison facile, urgence dilue fidélité", "Créer dépendance par expertise"],
        ["Pouvoir des fournisseurs", "2/5  ●●○○○", "Matériel standardisé", "Négociation volume installations"],
        ["Menace nouveaux entrants", "4/5  ●●●●○", "Barrière faible (auto-entrepreneurs)", "Monter en complexité technique"],
        ["Menace produits substituts", "1/5  ●○○○○", "Pas d'alternative à l'électricien", "Exploiter cette position"],
    ]
    story.append(make_table(porter_headers, porter_rows, col_widths=[115, 75, 135, 123]))

    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "<b>Insight stratégique :</b> La rivalité est la force dominante — s'en extraire par la relation client et monter vers l'installation où les barrières sont plus hautes.",
        S['insight']
    ))
    story.append(Spacer(1, 12))

    # 1.5 SWOT
    story.append(MiniSectionHeader("1.5 SWOT Enrichi — Croisements stratégiques"))
    story.append(Spacer(1, 5))
    story.append(make_swot())
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "<b>Quadrant prioritaire :</b> S×O — Lucas a déjà les atouts, il faut les exploiter offensivement.",
        S['body_navy']
    ))
    story.append(Spacer(1, 12))

    # 1.6 Coût de l'inaction
    story.append(MiniSectionHeader("1.6 Coût de l'inaction"))
    story.append(Spacer(1, 5))

    inac_headers = ["Période", "Manque à gagner", "Cumulé", "Risque"]
    inac_rows = [
        ["M+1", "1 400€", "1 400€", "Épuisement physique"],
        ["M+3", "4 200€", "5 600€", "Concurrence s'installe"],
        ["M+6", "8 400€", "14 000€", "Décrochage définitif marché installations"],
    ]
    story.append(make_table(inac_headers, inac_rows, col_widths=[60, 100, 90, 198],
                            header_bg=RED_ALERT))

    # ── SEPARATOR PAGE 2 ────────────────────────
    story.append(PageBreak())
    story.append(SeparatorPage("02", "DÉCISION", "Options scorées",
                               "VRIO · Ansoff · Options A/B/C · Recommandation"))
    story.append(PageBreak())

    # ── PARTIE 2 — DÉCISION ─────────────────────
    story.append(SectionHeader("PARTIE 2 — DÉCISION"))
    story.append(Spacer(1, 8))

    # 2.1 VRIO
    story.append(MiniSectionHeader("2.1 Analyse VRIO — Avantage concurrentiel durable"))
    story.append(Spacer(1, 5))

    vrio_headers = ["Ressource / Compétence", "Valeur ?", "Rare ?", "Inimitable ?", "Organisé ?", "Avantage"]
    vrio_rows = [
        ["Réactivité weekend", "Oui", "Oui", "Non", "Non", "Temporaire"],
        ["Clientèle fidèle 3 ans", "Oui", "Oui", "Oui", "Non", "Potentiel durable"],
        ["Zéro défaut qualité", "Oui", "Oui", "Oui", "Oui", "Durable ★"],
    ]

    vrio_style_extra = [
        ('BACKGROUND', (5, 3), (5, 3), HexColor('#1A7A4A')),
        ('TEXTCOLOR', (5, 3), (5, 3), WHITE),
        ('FONTNAME', (5, 3), (5, 3), 'Helvetica-Bold'),
    ]
    vt = make_table(vrio_headers, vrio_rows, col_widths=[130, 45, 45, 55, 55, 70])
    story.append(vt)
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "<b>Conclusion VRIO :</b> La qualité zéro défaut est l'avantage durable. Organiser la fidélité client pour le rendre inimitable (base données, historique, relation personnalisée).",
        S['insight']
    ))
    story.append(Spacer(1, 12))

    # 2.2 Ansoff
    story.append(MiniSectionHeader("2.2 Matrice Ansoff — Axes de croissance"))
    story.append(Spacer(1, 5))

    ansoff_headers = ["Stratégie", "Description pour CE client", "ROI estimé", "Délai", "Score"]
    ansoff_rows = [
        ["Pénétration marché ★", "Vendre installations aux clients dépannage actuels", "2 000€/mois", "2 mois", "9/10"],
        ["Développement marché", "Prospecter B2B (commerces, bureaux)", "1 200€/mois", "4 mois", "6/10"],
        ["Développement produit", "Maintenance préventive, domotique, bornes électriques", "800€/mois", "6 mois", "5/10"],
        ["Diversification", "Autres corps de métiers (plomberie)", "400€/mois", "8 mois", "3/10"],
    ]
    at = make_table(ansoff_headers, ansoff_rows, col_widths=[95, 170, 70, 50, 63])
    story.append(at)
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "<b>Recommandation Ansoff :</b> Pénétration marché en priorité absolue (clients acquis + confiance établie), puis développement marché B2B.",
        S['body_navy']
    ))
    story.append(Spacer(1, 14))

    # 2.3 Options scorées
    story.append(MiniSectionHeader("2.3 Options scorées — Formule : (ROI×0,4) + (Prob×0,4) − (Diff×0,2)"))
    story.append(Spacer(1, 8))

    story.append(ScoreBar(
        "OPTION A",
        "Pivot Installateur Premium",
        score=8.2, roi=9, proba=8, diff=3, is_best=True
    ))
    story.append(Spacer(1, 6))
    story.append(ScoreBar(
        "OPTION B",
        "Spécialiste Dépannage Urgent",
        score=6.4, roi=6, proba=9, diff=2, is_best=False
    ))
    story.append(Spacer(1, 6))
    story.append(ScoreBar(
        "OPTION C",
        "Multi-services Électrique",
        score=2.6, roi=5, proba=5, diff=7, is_best=False
    ))
    story.append(Spacer(1, 10))

    # Options comparison table
    opt_headers = ["Option", "ROI", "Proba", "Diff", "Score"]
    opt_rows = [
        ["A — Installateur Premium ★", "9/10", "8/10", "3/10", "8,2/10"],
        ["B — Spécialiste Dépannage", "6/10", "9/10", "2/10", "6,4/10"],
        ["C — Multi-services", "5/10", "5/10", "7/10", "2,6/10"],
    ]
    ot = make_table(opt_headers, opt_rows, col_widths=[175, 55, 55, 55, 108])
    story.append(ot)
    story.append(Spacer(1, 12))

    # 2.4 Option dangereuse
    story.append(MiniSectionHeader("2.4 Option dangereuse — À éviter absolument"))
    story.append(Spacer(1, 5))
    danger_data = [[Paragraph(
        "⚠  <b>Baisser encore les prix</b> pour \"être compétitif\" : cela attirerait uniquement des clients price-sensitive, réduirait la marge de 33% à 15%, nécessiterait 2,8× plus de chantiers pour le même résultat, et détruirait définitivement le positionnement qualité construit en 3 ans.",
        S['body']
    )]]
    dt = Table(danger_data, colWidths=[448])
    dt.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), HexColor('#FFF0EE')),
        ('LINEBEFORE', (0, 0), (0, -1), 4, RED_ALERT),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(dt)
    story.append(Spacer(1, 12))

    # 2.5 Recommandation
    story.append(MiniSectionHeader('2.5 Recommandation — "Si j\'étais à votre place"'))
    story.append(Spacer(1, 5))
    reco_text = (
        "Je choisirais le <b>pivot installateur premium</b> en exploitant ma base client existante. "
        "La logique est imparable : j'ai déjà la confiance, la réputation qualité et l'accès aux foyers. "
        "Je commencerais par appeler mes 20 meilleurs clients pour proposer un audit électrique gratuit, "
        "identifier 2-3 besoins d'installation par foyer (prises, éclairage, tableau, sécurité). "
        "Mon argument massue : <i>\"Vous me connaissez depuis 3 ans, vous savez que je fais du travail soigné. "
        "Autant que ce soit moi qui fasse vos installations plutôt qu'un inconnu moins cher qui bâclera.\"</i> "
        "Je facturerai ces installations 2 500€ moyenne avec prime réactivité 20% (disponible weekend/soir).<br/>"
        "<b>Première phrase demain matin :</b> <i>\"Bonjour Madame Dupont, c'est Lucas votre électricien — "
        "j'aimerais passer vous voir 30 minutes cette semaine pour un audit gratuit de votre installation électrique.\"</i>"
    )
    reco_data = [[Paragraph(reco_text, S['body'])]]
    reco_tbl = Table(reco_data, colWidths=[448])
    reco_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), HexColor('#F0F4FA')),
        ('LINEBEFORE', (0, 0), (0, -1), 4, NAVY),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(reco_tbl)
    story.append(Spacer(1, 12))

    # 2.6 Risques
    story.append(MiniSectionHeader("2.6 Risques à anticiper"))
    story.append(Spacer(1, 5))

    risk_headers = ["Type", "Description", "Probabilité", "Solution"]
    risk_rows = [
        ["Financier", "Trous de planning pendant transition", "Moyenne", "Garder 30% dépannage minimum"],
        ["Opérationnel", "Manque d'outillage installation complexe", "Faible", "Location matériel ou sous-traitance ponctuelle"],
        ["Marché", "Clients fidèles choqués par nouvelle tarification", "Faible", "Communication transparente sur évolution"],
        ["Légal", "Assurance inadaptée aux gros chantiers", "Moyenne", "Vérifier couverture avec assureur"],
    ]
    story.append(make_table(risk_headers, risk_rows, col_widths=[70, 160, 75, 143]))
    story.append(Spacer(1, 12))

    # 2.7 Seuils
    story.append(MiniSectionHeader("2.7 Seuils Stop / Pivot / Continue"))
    story.append(Spacer(1, 5))

    seuil_headers = ["Signal", "Indicateur chiffré", "Délai", "Justification", "Action immédiate"]
    seuil_rows = [
        ["STOP si", "<1 installation vendue", "6 semaines", "Délai normal prospection → devis → signature", "Retour dépannage exclusif"],
        ["PIVOT si", "1-2 installations/mois", "8 semaines", "Rythme insuffisant mais validation concept", "Mixer B2B + B2C"],
        ["CONTINUE si", ">3 installations/mois", "4 semaines", "Validation rapide = accélérer", "Recruter apprenti"],
    ]
    story.append(make_table(seuil_headers, seuil_rows, col_widths=[58, 80, 55, 140, 115]))

    # ── SEPARATOR PAGE 3 ────────────────────────
    story.append(PageBreak())
    story.append(SeparatorPage("03", "DÉPLOIEMENT", "Plan d'action",
                               "Semaine 1 · Jalons M+1 à M+6 · Impact financier · McKinsey 7S"))
    story.append(PageBreak())

    # ── PARTIE 3 — DÉPLOIEMENT ──────────────────
    story.append(SectionHeader("PARTIE 3 — DÉPLOIEMENT"))
    story.append(Spacer(1, 8))

    # 3.1 Plan Semaine 1
    story.append(MiniSectionHeader("3.1 Plan Semaine 1"))
    story.append(Spacer(1, 5))

    s1_headers = ["Jour", "Action", "Coût (€)", "Temps", "Résultat"]
    s1_rows = [
        ["Lundi", "Créer liste 20 meilleurs clients + grille audit", "0€", "2h", "Base prospects qualifiés"],
        ["Mardi", "Appeler 10 premiers clients — proposer audit", "0€", "3h", "3-4 RDV programmés"],
        ["Mercredi", "Création support commercial (tarifs, visuels)", "50€", "4h", "Outils de vente"],
        ["Jeudi", "2 premiers audits terrain", "30€", "4h", "2 devis à préparer"],
        ["Vendredi", "Préparation devis + appel 10 autres clients", "0€", "3h", "Pipeline constitué"],
    ]
    story.append(make_table(s1_headers, s1_rows, col_widths=[55, 165, 50, 40, 138]))
    story.append(Spacer(1, 8))

    # Budget ROI
    budget_data = [[
        Paragraph("<b>Budget semaine 1 :</b> 80€ cash + 320€ temps valorisé (20€/h) = <b>400€ total</b>", S['body_navy']),
        Paragraph("<b>ROI semaine 1 attendu :</b> 2 devis 2 500€ pour 80€ = <b>ratio 62:1</b>", S['body_navy']),
    ]]
    bt = Table(budget_data, colWidths=[224, 224])
    bt.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), HexColor('#EEF2F8')),
        ('BACKGROUND', (1, 0), (1, 0), HexColor('#FFF8E7')),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('LINEAFTER', (0, 0), (0, -1), 1, GREY_LINE),
    ]))
    story.append(bt)
    story.append(Spacer(1, 14))

    # 3.2 Jalons
    story.append(MiniSectionHeader("3.2 Jalons M+1 à M+6"))
    story.append(Spacer(1, 5))

    jalon_headers = ["Période", "Focus", "Action concrète", "Source prospects", "Indicateur"]
    jalon_rows = [
        ["M+1", "Validation concept", "40 audits réalisés, 8 devis envoyés", "Clients fidèles existants", "2 installations signées"],
        ["M+3", "Montée en puissance", "Processus industrialisé", "Bouche-à-oreille + recommandations", "6 installations/mois"],
        ["M+6", "Stabilisation premium", "Mix 70% installation 30% dépannage", "Réseau constitué + digital", "2 800€ net objectif atteint"],
    ]
    story.append(make_table(jalon_headers, jalon_rows, col_widths=[38, 70, 120, 118, 102]))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "<b>Point de vigilance M+1 :</b> Résistance clients aux nouveaux prix — préparer arguments valeur et témoignages qualité.",
        S['body']
    ))
    story.append(Spacer(1, 14))

    # 3.3 Impact financier
    story.append(MiniSectionHeader("3.3 Impact financier prévisionnel"))
    story.append(Spacer(1, 5))
    story.append(Paragraph(
        "<b>Calcul :</b> 6 installations/mois × 2 500€ × 40% marge = <b>6 000€ bénéfice</b>",
        S['body_navy']
    ))
    story.append(Paragraph(
        "<i>Hypothèses : 40% marge installation vs 33% dépannage, 6 installations réalisables/mois, prix moyen 2 500€ accepté par le marché local</i>",
        S['small_grey']
    ))
    story.append(Spacer(1, 8))

    # Financial table
    impact_headers = ["Période", "Aujourd'hui", "Projection", "Gain"]
    impact_rows = [
        ["M+1", "1 400€", "1 800€", "+400€"],
        ["M+3", "1 400€", "2 400€", "+1 000€"],
        ["M+6", "1 400€", "2 800€", "+1 400€"],
    ]
    story.append(make_table(impact_headers, impact_rows, col_widths=[80, 120, 120, 128]))
    story.append(Spacer(1, 12))

    # BAR CHART
    chart_data = [
        ("M+1", 1400, 1800),
        ("M+3", 1400, 2400),
        ("M+6", 1400, 2800),
    ]
    story.append(BarChart(chart_data, width=420, height=140))
    story.append(Spacer(1, 14))

    # 3.4 Positionnement
    story.append(MiniSectionHeader("3.4 Positionnement & Message"))
    story.append(Spacer(1, 5))

    story.append(Paragraph(
        '<b>Slogan :</b> "L\'électricien que vous connaissez, l\'installation que vous méritez"',
        S['body_navy']
    ))
    story.append(Spacer(1, 6))

    messages_key = [
        ("Message clé 1 — Confiance acquise",
         '"3 ans de dépannages impeccables chez vous, vous savez que je fais du travail soigné. Autant que ce soit moi qui réalise vos installations."'),
        ("Message clé 2 — Réactivité premium",
         '"Installation prévue lundi, panne dimanche ? J\'adapte mon planning. Service qu\'aucune grande enseigne ne peut offrir."'),
        ("Message clé 3 — Garantie totale",
         '"Zéro défaut depuis 3 ans, je garantis mes installations 5 ans pièces et main d\'œuvre. Si problème, j\'interviens sous 24h."'),
    ]
    for title, msg in messages_key:
        msg_row = [[
            Paragraph(title, S['label_gold']),
            Paragraph(msg, S['message_text']),
        ]]
        mt = Table(msg_row, colWidths=[148, 300])
        mt.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), NAVY),
            ('BACKGROUND', (1, 0), (1, 0), GREY_LIGHT),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 7),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('LINEBELOW', (0, 0), (-1, -1), 0.5, GREY_LINE),
        ]))
        story.append(mt)

    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "<b>Canal prioritaire :</b> Téléphone direct avec clients existants puis recommandations",
        S['body']
    ))
    story.append(Spacer(1, 14))

    # 3.5 McKinsey 7S
    story.append(MiniSectionHeader("3.5 Alignement McKinsey 7S — Diagnostic interne"))
    story.append(Spacer(1, 5))

    s7_headers = ["Élément 7S", "Situation actuelle", "Note /5", "Désalignement"]
    s7_rows = [
        ["Strategy", "Dépannage réactif sans vision long terme", "2/5", "Manque de cap commercial"],
        ["Structure", "Solo efficace pour dépannage", "4/5", "—"],
        ["Systems", "Processus dépannage rodé, commercial absent", "2/5", "Pas de CRM ni suivi prospects"],
        ["Skills", "Excellence technique, commercial faible", "3/5", "Formation vente nécessaire"],
        ["Staff", "Un homme orchestre compétent", "4/5", "—"],
        ["Style", "Artisan humble, manque d'ambition commerciale", "2/5", "Sous-estimation de sa valeur"],
        ["Shared Values", "Qualité irréprochable, service client", "5/5", "—"],
    ]
    story.append(make_table(s7_headers, s7_rows, col_widths=[75, 175, 50, 148]))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "<b>Désalignement prioritaire :</b> Strategy — créer plan commercial structuré avec objectifs chiffrés et actions quotidiennes",
        S['body_navy']
    ))
    story.append(Paragraph(
        "<b>Note globale 7S : 22/35</b>",
        S['body_bold']
    ))
    story.append(Spacer(1, 14))

    # 3.6 Les 3 règles
    story.append(MiniSectionHeader("3.6 Les 3 règles — Non négociables"))
    story.append(Spacer(1, 8))

    rules = [
        ("1", "Ne jamais négocier sur le prix des installations",
         "Obstacle : peur de perdre le client. Comment surmonter : préparer 3 arguments valeur (garantie, réactivité, relation). Si non respectée : retour spirale discount et échec de la transformation."),
        ("2", "Proposer systématiquement un audit lors de chaque dépannage",
         "Obstacle : \"le client est pressé\". Comment surmonter : phrase magique \"En 2 minutes je peux voir si d'autres éléments risquent de lâcher\". Si non respectée : perte de 50% des opportunités d'installation."),
        ("3", "KPI unique : Nombre d'audits réalisés (chaque samedi — carnet papier)",
         "Si en dessous de 8 audits/mois deux semaines consécutives : retour formation commerciale ou abandon du pivot installateur."),
    ]
    for num, title, body in rules:
        story.append(RuleBlock(num, title, body))
        story.append(Spacer(1, 6))

    # ── POUR ALLER PLUS LOIN ────────────────────
    story.append(Spacer(1, 8))
    story.append(GoldDivider())
    story.append(Spacer(1, 8))
    story.append(SectionHeader("POUR ALLER PLUS LOIN"))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "Ce diagnostic est fondé sur : CA mensuel, bénéfice, ressources clés déclarées, tentatives passées et objectif 6 mois.",
        S['body']
    ))
    story.append(Spacer(1, 6))
    story.append(Paragraph("<b>Pour affiner à 100% :</b>", S['body_bold']))
    story.append(Spacer(1, 4))

    affinage = [
        ("Heures travaillées réelles", "→ calcul rentabilité horaire et optimisation planning"),
        ("Liste clients avec historique", "→ segmentation et ciblage précis des prospects installations"),
        ("Analyse concurrence locale", "→ positionnement prix optimal pour installations"),
    ]
    aff_rows = [[Paragraph(f"<b>{item}</b>", S['body_navy']),
                 Paragraph(desc, S['body'])] for item, desc in affinage]
    at = Table(aff_rows, colWidths=[160, 288])
    at.setStyle(TableStyle([
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [WHITE, GREY_LIGHT]),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('LINEBEFORE', (0, 0), (0, -1), 3, GOLD),
    ]))
    story.append(at)
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "<b>Action recommandée :</b> Tracker pendant 2 semaines temps passé par type d'intervention pour optimiser le mix dépannage/installation.",
        S['body_navy']
    ))
    story.append(Spacer(1, 20))

    # Final confidentiality
    story.append(GoldDivider())
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "Rapport confidentiel — DECISIO AGENCY | Méthode D3™ | contact@decisio.agency",
        S['small_grey']
    ))
    story.append(Paragraph(
        "Rapport strictement confidentiel — DECISIO AGENCY · Méthode D3™ · contact@decisio.agency",
        S['small_grey']
    ))

    return story


# ─────────────────────────────────────────────
# MAIN BUILD
# ─────────────────────────────────────────────
def generate_pdf(report_text=None, nom='Client', secteur='', mode='premium', date_str=None):
    import tempfile, os
    if nom: CLIENT['nom'] = nom
    if secteur: CLIENT['metier'] = secteur
    if date_str: CLIENT['date'] = date_str
    cover_buf = make_cover()
    tmp = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
    tmp.close()
    content_path = tmp.name
    doc = SimpleDocTemplate(
        content_path, pagesize=A4,
        leftMargin=40, rightMargin=40, topMargin=45, bottomMargin=45,
        title="DECISIO Audit", author="DECISIO AGENCY",
    )
    story = build_story()
    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
    from pypdf import PdfWriter, PdfReader
    writer = PdfWriter()
    cover_buf.seek(0)
    for page in PdfReader(cover_buf).pages:
        writer.add_page(page)
    for page in PdfReader(content_path).pages:
        writer.add_page(page)
    output_buf = BytesIO()
    writer.write(output_buf)
    output_buf.seek(0)
    os.remove(content_path)
    return output_buf.read()

if __name__ == '__main__':
    generate_pdf('/home/claude/DECISIO_Audit_Lucas_Bernard_V17.pdf')
