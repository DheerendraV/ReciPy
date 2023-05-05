import faiss
from transformers import AutoTokenizer, AutoModel
import torch
import json
import random

## Converts query into word embeddings similar to the documents
def convert_to_embedding(query, model, tokenizer):
    tokens = {'input_ids': [], 'attention_mask': []}

    new_tokens = tokenizer.encode_plus(query, max_length=512,
                                       truncation=True, padding='max_length',
                                       return_tensors='pt')
    
    tokens['input_ids'].append(new_tokens['input_ids'][0])
    tokens['attention_mask'].append(new_tokens['attention_mask'][0])
    tokens['input_ids'] = torch.stack(tokens['input_ids'])
    tokens['attention_mask'] = torch.stack(tokens['attention_mask'])

    with torch.no_grad():
        outputs = model(**tokens)

    embeddings = outputs.last_hidden_state
    attention_mask = tokens['attention_mask']
    mask = attention_mask.unsqueeze(-1).expand(embeddings.size()).float()
    masked_embeddings = embeddings * mask
    summed = torch.sum(masked_embeddings, 1)
    summed_mask = torch.clamp(mask.sum(1), min=1e-9)
    mean_pooled = summed / summed_mask
    
    # Return first index as query is a single sentence 
    return mean_pooled[0] 

## Get k Ranked Documents (BERT)
def getRankedDocs(query,k):
    tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-distilroberta-v1') 
    model = AutoModel.from_pretrained('sentence-transformers/all-distilroberta-v1')
    
    with open("../data/index_keys_list.json","r") as fp:
        documents = json.load(fp)
    
    # Convert query into an embedding
    query_embedding = convert_to_embedding(query, model, tokenizer)

    index_loaded = faiss.read_index("../data/reciPY.index")
    
    # Get indices of ranked documents
    D, I = index_loaded.search(query_embedding[None, :], k)

    results = []
    for id in I[0]:
        try:
            results.append(documents[id])
        except:
            print(f"index {id} skipped")

    return results

## Format Results according to Schema
def parseQueryAnswer(query, results):
    queryAnswer = {"query": query,"rankedDocs": [] }
    for result in results:
        doc = {}
        doc["url"] = result.get('url','')
        doc['title'] = result.get('title',"")
        doc['snippets'] = {}
        doc['snippets']['content'] = " ".join(result.get('directions',''))[:155+random.randint(0,10)]
        doc['snippets']['content'] = doc['snippets']['content'] + "..."
        doc['snippets']['extras'] = {}
        if 'stats' in result.keys():
            if result['stats'].get('totalTime','---') != '---':
                doc['snippets']['extras']['Total time'] = result['stats']['totalTime']
            if result['stats'].get('servings','---') != '---':
                doc['snippets']['extras']['Servings'] = result['stats']['servings']
            if 'nutrition' in result['stats'].keys():
                if result['stats']['nutrition'].get('calories','---') != '---':
                    doc['snippets']['extras']['Calories'] = result['stats']['nutrition']['calories']
        queryAnswer['rankedDocs'].append(doc)
    return queryAnswer

def queryAnswer(query,k=10):
    results = getRankedDocs(query,k)
    queryAnswer = parseQueryAnswer(query, results)
    return queryAnswer

if __name__ == "__main__":
    query = input("Enter query:")
    res = queryAnswer(query,5)
    for r in res["rankedDocs"]:
        print(r)
    #print(getRankedDocs("Chicken Tikka Masala",5))