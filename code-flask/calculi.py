# calculs.py
from datetime import datetime


class DepenseInvalideError(Exception):
    """Exception levée quand une règle métier n'est pas respectée."""
    pass


def valider_depense(montant_centimes: int, date_str: str, date_debut_str: str, date_fin_str: str, payeur_id: int, participants_ids: list[int], membres_ids: list[int]):
    """Vérifie que la dépense respecte toutes les règles du sujet."""
    # Rule 1: Montant positif
    if montant_centimes <= 0:
        raise DepenseInvalideError("Une dépense doit avoir un montant strictement positif.")

    # Rule 2: Au moins un participant
    if not participants_ids:
        raise DepenseInvalideError("Une dépense doit avoir au moins un participant.")

    # Rule 3: Payeur et participants dans le groupe
    if payeur_id not in membres_ids:
        raise DepenseInvalideError("Le payeur n'appartient pas au groupe.")

    for p_id in participants_ids:
        if p_id not in membres_ids:
            raise DepenseInvalideError("Certains participants n'appartiennent pas au groupe.")

    # Rule 4: Date comprise dans le séjour (incluses)
    d = datetime.strptime(date_str, "%Y-%m-%d").date()
    d_debut = datetime.strptime(date_debut_str, "%Y-%m-%d").date()
    d_fin = datetime.strptime(date_fin_str, "%Y-%m-%d").date()

    if not (d_debut <= d <= d_fin):
        raise DepenseInvalideError("La date de la dépense doit être comprise dans le séjour.")


def calculer_soldes(membres: list[dict], depenses: list[dict]) -> dict[int, float]:
    """
    Calcule le solde exact de chaque membre en euros.
    
    - membres : liste de dictionnaires [{'id': 1, 'nom': 'Alice'}, ...] pour chaque membre dictionnaire
    - depenses : liste de dictionnaires [{'payeur_id': 1, 'montant_centimes': 3000, 'participants_ids': [1, 2, 3]}, ...]
    """
    """ membres = [
        {"id": 1, "nom": "Alice"},
        {"id": 2, "nom": "Bob"},
        {"id": 3, "nom": "Chloé"}
    ]
    Dans cette liste :

    membres[0] est le dictionnaire {"id": 1, "nom": "Alice"}.

    Si on prend ce dictionnaire et qu'on écrit m["id"], Python va chercher la valeur associée à la clé "id".

    Si m est {"id": 1, "nom": "Alice"}, alors m["id"] vaut 1.

    Si m est {"id": 2, "nom": "Bob"}, alors m["id"] vaut 2.
    """

    # Étape 1 : Initialiser les soldes à 0 centime pour chaque membre
    soldes_cents = {m["id"]: 0 for m in membres}

    """ 
    dictionnaire soldes_cents devient: 
    {
    1: 0,
    2: 0,
    3: 0
    }
    """

    # Étape 2 : Traiter chaque dépense
    for dep in depenses:
        montant = dep["montant_centimes"]
        payeur_id = dep["payeur_id"]
        parts = dep["participants_ids"]  # Ordre préservé !

        if not parts:
            continue

        # Le payeur avance l'argent (on lui rajoute à son solde)
        soldes_cents[payeur_id] += montant

        # Part de base et centimes restants
        n = len(parts)
        part_base = montant // n
        reste = montant % n

        # Répartition : le premier de la liste (index 0) prend le reste
        for idx, p_id in enumerate(parts):
            part_a_payer = part_base + (reste if idx == 0 else 0)
            soldes_cents[p_id] -= part_a_payer

    # Étape 3 : Convertir les centimes en euros (ex: 666 centimes -> 6.66 €)
    return {m_id: cents / 100.0 for m_id, cents in soldes_cents.items()}
