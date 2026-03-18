"""
DECISIO — Scoring automatique
Calcule les scores des 4 flux + score global à partir de l'analyse.
"""


def calculate_scores(analysis: dict) -> dict:
    """
    Calcule les scores automatiquement à partir de l'analyse D3™.
    Retourne un dict avec scores par flux + score global + niveau de maturité.
    """
    scores = {}

    # ── Extraction des données disponibles ──

    exec_data = analysis.get('synthese_executive', {})
    diag = analysis.get('diagnostic', {})
    decision = analysis.get('decision', {})
    deploy = analysis.get('deploiement', {})

    # ── Score de maturité global (depuis Claude) ──
    maturite_brut = exec_data.get('score_maturite', 5.0)
    try:
        maturite = float(maturite_brut)
    except (ValueError, TypeError):
        maturite = 5.0

    # ── Score probabilité de succès ──
    proba = exec_data.get('probabilite_succes', 50)
    try:
        proba = int(proba)
    except (ValueError, TypeError):
        proba = 50

    # ── Scores des options (meilleure option) ──
    options = decision.get('options', [])
    best_option_score = 0.0
    best_option = None
    for opt in options:
        s = opt.get('score', 0)
        try:
            s = float(s)
        except (ValueError, TypeError):
            s = 0.0
        if s > best_option_score:
            best_option_score = s
            best_option = opt

    # ── Calcul scores 4 flux (algorithme heuristique) ──

    # Flux Argent : basé sur marge nette et projections
    flux_argent = _score_argent(analysis)

    # Flux Temps : basé sur plan semaine 1 et complexité
    flux_temps = _score_temps(analysis)

    # Flux Décisions : basé sur clarté des options et score probabilité
    flux_decisions = _score_decisions(analysis, proba)

    # Flux Clients : basé sur positionnement et acquisition
    flux_clients = _score_clients(analysis)

    # ── Score global pondéré ──
    global_score = round(
        flux_argent * 0.35 +
        flux_temps * 0.25 +
        flux_decisions * 0.20 +
        flux_clients * 0.20,
        1
    )

    # ── Niveau de maturité ──
    if global_score >= 8.0:
        maturity_level = "Optimisé"
        maturity_color = "#1A7A4A"
    elif global_score >= 6.0:
        maturity_level = "En développement"
        maturity_color = "#C9A84C"
    elif global_score >= 4.0:
        maturity_level = "Fragile"
        maturity_color = "#E67E22"
    else:
        maturity_level = "Critique"
        maturity_color = "#C0392B"

    # ── Flux prioritaire (le plus faible) ──
    flux_map = {
        "Flux Argent": flux_argent,
        "Flux Temps": flux_temps,
        "Flux Décisions": flux_decisions,
        "Flux Clients": flux_clients
    }
    prioritaire = min(flux_map, key=flux_map.get)

    # ── Scores options A/B/C enrichis ──
    options_scored = []
    for opt in options:
        roi = opt.get('roi', 5)
        prob = opt.get('probabilite', 5)
        diff = opt.get('difficulte', 5)
        try:
            score = round((int(roi) * 0.4) + (int(prob) * 0.4) - (int(diff) * 0.2), 2)
        except (ValueError, TypeError):
            score = opt.get('score', 5.0)

        options_scored.append({
            **opt,
            "score_calcule": score,
            "est_recommande": opt.get('est_recommande', False)
        })

    return {
        "global_score": global_score,
        "maturity_level": maturity_level,
        "maturity_color": maturity_color,
        "probabilite_succes": proba,
        "flux": {
            "argent": flux_argent,
            "temps": flux_temps,
            "decisions": flux_decisions,
            "clients": flux_clients
        },
        "flux_prioritaire": prioritaire,
        "options_scored": options_scored,
        "best_option": best_option,
        "score_maturite_claude": maturite
    }


def _score_argent(analysis: dict) -> float:
    """Score du flux argent basé sur les données financières."""
    diag = analysis.get('diagnostic', {})
    deploy = analysis.get('deploiement', {})

    score = 5.0  # base

    # Analyse financière disponible ?
    fin = diag.get('analyse_financiere', [])
    if len(fin) >= 3:
        score += 0.5  # Données riches = meilleur diagnostic

    # Projections disponibles ?
    projections = deploy.get('impact_financier', {}).get('projections', [])
    if projections:
        # Vérifier le gain M+6
        for p in projections:
            if 'M+6' in str(p.get('periode', '')):
                gain = p.get('gain', 0)
                try:
                    gain = int(gain)
                    if gain > 2000:
                        score += 2.0
                    elif gain > 1000:
                        score += 1.0
                except (ValueError, TypeError):
                    pass

    # Coût de l'inaction calculé ?
    cout_inaction = diag.get('cout_inaction', [])
    if cout_inaction:
        score += 0.5

    return min(round(score, 1), 10.0)


def _score_temps(analysis: dict) -> float:
    """Score du flux temps basé sur le plan d'action."""
    deploy = analysis.get('deploiement', {})
    score = 5.0

    # Plan semaine 1 détaillé ?
    plan = deploy.get('plan_semaine_1', [])
    if len(plan) >= 5:
        score += 1.5
    elif len(plan) >= 3:
        score += 0.5

    # Jalons définis ?
    jalons = deploy.get('jalons', [])
    if len(jalons) >= 3:
        score += 1.0

    # KPI défini ?
    kpi = deploy.get('kpi_unique', '')
    if kpi and len(kpi) > 10:
        score += 1.0

    return min(round(score, 1), 10.0)


def _score_decisions(analysis: dict, proba: int) -> float:
    """Score du flux décisions basé sur la clarté des options."""
    decision = analysis.get('decision', {})
    score = 4.0

    # Probabilité de succès
    score += (proba / 100) * 3.0

    # Options scorées ?
    options = decision.get('options', [])
    if len(options) >= 3:
        score += 1.5
    elif len(options) >= 1:
        score += 0.5

    # Seuils Stop/Pivot/Continue définis ?
    seuils = decision.get('seuils', [])
    if seuils:
        score += 0.5

    return min(round(score, 1), 10.0)


def _score_clients(analysis: dict) -> float:
    """Score du flux clients basé sur positionnement et acquisition."""
    deploy = analysis.get('deploiement', {})
    score = 4.5

    # Positionnement défini ?
    pos = deploy.get('positionnement', {})
    if pos.get('slogan'):
        score += 0.5
    if len(pos.get('messages', [])) >= 2:
        score += 0.5
    if pos.get('canal_prioritaire'):
        score += 0.5

    # Quick win avec message défini ?
    qw = analysis.get('quick_win', {})
    if qw.get('message_accroche') and len(qw.get('message_accroche', '')) > 20:
        score += 1.5

    # McKinsey 7S ?
    s7 = deploy.get('mckinsey_7s', [])
    if s7:
        score += 0.5

    return min(round(score, 1), 10.0)
