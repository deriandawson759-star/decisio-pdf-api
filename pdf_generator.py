"""
DECISIO — PDF Generator V2
Playwright + Chromium headless → PDF pixel-perfect
Rendu identique à Chrome — CSS complet (flex, grid, custom fonts, animations off)
Score qualité cible : 10/10
"""

import os
import tempfile
from datetime import datetime
from playwright.sync_api import sync_playwright


# ─────────────────────────────────────────
# POINT D'ENTRÉE
# ─────────────────────────────────────────

def generate_pdf_from_data(client_data: dict, analysis: dict,
                           scores: dict, mode: str = 'premium') -> bytes:
    """
    Construit le HTML premium, lance Chromium headless,
    génère le PDF et retourne les bytes.
    """
    html = build_report_html(client_data, analysis, scores, mode)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
            ]
        )
        page = browser.new_page()

        # Injecter le HTML directement (pas besoin d'un serveur)
        page.set_content(html, wait_until='networkidle')

        # Attendre que les fonts Google soient chargées
        page.wait_for_timeout(1500)

        pdf_bytes = page.pdf(
            format='A4',
            print_background=True,
            margin={
                'top':    '18mm',
                'bottom': '16mm',
                'left':   '14mm',
                'right':  '14mm',
            },
            display_header_footer=False,   # On gère header/footer en CSS
        )

        browser.close()

    return pdf_bytes


# ─────────────────────────────────────────
# HTML BUILDER
# ─────────────────────────────────────────

