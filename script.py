import spacy
import re
import requests
from urllib.parse import quote
import xml.etree.ElementTree as ET
from SPARQLWrapper import SPARQLWrapper, JSON

# Charger le modèle français de spaCy
nlp = spacy.load("fr_core_news_sm")

def lookup_dbpedia(entity):
    """ Cherche l'URI DBpedia correspondant à une entité donnée. """
    safe_entity = quote(entity)
    url = f"http://lookup.dbpedia.org/api/search/KeywordSearch?QueryString={safe_entity}"
    headers = {'Accept': 'application/xml'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        try:
            root = ET.fromstring(response.content)
            uri_element = root.find('.//URI')
            if uri_element is not None:
                return uri_element.text
        except ET.ParseError as e:
            print(f"Error parsing XML: {e}")
    return None

def determine_response_type(question):
    """ Détermine le type de réponse attendue pour une question donnée. """
    if re.search(r"\b(qui|Quelle personne)\b", question, re.IGNORECASE):
        return "Personne"
    elif re.search(r"\b(ou|Quel lieu|Quelle ville)\b", question, re.IGNORECASE):
        return "Lieu"
    elif re.search(r"\b(quand|Quelle date)\b", question, re.IGNORECASE):
        return "Date"
    elif re.search(r"\b(combien|Quel nombre|Quelle quantité)\b", question, re.IGNORECASE):
        return "Quantité"
    for ent in nlp(question).ents:
        if ent.label_ == "LOC":
            return "Lieu"
        elif ent.label_ == "PER":
            return "Personne"
        elif ent.label_ == "DATE":
            return "Date"
        elif ent.label_ == "NUM":
            return "Quantité"
    return "Inconnu"

def execute_sparql_query(entity_uri, property):
    print ("entity uri:+" + entity_uri)
    print("property:+" + property)
    """ Exécute une requête SPARQL pour une propriété donnée d'une entité. """
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    query = f"""
    PREFIX dbo: <http://dbpedia.org/ontology/>
    SELECT ?response WHERE {{
        <{entity_uri}> dbo:{property} ?uri .
    }} LIMIT 1
    """
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return [result["response"]["value"] for result in results["results"]["bindings"]]

def process_question(question):
    """ Traite une question pour déterminer le type de réponse, l'entité concernée et récupère les données correspondantes. """
    response_type = determine_response_type(question)
    doc = nlp(question)
    entity = None
    for ent in doc.ents:
        entity = ent.text.replace(" ", "_")
        break
    if not entity:
        return "Aucune entité principale identifiée dans la question."

    entity_uri = lookup_dbpedia(entity)
    if not entity_uri:
        return "Aucune URI trouvée pour l'entité mentionnée."

    property_dict = {
        "Personne": "director",  
        "Lieu": "location",
        "Date": "date",
        "Quantité": "population"
    }

    property = property_dict.get(response_type, "unknown")
    if property == "unknown":
        return "Type de réponse non supporté."

    results = execute_sparql_query(entity_uri, property)
    return results
# Exemple d'utilisation
question = input("Poser votre question :  ")
response = process_question(question)
print("Réponse à la question :", response)
