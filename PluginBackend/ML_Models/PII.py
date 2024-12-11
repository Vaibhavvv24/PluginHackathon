import spacy

def extract_named_entities(text):
    """
    Function to extract named entities like proper names, locations, and organizations using spaCy.
    
    :param text: Input text
    :return: List of extracted named entities
    """
    # Load the pre-trained spaCy model (en_core_web_sm)
    nlp = spacy.load("en_core_web_sm")
    
    # Process the text
    doc = nlp(text)
    
    # Extract named entities
    named_entities = [(ent.text, ent.label_) for ent in doc.ents]
    return named_entities

# Example usage
input_text = """
Hello, myname is Soham Pawar and I am from team AIPioneers for the Plugin hackathon
"""

entities = extract_named_entities(input_text)
print("Named Entities:\n", entities)
