# Infrastructure


## Table of Contents

- [Infrastructure](#infrastructure)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Azure OpenAI](#azure-openai)
  - [Azure AI Search](#azure-ai-search)
      - [Azure Services Deployment: Azure AI Search and Azure OpenAI](#azure-services-deployment-azure-ai-search-and-azure-openai)
  - [Azure Container App Deployment](#azure-container-app-deployment)
  - [Further Details: Service Principal and Tokens](#further-details-service-principal-and-tokens)
    - [Azure Credentials: Service Principal](#azure-credentials-service-principal)
      - [Github Personal Access Token](#github-personal-access-token)
  - [Summary of Variables and Secrets](#summary-of-variables-and-secrets)
  - [Github Actions Workflow Overview](#github-actions-workflow-overview)
  - [Triggering the Deployment](#triggering-the-deployment)
  - [FastAPI](#fastapi)
    - [Add your keys](#add-your-keys)
  - [Generate a PAT](#generate-a-pat)
  - [Create an Azure Service Principal](#create-an-azure-service-principal)
  - [Azure Container Apps](#azure-container-apps)
  - [Change defaults](#change-defaults)
  - [Gotchas](#gotchas)
  - [API Best Practices](#api-best-practices)
    - [Use HTTP Error codes](#use-http-error-codes)
    - [Accept request types sparingly](#accept-request-types-sparingly)

## Overview

First, we need to 

- Azure AI Search (access from everywhere):
  - It will contain and index.
  - We need to fill in the index programmatically, as shown in the previous section.
- Azure OpenAI (access from everywhere)
  - Chat model, e.g., `gpt-4o-mini`
  - Embeddings model, e.g., `text-embedding-ada-002`

Second, we need to 

Finally, the deployment deployment of the backend occurs following these steps:

1. Our code is pushed to Github
2. Github Actions packages he code into an image (Dockerfile) 
3. Github Actions triggers the building the Container
4. The resulting Container is pushed to the Github Container Registry
5. Github Actions triggers the pulling of the Container on Azure

Even though we have deployed one container, Azure takes care of the scaling automatically performing horizontal scaling: if more users request/use the app, more replicas are deployed.

## Azure OpenAI

![Azure OpenAI](../assets/create_azure_open_ai.png)

![Azure OpenAI Model Update](../assets/azure_openai_model_update.png)

![Azure AI Foundry Deployments](../assets/auzure_ai_foundry_deployments.png)

![Azure AI Foundry Playground](../assets/auzure_ai_foundry_playground.png)

## Azure AI Search

![Create Azure AI Search](../assets/create_azure_ai_search.png)

![Azure AI Search](../assets/azure_ai_search_service.png)

#### Azure Services Deployment: Azure AI Search and Azure OpenAI

We need to deploy the following Azure services beforehand. Additionally, we need to save/note their associated secrets and variables separately.

Here's a summary of my manual deployments:

- Azure AI Search (France Central):
  - It will contain and index.
  - We need to fill in the index programmatically, as shown in the previous section.
  - Variables created:
    - `AZURE_SEARCH_INDEX_NAME=demo-coursera-ai-search`
    - `AZURE_SEARCH_API_KEY=xxx`
    - `AZURE_SEARCH_ENDPOINT=https://demo-coursera-ai-search.search.windows.net`
  - Other names:
    - RG name Azure Search: `rg-demo-coursera-ai-search`
    - Azure Search service name: `demo-coursera-ai-search`
- Azure OpenAI (East US, access from everywhere)
  - Chat model, deployed beforehand.
    - `CHAT_DEPLOYMENT_NAME=gpt-4o-mini`
  - Embeddings model, deployed beforehand.
    - `EMBEDDING_DEPLOYMENT_NAME=text-embedding-ada-002`
  - Further variables created:
    - `AZURE_OPENAI_API_VERSION=2024-08-01-preview`
    - `AZURE_OPENAI_API_KEY=xxx`
    - Short/base endpoint: `AZURE_OPENAI_ENDPOINT=https://demo-coursera-azure-openai.openai.azure.com/`
    - Long URI: `AZURE_OPENAI_ENDPOINT_URI=https://demo-coursera-azure-openai.openai.azure.com/openai/deployments/gpt-4o-mini/chat/completions?api-version=2024-08-01-preview`
  - Other names:
    - RG name OpenAI: `rg-demo-coursera-azure-openai`
    - OpenAI service name: `demo-coursera-azure-openai`

After that, we have a similar situation as in the previous section.

Now, we can start preparing our Azure Container App service which will contain the app in [mxagar/azure-rag-app](https://github.com/mxagar/azure-rag-app).

Note that if we make use of additional services, i.e., Azure Document Intelligence, we need to deploy them similarly and note/store their associated variables/secrets similarly.

:warning: **Never commit secrets!**

## Azure Container App Deployment

To deploy the app in [mxagar/azure-rag-app](https://github.com/mxagar/azure-rag-app) we need to deploy an [Azure Container App](https://azure.microsoft.com/en-us/products/container-apps); another option would have been an [Azure Web App or App Service](https://azure.microsoft.com/en-us/products/app-service/web). Check this link:

[Azure App Service vs Azure Container Apps - which to use?](https://learn.microsoft.com/en-us/answers/questions/1337789/azure-app-service-vs-azure-container-apps-which-to); TLDR; both are scalable and very similar, but Azure Container Apps seem to offer more control on the container image we want to use and the overal configuration.

    Azure Portal: Search Container App > Create
      Subscription: Azure subscription 1
      Resource group: (new) rg-demo-coursera-rag-backend
      Container app name: demo-coursera-rag-backend
        We need this name later!
      Deployment source: Container image
      Region: France Central
    Container: we can select the Quickstart image for now: Simple hello world container

![Create Container App](./assets/create_container_app.png)

We can select the Quickstart image in the beginning (Simple hello world container); alternatively, if we already have pushed our image to a registry, we can define it in the Container tab. Once deployed, if we go to our resource, we see it has an URL we can visit.

![Container App](./assets/container_app.png)

Interesting links:

- [Quickstart: Build and deploy from local source code to Azure Container Apps](https://learn.microsoft.com/en-us/azure/container-apps/quickstart-code-to-cloud?tabs=bash%2Cpython)
- [Azure Container Apps samples](https://learn.microsoft.com/en-us/azure/container-apps/samples)

## Further Details: Service Principal and Tokens


### Azure Credentials: Service Principal

To set the Azure credentials, we need a **Service Principal** in Azure. A Service Principal in Azure is a security identity used by applications, services, or automation tools to access specific Azure resources. It operates like a user identity but is specifically designed for non-human interactions, such as running applications, scripts, or CI/CD pipelines securely.

To create a Service Principal:

1. We need to install [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli-windows?tabs=azure-cli).
2. We need to log in using the Azure CLI; when we run the command, a web browser will open to log in; then, we will get back a JSON which conatins information about our subscriptions.
```bash
az login
```
3. We need the [Azure subscription ID](https://portal.azure.com/#view/Microsoft_Azure_Billing/SubscriptionsBladeV2) associated with our resources: `AZURE_SUBSCRIPTION_ID`; if problems, [check this guide](https://docs.microsoft.com/en-us/azure/azure-portal/get-subscription-tenant-id).
4. We need to create a Service Principal with the following details: the AppID, password, and tenant information.
    - Create one with this command and assign the IAM role for the subscription (I did not try this one, but the next).
    ```bash
    az ad sp create-for-rbac -n "REST API Service Principal"
    ```
    - **(Recommended) Alternatively**, set the proper role access using the following command, and save the output JSON, to be set in Github as the value of `AZURE_CREDENTIALS`:
    ```bash
    az ad sp create-for-rbac --name "CICD" --role contributor --scopes /subscriptions/$AZURE_SUBSCRIPTION_ID --sdk-auth
    ``` 

I saved in the uncommitted/ignored `.azure_credentials` all the output from both commands.

#### Github Personal Access Token

| Variable | Type | From | Description | (Example) Value |
|---|---|---|---|---|
| A | secret/variable | Azure/Github | Bla | xxx |


The access token will need to be added as an Action secret.
It is needed because Azure will need to authenticate against the GitHub Container Registry to pull the image.

- [Create one Gihub Personal Access Token (PAT)](https://github.com/settings/tokens/new?description=Azure+Container+Apps+access&scopes=write:packages) with enough permissions to write to packages. Manual access in Github web UI: `Profile > Developer settings (left menu) > Personal access tokens > Tokens (classic)`. Use scope: `write:packages`.
- Save it in `.env` for now as `GH_PAT`.

![Github PAT](./assets/github_pat.png)

## Summary of Variables and Secrets

Now, we can insert all the variable and secret values into our Github repository, i.e., [mxagar/azure-rag-app](https://github.com/mxagar/azure-rag-app).

- We can either define the variables in the YAML or also in Github Web UI: Repo > Settings > Secrets and variables: Actions > Repository variables
  - Then, they are accessible in the YAML as `${{ env.VARIABLE_NAME }}`
- BUT: The secrets need to be entered in the Github Web UI: Repo > Settings > Secrets and variables: Actions > Repository secrets
  - Then, they are accessible in the YAML as `${{ secrets.VARIABLE_NAME }}`

![Github Variables and Secrets](./assets/github_variables_secrets.png)

The values must have been collected so far, and they have been referenced in the workflow `.github/workflows/main.yaml`.

Variables:

```bash
# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://<azure-openai-resource-name>.openai.azure.com
AZURE_OPENAI_ENDPOINT_URI=<AZURE_OPENAI_ENDPOINT>/openai/deployments/<CHAT_DEPLOYMENT_NAME>/chat/completions?api-version=<AZURE_OPENAI_API_VERSION>
AZURE_OPENAI_API_VERSION=2024-08-01-preview
CHAT_DEPLOYMENT_NAME=<chat-deployment-name>
EMBEDDING_DEPLOYMENT_NAME=<embedding-deployment-name>
# Azure AI Search
AZURE_SEARCH_ENDPOINT=https://<azure-search-service-name>.search.windows.net
AZURE_SEARCH_INDEX_NAME=<azure-search-index-name>
# Azure Container App
AZURE_CONTAINER_APP_NAME=<>
AZURE_CONTAINER_RG_NAME=<>

# --- NOT USED:
# Azure Document Intelligence (PDF parser)
AZURE_DOCUMENTINTELLIGENCE_ENDPOINT=https://<azure-document-intelligence-name>.cognitiveservices.azure.com/
```

Secrets:

```bash
# Azure OpenAI (Obtainable from Azure Portal - Keys)
AZURE_OPENAI_API_KEY=xxx
# Azure AI Search (Obtainable from Azure Portal - Keys)
AZURE_SEARCH_API_KEY=xxx
# Azure Credential (JSON obtained when creating Service Principal)
AZURE_CREDENTIALS=xxx
# Github Credential (PAT, obtained from Github)
GH_PAT=xxx

# --- NOT USED:
# Azure Subscription ID
AZURE_SUBSCRIPTION_ID=xxx
# Azure Document Intelligence (Obtainable from Azure Portal - Keys)
AZURE_DOCUMENTINTELLIGENCE_API_KEY=xxx
```

## Github Actions Workflow Overview

The Container App will have running the container of the app defined in [mxagar/azure-rag-app](https://github.com/mxagar/azure-rag-app); that app will be packaged into an image which will be stored in the Github Container Registry, as a package. All that happens in the Github Actions Workflow `.github/workflows/main.yaml` from the app repository. Note that we could also use another registry, though, e.g., an Azure registry.

Some important points to consider in `.github/workflows/main.yaml`:

- `AZURE_CONTAINER_APP_NAME`, `AZURE_CONTAINER_RG_NAME`: These are the names related to the deployed Container App.
  - We can either define the variables in the YAML or also in Github Web UI: Repo > Settings > Secrets and variables: Actions > Repository variables
    - Then, they are accessible in the YAML as `${{ env.VARIABLE_NAME }}`
  - BUT: The secrets need to be entered in the Github Web UI: Repo > Settings > Secrets and variables: Actions > Repository secrets
    - Then, they are accessible in the YAML as `${{ secrets.VARIABLE_NAME }}`
- `on: workflow_dispatch`: This allows to trigger the workflow manually.
- We have two `jobs`: `build` and `deploy`:
  - `jobs: build`: This is the job of the workflow that builds the container:
    - It uses pre-defined actions to checkout the branch, setup build, log in to the container registry, and build and push.
    - Some secrets/variables are automatic: `github.actor`, etc.
  - `jobs: deploy`: This is the job of the workflow that deploys the container:
    - Here, we log in to Azure and then the `az-cli` commands for deployment are executed.
    - Some secrets/variables need to be set in the Github Web UI, e.g.: `secrets.AZURE_CREDENTIALS`.

The values of the variables and the secrets are defined and collected in different steps.
See [Setting the Variables and Secrets of the Github Action/Workflow](#setting-the-variables-and-secrets-of-the-github-actionworkflow) below.

Contents in `.github/workflows/main.yaml`:

```yaml
name: Trigger auto deployment for RAG app container

#env:
#  AZURE_CONTAINER_APP_NAME: <app-container-name>
#  AZURE_CONTAINER_RG_NAME: <app-container-rg-name>

# When this action will be executed
on:
  # Automatically trigger it when detected changes in repo. Remove comments to enable
  #push:
  #  branches:
  #    [ main ]

  # Allow mannually trigger
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout to the branch
        uses: actions/checkout@v2

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v1

      - name: Log in to GitHub container registry
        uses: docker/login-action@v1.10.0
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GH_PAT }}

      - name: Lowercase the repo name and username
        run: echo "REPO=${GITHUB_REPOSITORY,,}" >>${GITHUB_ENV}

      - name: Build and push container image to registry
        uses: docker/build-push-action@v2
        with:
          push: true
          tags: ghcr.io/${{ env.REPO }}:${{ github.sha }}
          file: ./Dockerfile

  deploy:
    runs-on: ubuntu-latest
    needs: build

    steps:
      - name: Azure Login
        uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}

      - name: Lowercase the repo name and username
        run: echo "REPO=${GITHUB_REPOSITORY,,}" >>${GITHUB_ENV}

      - name: Deploy to containerapp
        uses: azure/CLI@v1
        with:
          inlineScript: |
            az config set extension.use_dynamic_install=yes_without_prompt
            az containerapp registry set -n ${{ env.AZURE_CONTAINER_APP_NAME }} -g ${{ env.AZURE_CONTAINER_RG_NAME }} --server ghcr.io --username  ${{ github.actor }} --password ${{ secrets.GH_PAT }}
            az containerapp update \
              -n ${{ env.AZURE_CONTAINER_APP_NAME }} \
              -g ${{ env.AZURE_CONTAINER_RG_NAME }} \
              --set-env-vars \
              OPENAI_API_TYPE=azure \
              AZURE_OPENAI_ENDPOINT=${{ env.AZURE_OPENAI_ENDPOINT }} \
              AZURE_OPENAI_API_KEY=${{ secrets.AZURE_OPENAI_API_KEY }} \
              AZURE_OPENAI_API_VERSION=${{ env.AZURE_OPENAI_API_VERSION }} \
              AZURE_SEARCH_ENDPOINT=${{ env.AZURE_SEARCH_ENDPOINT }} \
              AZURE_SEARCH_API_KEY=${{ secrets.AZURE_SEARCH_API_KEY }} \
              AZURE_SEARCH_INDEX_NAME=${{ env.AZURE_SEARCH_INDEX_NAME }}
            az containerapp update -n ${{ env.AZURE_CONTAINER_APP_NAME }} -g ${{ env.AZURE_CONTAINER_RG_NAME }} --cpu 2 --memory 4Gi
            az containerapp update -n ${{ env.AZURE_CONTAINER_APP_NAME }} -g ${{ env.AZURE_CONTAINER_RG_NAME }} --image ghcr.io/${{ env.REPO }}:${{ github.sha }}
```

What's happening during the deployment?

```bash
# Configure the Azure CLI to automatically install required extensions without asking for user confirmation.
az config set extension.use_dynamic_install=yes_without_prompt
# Configure an Azure Container App to authenticate with a container image registry (e.g., GitHub Container Registry) to pull container images.
az containerapp registry set -n ${{ env.AZURE_CONTAINER_APP_NAME }} -g ${{ env.AZURE_CONTAINER_RG_NAME }} --server ghcr.io --username  ${{ github.actor }} --password ${{ secrets.GH_PAT }}
# Update the environment variables for the specified Azure Container App
# These variables would be usually in our .env
# We can add here all the variables we need, BUT NO secrets!
az containerapp update \
  -n ${{ env.AZURE_CONTAINER_APP_NAME }} \
  -g ${{ env.AZURE_CONTAINER_RG_NAME }} \
  --set-env-vars \
  OPENAI_API_TYPE=azure \
  AZURE_OPENAI_ENDPOINT=${{ env.AZURE_OPENAI_ENDPOINT }} \
  AZURE_OPENAI_API_KEY=${{ secrets.AZURE_OPENAI_API_KEY }} \
  AZURE_OPENAI_API_VERSION=${{ env.AZURE_OPENAI_API_VERSION }} \
  AZURE_SEARCH_ENDPOINT=${{ env.AZURE_SEARCH_ENDPOINT }} \
  AZURE_SEARCH_API_KEY=${{ secrets.AZURE_SEARCH_API_KEY }} \
  AZURE_SEARCH_INDEX_NAME=${{ env.AZURE_SEARCH_INDEX_NAME }}
# Update the compute resources allocated to the container app: 2 CPUs, 4GB memory
az containerapp update -n ${{ env.AZURE_CONTAINER_APP_NAME }} -g ${{ env.AZURE_CONTAINER_RG_NAME }} --cpu 2 --memory 4Gi
# Deploy a new version of the container app using an updated container image from the registry
az containerapp update -n ${{ env.AZURE_CONTAINER_APP_NAME }} -g ${{ env.AZURE_CONTAINER_RG_NAME }} --image ghcr.io/${{ env.REPO }}:${{ github.sha }}
```

## Triggering the Deployment


![Github Actions](../assets/github_actions.png)

![Triggering Github Workflow](../assets/github_workflow.png)


## FastAPI

![FastAPI Swagger](../assets/fast_api.png)


### Add your keys

Find the Azure OpenAI Keys in the Azure OpenAI Service. Note, that keys aren't in the studio, but in the resource itself. Add them to a local `.env` file. This repository ignores the `.env` file to prevent you (and me) from adding these keys by mistake.

Your `.env` file should look like this:

```
# Azure OpenAI
OPENAI_API_TYPE="azure"
OPENAI_API_BASE="https://demo-alfredo-openai.openai.azure.com/"
OPENAI_API_KEY="x"
OPENAI_API_VERSION="2023-07-01-preview"

# Azure Cognitive Search
SEARCH_SERVICE_NAME="https://demo-alfredo.search.windows.net"
SEARCH_API_KEY="x"
SEARCH_INDEX_NAME="demo-index"
```

Note that the Azure Cognitive Search is only needed if you are following the Retrieval Augmented Guidance (RAG) demo. It isn't required for a simple Chat application.

## Generate a PAT

The access token will need to be added as an Action secret. [Create one](https://github.com/settings/tokens/new?description=Azure+Container+Apps+access&scopes=write:packages) with enough permissions to write to packages. It is needed because Azure will need to authenticate against the GitHub Container Registry to pull the image.

## Create an Azure Service Principal

You'll need the following:

1. An Azure subscription ID [find it here](https://portal.azure.com/#view/Microsoft_Azure_Billing/SubscriptionsBlade) or [follow this guide](https://docs.microsoft.com/en-us/azure/azure-portal/get-subscription-tenant-id)
1. A Service Principal with the following details the AppID, password, and tenant information. Create one with: `az ad sp create-for-rbac -n "REST API Service Principal"` and assign the IAM role for the subscription. Alternatively set the proper role access using the following command (use a real subscription id and replace it):

```
az ad sp create-for-rbac --name "CICD" --role contributor --scopes /subscriptions/$AZURE_SUBSCRIPTION_ID --sdk-auth
``` 


## Azure Container Apps

Make sure you have one instance already created, and then capture the name and resource group. These will be used in the workflow file.

## Change defaults 

Make sure you use 2 CPU cores and 4GB of memory per container. Otherwise you may get an error because loading HuggingFace with FastAPI requires significant memory upfront.

## Gotchas

There are a few things that might get you into a failed state when deploying:

* Not having enough RAM per container
* Not using authentication for accessing the remote registry (ghcr.io in this case). Authentication is always required
* Not using a `GITHUB_TOKEN` or not setting the write permissions for "packages". Go to `settings/actions` and make sure that "Read and write permissions" is set for "Workflow permissions" section
* Different port than 80 in the container. By default Azure Container Apps use 80. Update to match the container.

If running into trouble, check logs in the portal or use the following with the Azure CLI:

```
az containerapp logs  show  --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP_NAME --follow
```

Update both variables to match your environment

## API Best Practices

Although there are a few best practices for using the FastAPI framework, there are many different other suggestions to build solid HTTP APIs that can be applicable anywhere. 

### Use HTTP Error codes
The HTTP specification has several error codes available. Make use of the appropriate error code to match the condition that caused it. For example the `401` HTTP code can be used when access is unauthorized. You shouldn't use a single error code as a catch-all error.

Here are some common scenarios associated with HTTP error codes:

- `400 Bad request`: Use this to indicate a schema problem. For example if the server expected a string but got an integer
- `401 Unauthorized`: When authentication is required and it wasn't present or satisfied
- `404 Not found`: When the resource doesn't exist

Note that it is a good practice to use `404 Not Found` to protect from requests that try to find if a resource exists without being authenticated. A good example of this is a service that doesn't want to expose usernames unless you are authenticated.


### Accept request types sparingly

| GET | POST | PUT | HEAD|
|---|---|---|---|
| Read Only | Write Only | Update existing | Does it exist? |
