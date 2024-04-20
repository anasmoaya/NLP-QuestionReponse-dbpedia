import spacy
import re

# Charger le modèle français
nlp = spacy.load("fr_core_news_sm")

def determine_response_type(question):
    doc = nlp(question)
    
    # Recherche de patterns typiques pour classifier le type de question
    if re.search(r"\b(qui|Quel|Quelle personne)\b", question):
        return "Personne"
    elif re.search(r"\b(où|Quel lieu|Quelle ville)\b", question):
        return "Lieu"
    elif re.search(r"\b(quand|Quelle date)\b", question):
        return "Date"
    elif re.search(r"\b(combien|Quel nombre|Quelle quantité)\b", question):
        return "Quantité"
    
    # Analyser les entités pour aider à déterminer le type
    for ent in doc.ents:
        if ent.label_ == "LOC":
            return "Lieu"
        elif ent.label_ == "PER":
            return "Personne"
        elif ent.label_ == "DATE":
            return "Date"
        elif ent.label_ == "NUM":
            return "Nombre"

    return "Inconnu"  # Retourner Inconnu si aucun type n'est clairement identifié

# Exemple d'utilisation
question = "quelle est le nombre de questions ?"
response_type = determine_response_type(question)
print("Type de réponse attendue:", response_type)
