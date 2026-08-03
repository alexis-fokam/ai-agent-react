"""
agent.py
--------
Construit l'agent ReAct (Reasoning + Acting) : un LLM capable de raisonner
sur une question, décider quel outil utiliser (le cas échéant), l'exécuter,
observer le résultat, et éventuellement enchaîner un autre outil, jusqu'à
pouvoir donner une réponse finale à l'utilisateur.

On utilise create_react_agent de LangGraph, qui gère automatiquement toute
cette boucle "penser → agir → observer → répondre".
"""

from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent

from tools import ALL_TOOLS

SYSTEM_PROMPT = """Tu es un assistant métier pour une entreprise de vente en gros.
Tu as accès à des outils pour : vérifier le statut d'une commande, calculer un devis,
et consulter la météo. Utilise TOUJOURS un outil quand la question s'y prête, plutôt
que de répondre de mémoire. Si une information manque pour utiliser un outil
(ex: numéro de commande), demande-la clairement à l'utilisateur.
Réponds toujours en français, de façon claire et professionnelle."""


def _extract_text(content) -> str:
    """
    Normalise le contenu d'un message en texte simple. Les modèles Gemini
    récents renvoient parfois une liste de blocs (texte, signatures de
    raisonnement, etc.) au lieu d'une simple chaîne de caractères.
    """
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text", ""))
        return "".join(parts)
    return str(content)


def build_agent(google_api_key: str):
    """
    Crée et retourne l'agent prêt à être invoqué.
    """
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=google_api_key,
        temperature=0,
    )

    agent = create_react_agent(
        model=llm,
        tools=ALL_TOOLS,
        prompt=SYSTEM_PROMPT,
    )
    return agent


def run_agent(agent, message: str, chat_history: list) -> dict:
    """
    Envoie un message à l'agent et récupère la réponse finale + le détail
    des étapes de raisonnement (quels outils ont été appelés, avec quels
    résultats) pour pouvoir les afficher dans l'interface.
    """
    messages = chat_history + [{"role": "user", "content": message}]
    result = agent.invoke({"messages": messages})

    all_messages = result["messages"]

    # On extrait les étapes intermédiaires (appels d'outils) pour l'affichage "logs"
    steps = []
    for msg in all_messages:
        msg_type = type(msg).__name__
        if msg_type == "AIMessage" and getattr(msg, "tool_calls", None):
            for call in msg.tool_calls:
                steps.append({"type": "tool_call", "name": call["name"], "args": call["args"]})
        elif msg_type == "ToolMessage":
            steps.append({"type": "tool_result", "content": msg.content})

    final_answer = _extract_text(all_messages[-1].content)

    return {
        "answer": final_answer,
        "steps": steps,
        "messages": all_messages,
    }
