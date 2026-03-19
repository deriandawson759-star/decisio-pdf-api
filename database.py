"""
DECISIO — Supabase Integration
Stockage des prospects et audits pour pipeline client.
"""

import os
import json
from datetime import datetime

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False


def get_client() -> "Client | None":
    """Retourne le client Supabase si configuré, sinon None."""
    if not SUPABASE_AVAILABLE:
        return None
    url = os.environ.get('SUPABASE_URL')
    key = os.environ.get('SUPABASE_SERVICE_KEY')
    if not url or not key:
        return None
    return create_client(url, key)


def save_prospect(client_data: dict) -> dict | None:
    """
    Enregistre un prospect dans la table `prospects`.
    Retourne la ligne insérée ou None en cas d'erreur.
    """
    db = get_client()
    if db is None:
        return None

    row = {
        "nom":     client_data.get('nom', 'Client'),
        "secteur": client_data.get('secteur', ''),
        "offre":   client_data.get('mode', 'premium'),
        "email":   client_data.get('email', ''),
        "date":    datetime.utcnow().isoformat(),
    }

    try:
        result = db.table('prospects').insert(row).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"[Supabase] save_prospect error: {e}")
        return None


def save_audit(prospect_id: str | None, analysis: dict, scores: dict,
               client_data: dict) -> dict | None:
    """
    Enregistre un audit complet dans la table `audits`.
    Retourne la ligne insérée ou None en cas d'erreur.
    """
    db = get_client()
    if db is None:
        return None

    row = {
        "prospect_id":   prospect_id,
        "nom":           client_data.get('nom', 'Client'),
        "secteur":       client_data.get('secteur', ''),
        "mode":          client_data.get('mode', 'premium'),
        "analyse_json":  json.dumps(analysis, ensure_ascii=False),
        "scores_json":   json.dumps(scores, ensure_ascii=False),
        "score_global":  scores.get('global_score', 0),
        "maturite":      scores.get('maturity_level', ''),
        "date":          datetime.utcnow().isoformat(),
    }

    try:
        result = db.table('audits').insert(row).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"[Supabase] save_audit error: {e}")
        return None


def list_prospects(limit: int = 50) -> list:
    """Retourne les derniers prospects enregistrés."""
    db = get_client()
    if db is None:
        return []
    try:
        result = (
            db.table('prospects')
            .select('*')
            .order('date', desc=True)
            .limit(limit)
            .execute()
        )
        return result.data or []
    except Exception as e:
        print(f"[Supabase] list_prospects error: {e}")
        return []


def list_audits(limit: int = 50) -> list:
    """Retourne les derniers audits enregistrés."""
    db = get_client()
    if db is None:
        return []
    try:
        result = (
            db.table('audits')
            .select('id, nom, secteur, mode, score_global, maturite, date')
            .order('date', desc=True)
            .limit(limit)
            .execute()
        )
        return result.data or []
    except Exception as e:
        print(f"[Supabase] list_audits error: {e}")
        return []
