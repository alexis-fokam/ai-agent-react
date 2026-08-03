"""
app.py
------
Interface Streamlit pour discuter avec l'agent et voir en direct
son raisonnement (quels outils il choisit d'utiliser et pourquoi).
"""

import os
import streamlit as st
from dotenv import load_dotenv

from agent import build_agent, run_agent

load_dotenv()

st.set_page_config(page_title="Agent IA - Automatisation métier", page_icon="🤖", layout="centered")

st.title("🤖 Agent IA d'automatisation métier")
st.caption(
    "Cet agent peut vérifier une commande, calculer un devis, ou donner la météo. "
    "Contrairement à un chatbot classique, il exécute de vraies actions via des outils."
)

with st.expander("💡 Exemples de questions à essayer"):
    st.markdown(
        "- Où en est la commande CMD-1001 ?\n"
        "- Combien coûtent 10 sacs de riz 25kg ?\n"
        "- Quelle est la météo à Douala ?\n"
        "- Vérifie la commande CMD-1002 et donne-moi aussi le prix de 5 sacs de riz 25kg"
    )

google_api_key = os.getenv("GOOGLE_API_KEY") or st.secrets.get("GOOGLE_API_KEY", None)

if not google_api_key:
    st.error(
        "⚠️ Clé API Google manquante. Ajoute GOOGLE_API_KEY dans ton fichier .env "
        "(en local) ou dans les Secrets Streamlit Cloud (en production)."
    )
    st.stop()

if "agent" not in st.session_state:
    st.session_state.agent = build_agent(google_api_key)
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "display_log" not in st.session_state:
    st.session_state.display_log = []

question = st.chat_input("Pose ta question à l'agent...")

if question:
    with st.spinner("🧠 L'agent réfléchit et exécute les outils nécessaires..."):
        result = run_agent(st.session_state.agent, question, st.session_state.chat_history)

    st.session_state.chat_history.append({"role": "user", "content": question})
    st.session_state.chat_history.append({"role": "assistant", "content": result["answer"]})
    st.session_state.display_log.append(
        {"question": question, "answer": result["answer"], "steps": result["steps"]}
    )

# --- Affichage de la conversation ---
for exchange in st.session_state.display_log:
    with st.chat_message("user"):
        st.write(exchange["question"])

    with st.chat_message("assistant"):
        if exchange["steps"]:
            with st.expander("🔍 Voir le raisonnement de l'agent"):
                for step in exchange["steps"]:
                    if step["type"] == "tool_call":
                        st.markdown(f"**🔧 Appel de l'outil** `{step['name']}` avec `{step['args']}`")
                    else:
                        st.markdown(f"**📋 Résultat obtenu :** {step['content']}")
        st.write(exchange["answer"])

if not st.session_state.display_log:
    st.info("👆 Pose une question ci-dessous pour démarrer.")
