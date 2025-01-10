"""Description.

Original idea/source: https://github.com/alfredodeza/azure-rag
(But the code was considerable changed)

Run (local):

    # Launch FastAPI app locally
    cd .../azure-rag-app
    uvicorn --env-file .env --host 0.0.0.0 --port 8080 backend.api:app

    # Open browser and go to http://localhost:8080/docs
    # Go to /ask and click on 'Try it out'
    # Enter a question and click on 'Execute', e.g.:
    # "What is the best Bourbon Barrel wine?"
    # Check response in Web UI

Use:

    import requests

    # Define the URL and payload
    url = "http://127.0.0.1:8080/ask"
    payload = {"query": "Which is the best wine?"}
    headers = {
        "Content-Type": "application/json"
    }

    # Make the POST request
    response = requests.post(
        url,
        json=payload,
        headers=headers,
        proxies={"http": None, "https": None}  # Use this only if you have any proxies...
    )

    if response.status_code == 200:
        print(response.json().get("response"))
    else:
        print("Error:", response.status_code)

Author: Mikel Sagardia
Date: 2025-01-10
"""
import os
import pathlib
from dotenv import load_dotenv
from pydantic import BaseModel
import yaml

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI
from langchain_community.vectorstores import AzureSearch
from langchain_community.retrievers import AzureAISearchRetriever
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough


# Load environment variables (local execution)
CURRENT_DIR = pathlib.Path(__file__).parent.resolve()
ROOT_DIR = CURRENT_DIR.parent
ENV_FILE = os.path.join(ROOT_DIR, '.env')
try:
    _ = load_dotenv(ENV_FILE, override=True)
except Exception:
    pass


# Retrieve variables
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_ENDPOINT_URI = os.getenv("AZURE_OPENAI_ENDPOINT_URI")
EMBEDDING_DEPLOYMENT_NAME = os.getenv("EMBEDDING_DEPLOYMENT_NAME")
CHAT_DEPLOYMENT_NAME = os.getenv("CHAT_DEPLOYMENT_NAME")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
AZURE_SEARCH_INDEX_NAME = os.getenv("AZURE_SEARCH_INDEX_NAME")


# Load configuration
def load_config(config_path: str | pathlib.Path) -> dict:
    if isinstance(config_path, pathlib.Path):
        config_path = str(config_path)
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
    except Exception as e:
        print(f"Error loading config.yaml: {e}")

    return config

config_path = CURRENT_DIR / "config.yaml"
config = load_config(config_path=config_path)

# Connect to Azure OpenAI - Embeddings Model
embeddings = AzureOpenAIEmbeddings(
    deployment=EMBEDDING_DEPLOYMENT_NAME,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,  # Short/base URL
    api_version=AZURE_OPENAI_API_VERSION,
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    chunk_size=1
)

# Connect to Azure AI Search
search = AzureSearch(
    azure_search_endpoint=AZURE_SEARCH_ENDPOINT,
    azure_search_key=os.getenv("AZURE_SEARCH_API_KEY"),
    index_name=AZURE_SEARCH_INDEX_NAME,
    embedding_function=embeddings.embed_query,
)

# Connect to Azure AI Search Retriever
retriever = AzureAISearchRetriever(
    content_key="content",
    api_key=os.getenv("AZURE_SEARCH_API_KEY"),
    index_name=AZURE_SEARCH_INDEX_NAME,
    service_name=AZURE_SEARCH_ENDPOINT,
    top_k=1,
)

# Initialize Azure OpenAI - Chat Model
chat_model = AzureChatOpenAI(
    azure_endpoint=AZURE_OPENAI_ENDPOINT_URI,  # Long URI, not the base
    openai_api_version=AZURE_OPENAI_API_VERSION,
    openai_api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    temperature=config.get("chat_temperature", 0.7),
    max_tokens=config.get("chat_max_tokens", 2000),
    top_p=config.get("chat_top_p", 0.8),
)


# FastAPI app
app = FastAPI()


class Body(BaseModel):
    query: str


@app.get('/')
def root():
    return RedirectResponse(url='/docs', status_code=301)


@app.post('/ask')
def ask(body: Body):
    chatbot_response = chatbot(body.query)
    return {'response': chatbot_response}


def create_prompt():
    return ChatPromptTemplate.from_messages([
        ("system", (
            "You are a world-class assistant. "
            "Answer the last question based only on the last context provided. "
        )),
        ("ai", (
            "Context: {context}"
        )),        
        ("human", (
            "Question: {question}"
        )),
    ])


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def chatbot(query: str):
    history = create_prompt()
    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | history
        | chat_model
        | StrOutputParser()
    )
    response = chain.invoke(query)

    return response