def build_report_html(client_data: dict, analysis: dict,
                      scores: dict, mode: str) -> str:

    nom      = client_data.get('nom', 'Client')
    secteur  = client_data.get('secteur', '')
    date_str = client_data.get('date',
               datetime.now().strftime('%d %B %Y'))

    exec_data = analysis.get('synthese_executive', {})
    quick_win = analysis.get('quick_win', {})
    diag      = analysis.get('diagnostic', {})
    decision  = analysis.get('decision', {})
    deploy    = analysis.get('deploiement', {})
    plus_loin = analysis.get('pour_aller_plus_loin', {})

    flux          = scores.get('flux', {})
    global_score  = scores.get('global_score', 5.0)
    maturity      = scores.get('maturity_level', 'En développement')
    maturity_color= scores.get('maturity_color', '#C9A84C')
    proba         = scores.get('probabilite_succes', 50)
    options       = scores.get('options_scored', [])

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>DECISIO — Rapport D3™ — {_h(nom)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&display=swap" rel="stylesheet">
<style>{_css()}</style>
</head>
<body>

<!-- ══════════════════════════════════════════ -->
<!--  COUVERTURE                                -->
<!-- ══════════════════════════════════════════ -->
<div class="cover">
  <div class="cover-left">
    <div class="cl-brand">DECISIO</div>
    <div class="cl-method">MÉTHODE D3™</div>
    <div class="cl-tag">FIRST PRINCIPLES · AI-POWERED · 48H</div>
    <div class="cl-rule"></div>
    <div class="cl-steps">
      <div class="cl-step"><span class="sn">01</span><div><div class="st">DIAGNOSTIC</div><div class="ss">Analyse complète</div></div></div>
      <div class="cl-dot"></div>
      <div class="cl-step"><span class="sn">02</span><div><div class="st">DÉCISION</div><div class="ss">Options scorées</div></div></div>
      <div class="cl-dot"></div>
      <div class="cl-step"><span class="sn">03</span><div><div class="st">DÉPLOIEMENT</div><div class="ss">Plan d'action</div></div></div>
    </div>
    <div class="cl-website">decisio.agency · contact@decisio.agency</div>
  </div>
  <div class="cover-right">
    <div class="cr-badge">
      <div class="cr-badge-title">AUDIT STRATÉGIQUE</div>
      <div class="cr-badge-price">2 490 €</div>
      <div class="cr-badge-sub">Livraison 48h · Méthode D3™ · Confidentiel</div>
    </div>
    <div class="cr-name">{_h(nom)}</div>
    <div class="cr-underline"></div>
    <div class="cr-sector">{_h(secteur)}</div>
    <div class="cr-date">{_h(date_str)}</div>
    <div class="cr-divider"></div>
    <div class="cr-conf">
      Ce rapport est strictement confidentiel et destiné au seul usage du client désigné.
      Toute reproduction est interdite sans autorisation écrite de DECISIO AGENCY.
    </div>
  </div>
</div>

<!-- ══════════════════════════════════════════ -->
<!--  SYNTHÈSE EXECUTIVE                        -->
<!-- ══════════════════════════════════════════ -->
<div class="page">
  <div class="page-hdr"><span class="ph-l">DECISIO · MÉTHODE D3™</span><span class="ph-r">{_h(nom)} · {_h(secteur)}</span></div>

  <div class="sec-hdr">SYNTHÈSE EXECUTIVE</div>

  <div class="insight-box">
    <div class="ib-label">⚡ KEY INSIGHT</div>
    <div class="ib-text">{_h(analysis.get('key_insight',''))}</div>
  </div>

  <div class="two-col">
    <div class="exec-card navy-bl">
      <div class="ec-label">PROBLÈME PERÇU</div>
      <div class="ec-val">{_h(analysis.get('probleme_percu',''))}</div>
    </div>
    <div class="exec-card gold-bl">
      <div class="ec-label">PROBLÈME RÉEL</div>
      <div class="ec-val">{_h(analysis.get('probleme_reel',''))}</div>
    </div>
  </div>

  <div class="exec-grid">
    <div class="eg-cell">
      <div class="eg-label">VRAI PROBLÈME</div>
      <div class="eg-val">{_h(exec_data.get('vrai_probleme',''))}</div>
    </div>
    <div class="eg-cell gold-bl">
      <div class="eg-label">SOLUTION OPTIMALE</div>
      <div class="eg-val">{_h(exec_data.get('solution_optimale',''))}</div>
    </div>
    <div class="eg-cell">
      <div class="eg-label">ACTION #1 — 48H</div>
      <div class="eg-val bold-navy">{_h(exec_data.get('action_48h',''))}</div>
    </div>
    <div class="eg-cell navy-bg">
      <div class="eg-label gold-lbl">IMPACT M+6</div>
      <div class="eg-val white-val">{_h(exec_data.get('impact_m6',''))}</div>
    </div>
  </div>

  <!-- Scores overview -->
  <div class="score-row">
    <div class="sc-block">
      <div class="sc-circle" style="border-color:{maturity_color}">
        <div class="sc-num">{global_score}</div>
        <div class="sc-den">/10</div>
      </div>
      <div class="sc-lbl">SCORE GLOBAL</div>
      <div class="sc-lvl" style="color:{maturity_color}">{maturity}</div>
    </div>

    <div class="flux-col">
      {_flux_bars(flux)}
    </div>

    <div class="sc-block">
      <div class="sc-circle gold-circle">
        <div class="sc-num">{proba}</div>
        <div class="sc-den">%</div>
      </div>
      <div class="sc-lbl">PROBABILITÉ SUCCÈS</div>
      <div class="sc-lvl">Maturité : {exec_data.get('score_maturite','?')}/10</div>
    </div>
  </div>
</div>

<!-- ══════════════════════════════════════════ -->
<!--  SÉPARATEUR 01 — DIAGNOSTIC                -->
<!-- ══════════════════════════════════════════ -->
{_sep('01','DIAGNOSTIC','Analyse stratégique — First Principles',
      'Analyse financière · 5 Pourquoi · Porter · SWOT · Coût inaction')}

<!-- ══════════════════════════════════════════ -->
<!--  QUICK WIN 48H                             -->
<!-- ══════════════════════════════════════════ -->
<div class="page">
  <div class="page-hdr"><span class="ph-l">DECISIO · MÉTHODE D3™</span><span class="ph-r">{_h(nom)} · {_h(secteur)}</span></div>
  <div class="sec-hdr gold-hdr">⚡ QUICK WIN — ACTION DANS LES 48H</div>

  <div class="qw-grid">
    <div class="qw-left">
      <div class="mini-hdr">ACTION PRIORITAIRE</div>
      <div class="qw-action">{_h(quick_win.get('action',''))}</div>
      <div class="mini-hdr mt10">POURQUOI ÇA MARCHE</div>
      <p class="body-p">{_h(quick_win.get('pourquoi',''))}</p>
      <div class="mini-hdr mt10">RÉSULTAT ATTENDU</div>
      <div class="result-pill">{_h(quick_win.get('resultat_attendu',''))}</div>
    </div>
    <div class="qw-right">
      <div class="mini-hdr">MESSAGE 1 — ACCROCHE</div>
      <div class="msg-box">{_h(quick_win.get('message_accroche',''))}</div>
      <div class="mini-hdr mt10">MESSAGE 2 — SUIVI</div>
      <div class="msg-box">{_h(quick_win.get('message_suivi',''))}</div>
      <div class="mini-hdr mt10">RELANCE 48H SANS RÉPONSE</div>
      <div class="msg-box relance">{_h(quick_win.get('relance_48h',''))}</div>
    </div>
  </div>

  <!-- PARTIE 1 — DIAGNOSTIC -->
  <div class="mini-hdr mt16">1.1 ANALYSE FINANCIÈRE</div>
  {_fin_table(diag.get('analyse_financiere',[]))}

  <div class="mini-hdr mt16">1.2 DÉCONSTRUCTION — 5 POURQUOI</div>
  {_cinq_pourquoi(diag)}

  <div class="verite">
    <div class="v-lbl">💡 VÉRITÉ FONDAMENTALE</div>
    <div class="v-txt">{_h(diag.get('verite_fondamentale',''))}</div>
  </div>

  <div class="mini-hdr mt16">1.3 PORTER'S FIVE FORCES</div>
  {_porter(diag.get('forces_porter',[]))}

  <div class="mini-hdr mt16">1.4 SWOT — CROISEMENTS STRATÉGIQUES</div>
  {_swot(diag.get('swot',{{}}))}

  <div class="mini-hdr mt16">1.5 COÛT DE L'INACTION</div>
  {_cout_inaction(diag.get('cout_inaction',[]))}
</div>

<!-- ══════════════════════════════════════════ -->
<!--  SÉPARATEUR 02 — DÉCISION                  -->
<!-- ══════════════════════════════════════════ -->
{_sep('02','DÉCISION','Options scorées — Recommandation stratégique',
      'VRIO · Ansoff · Options A/B/C · Risques · Seuils Stop/Pivot/Continue')}

<!-- ══════════════════════════════════════════ -->
<!--  PARTIE 2 — DÉCISION                       -->
<!-- ══════════════════════════════════════════ -->
<div class="page">
  <div class="page-hdr"><span class="ph-l">DECISIO · MÉTHODE D3™</span><span class="ph-r">{_h(nom)} · {_h(secteur)}</span></div>

  <div class="mini-hdr">2.1 ANALYSE VRIO — AVANTAGE CONCURRENTIEL</div>
  {_vrio(decision.get('analyse_vrio',[]), decision.get('conclusion_vrio',''))}

  <div class="mini-hdr mt16">2.2 OPTIONS SCORÉES</div>
  <div class="formula">Formule : (ROI × 0,4) + (Probabilité × 0,4) − (Difficulté × 0,2)</div>
  {_options(options)}

  <div class="rec-block">
    <div class="rb-lbl">🎯 RECOMMANDATION — "SI J'ÉTAIS À VOTRE PLACE"</div>
    <div class="rb-txt">{_h(decision.get('recommandation_finale',''))}</div>
    <div class="rb-action-lbl">PREMIÈRE PHRASE À DIRE DEMAIN MATIN :</div>
    <div class="rb-action">« {_h(decision.get('premiere_phrase_demain',''))} »</div>
  </div>

  <div class="danger-block">
    <div class="db-lbl">⚠️ OPTION DANGEREUSE — À ÉVITER ABSOLUMENT</div>
    <div class="db-txt">{_h(decision.get('option_dangereuse',''))}</div>
  </div>

  <div class="mini-hdr mt16">2.3 RISQUES À ANTICIPER</div>
  {_risks(decision.get('risques',[]))}

  <div class="mini-hdr mt16">2.4 SEUILS STOP / PIVOT / CONTINUE</div>
  {_seuils(decision.get('seuils',[]))}
</div>

<!-- ══════════════════════════════════════════ -->
<!--  SÉPARATEUR 03 — DÉPLOIEMENT               -->
<!-- ══════════════════════════════════════════ -->
{_sep('03','DÉPLOIEMENT','Plan d\'action immédiat et projections',
      'Plan Semaine 1 · Jalons M+1/M+3/M+6 · Projections · McKinsey 7S')}

<!-- ══════════════════════════════════════════ -->
<!--  PARTIE 3 — DÉPLOIEMENT                    -->
<!-- ══════════════════════════════════════════ -->
<div class="page">
  <div class="page-hdr"><span class="ph-l">DECISIO · MÉTHODE D3™</span><span class="ph-r">{_h(nom)} · {_h(secteur)}</span></div>

  <div class="mini-hdr">3.1 PLAN SEMAINE 1</div>
  {_plan_semaine(deploy.get('plan_semaine_1',[]),
                 deploy.get('budget_semaine_1',''),
                 deploy.get('roi_semaine_1',''))}

  <div class="mini-hdr mt16">3.2 JALONS M+1 → M+6</div>
  {_jalons(deploy.get('jalons',[]))}

  <div class="mini-hdr mt16">3.3 IMPACT FINANCIER PRÉVISIONNEL</div>
  {_projections(deploy.get('impact_financier',{{}}))}

  <div class="mini-hdr mt16">3.4 POSITIONNEMENT ET MESSAGE</div>
  {_positionnement(deploy.get('positionnement',{{}}))}

  <div class="mini-hdr mt16">3.5 McKINSEY 7S — DIAGNOSTIC INTERNE</div>
  {_7s(deploy.get('mckinsey_7s',[]),
       deploy.get('desalignement_prioritaire',''),
       deploy.get('note_globale_7s',''))}

  <div class="mini-hdr mt16">3.6 LES 3 RÈGLES NON NÉGOCIABLES</div>
  {_regles(deploy.get('regles_non_negociables',[]))}

  <div class="gold-rule"></div>
  <div class="mini-hdr">POUR ALLER PLUS LOIN</div>
  {_plus_loin(plus_loin)}
</div>

<!-- ══════════════════════════════════════════ -->
<!--  PAGE FINALE                               -->
<!-- ══════════════════════════════════════════ -->
<div class="final-page">
  <div class="fp-brand">DECISIO</div>
  <div class="fp-method">MÉTHODE D3™</div>
  <div class="fp-rule"></div>
  <div class="fp-tag">Chaque décision compte.</div>
  <div class="fp-sub">Ce rapport est la propriété exclusive de {_h(nom)}.</div>
  <div class="fp-contact">decisio.agency · contact@decisio.agency</div>
</div>

</body>
</html>"""


# ─────────────────────────────────────────
# CSS PREMIUM — CHROMIUM FULL SUPPORT
# ─────────────────────────────────────────

def _css() -> str:
    return """
/* ── RESET & BASE ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --navy:       #1A3A5C;
  --navy-l:     #2C5282;
  --navy-pale:  #EEF2F8;
  --gold:       #C9A84C;
  --gold-l:     #E8D49A;
  --gold-pale:  #FBF5E6;
  --dark:       #1C1C1C;
  --grey-d:     #4A4A4A;
  --grey-m:     #888888;
  --grey-l:     #F2F4F7;
  --grey-ln:    #D8DCE5;
  --red:        #C0392B;
  --green:      #1A7A4A;
  --white:      #FFFFFF;
}

body {
  font-family: 'DM Sans', sans-serif;
  font-size: 9pt;
  color: var(--dark);
  line-height: 1.55;
  background: #fff;
  -webkit-print-color-adjust: exact;
  print-color-adjust: exact;
}

/* ── PRINT PAGINATION ── */
@media print {
  .page-break { page-break-before: always; }
  .no-break   { page-break-inside: avoid; }
}

/* ── COVER ── */
.cover {
  display: flex;
  width: 210mm;
  height: 297mm;
  page-break-after: always;
  overflow: hidden;
}

.cover-left {
  width: 95mm;
  min-height: 297mm;
  background: var(--navy);
  padding: 28mm 10mm 14mm 14mm;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
}

.cover-left::before {
  content: '';
  position: absolute;
  inset: 0;
  background: repeating-linear-gradient(
    -45deg, transparent, transparent 30px,
    rgba(255,255,255,.025) 30px, rgba(255,255,255,.025) 31px
  );
}

.cl-brand {
  font-family: 'Playfair Display', serif;
  font-size: 40pt;
  font-weight: 900;
  color: #fff;
  letter-spacing: -1px;
  line-height: 1;
  position: relative;
}
.cl-method {
  font-size: 9pt;
  font-weight: 600;
  color: var(--gold);
  letter-spacing: 3px;
  text-transform: uppercase;
  margin-top: 5px;
  position: relative;
}
.cl-tag {
  font-size: 7pt;
  color: rgba(170,187,204,.8);
  letter-spacing: 1.2px;
  margin-top: 3px;
  position: relative;
}
.cl-rule {
  width: 60mm;
  height: 1px;
  background: var(--gold);
  margin: 14px 0;
  position: relative;
}
.cl-steps { flex: 1; position: relative; }
.cl-step {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  margin-bottom: 5px;
}
.sn {
  font-family: 'Playfair Display', serif;
  font-size: 18pt;
  font-weight: 700;
  color: var(--gold);
  line-height: 1;
  min-width: 30px;
}
.st { font-size: 9pt; font-weight: 700; color: #fff; letter-spacing: 1px; }
.ss { font-size: 7.5pt; color: rgba(170,187,204,.7); margin-top: 1px; }
.cl-dot {
  width: 1px;
  height: 12px;
  background: rgba(201,168,76,.3);
  margin-left: 14px;
  margin-bottom: 4px;
}
.cl-website {
  font-size: 7pt;
  color: rgba(122,154,188,.7);
  position: relative;
}

.cover-right {
  flex: 1;
  background: #fff;
  padding: 22mm 14mm 14mm 18mm;
  display: flex;
  flex-direction: column;
}

.cr-badge {
  background: var(--grey-l);
  border-left: 4px solid var(--navy);
  padding: 10px 14px;
  margin-bottom: 22px;
}
.cr-badge-title {
  font-size: 8.5pt;
  font-weight: 700;
  color: var(--navy);
  letter-spacing: 2px;
  text-transform: uppercase;
}
.cr-badge-price {
  font-family: 'Playfair Display', serif;
  font-size: 22pt;
  font-weight: 700;
  color: var(--gold);
  line-height: 1.2;
}
.cr-badge-sub { font-size: 7.5pt; color: var(--grey-d); }

.cr-name {
  font-family: 'Playfair Display', serif;
  font-size: 26pt;
  font-weight: 700;
  color: var(--dark);
  line-height: 1.1;
}
.cr-underline {
  width: 44mm;
  height: 2px;
  background: var(--gold);
  margin: 6px 0;
}
.cr-sector { font-size: 13pt; font-weight: 500; color: var(--grey-d); }
.cr-date   { font-size: 9pt;  color: var(--grey-m); margin-top: 4px; }
.cr-divider {
  width: 100%;
  height: 1px;
  background: var(--grey-ln);
  margin: 18px 0;
}
.cr-conf {
  font-size: 7pt;
  color: var(--grey-d);
  line-height: 1.5;
  background: var(--grey-l);
  padding: 10px 12px;
  border-left: 2px solid var(--grey-ln);
}

/* ── PAGE WRAPPER ── */
.page {
  padding: 0;
  page-break-before: always;
}
.page:first-of-type { page-break-before: auto; }

/* ── PAGE HEADER ── */
.page-hdr {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1.5px solid var(--navy);
  padding-bottom: 4px;
  margin-bottom: 12px;
  font-size: 7pt;
}
.ph-l { font-weight: 700; color: var(--navy); }
.ph-r { color: var(--grey-d); }

/* ── SECTION HEADERS ── */
.sec-hdr {
  background: var(--navy);
  color: #fff;
  font-size: 10pt;
  font-weight: 700;
  padding: 7px 12px 7px 16px;
  margin: 0 0 12px;
  border-left: 4px solid var(--gold);
  letter-spacing: .5px;
}
.gold-hdr { background: var(--gold); color: var(--navy); border-left-color: var(--navy); }

.mini-hdr {
  background: var(--navy-pale);
  border-left: 3px solid var(--navy);
  color: var(--navy);
  font-size: 8.5pt;
  font-weight: 700;
  padding: 5px 10px 5px 12px;
  margin: 0 0 8px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.mini-hdr::before {
  content: '';
  display: inline-block;
  width: 6px;
  height: 6px;
  background: var(--gold);
  border-radius: 1px;
  flex-shrink: 0;
}
.mt10 { margin-top: 10px; }
.mt16 { margin-top: 16px; }

/* ── KEY INSIGHT ── */
.insight-box {
  background: var(--navy);
  border-left: 5px solid var(--gold);
  padding: 14px 16px;
  margin-bottom: 14px;
}
.ib-label {
  font-size: 7pt;
  font-weight: 700;
  color: var(--gold);
  letter-spacing: 2px;
  text-transform: uppercase;
  margin-bottom: 6px;
}
.ib-text {
  font-size: 10.5pt;
  font-weight: 600;
  color: #fff;
  line-height: 1.5;
}

/* ── TWO COL ── */
.two-col {
  display: flex;
  gap: 10px;
  margin-bottom: 12px;
}
.two-col > * { flex: 1; }

.exec-card {
  background: var(--grey-l);
  padding: 10px 12px;
}
.navy-bl { border-left: 4px solid var(--navy); }
.gold-bl  { border-left: 4px solid var(--gold); }

.ec-label {
  font-size: 6.5pt;
  font-weight: 700;
  color: var(--grey-m);
  letter-spacing: 1.5px;
  text-transform: uppercase;
  margin-bottom: 4px;
}
.ec-val { font-size: 8.5pt; line-height: 1.45; }

/* ── EXEC GRID ── */
.exec-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin-bottom: 14px;
}
.eg-cell {
  background: var(--grey-l);
  padding: 10px 12px;
  border-left: 3px solid var(--grey-ln);
}
.eg-cell.gold-bl  { border-left-color: var(--gold); }
.eg-cell.navy-bg  { background: var(--navy); border-left-color: var(--gold); }

.eg-label {
  font-size: 6.5pt;
  font-weight: 700;
  color: var(--grey-m);
  letter-spacing: 1.5px;
  text-transform: uppercase;
  margin-bottom: 4px;
}
.gold-lbl   { color: var(--gold) !important; }
.eg-val     { font-size: 8.5pt; }
.bold-navy  { font-weight: 700; color: var(--navy); }
.white-val  { color: #fff; font-weight: 600; font-size: 9.5pt; }

/* ── SCORE ROW ── */
.score-row {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  background: var(--grey-l);
  padding: 14px;
  margin-bottom: 12px;
}
.sc-block { text-align: center; min-width: 80px; }
.sc-circle {
  width: 66px;
  height: 66px;
  border-radius: 50%;
  border: 4px solid var(--navy);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  margin: 0 auto 6px;
  background: #fff;
}
.gold-circle { border-color: var(--gold); }
.sc-num {
  font-family: 'Playfair Display', serif;
  font-size: 18pt;
  font-weight: 700;
  color: var(--navy);
  line-height: 1;
}
.sc-den   { font-size: 7pt; color: var(--grey-m); }
.sc-lbl   { font-size: 6.5pt; font-weight: 700; letter-spacing: 1px; color: var(--grey-m); text-transform: uppercase; }
.sc-lvl   { font-size: 7.5pt; font-weight: 600; margin-top: 2px; color: var(--navy); }

.flux-col { flex: 1; }
.fb-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}
.fb-lbl   { width: 90px; font-size: 7.5pt; color: var(--grey-d); font-weight: 500; }
.fb-track {
  flex: 1;
  height: 10px;
  background: var(--grey-ln);
  border-radius: 5px;
  overflow: hidden;
}
.fb-fill  { height: 100%; background: var(--gold); border-radius: 5px; }
.fb-score { width: 30px; font-size: 7.5pt; font-weight: 700; color: var(--navy); text-align: right; }

/* ── SEPARATOR PAGE ── */
.sep-page {
  width: 210mm;
  min-height: 297mm;
  background: var(--navy);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  page-break-before: always;
  page-break-after: always;
  text-align: center;
}
.sep-page::before {
  content: '';
  position: absolute;
  inset: 0;
  background: repeating-linear-gradient(
    -45deg, transparent, transparent 42px,
    rgba(255,255,255,.018) 42px, rgba(255,255,255,.018) 43px
  );
}
.sep-bg-num {
  position: absolute;
  font-family: 'Playfair Display', serif;
  font-size: 260pt;
  font-weight: 900;
  color: rgba(255,255,255,.04);
  letter-spacing: -20px;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -52%);
  white-space: nowrap;
  user-select: none;
}
.sep-inner  { position: relative; z-index: 2; }
.sep-gold-l { width: 80px; height: 2px; background: var(--gold); margin: 0 auto 20px; }
.sep-num    {
  font-family: 'Playfair Display', serif;
  font-size: 72pt;
  font-weight: 900;
  color: var(--gold);
  line-height: 1;
  margin-bottom: 10px;
}
.sep-title  { font-size: 28pt; font-weight: 700; color: #fff; letter-spacing: 4px; text-transform: uppercase; }
.sep-sub    { font-size: 12pt; color: var(--gold-l); margin-top: 8px; font-weight: 300; }
.sep-desc   { font-size: 8pt; color: rgba(170,187,204,.7); margin-top: 8px; letter-spacing: 1px; }
.sep-foot   {
  position: absolute;
  bottom: 14mm;
  font-size: 7pt;
  color: var(--gold);
  font-weight: 600;
  letter-spacing: 2px;
}

/* ── QUICK WIN ── */
.qw-grid { display: flex; gap: 12px; margin-bottom: 14px; }
.qw-left  { flex: 1; }
.qw-right { flex: 1; }

.qw-action {
  font-size: 10pt;
  font-weight: 700;
  color: var(--navy);
  background: var(--gold-pale);
  border-left: 4px solid var(--gold);
  padding: 10px 12px;
  margin-bottom: 8px;
}
.result-pill {
  display: inline-block;
  background: var(--green);
  color: #fff;
  font-size: 7.5pt;
  font-weight: 600;
  padding: 4px 12px;
  border-radius: 20px;
}
.msg-box {
  background: var(--navy-pale);
  border-left: 3px solid var(--navy);
  padding: 8px 10px;
  font-size: 8pt;
  line-height: 1.45;
  color: var(--dark);
  margin-bottom: 4px;
  font-style: italic;
}
.msg-box.relance { border-left-color: var(--gold); background: var(--gold-pale); }

/* ── TABLES ── */
table { width: 100%; border-collapse: collapse; margin-bottom: 10px; font-size: 7.5pt; }
thead tr { background: var(--navy); color: #fff; }
thead th { padding: 6px 8px; text-align: left; font-weight: 700; font-size: 7pt; letter-spacing: .5px; }
tbody tr:nth-child(odd)  { background: #fff; }
tbody tr:nth-child(even) { background: var(--grey-l); }
tbody td { padding: 5px 8px; vertical-align: top; border-bottom: 1px solid var(--grey-ln); }
tbody tr:first-child td  { border-top: 2px solid var(--navy); }
.td-b  { font-weight: 700; color: var(--navy); }
.td-c  { text-align: center; }

/* ── 5 POURQUOI ── */
.pq-row {
  display: flex;
  gap: 8px;
  padding: 6px 10px;
  border-left: 3px solid var(--grey-ln);
  margin-bottom: 4px;
  background: var(--grey-l);
}
.pq-n { font-size: 7pt; font-weight: 700; color: var(--gold); min-width: 65px; }
.pq-t { font-size: 8pt; line-height: 1.4; }

/* ── VÉRITÉ FONDAMENTALE ── */
.verite {
  background: var(--navy);
  padding: 12px 16px;
  margin: 10px 0;
}
.v-lbl { font-size: 7pt; font-weight: 700; color: var(--gold); letter-spacing: 2px; margin-bottom: 5px; }
.v-txt { font-size: 10pt; font-weight: 600; color: #fff; font-style: italic; line-height: 1.5; }

/* ── SWOT ── */
.swot { width: 100%; border-collapse: collapse; margin-bottom: 10px; }
.swot td { width: 50%; padding: 10px 12px; vertical-align: top; font-size: 8pt; border: 1px solid var(--grey-ln); }
.swot .sh { background: var(--navy); color: #fff; font-weight: 700; text-align: center; font-size: 8pt; letter-spacing: 1px; }
.swot .so { background: #EBF5EB; }
.swot .st { background: #FFF3E0; }
.swot .wo { background: #E8F0FB; }
.swot .wt { background: #FDECEA; }

/* ── OPTIONS ── */
.formula { font-size: 7.5pt; color: var(--grey-m); font-style: italic; margin-bottom: 8px; padding: 4px 8px; background: var(--grey-l); border-left: 2px solid var(--grey-ln); }

.opt-bar {
  background: var(--grey-l);
  border: 1px solid var(--grey-ln);
  padding: 10px 12px;
  margin-bottom: 6px;
  position: relative;
}
.opt-rec {
  background: var(--gold-pale);
  border: 2px solid var(--gold);
}
.opt-badge {
  position: absolute;
  top: 8px; right: 8px;
  background: var(--gold);
  color: var(--navy);
  font-size: 6.5pt;
  font-weight: 700;
  padding: 2px 8px;
  letter-spacing: 1px;
}
.opt-hdr  { display: flex; align-items: center; gap: 10px; margin-bottom: 6px; }
.opt-let  { font-family: 'Playfair Display', serif; font-size: 18pt; font-weight: 700; color: var(--navy); line-height: 1; }
.opt-name { font-size: 9.5pt; font-weight: 700; color: var(--navy); }
.opt-desc { font-size: 7.5pt; color: #888; }
.opt-track { height: 12px; background: var(--grey-ln); border-radius: 6px; overflow: hidden; margin: 4px 0; }
.opt-fill  { height: 100%; border-radius: 6px; background: var(--navy); }
.opt-fill.rec { background: var(--gold); }
.opt-metrics { display: flex; gap: 20px; margin-top: 5px; }
.met { font-size: 7pt; color: var(--grey-m); }
.met strong { color: var(--navy); }

/* ── RECOMMENDATION ── */
.rec-block { background: var(--navy); padding: 14px 16px; margin: 12px 0; }
.rb-lbl { font-size: 7pt; font-weight: 700; color: var(--gold); letter-spacing: 2px; margin-bottom: 6px; }
.rb-txt { font-size: 9pt; color: #fff; line-height: 1.5; margin-bottom: 8px; }
.rb-action-lbl { font-size: 6.5pt; font-weight: 700; color: var(--gold); letter-spacing: 1px; text-transform: uppercase; margin-bottom: 4px; }
.rb-action { font-size: 9.5pt; font-weight: 600; color: #fff; font-style: italic; }

/* ── DANGER ── */
.danger-block { background: #FFF5F5; border-left: 4px solid var(--red); padding: 10px 12px; margin: 8px 0; }
.db-lbl { font-size: 7pt; font-weight: 700; color: var(--red); letter-spacing: 1.5px; margin-bottom: 4px; }
.db-txt { font-size: 8.5pt; line-height: 1.45; }

/* ── PROJECTIONS ── */
.proj-row { display: flex; gap: 10px; margin-bottom: 10px; }
.proj-card { flex: 1; background: var(--grey-l); padding: 10px 12px; text-align: center; border-top: 3px solid var(--navy); }
.pp { font-size: 7pt; font-weight: 700; color: var(--grey-m); text-transform: uppercase; letter-spacing: 1px; margin-bottom: 4px; }
.pt { font-size: 8pt; color: var(--grey-d); }
.pa { font-size: 10pt; color: var(--gold); margin: 3px 0; }
.pv { font-size: 12pt; font-weight: 700; color: var(--navy); }
.pg { font-size: 8pt; font-weight: 600; color: var(--green); }

/* ── RÈGLES ── */
.regle {
  display: flex;
  gap: 12px;
  background: var(--grey-l);
  padding: 10px 12px;
  margin-bottom: 6px;
  border-left: 3px solid var(--navy);
}
.rg-badge {
  width: 28px; height: 28px; min-width: 28px;
  background: var(--gold);
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: 10pt; color: var(--navy);
}
.rg-title { font-size: 9pt; font-weight: 700; color: var(--navy); margin-bottom: 3px; }
.rg-body  { font-size: 8pt; line-height: 1.4; }
.rg-cons  { font-size: 7.5pt; color: var(--red); font-style: italic; margin-top: 3px; }

/* ── GOLD RULE ── */
.gold-rule {
  height: 2px;
  background: linear-gradient(to right, var(--navy), var(--gold), var(--navy));
  margin: 20px 0 12px;
}

/* ── BODY TEXT ── */
p.body-p { font-size: 8.5pt; line-height: 1.5; margin-bottom: 6px; }

/* ── FINAL PAGE ── */
.final-page {
  width: 210mm;
  min-height: 297mm;
  background: var(--navy);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  page-break-before: always;
}
.fp-brand {
  font-family: 'Playfair Display', serif;
  font-size: 52pt; font-weight: 900;
  color: #fff; letter-spacing: -2px;
}
.fp-method { font-size: 10pt; font-weight: 600; color: var(--gold); letter-spacing: 4px; text-transform: uppercase; margin-top: 6px; }
.fp-rule   { width: 60px; height: 2px; background: var(--gold); margin: 20px auto; }
.fp-tag    { font-size: 16pt; color: #fff; font-style: italic; }
.fp-sub    { font-size: 9pt; color: rgba(170,187,204,.6); margin-top: 8px; }
.fp-contact{ font-size: 8pt; color: var(--gold); margin-top: 20px; letter-spacing: 1px; }
"""


# ─────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────

def _h(v) -> str:
    """Escape HTML — sécurité XSS + gestion None/dict/list."""
    if v is None: return ''
    if isinstance(v, (dict, list)): v = str(v)
    return (str(v)
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;'))


def _sep(num, title, sub, desc) -> str:
    return f"""<div class="sep-page">
  <div class="sep-bg-num">{num}</div>
  <div class="sep-inner">
    <div class="sep-gold-l"></div>
    <div class="sep-num">{num}</div>
    <div class="sep-title">{title}</div>
    <div class="sep-sub">{sub}</div>
    <div class="sep-desc">{desc}</div>
  </div>
  <div class="sep-foot">DECISIO AGENCY · MÉTHODE D3™ · CONFIDENTIEL</div>
</div>"""


def _flux_bars(flux: dict) -> str:
    items = [('argent','Flux Argent'),('temps','Flux Temps'),
             ('decisions','Flux Décisions'),('clients','Flux Clients')]
    out = ''
    for k, lbl in items:
        s = flux.get(k, 5.0)
        try: s = float(s)
        except: s = 5.0
        pct = min(s * 10, 100)
        out += f"""<div class="fb-row">
  <div class="fb-lbl">{lbl}</div>
  <div class="fb-track"><div class="fb-fill" style="width:{pct}%"></div></div>
  <div class="fb-score">{s}/10</div>
</div>"""
    return out


def _fin_table(rows: list) -> str:
    if not rows: return '<p class="body-p">Données non disponibles.</p>'
    h = '<table><thead><tr><th>Indicateur</th><th>Valeur</th><th>Interprétation</th></tr></thead><tbody>'
    for r in rows:
        h += f'<tr><td class="td-b">{_h(r.get("indicateur",""))}</td><td class="td-c">{_h(r.get("valeur",""))}</td><td>{_h(r.get("interpretation",""))}</td></tr>'
    return h + '</tbody></table>'


def _cinq_pourquoi(diag: dict) -> str:
    pqs = diag.get('cinq_pourquoi', [])
    if not pqs: return ''
    out = ''
    for i, p in enumerate(pqs[:5]):
        out += f"""<div class="pq-row">
  <div class="pq-n">POURQUOI {i+1}</div>
  <div class="pq-t"><strong>Q :</strong> {_h(p.get('question',''))}<br><strong>R :</strong> {_h(p.get('reponse',''))}</div>
</div>"""
    return out


def _porter(forces: list) -> str:
    if not forces: return ''
    h = '<table><thead><tr><th>Force</th><th>Intensité</th><th>Impact</th><th>Levier</th></tr></thead><tbody>'
    for f in forces:
        n = int(f.get('intensite', 3))
        stars = '●' * n + '○' * (5 - n)
        h += f'<tr><td class="td-b">{_h(f.get("force",""))}</td><td class="td-c">{stars} {n}/5</td><td>{_h(f.get("impact",""))}</td><td>{_h(f.get("levier",""))}</td></tr>'
    return h + '</tbody></table>'


def _swot(s: dict) -> str:
    if not s: return ''
    return f"""<table class="swot">
<tr>
  <td class="sh" style="background:var(--navy)"></td>
  <td class="sh">Opportunités (O)</td>
  <td class="sh">Menaces (T)</td>
</tr>
<tr>
  <td class="sh" style="background:var(--navy-l)">Forces (S)</td>
  <td class="so">{_h(s.get('so',''))}</td>
  <td class="st">{_h(s.get('st',''))}</td>
</tr>
<tr>
  <td class="sh" style="background:var(--navy-l)">Faiblesses (W)</td>
  <td class="wo">{_h(s.get('wo',''))}</td>
  <td class="wt">{_h(s.get('wt',''))}</td>
</tr>
</table>
<p class="body-p"><strong>Quadrant prioritaire :</strong> {_h(s.get('quadrant_prioritaire',''))}</p>"""


def _cout_inaction(rows: list) -> str:
    if not rows: return ''
    h = '<table><thead><tr><th>Période</th><th>Manque à gagner</th><th>Cumulé</th><th>Risque</th></tr></thead><tbody>'
    for r in rows:
        try: m = f"{int(r.get('manque',0)):,}€".replace(',',' ')
        except: m = str(r.get('manque',''))
        try: c = f"{int(r.get('cumule',0)):,}€".replace(',',' ')
        except: c = str(r.get('cumule',''))
        h += f'<tr><td class="td-b">{_h(r.get("periode",""))}</td><td class="td-c" style="color:var(--red);font-weight:700">{m}</td><td class="td-c" style="color:var(--red)">{c}</td><td>{_h(r.get("risque",""))}</td></tr>'
    return h + '</tbody></table>'


def _vrio(vrio: list, conclusion: str) -> str:
    if not vrio: return f'<p class="body-p">{_h(conclusion)}</p>'
    def yn(v): return '✓' if v else '✗'
    h = '<table><thead><tr><th>Ressource</th><th>Valeur</th><th>Rare</th><th>Inimitable</th><th>Organisé</th><th>Avantage</th></tr></thead><tbody>'
    for r in vrio:
        h += f'<tr><td class="td-b">{_h(r.get("ressource",""))}</td><td class="td-c">{yn(r.get("valeur"))}</td><td class="td-c">{yn(r.get("rare"))}</td><td class="td-c">{yn(r.get("inimitable"))}</td><td class="td-c">{yn(r.get("organise"))}</td><td>{_h(r.get("avantage",""))}</td></tr>'
    h += '</tbody></table>'
    if conclusion: h += f'<p class="body-p"><strong>Conclusion VRIO :</strong> {_h(conclusion)}</p>'
    return h


def _options(opts: list) -> str:
    out = ''
    for opt in opts:
        rec  = opt.get('est_recommande', False)
        sc   = opt.get('score_calcule', opt.get('score', 5.0))
        try: sc = float(sc)
        except: sc = 5.0
        pct = min(sc * 10, 100)
        out += f"""<div class="opt-bar {'opt-rec' if rec else ''}">
  {'<div class="opt-badge">★ RECOMMANDÉ</div>' if rec else ''}
  <div class="opt-hdr">
    <div class="opt-let">{_h(opt.get('lettre',''))}</div>
    <div>
      <div class="opt-name">{_h(opt.get('nom',''))}</div>
      <div class="opt-desc">{_h(opt.get('description',''))}</div>
    </div>
  </div>
  <div class="opt-track"><div class="opt-fill {'rec' if rec else ''}" style="width:{pct}%"></div></div>
  <div class="opt-metrics">
    <span class="met">ROI <strong>{opt.get('roi','?')}/10</strong></span>
    <span class="met">Probabilité <strong>{opt.get('probabilite','?')}/10</strong></span>
    <span class="met">Difficulté <strong>{opt.get('difficulte','?')}/10</strong></span>
    <span class="met">Score <strong>{sc}/10</strong></span>
  </div>
</div>"""
    return out


def _risks(risks: list) -> str:
    if not risks: return ''
    h = '<table><thead><tr><th>Type</th><th>Description</th><th>Probabilité</th><th>Solution</th></tr></thead><tbody>'
    for r in risks:
        h += f'<tr><td class="td-b">{_h(r.get("type",""))}</td><td>{_h(r.get("description",""))}</td><td class="td-c">{_h(r.get("probabilite",""))}</td><td>{_h(r.get("solution",""))}</td></tr>'
    return h + '</tbody></table>'


def _seuils(seuils: list) -> str:
    if not seuils: return ''
    colors = {'Stop':'var(--red)','Pivot':'#E67E22','Continue':'var(--green)'}
    h = '<table><thead><tr><th>Signal</th><th>Indicateur</th><th>Délai</th><th>Action</th></tr></thead><tbody>'
    for s in seuils:
        sig = s.get('signal','')
        col = colors.get(sig, '#888')
        h += f'<tr><td style="font-weight:700;color:{col}">{_h(sig)}</td><td>{_h(s.get("indicateur",""))}</td><td class="td-c">{s.get("delai_semaines","?")} sem.</td><td>{_h(s.get("action",""))}</td></tr>'
    return h + '</tbody></table>'


def _plan_semaine(plan: list, budget: str, roi: str) -> str:
    if not plan: return ''
    h = '<table><thead><tr><th>Jour</th><th>Action</th><th>Coût</th><th>Temps</th><th>Résultat</th></tr></thead><tbody>'
    for r in plan:
        h += f'<tr><td class="td-b">{_h(r.get("jour",""))}</td><td>{_h(r.get("action",""))}</td><td class="td-c">{r.get("cout_eur",0)}€</td><td class="td-c">{r.get("temps_h",0)}h</td><td>{_h(r.get("resultat",""))}</td></tr>'
    h += '</tbody></table>'
    if budget: h += f'<p class="body-p"><strong>Budget :</strong> {_h(budget)}</p>'
    if roi:    h += f'<p class="body-p"><strong>ROI attendu :</strong> {_h(roi)}</p>'
    return h


def _jalons(jalons: list) -> str:
    if not jalons: return ''
    h = '<table><thead><tr><th>Période</th><th>Focus</th><th>Action</th><th>Source</th><th>KPI</th></tr></thead><tbody>'
    for j in jalons:
        h += f'<tr><td class="td-b">{_h(j.get("periode",""))}</td><td>{_h(j.get("focus",""))}</td><td>{_h(j.get("action",""))}</td><td>{_h(j.get("source_prospects",""))}</td><td style="font-weight:600;color:var(--navy)">{_h(j.get("kpi",""))}</td></tr>'
    return h + '</tbody></table>'


def _projections(impact: dict) -> str:
    if not impact: return ''
    calcul  = impact.get('calcul','')
    hypos   = impact.get('hypotheses',[])
    projs   = impact.get('projections',[])
    out = ''
    if calcul: out += f'<p class="body-p"><strong>Calcul :</strong> {_h(calcul)}</p>'
    if hypos:  out += '<p class="body-p"><strong>Hypothèses :</strong> ' + ' · '.join(_h(x) for x in hypos) + '</p>'
    if projs:
        out += '<div class="proj-row">'
        for p in projs:
            try: tf = f"{int(p.get('aujourd_hui',0)):,}€".replace(',',' ')
            except: tf = str(p.get('aujourd_hui',''))
            try: pf = f"{int(p.get('projection',0)):,}€".replace(',',' ')
            except: pf = str(p.get('projection',''))
            try: gf = f"+{int(p.get('gain',0)):,}€".replace(',',' ')
            except: gf = str(p.get('gain',''))
            out += f"""<div class="proj-card">
  <div class="pp">{_h(p.get('periode',''))}</div>
  <div class="pt">{tf}</div>
  <div class="pa">→</div>
  <div class="pv">{pf}</div>
  <div class="pg">{gf}</div>
</div>"""
        out += '</div>'
    return out


def _positionnement(pos: dict) -> str:
    if not pos: return ''
    out = ''
    slogan = pos.get('slogan','')
    msgs   = pos.get('messages',[])
    canal  = pos.get('canal_prioritaire','')
    if slogan:
        out += f'<div style="background:var(--navy);color:#fff;padding:12px 16px;font-size:11pt;font-weight:700;font-style:italic;margin-bottom:10px;border-left:4px solid var(--gold)">&ldquo;{_h(slogan)}&rdquo;</div>'
    if msgs:
        out += '<table><thead><tr><th>Thème</th><th>Message clé</th></tr></thead><tbody>'
        for m in msgs:
            out += f'<tr><td class="td-b">{_h(m.get("theme",""))}</td><td>{_h(m.get("texte",""))}</td></tr>'
        out += '</tbody></table>'
    if canal: out += f'<p class="body-p"><strong>Canal prioritaire :</strong> {_h(canal)}</p>'
    return out


def _7s(s7: list, des: str, note: str) -> str:
    if not s7: return ''
    h = '<table><thead><tr><th>Élément 7S</th><th>Situation actuelle</th><th>Note /5</th><th>Désalignement</th></tr></thead><tbody>'
    for r in s7:
        nv = int(r.get('note', 3))
        stars = '●' * nv + '○' * (5 - nv)
        h += f'<tr><td class="td-b">{_h(r.get("element",""))}</td><td>{_h(r.get("situation",""))}</td><td class="td-c">{stars}</td><td>{_h(r.get("desalignement",""))}</td></tr>'
    h += '</tbody></table>'
    if des:  h += f'<p class="body-p"><strong>Désalignement prioritaire :</strong> {_h(des)}</p>'
    if note: h += f'<p class="body-p"><strong>Note globale 7S :</strong> {_h(note)}/35</p>'
    return h


def _regles(regles: list) -> str:
    out = ''
    for r in regles:
        out += f"""<div class="regle">
  <div class="rg-badge">{r.get('numero','?')}</div>
  <div>
    <div class="rg-title">{_h(r.get('regle',''))}</div>
    <div class="rg-body"><strong>Obstacle :</strong> {_h(r.get('obstacle',''))} · <strong>Solution :</strong> {_h(r.get('solution',''))}</div>
    <div class="rg-cons">Si non respectée : {_h(r.get('consequence',''))}</div>
  </div>
</div>"""
    return out


def _plus_loin(data: dict) -> str:
    if not data: return ''
    base = data.get('base_diagnostique','')
    mans = data.get('donnees_manquantes',[])
    act  = data.get('action_suivi','')
    out  = ''
    if base: out += f'<p class="body-p"><strong>Ce diagnostic est fondé sur :</strong> {_h(base)}</p>'
    if mans:
        out += '<table><thead><tr><th>Donnée manquante</th><th>Ce que ça permettrait</th></tr></thead><tbody>'
        for m in mans:
            out += f'<tr><td class="td-b">{_h(m.get("donnee",""))}</td><td>{_h(m.get("apport",""))}</td></tr>'
        out += '</tbody></table>'
    if act: out += f'<div style="background:var(--gold-pale);border-left:4px solid var(--gold);padding:10px 12px;margin-top:8px"><strong>Action recommandée :</strong> {_h(act)}</div>'
    return out
