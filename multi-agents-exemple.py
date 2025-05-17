import os
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(model="gpt-4o")


def orchestrateur(state):
    message = state["message"]
    prompt = f"""
    Détermine précisément l'intention de l'utilisateur parmi les suivantes : 
    - faq (question fréquente)
    - rdv (prise de rendez-vous)
    - filtrage (qualification prospect)
    - objectif (gestion objectifs GoHighLevel)

    Réponds uniquement par faq, rdv, filtrage ou objectif.
    Message: "{message}"
    """
    intention = llm.invoke(prompt).content.strip().lower()
    if intention not in ["faq", "rdv", "filtrage", "objectif"]:
        raise ValueError(f"Intention inconnue : {intention}")
    return {"intention": intention, "message": message}


def agent_faq(state):
    question = state["message"]
    # Ici on simule un appel à une base vectorielle de FAQ
    print(f"[FAQ] Recherche simulée pour : {question}")
    reponse_faq = "Voici la réponse à votre question (FAQ simulée)."
    return {"réponse": reponse_faq}


def agent_rdv(state):
    message = state["message"]
    
    # Simulation extraction infos RDV par LLM (à remplacer par un vrai appel)
    extraction_prompt = f"""
    Extrait la date, l'heure, nom et email du message : "{message}".
    Renvoie uniquement JSON : {{"date":"YYYY-MM-DD","heure":"HH:MM","nom":"Nom","email":"email@example.com"}}
    """
    infos_rdv = llm.invoke(extraction_prompt).content.strip()
    
    # Simuler appel API GoHighLevel
    print(f"[RDV] Simulation de prise de RDV via GoHighLevel : {infos_rdv}")
    return {"réponse": f"RDV confirmé (simulation) avec les infos : {infos_rdv}"}

def agent_filtrage(state):
    message = state["message"]
    qualification_prompt = f"""
    Classe ce prospect en 'curieux', 'client' ou 'prospect chaud'.
    Message : "{message}"
    """
    qualification = llm.invoke(qualification_prompt).content.strip().lower()
    
    print(f"[Filtrage] Qualification du prospect : {qualification}")
    
    if qualification == "prospect chaud":
        return {"réponse": "Prospect qualifié pour RDV. Proposition de RDV recommandée."}
    elif qualification == "client":
        return {"réponse": "Client existant détecté. Proposer une assistance personnalisée."}
    else:
        return {"réponse": "Simple curieux identifié. Réponse standard recommandée."}


def agent_objectif(state):
    message = state["message"]
    # Simuler gestion objectifs (extraction et mise à jour via GoHighLevel)
    objectif_prompt = f"""
    Identifie et extrait les objectifs à définir ou à modifier dans le message suivant :
    "{message}"
    Renvoie une description courte en une phrase de l'objectif.
    """
    objectif = llm.invoke(objectif_prompt).content.strip()

    print(f"[Objectif] Simulation mise à jour de l'objectif dans GoHighLevel : {objectif}")
    return {"réponse": f"Objectif mis à jour (simulation) : {objectif}"}


graph = StateGraph(dict)

# Ajouter les nœuds agents au graphe
graph.add_node("orchestrateur", orchestrateur)
graph.add_node("faq", agent_faq)
graph.add_node("rdv", agent_rdv)
graph.add_node("filtrage", agent_filtrage)
graph.add_node("objectif", agent_objectif)

# Point d'entrée du workflow
graph.set_entry_point("orchestrateur")

# Définition des transitions conditionnelles
graph.add_conditional_edges(
    "orchestrateur",
    lambda state: state["intention"],
    {"faq": "faq", "rdv": "rdv", "filtrage": "filtrage", "objectif": "objectif"}
)

# Fin des branches du workflow
graph.add_edge("faq", END)
graph.add_edge("rdv", END)
graph.add_edge("filtrage", END)
graph.add_edge("objectif", END)

# Compiler l'application
app = graph.compile()


# Test prise de RDV
result = app.invoke({"message": "Je souhaite un RDV vendredi à 15h, je suis Léa Pélissier, lea@example.com"})
print(result)

# Test FAQ
result = app.invoke({"message": "Quels sont vos tarifs ?"})
print(result)

# Test Filtrage Prospect
result = app.invoke({"message": "Je suis intéressé mais je ne sais pas encore."})
print(result)

# Test Gestion Objectif
result = app.invoke({"message": "Pouvez-vous mettre à jour mon prénom dans votre CRM en Pierre ?"})
print(result)



