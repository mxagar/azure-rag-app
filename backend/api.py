import os
from os.path import dirname
from pprint import pprint
from dotenv import load_dotenv

import openai
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI
from langchain.vectorstores import AzureSearch
from langchain_community.retrievers import AzureAISearchRetriever

# Embeddings
# Store
# Retriever
# Chat

app = FastAPI()

# Load environment variables
current_dir = os.path.abspath(".")
root_dir = dirname(current_dir)
env_file = os.path.join(root_dir, '.env')
env_file_loaded = False
try:
    env_file_loaded = load_dotenv(env_file, override=True)
except Exception as e:
    print(f"Error loading .env file: {e}")

# Retrieve Azure credentials and variables
azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
azure_openai_endpoint_uri = os.getenv("AZURE_OPENAI_ENDPOINT_URI")
embedding_deployment_name = os.getenv("EMBEDDING_DEPLOYMENT_NAME")
chat_deployment_name = os.getenv("CHAT_DEPLOYMENT_NAME")
azure_openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")
azure_openai_api_version = os.getenv("AZURE_OPENAI_API_VERSION")
azure_search_api_key = os.getenv("AZURE_SEARCH_API_KEY")
azure_search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
azure_search_index_name = os.getenv("AZURE_SEARCH_INDEX_NAME")

# Connect to Azure OpenAI - Embeddings Model
embeddings = AzureOpenAIEmbeddings(
    deployment=embedding_deployment_name,
    azure_endpoint=azure_openai_endpoint,  # Short/base URL
    api_version=azure_openai_api_version,
    api_key=azure_openai_api_key,
    chunk_size=1
)

# Connect to Azure AI Search
search = AzureSearch(
    azure_search_endpoint=azure_search_endpoint,
    azure_search_key=azure_search_api_key,
    index_name=azure_search_index_name,
    embedding_function=embeddings.embed_query,
)

# Connect to Azure AI Search Retriever
retriever = AzureAISearchRetriever(
    content_key="content",
    api_key=azure_search_api_key,
    index_name=azure_search_index_name,
    service_name=azure_search_endpoint,
    top_k=1,
)

# Initialize Azure OpenAI - Chat Model
chat_model = AzureChatOpenAI(
    azure_endpoint=azure_openai_endpoint_uri, # Long URI, not the base
    openai_api_version=azure_openai_api_version,
    openai_api_key=azure_openai_api_key,
    temperature=0.7,
    max_tokens=2000,
    top_p=0.8,
)


class Body(BaseModel):
    query: str


@app.get('/')
def root():
    return RedirectResponse(url='/docs', status_code=301)


@app.post('/ask')
def ask(body: Body):
    """
    Use the query parameter to interact with the Azure OpenAI Service
    using the Azure Cognitive Search API for Retrieval Augmented Generation.
    """
    search_result = search(body.query)
    chat_bot_response = assistant(body.query, search_result)
    return {'response': chat_bot_response}



def search(query):
    """
    Send the query to Azure Cognitive Search and return the top result
    """
    docs = search.similarity_search_with_relevance_scores(
        query=query,
        k=5,
    )
    result = docs[0][0].page_content
    print(result)
    return result


def assistant(query, context):
    messages=[
        # Set the system characteristics for this chat bot
        {"role": "system", "content": "Asisstant is a chatbot that helps you find the best wine for your taste."},

        # Set the query so that the chatbot can respond to it
        {"role": "user", "content": query},

        # Add the context from the vector search results so that the chatbot can use
        # it as part of the response for an augmented context
        {"role": "assistant", "content": context}
    ]

    response = openai.ChatCompletion.create(
        engine="demo-alfredo",
        messages=messages,
    )
    return response['choices'][0]['message']['content']