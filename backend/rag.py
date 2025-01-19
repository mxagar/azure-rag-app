"""This module contains the implementation of
a RAG (Retrieval-Augmented Generation) system.

Azure services are used:

- Azure OpenAI for embeddings and chat models
- Azure AI Search for document search/retrieval

Those need to be setup beforehand.

Author: Mikel Sagardia
Date: 2025-01-10
"""
import os
import pathlib
from dotenv import load_dotenv
from typing import List
import yaml

from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI
from langchain_community.vectorstores import AzureSearch
from langchain_community.retrievers import AzureAISearchRetriever
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.documents.base import Document

from preprocessing import get_preprocessor


# Define paths
CURRENT_DIR = pathlib.Path(__file__).parent.resolve()
ROOT_DIR = CURRENT_DIR.parent


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


# Load environment variables (local execution)
ENV_FILE = os.path.join(ROOT_DIR, config.get("env_file", ".env"))
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
# RAG API Key
RAG_API_KEY = os.getenv("RAG_API_KEY")


# Connect to Azure OpenAI - Embeddings Model
embeddings = AzureOpenAIEmbeddings(
    deployment=EMBEDDING_DEPLOYMENT_NAME,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,  # Short/base URL
    api_version=AZURE_OPENAI_API_VERSION,
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    chunk_size=1
)

# Connect to Azure AI Search
vectorstore = AzureSearch(
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
    top_k=config.get("retriever_top_k", 3),
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


def chat(query: str):
    history = create_prompt()
    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | history
        | chat_model
        | StrOutputParser()
    )
    response = chain.invoke(query)

    return response


def ingest(
    filenames: str | pathlib.Path | List[pathlib.Path|str],
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    percentage: float = 1.0,
) -> List[str]:
    if isinstance(filenames, pathlib.Path) or isinstance(filenames, str):
        filenames = [filenames]
    docs = []

    for file in filenames:
        preprocessor = get_preprocessor(str(file), chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        d = preprocessor.load_split(file)
        docs.extend(d)

    if percentage < 1.0:
        docs = docs[:int(len(docs) * percentage)]

    ids = vectorstore.add_documents(documents=docs)

    return ids


def retrieve(
    query: str,
    top_k: int = 1
) -> List[Document]:
    docs = retriever.invoke(query)

    config_top_k = config.get("retriever_top_k", None)
    if config_top_k is not None:
        # Sort and filter the documents by the score in descending order and pick the top k
        k = min(top_k, len(docs))  # Ensure k is not greater than the number of documents
        top_k_docs = sorted(docs, key=lambda doc: doc.metadata['@search.score'], reverse=True)[:k]

        return top_k_docs

    return docs
