import json
from pprint import pprint
import os
import time

from dotenv import load_dotenv
from elasticsearch import Elasticsearch

load_dotenv()


class Search:
    def __init__(self):
        self.es = Elasticsearch('http://localhost:9200')  # <-- connection options need to be added here
        client_info = self.es.info()
        print('Connected to Elasticsearch!')
        pprint(client_info.body)


    

    # Method to atomatically create and delete indexes
    # Change my_documents to documents
    def create_index(self):
        self.es.indices.delete(index='documents', ignore_unavailable=True)
        self.es.indices.create(index='documents')

    # Method used to insert documents
    #def insert_document(self, document):
    #    return self.es.index(index='my_documents', body=document)


    # We use the bulk methode to insert the documents because it will insert all them as a single document
    # It's also scale well for the case we have many documents
    def insert_documents(self, documents):
        operations = []
        for document in documents:
            operations.append({'index': {'_index': 'documents'}})
            operations.append(document)

        # Execute bulk operation
        response = self.es.bulk(operations=operations)
        
        # Check if any errors occurred during insertion
        if response['errors']:
            print("Errors occurred while inserting documents.")
        else:
            print(f"Successfully inserted {len(documents)} documents.")
        return response


    # The reindex method does what the create_index and insert_document does at the same time
    # Change documents to my documents
    def reindex(self):
        self.create_index()
        with open('construction_material.json', 'rt') as f:
            documents = json.loads(f.read())
        return self.insert_documents(documents)
    

    # The search methods is used to submit a search query
    def search(self, **query_args):
        return self.es.search(index='documents', **query_args)
        # Modifier my_documents en documents
    

    # Method to locate a document and print out all it's contain
    def retrieve_document(self, id):
        return self.es.get(index='documents', id=id)

