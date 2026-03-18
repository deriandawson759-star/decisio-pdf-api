"""
DECISIO — AI Analyzer
Appelle Claude API avec le prompt D3™ et retourne un JSON structuré.
"""

import os
import json
import anthropic
from datetime import datetime

client = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))

SYSTEM_PROMPT = """Tu es un consultant stratégique senior DECISIO, niveau McKinsey/BCG.
Tu analyses les entreprises avec la Méthode D3™ (Diagnostic, Décision, Déploiement).

RÈGLES ABSOLUES :
1. Réponds UNIQUEMENT en JSON valide — aucun texte avant ou après
2. Ne jamais inventer de chiffres — utilise les données fournies, estime les manquantes avec mention "estimé"
3. Chaque insight doit être spécifique et non-évident
4. Le Key Insight doit surprendre — dire ce que le client ne sait pas encore
5. Les actions 48h doivent être tellement concrètes qu'on peut les déléguer à quelqu'un

FORMAT JSON ATTENDU (respecte exactement cette structure) :
{
  "key_insight": "string — vérité non-évidente en 1-2 phrases",
  "probleme_percu": "string — ce que le client croit être son problème",
  "probleme_reel": "string — ce qui se passe vraiment",
  "cause_racine": {
    "niveau_1": "string — symptôme visible",
    "niveau_2": "string — cause systémique",
    "niveau_3": "string — cause fondamentale irréductible"
  },
  "synthese_executive": {
    "vrai_probleme": "string — 1 phrase directe",
    "solution_optimale": "string — 1 phrase, action transformatrice",
    "action_48h": "string — action concrète immédiate",
    "impact_m6": "string — chiffre net/mois attendu",
    "probabilite_succes": "integer — 0 à 100",
    "score_maturite": "float — 0 à 10"
  },
  "quick_win": {
    "action": "string — description précise",
    "pourquoi": "string — explication courte",
    "message_accroche": "string — texte exact du message à envoyer",
    "message_suivi": "string — message de suivi",
    "resultat_attendu": "string — résultat chiffré sous X jours",
    "relance_48h": "string — message de relance court"
  },
  "diagnostic": {
    "analyse_financiere": [
      {"indicateur": "string", "valeur": "string", "interpretation": "string"}
    ],
    "cinq_pourquoi": [
      {"question": "string", "reponse": "string"}
    ],
    "verite_fondamentale": "string — cause racine en 1 phrase percutante",
    "forces_porter": [
      {"force": "string", "intensite": "integer 1-5", "impact": "string", "levier": "string"}
    ],
    "swot": {
      "so": "string — stratégie offensive forces × opportunités",
      "st": "string — stratégie défensive forces × menaces",
      "wo": "string — stratégie développement faiblesses × opportunités",
      "wt": "string — stratégie survie faiblesses × menaces",
      "quadrant_prioritaire": "string"
    },
    "cout_inaction": [
      {"periode": "string", "manque": "integer", "cumule": "integer", "risque": "string"}
    ]
  },
  "decision": {
    "analyse_vrio": [
      {"ressource": "string", "valeur": true, "rare": true, "inimitable": true, "organise": true, "avantage": "string"}
    ],
    "conclusion_vrio": "string",
    "ansoff": [
      {"strategie": "string", "description": "string", "roi_mensuel": "integer", "delai_mois": "integer", "score": "float"}
    ],
    "recommandation_ansoff": "string",
    "options": [
      {
        "lettre": "A",
        "nom": "string",
        "description": "string",
        "roi": "integer 1-10",
        "probabilite": "integer 1-10",
        "difficulte": "integer 1-10",
        "score": "float",
        "est_recommande": true
      }
    ],
    "option_dangereuse": "string — option à éviter absolument et pourquoi",
    "recommandation_finale": "string — en 1ère personne, concrète",
    "premiere_phrase_demain": "string — exactement ce qu'il faut dire demain matin",
    "risques": [
      {"type": "string", "description": "string", "probabilite": "string", "solution": "string"}
    ],
    "seuils": [
      {"signal": "Stop|Pivot|Continue", "indicateur": "string", "delai_semaines": "integer", "justification": "string", "action": "string"}
    ]
  },
  "deploiement": {
    "plan_semaine_1": [
      {"jour": "string", "action": "string", "cout_eur": "integer", "temps_h": "float", "resultat": "string"}
    ],
    "budget_semaine_1": "string",
    "roi_semaine_1": "string",
    "jalons": [
      {"periode": "string", "focus": "string", "action": "string", "source_prospects": "string", "kpi": "string"}
    ],
    "impact_financier": {
      "calcul": "string — formule explicite",
      "hypotheses": ["string"],
      "projections": [
        {"periode": "string", "aujourd_hui": "integer", "projection": "integer", "gain": "integer"}
      ]
    },
    "positionnement": {
      "slogan": "string",
      "messages": [
        {"theme": "string", "texte": "string"}
      ],
      "canal_prioritaire": "string"
    },
    "mckinsey_7s": [
      {"element": "string", "situation": "string", "note": "integer 1-5", "desalignement": "string"}
    ],
    "desalignement_prioritaire": "string",
    "note_globale_7s": "integer",
    "regles_non_negociables": [
      {"numero": "integer", "regle": "string", "obstacle": "string", "solution": "string", "consequence": "string"}
    ],
    "kpi_unique": "string",
    "kpi_frequence": "string",
    "kpi_seuil": "string",
    "kpi_action_corrective": "string"
  },
  "pour_aller_plus_loin": {
    "base_diagnostique": "string — données utilisées pour l'analyse",
    "donnees_manquantes": [
      {"donnee": "string", "apport": "string"}
    ],
    "action_suivi": "string"
  }
}"""


