"""
Calcul de la prévision des besoins en eau ET décision automatique de
l'irrigation.

IMPORTANT : ces deux fonctions contiennent des calculs volontairement
simples (seuils sur l'humidité du sol), en attendant ton propre modèle
de prévision — c'est la partie la plus importante de ton thème
académique. Remplace-les par ta vraie logique sans toucher aux vues :
la forme des données retournées doit juste rester la même.
"""

SEUIL_HUMIDITE_SOL = 50.0


def calculer_prevision(derniere_mesure):
    if derniere_mesure is None:
        return {
            'besoin_eau': False,
            'message': "Aucune mesure reçue pour cette parcelle. La prévision sera disponible dès qu'un capteur enverra des données.",
            'raisons': [],
            'courbe': [],
        }

    humidite = derniere_mesure.humidite_sol
    besoin_eau = humidite < SEUIL_HUMIDITE_SOL

    message = (
        "L'humidité du sol est sous le seuil recommandé, un arrosage est conseillé prochainement."
        if besoin_eau else
        "L'humidité du sol est à un niveau satisfaisant, aucun arrosage n'est nécessaire pour l'instant."
    )

    raisons = [{
        'titre': "Humidité du sol actuelle",
        'detail': f"{humidite:.1f}%, contre un seuil de {SEUIL_HUMIDITE_SOL:.0f}% recommandé pour cette culture.",
    }]

    if derniere_mesure.temperature is not None and derniere_mesure.temperature >= 28:
        raisons.append({
            'titre': "Température élevée",
            'detail': f"{derniere_mesure.temperature:.1f}°C mesurés, ce qui accélère l'évaporation de l'eau du sol.",
        })

    courbe = [
        {'label': 'Maint.', 'valeur': round(humidite, 1)},
        {'label': '+6h', 'valeur': round(max(humidite - 6, 0), 1)},
        {'label': '+12h', 'valeur': round(max(humidite - 11, 0), 1)},
        {'label': '+24h', 'valeur': round(max(humidite - 18, 0), 1)},
    ]

    return {'besoin_eau': besoin_eau, 'message': message, 'raisons': raisons, 'courbe': courbe}


# --- Décision automatique de l'irrigation ---
#
# En mode auto, c'est cette fonction qui décide, à chaque mesure reçue,
# si la pompe doit tourner — sans aucune intervention de l'agriculteur.
#
# Deux seuils différents (plutôt qu'un seul) pour éviter que la pompe
# s'allume/s'éteigne en boucle quand l'humidité oscille autour d'une
# valeur unique (hystérésis) :
#   - en dessous de SEUIL_DEMARRAGE_AUTO -> on démarre l'irrigation
#   - au dessus de SEUIL_ARRET_AUTO      -> on l'arrête
#   - entre les deux                      -> on ne change rien

SEUIL_DEMARRAGE_AUTO = 35.0
SEUIL_ARRET_AUTO = 55.0


def decider_irrigation_auto(humidite_sol, irrigation_active_actuellement):
    """Renvoie True si la pompe doit tourner, False sinon, en fonction de
    l'humidité du sol et de l'état actuel (pour l'hystérésis)."""
    if humidite_sol is None:
        return irrigation_active_actuellement

    if humidite_sol < SEUIL_DEMARRAGE_AUTO:
        return True
    if humidite_sol > SEUIL_ARRET_AUTO:
        return False
    return irrigation_active_actuellement