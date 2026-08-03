# Agent IA d'automatisation métier (ReAct)

Agent IA capable d'exécuter de vraies actions — pas seulement discuter — en
utilisant des outils personnalisés : vérification de commandes, calcul de
devis, et consultation météo en temps réel.

## 🎯 Fonctionnalités

- Raisonnement ReAct (Reasoning + Acting) : l'agent décide seul quel outil
  utiliser selon la question posée
- 3 outils personnalisés :
  - `verifier_statut_commande` — consulte une base de commandes (JSON)
  - `calculer_devis` — calcule un prix à partir d'un catalogue produit
  - `obtenir_meteo` — appelle une vraie API météo (Open-Meteo, gratuite)
- Interface conversationnelle avec affichage du raisonnement (quels outils
  ont été appelés, avec quels résultats)
- Peut enchaîner plusieurs outils pour répondre à une seule question complexe

## 🛠️ Stack technique

- **Python 3.11+**
- **LangGraph** — orchestration de l'agent ReAct
- **LangChain** — définition des outils
- **Google Gemini API** — moteur de raisonnement (LLM)
- **Streamlit** — interface conversationnelle

## 🚀 Installation locale

```bash
git clone https://github.com/alexis-fokam/ai-agent-react.git
cd ai-agent-react
python -m venv venv
source venv/bin/activate  # Windows : venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Ouvre .env et colle ta clé Google API (gratuite sur https://aistudio.google.com/apikey)
streamlit run app.py
```

## 🌐 Démo en ligne

👉 [Lien de la démo Streamlit Cloud à ajouter ici]

## 💬 Exemples de questions

- "Où en est la commande CMD-1001 ?"
- "Combien coûtent 10 sacs de riz 25kg ?"
- "Quelle est la météo à Douala ?"
- "Vérifie la commande CMD-1002 et donne-moi le prix de 5 sacs de riz 25kg"

## 📂 Structure du projet

```
ai-agent-react/
├── app.py                      # Interface Streamlit (chat + logs de raisonnement)
├── agent.py                    # Construction de l'agent ReAct (LangGraph)
├── tools.py                    # Définition des 3 outils personnalisés
├── data/
│   ├── orders.json             # Base de commandes fictive
│   └── pricing.json            # Catalogue de prix fictif
├── requirements.txt
├── .env.example
└── .streamlit/
    └── secrets.toml.example
```

## 👤 Auteur

Alexis Mvondo Fokam — [Portfolio](https://portfolio-alexis-fokam.netlify.app) — [LinkedIn](https://linkedin.com/in/alexis-fokam)
