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

st.set_page_config(
    page_title="Agent IA - Automatisation métier",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

EXAMPLE_QUESTIONS = [
    "Où en est la commande CMD-1001 ?",
    "Combien coûtent 10 sacs de riz 25kg ?",
    "Quelle est la météo à Douala ?",
    "Vérifie la commande CMD-1002 et donne-moi aussi le prix de 5 sacs de riz 25kg",
]

# --------------------------------------------------------------------------
# Styles
# --------------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .block-container { padding-top: 2rem; max-width: 900px; }

    /* Hero banner */
    .hero {
        background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%);
        border-radius: 20px;
        padding: 2rem 2.25rem;
        margin-bottom: 1.75rem;
        box-shadow: 0 8px 24px rgba(99, 102, 241, 0.25);
    }
    .hero h1 {
        color: #FFFFFF;
        font-size: 1.9rem;
        font-weight: 700;
        margin: 0 0 0.4rem 0;
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }
    .hero p {
        color: rgba(255,255,255,0.9);
        font-size: 0.98rem;
        margin: 0;
        line-height: 1.5;
    }
    .hero .badge {
        display: inline-block;
        background: rgba(255,255,255,0.18);
        color: #fff;
        border-radius: 999px;
        padding: 0.2rem 0.7rem;
        font-size: 0.75rem;
        font-weight: 600;
        margin-top: 0.85rem;
        letter-spacing: 0.02em;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: #F4F5FA;
        border-right: 1px solid #E5E3F5;
    }
    section[data-testid="stSidebar"] .sidebar-title {
        font-weight: 700;
        font-size: 1.05rem;
        color: #1E1B2E;
        margin-bottom: 0.25rem;
    }
    section[data-testid="stSidebar"] .sidebar-sub {
        font-size: 0.85rem;
        color: #6B7280;
        margin-bottom: 1rem;
    }
    section[data-testid="stSidebar"] .stButton button {
        text-align: left;
        justify-content: flex-start;
        border-radius: 10px;
        border: 1px solid #E5E3F5;
        background: #FFFFFF;
        color: #3730A3;
        font-size: 0.85rem;
        padding: 0.55rem 0.8rem;
        margin-bottom: 0.4rem;
        transition: all 0.15s ease;
    }
    section[data-testid="stSidebar"] .stButton button:hover {
        border-color: #6366F1;
        background: #EEF0FF;
        color: #4338CA;
    }

    /* Chat bubbles */
    [data-testid="stChatMessage"] {
        border-radius: 16px;
        padding: 0.4rem 0.6rem;
        margin-bottom: 0.6rem;
    }
    [data-testid="stChatMessageAvatarUser"] { background-color: #6366F1 !important; }
    [data-testid="stChatMessageAvatarAssistant"] { background-color: #F59E0B !important; }

    .stChatInput textarea { border-radius: 12px !important; }

    /* Reasoning expander */
    .stExpander {
        border-radius: 12px !important;
        border: 1px solid #E5E3F5 !important;
        background: #FAFAFF;
    }
    .step-tool {
        background: #EEF0FF;
        border-left: 3px solid #6366F1;
        border-radius: 8px;
        padding: 0.5rem 0.75rem;
        margin-bottom: 0.4rem;
        font-size: 0.87rem;
    }
    .step-result {
        background: #F0FDF4;
        border-left: 3px solid #22C55E;
        border-radius: 8px;
        padding: 0.5rem 0.75rem;
        margin-bottom: 0.4rem;
        font-size: 0.87rem;
    }

    .empty-state {
        text-align: center;
        color: #6B7280;
        padding: 2.5rem 1rem;
        border: 1px dashed #E5E3F5;
        border-radius: 16px;
        font-size: 0.95rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------------------------------
# Hero header
# --------------------------------------------------------------------------
st.markdown(
    """
    <div class="hero">
        <h1>🤖 Agent IA d'automatisation métier</h1>
        <p>Cet agent peut vérifier une commande, calculer un devis, ou donner la météo.
        Contrairement à un chatbot classique, il exécute de vraies actions via des outils.</p>
        <span class="badge">⚡ Propulsé par Gemini + LangGraph</span>
    </div>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------------------------------
# Clé API
# --------------------------------------------------------------------------
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

# --------------------------------------------------------------------------
# Sidebar : exemples + actions
# --------------------------------------------------------------------------
with st.sidebar:
    st.markdown('<div class="sidebar-title">💡 Exemples de questions</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-sub">Clique pour envoyer directement à l\'agent</div>', unsafe_allow_html=True)

    for i, ex in enumerate(EXAMPLE_QUESTIONS):
        if st.button(ex, key=f"example_{i}", use_container_width=True):
            st.session_state.pending_question = ex

    st.divider()
    if st.button("🗑️ Nouvelle conversation", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.display_log = []
        st.rerun()

# --------------------------------------------------------------------------
# Traitement de la question (saisie libre ou exemple cliqué)
# --------------------------------------------------------------------------
prefill_question = st.session_state.pop("pending_question", None)
typed_question = st.chat_input("Pose ta question à l'agent...")
question = prefill_question or typed_question

if question:
    with st.spinner("🧠 L'agent réfléchit et exécute les outils nécessaires..."):
        result = run_agent(st.session_state.agent, question, st.session_state.chat_history)

    st.session_state.chat_history.append({"role": "user", "content": question})
    st.session_state.chat_history.append({"role": "assistant", "content": result["answer"]})
    st.session_state.display_log.append(
        {"question": question, "answer": result["answer"], "steps": result["steps"]}
    )

# --------------------------------------------------------------------------
# Affichage de la conversation
# --------------------------------------------------------------------------
for exchange in st.session_state.display_log:
    with st.chat_message("user", avatar="🧑"):
        st.write(exchange["question"])

    with st.chat_message("assistant", avatar="🤖"):
        if exchange["steps"]:
            with st.expander("🔍 Voir le raisonnement de l'agent"):
                for step in exchange["steps"]:
                    if step["type"] == "tool_call":
                        st.markdown(
                            f'<div class="step-tool">🔧 <b>Appel de l\'outil</b> '
                            f'<code>{step["name"]}</code> avec <code>{step["args"]}</code></div>',
                            unsafe_allow_html=True,
                        )
                    else:
                        st.markdown(
                            f'<div class="step-result">📋 <b>Résultat obtenu :</b> {step["content"]}</div>',
                            unsafe_allow_html=True,
                        )
        st.write(exchange["answer"])

if not st.session_state.display_log:
    st.markdown(
        '<div class="empty-state">👆 Pose une question ci-dessous, ou choisis un exemple dans la barre latérale pour démarrer.</div>',
        unsafe_allow_html=True,
    )