def analyze_business(client_data: dict) -> dict:
    """
    Analyse un business avec la Méthode D3™ via Claude API.
    Retourne un dict JSON structuré.
    """
    # Construction du prompt utilisateur
    user_prompt = _build_user_prompt(client_data)

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            system=SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )

        raw_text = message.content[0].text.strip()

        # Nettoyage : enlever les backticks si présents
        if raw_text.startswith("```"):
            raw_text = raw_text.split("```")[1]
            if raw_text.startswith("json"):
                raw_text = raw_text[4:].strip()

        analysis = json.loads(raw_text)
        return analysis

    except json.JSONDecodeError as e:
        # Fallback : retourner un JSON minimal d'erreur
        return _fallback_analysis(client_data, str(e))
    except Exception as e:
        return _fallback_analysis(client_data, str(e))


def _build_user_prompt(data: dict) -> str:
    """Construit le prompt utilisateur à partir des données client."""
    nom = data.get('nom', 'Client')
    secteur = data.get('secteur', 'Non précisé')
    probleme = data.get('probleme', 'Non précisé')
    ca = data.get('ca_mensuel', 'Non précisé')
    charges = data.get('charges_mensuel', 'Non précisé')
    objectif = data.get('objectif_net', 'Non précisé')
    employes = data.get('nb_employes', 0)
    annees = data.get('annees_activite', 'Non précisé')
    contexte = data.get('contexte', '')
    date_str = data.get('date', datetime.now().strftime('%d %B %Y'))
    mode = data.get('mode', 'premium')

    # Calcul net si possible
    net_str = "Non calculable"
    if isinstance(ca, (int, float)) and isinstance(charges, (int, float)):
        net = ca - charges
        net_str = f"{net}€/mois"

    prompt = f"""DONNÉES CLIENT POUR ANALYSE D3™

Client : {nom}
Secteur d'activité : {secteur}
Date du rapport : {date_str}
Mode d'audit : {mode.upper()}

SITUATION FINANCIÈRE
- CA mensuel estimé : {ca}€
- Charges mensuelles : {charges}€
- Revenu net actuel : {net_str}
- Objectif net visé : {objectif}€/mois
- Nombre d'employés : {employes}
- Années d'activité : {annees}

PROBLÈME EXPRIMÉ PAR LE CLIENT
"{probleme}"

CONTEXTE SUPPLÉMENTAIRE
{contexte if contexte else "Aucun contexte supplémentaire fourni."}

INSTRUCTION
Produis l'analyse D3™ complète pour ce client.
Le Key Insight doit être non-évident et spécifique à ce business.
Les projections financières doivent être basées sur les chiffres fournis.
Toutes les actions doivent être immédiatement applicables.
"""
    return prompt


def _fallback_analysis(data: dict, error: str) -> dict:
    """Analyse de secours si Claude API échoue."""
    nom = data.get('nom', 'Client')
    return {
        "key_insight": f"Analyse en cours pour {nom}. Une erreur technique s'est produite.",
        "probleme_percu": data.get('probleme', 'Non précisé'),
        "probleme_reel": "Analyse non disponible — erreur API",
        "cause_racine": {
            "niveau_1": "Données insuffisantes",
            "niveau_2": f"Erreur: {error[:100]}",
            "niveau_3": "Relancer l'analyse"
        },
        "synthese_executive": {
            "vrai_probleme": "Analyse incomplète",
            "solution_optimale": "Relancer la génération",
            "action_48h": "Contacter le support DECISIO",
            "impact_m6": "À calculer",
            "probabilite_succes": 0,
            "score_maturite": 0
        },
        "error": error
    }
