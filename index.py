import os
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from collections import defaultdict
import math

# nltk.download('punkt')
# nltk.download('stopwords')

# Directory containing the documents
doc_dir = 'docs'

# Create a dictionary to store the inverted index
inverted_index = defaultdict(list)

# Loop over the documents in the directory
for filename in os.listdir(doc_dir):
    # Read the document
    with open(os.path.join(doc_dir, filename), 'r') as f:
        doc = f.read()
    
    # Tokenize the text
    tokens = word_tokenize(doc)

    # Remove stop words
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [token for token in tokens if token.lower() not in stop_words]

    # Stem the terms
    stemmer = PorterStemmer()
    stemmed_tokens = [stemmer.stem(token) for token in filtered_tokens]

     # Add the document ID and paragraph number to the inverted index for each term
    para_num = 1
    for para in doc.split('\n\n'):  # Split document into paragraphs
        para_tokens = word_tokenize(para)
        para_filtered_tokens = [token for token in para_tokens if token.lower() not in stop_words]
        para_stemmed_tokens = [stemmer.stem(token) for token in para_filtered_tokens]
        for term in set(para_stemmed_tokens):
            inverted_index[term].append((filename, para_num))
        para_num += 1

# Define a function to search for documents that match a query and rank them by cosine similarity
def search(query):
    # Tokenize, remove stop words, and stem the query terms
    query_tokens = word_tokenize(query)
    query_filtered_tokens = [token for token in query_tokens if token.lower() not in stop_words]
    query_stemmed_tokens = [stemmer.stem(token) for token in query_filtered_tokens]
    
    # Find the documents that contain any of the query terms
    doc_sets = [set(inverted_index[term]) for term in query_stemmed_tokens]
    matching_docs = set.union(*doc_sets)
    
    # Compute the document vectors
    doc_vectors = {}
    for doc_id, _ in matching_docs:
        # Read the document
        with open(os.path.join(doc_dir, doc_id), 'r') as f:
            doc = f.read()
        
        # Tokenize, remove stop words, and stem the document terms
        doc_tokens = word_tokenize(doc)
        doc_filtered_tokens = [token for token in doc_tokens if token.lower() not in stop_words]
        doc_stemmed_tokens = [stemmer.stem(token) for token in doc_filtered_tokens]
        
        # Count the frequency of each term in the document
        term_freq = defaultdict(int)
        for term in doc_stemmed_tokens:
            term_freq[term] += 1
        
        # Compute the document vector
        doc_vector = {}
        for term, freq in term_freq.items():
            doc_vector[term] = freq / len(doc_stemmed_tokens)
        
        # Add the document vector to the dictionary
        doc_vectors[doc_id] = doc_vector
    
    # Compute the query vector
    query_vector = {}
    for term in query_stemmed_tokens:
        query_vector[term] = (1 + math.log(query_stemmed_tokens.count(term))) * math.log(len(doc_vectors) / len(inverted_index[term]))
    
    # Compute the cosine similarity between the query vector and each document vector
    scores = {}
    for doc_id in doc_vectors.keys():
        score = 0
        for term, weight in query_vector.items():
            if term in doc_vectors[doc_id]:
                score += weight * doc_vectors[doc_id][term]
        scores[doc_id] = score
    
    # Sort the results by cosine similarity
    results = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    # Return the matching documents
    return results

# Example query
query = "Joel felt that"

# Search for matching documents and rank them by cosine similarity
results = search(query)

# Print the results
for doc_id, score in results:
    print(f'{doc_id}: {score}')