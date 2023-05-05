from typing import Union

from bertQuery import queryAnswer
from luceneQuery import searchAnswer
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_headers=["*"],
    allow_methods=["*"],
    
)


class requestBody(BaseModel):
    searchText: str
    indexOption: str


@app.post("/search")
async def root(item: requestBody):
    if item.indexOption == 'bert':
        print("In Bert Indexing")
        result = queryAnswer(item.searchText,30)
    elif item.indexOption == 'lucene':
        print("In Lucene Indexing")
        result = searchAnswer(item.searchText,30)
    return result
