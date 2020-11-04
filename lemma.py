import spacy

if __name__ == "__main__":
    nlp = spacy.load('en_core_web_sm', disable=['ner'])

    prefixes = ['dry', 'dried', 'fresh', 'hot']
    colors = ['red', 'green']
    terms = ['chile',  'chili', 'chilli',
             'chiles', 'chilis', 'chilies', 'chillies']

    for prefix in prefixes:
        for color in colors:
            for term in terms:
                sentence = ' '.join([prefix, color, term])
                tokens = nlp(sentence)
                lemma_noun_chunks = [chunk.lemma_ for chunk in tokens.noun_chunks]
                print(lemma_noun_chunks)
