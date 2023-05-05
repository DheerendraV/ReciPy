# Run with first argument as location of Index folder

import sys, os, lucene
from java.nio.file import Paths
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.queryparser.classic import QueryParser, QueryParserBase
from org.apache.lucene.queryparser.classic import MultiFieldQueryParser as mfqp
from org.apache.lucene.store import NIOFSDirectory
from org.apache.lucene.search import IndexSearcher

import random

INDEX_DIR = "../data/reciPYLucene/"


def run(searcher, analyzer, query, k):

    queryAnswer = {"query": query, "rankedDocs": []}

    query = mfqp.parse([query, query], ["directions", "title"],analyzer)

    scoreDocs = searcher.search(query, k).scoreDocs
    print(f"{len(scoreDocs)} total matching documents.")

    for hit in scoreDocs:
        result = searcher.doc(hit.doc)

        doc = {}
        doc["url"] = result.get('url',)
        doc['title'] = result.get('title')
        doc['snippets'] = {}
        try:
            directions = result.get('directions')
            doc['snippets']['content'] = directions[:155+random.randint(0,10)]
            doc['snippets']['content'] = doc['snippets']['content'] + "..."
            directions = ""
        except:
            print("directions error")
        doc['snippets']['extras'] = {}
        if result.get('total Time') != '---':
            doc['snippets']['extras']['Total time'] = result.get('totalTime')
        if result.get('servings') != '---':
            doc['snippets']['extras']['Servings'] = result.get('servings')
        if result.get('calories') != '---':
            doc['snippets']['extras']['Calories'] = result.get('calories')

        queryAnswer['rankedDocs'].append(doc)

    return queryAnswer


def searchAnswer(query, k):
    try:
        lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    except:
        print("Lucene is running")

    directory = NIOFSDirectory(Paths.get(INDEX_DIR))

    searcher = IndexSearcher(DirectoryReader.open(directory))
    analyzer = StandardAnalyzer()
    return run(searcher, analyzer, query, k)


if __name__ == '__main__':
    query = input("Enter query:")
    res = searchAnswer(query, 10)
    for r in res["rankedDocs"]:
        print(r)