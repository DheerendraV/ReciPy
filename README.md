# CS242-project

## To crawl
1. Go to scripts directory
2. Run crawl.sh

## To index with lucene
1. Go to scripts directory 
2. (Optional) Run indexHelper.sh [helper script to show what flags you can use]
3. Run runIndexer.sh

## To index with BERT
1. Go to scripts directory 
2. Run bert-indexer.sh

## To search the indexes
1. Go to scripts
2. Run bertSearch.sh or luceneSearch.sh

## Dependencies and Requirements
- Must have MongoDB Installed for crawlers to transfer data into
- MongoDB Compass highly recommended
- Lucene was used for indexing
- Libraries for BERT: faiss, sklearn and torch
- Indexing Data (if NOT using provided json)
    - Export crawled data from MongoDB Compass as json file
    - Replace sample json file in indexing directory
    - Run indexer (see above)
    - NOTE: current json is sample data we crawled with our crawlers already

## Repo Info
- API/: Folder for FastAPI Application Server
- crawlers/: one for each source
- data/: this folder contains the data collected from all the individual data-sources
- scripts/: folder with relevant scripts
    - crawl.sh: will launch all the crawlers in parallel 
    - *C.sh: will run the individual site crawlers. this can be used to test/ crawl individually
    - indexHelper.sh to get help for the flags that can be used
    - runIndexer.sh -f [filename] -d [directory] -t [testing] -q [query on]-c [results count] -m [sample size for testing]
- indexer/: folder to keep indexing related information such as:
    - json file for all recipes. 
    - indexing class file
    
- recipy-client/: client code (Client Deployed here https://ir-client.vercel.app/)
- utils/: contains the scripts used by the team for schema validation and data aggregation. 
    - DataAggregation.py - used to build the merged data set ("final-recipes.json")
    - IRSchemaLint.py - used to validate the schema for a given parser again the standard definition
