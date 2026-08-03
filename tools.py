"""
tools.py
--------
Définit les "outils" (tools) que l'agent IA peut décider d'utiliser pour
répondre à une demande. Chaque outil est une fonction Python normale,
décorée avec @tool pour que LangChain sache la présenter au LLM.

C'est la différence clé entre un simple chatbot et un agent :
un chatbot ne fait que parler, un agent peut AGIR (consulter une base,
faire un calcul, appeler une API) puis répondre avec le résultat réel.
"""

import json
import os
import requests
from langchain_core.tools import tool

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


@tool
def verifier_statut_commande(numero_commande: str) -> str:
    """
    Vérifie le statut d'une commande à partir de son numéro (ex: CMD-1001).
    Retourne le statut, le client, les produits, et les infos de livraison si disponibles.
    Utilise cet outil dès qu'un utilisateur demande où en est une commande.
    """
    with open(os.path.join(DATA_DIR, "orders.json"), encoding="utf-8") as f:
        commandes = json.load(f)

    commande = commandes.get(numero_commande.upper())
    if not commande:
        return f"Aucune commande trouvée avec le numéro {numero_commande}."

    return (
        f"Commande {numero_commande} — Client : {commande['client']}\n"
        f"Statut : {commande['statut']}\n"
        f"Produits : {', '.join(commande['produits'])}\n"
        f"Transporteur : {commande.get('transporteur') or 'non assigné'}\n"
        f"Date d'expédition : {commande.get('date_expedition') or 'pas encore expédiée'}"
    )


@tool
def calculer_devis(produit: str, quantite: int) -> str:
    """
    Calcule le prix total pour une quantité donnée d'un produit du catalogue.
    Le nom du produit doit correspondre approximativement au catalogue
    (ex: "sac de riz 25kg", "sucre en poudre 1kg").
    Utilise cet outil dès qu'un utilisateur demande un prix, un devis ou un total.
    """
    with open(os.path.join(DATA_DIR, "pricing.json"), encoding="utf-8") as f:
        catalogue = json.load(f)

    produit_normalise = produit.lower().strip()
    prix_unitaire = catalogue.get(produit_normalise)

    if prix_unitaire is None:
        produits_disponibles = ", ".join(catalogue.keys())
        return (
            f"Produit '{produit}' non trouvé dans le catalogue. "
            f"Produits disponibles : {produits_disponibles}"
        )

    total = prix_unitaire * quantite
    return (
        f"{quantite} x {produit_normalise} = {total:,} FCFA "
        f"(prix unitaire : {prix_unitaire:,} FCFA)"
    ).replace(",", " ")


@tool
def obtenir_meteo(ville: str) -> str:
    """
    Donne la météo actuelle pour une ville donnée, en utilisant une vraie
    API météo gratuite (Open-Meteo, sans clé requise).
    Utilise cet outil quand un utilisateur demande la météo quelque part.
    """
    # Étape 1 : convertir le nom de ville en coordonnées GPS
    geo_url = "https://geocoding-api.open-meteo.com/v1/search"
    geo_resp = requests.get(geo_url, params={"name": ville, "count": 1}, timeout=10)
    geo_data = geo_resp.json()

    if not geo_data.get("results"):
        return f"Ville '{ville}' introuvable."

    lieu = geo_data["results"][0]
    lat, lon = lieu["latitude"], lieu["longitude"]
    nom_complet = f"{lieu['name']}, {lieu.get('country', '')}"

    # Étape 2 : récupérer la météo actuelle pour ces coordonnées
    weather_url = "https://api.open-meteo.com/v1/forecast"
    weather_resp = requests.get(
        weather_url,
        params={"latitude": lat, "longitude": lon, "current_weather": True},
        timeout=10,
    )
    weather_data = weather_resp.json().get("current_weather", {})

    if not weather_data:
        return f"Impossible de récupérer la météo pour {nom_complet}."

    return (
        f"Météo actuelle à {nom_complet} : "
        f"{weather_data['temperature']}°C, "
        f"vent {weather_data['windspeed']} km/h."
    )


# Liste de tous les outils, importée par agent.py
ALL_TOOLS = [verifier_statut_commande, calculer_devis, obtenir_meteo]
