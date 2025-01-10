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
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('RAG_API_KEY')}",
    }

    # Make the POST request
    response = requests.post(
        url,
        json=payload,
        headers=headers,
        proxies={"http": None, "https": None}  # Local use, no proxies...
        #proxies={"http": os.getenv("HTTP_PROXY", None), "https": os.getenv("HTTPS_PROXY", None)}  # Use this only if you have any proxies...
    )

    if response.status_code == 200:
        print(response.json().get("response"))
    else:
        print("Error:", response.status_code)

Author: Mikel Sagardia
Date: 2025-01-10
"""
from pydantic import BaseModel

from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import RedirectResponse

from rag import chatbot, RAG_API_KEY


# FastAPI app
app = FastAPI()
security = HTTPBearer()


class Body(BaseModel):
    query: str


@app.get('/')
def root():
    return RedirectResponse(url='/docs', status_code=301)


@app.post("/ask")
def ask(body: Body, credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != RAG_API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
    chatbot_response = chatbot(body.query)
    return {'response': chatbot_response}
