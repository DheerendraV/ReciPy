from transformers import AutoTokenizer, AutoModel
import torch
# comparisons for indexing
from sklearn.metrics.pairwise import cosine_similarity
# actual index building
import faiss
import json
from timeit import default_timer as timer

tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-distilroberta-v1')
model = AutoModel.from_pretrained('sentence-transformers/all-distilroberta-v1')

# Format:
# MAX 512 tokens != words
# ---> Each sentence will be at MOST 355 words
# Our indexing is more than 355 words, so it will be split!
# ---> EACH index object will start with "[recipe-title] [website-name]"
# ---> if we get a HIT on an indexed item, we can work back to the original source that way
# ---> allows us to show a "blurb"
# To work with split, there will be overlap too
# ---> use stride of 1 sentence; the last sentence of the last item will be the first of the new one
# ---> remember! do NOT exceed 355 word limit, or else it will be truncated in indexing
# Should probably hash the [recipe-title] [website-name] part for easier lookup
# ---> even if not exactly a hash, lookup should be fast

with open("../data/final-recipes.json", 'r') as f:
  recipe_file = json.load(f) # returns list of dicts

sentences = [] # where the info to be indexed in will be stored
recipe_keys = {}
sentence_keys = {}
index_keys_list = []
index_keys_dict ={}
MAX_SENT_LENGTH = 355
index_cnt = 0

for recip in recipe_file:
  # create key in case we go over word limit
  reci_key = recip['title'] + ' ' + recip['dataSource']
  # keep length of key for word limit
  reci_length = len(reci_key.split())

  # set hash table so we can return to it later
  # recipe_keys[reci_key] = recip['url']

  # concatinate recipe
  concat_recip = ""
  if 'ingredients' in recip:
    for ingredient in recip['ingredients']:
      concat_recip += ingredient + ' '
  if 'directions' in recip:
    for direction in recip['directions']:
      concat_recip += direction + ' '
  if 'stats' in recip:
    if 'totalTime' in recip and recip['stats']['totalTime'] != "---":
      concat_recip += recip['stats']['totalTime'] + ' '
    if 'servings' in recip and recip['stats']['servings'] != "---":
      concat_recip += recip['stats']['servings'] + ' '

    if 'nutrition' in recip['stats']:
      for nutri in recip['stats']['nutrition']:
        if recip['stats']['nutrition'][nutri] != '---':
          concat_recip += recip['stats']['nutrition'][nutri] + ' ' + nutri + ' '

  concat_recip = concat_recip.replace('.','').replace(',','')
  concat_recip = concat_recip.split()

  # Start indexing sentence builder

  concat_cnt = 0
  while(concat_cnt < len(concat_recip)):
    index_sent = reci_key + " | "
    # index_sent = ""
    word_cnt = reci_length + 1 # word count should start at key size, not 0
    while (word_cnt < MAX_SENT_LENGTH) and (concat_cnt < len(concat_recip)):
      index_sent += concat_recip[concat_cnt] + ' '
      concat_cnt += 1
      word_cnt += 1
    if concat_cnt < len(concat_recip):
      concat_cnt -= 10
    sentences.append(index_sent)
    recipe_keys[index_cnt] = recip['url']
    sentence_keys[index_cnt] = index_sent
    index_keys_list.append(recip)
    index_keys_dict[index_cnt] = recip
    index_cnt += 1

with open("../data/index_keys_list.json", "w") as outfile:
    json.dump(index_keys_list, outfile)

# sentences = sentences[0:600]
sent_groups = []
cnt = 0
step = 300
mean_pools = []
for i in range(int(len(sentences)/ 300)):
    sent_groups.append(sentences[cnt:(cnt+step)])
    cnt += step

if cnt < len(sentences):
    sent_groups.append(sentences[cnt:len(sentences)])

start = timer()

index = faiss.IndexFlatIP(768)

sg_cnt = 0
for sG in sent_groups:
    print(sg_cnt)
    sg_cnt += 1
    tokens = {'input_ids': [], 'attention_mask': []}

    for sentence in sG:
        # encode each sentence and append to dictionary
        new_tokens = tokenizer.encode_plus(sentence, max_length=512,
                                       truncation=True, padding='max_length',
                                       return_tensors='pt')
        tokens['input_ids'].append(new_tokens['input_ids'][0])
        tokens['attention_mask'].append(new_tokens['attention_mask'][0])
  
    tokens['input_ids'] = torch.stack(tokens['input_ids'])
    tokens['attention_mask'] = torch.stack(tokens['attention_mask'])

    with torch.no_grad():
        outputs = model(**tokens)
    # outputs.keys() # for debugging
    embeddings = outputs.last_hidden_state  # this is the only part we need to access
    # embeddings.shape  # for testing, should be [# sentences, 512, 768]

    # resize our attention_mask tensor:
    attention_mask = tokens['attention_mask']
    # attention_mask.shape  # for testing, should be [# sentences, 512]

    mask = attention_mask.unsqueeze(-1).expand(embeddings.size()).float()
    # mask.shape  # for testing, should be [# sentences, 512, 768]

    # apply the mask to filter useless tokens (padding)
    masked_embeddings = embeddings * mask

    # Then we sum the remained of the embeddings along axis 1, because we want to reduce the 512 tokens to 1 dimension
    summed = torch.sum(masked_embeddings, 1)
    # summed.shape  # for testing, should be [# sentences, 768]

    # clamp returns the same tensor with a range given, clamp is used to replace the zeros to a very minimal value
    # to avoid divide by zero error
    summed_mask = torch.clamp(mask.sum(1), min=1e-9)
    mean_pooled = summed / summed_mask

    index.add(mean_pooled)
# temp_tensor = mean_pools[0]
# for x in range(1, len(mean_pools)):
#     temp_tensor = torch.cat((temp_tensor, mean_pools[x]),0)

# Once we have the mean pooled values, we can just do the work with FAISS
# index = faiss.IndexFlatIP(768)   # build the index
print(index.is_trained)
# index.add(temp_tensor)           # add vectors to the index
print(index.ntotal)

# output index for query use
faiss.write_index(index,"../data/reciPY.index")

end = timer()
print("Training Time = ", end-start)

# with open('full_time.txt', 'w') as timeOut:
#     timeOut.write(str(end-start))
