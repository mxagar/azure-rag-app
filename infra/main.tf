provider "azurerm" {
  features {}

  client_id       = var.client_id
  client_secret   = var.client_secret
  subscription_id = var.subscription_id
  tenant_id       = var.tenant_id
}

# -- Utilities

resource "random_string" "unique_id" { # Random String for Uniqueness
  length  = 6
  special = false
  upper   = false
}

locals {
  # Concatenate static values to create a unique input for hashing
  hash_input = join("-", [var.subscription_id, var.resource_group_name, var.resource_group_location])
}

# -- Resource Group
resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.resource_group_location
}

# -- Azure OpenAI Service
resource "azurerm_cognitive_account" "openai" {
  #name                = var.openai_name
  name                = "${var.openai_name}-${substr(md5(local.hash_input), 0, 6)}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  kind                = "OpenAI"
  sku_name            = "S0" # Standard Tier

  tags = {
    environment = "demo"
    project     = "RAG Chatbot"
  }
}

# -- Azure AI Search
resource "azurerm_search_service" "ai_search" {
  #name                = var.ai_search_name
  #name                = "${var.ai_search_name}-${random_string.unique_id.result}"
  name                = "${var.ai_search_name}-${substr(md5(local.hash_input), 0, 6)}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "free"  # Free Tier
  partition_count     = 1
  replica_count       = 1

  tags = {
    environment = "demo"
    project     = "RAG Chatbot"
  }
}

# -- Azure Container App Environment
resource "azurerm_container_app_environment" "backend_container_env" {
  #name                = var.backend_container_env_name
  name                = "${var.backend_container_env_name}-${substr(md5(local.hash_input), 0, 6)}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  tags = {
    environment = "demo"
    project     = "RAG Chatbot"
  }
}

# -- Azure Container App
resource "azurerm_container_app" "backend_container" {
  #name                      = var.backend_container_name
  name                      = "${var.backend_container_name}-${substr(md5(local.hash_input), 0, 6)}"
  container_app_environment_id = azurerm_container_app_environment.backend_container_env.id
  resource_group_name       = azurerm_resource_group.main.name
  #location                  = azurerm_resource_group.main.location  # Inherited from the environment
  revision_mode                = "Single"

  ingress {
  external_enabled = true
  target_port      = 8000
  traffic_weight {
      latest_revision = true
      percentage      = 100
  }
  }

  template {
    # Placeholder Hello World image
    # This image will be replaced with the actual image in the CI/CD pipeline, e.g.:
    # az containerapp update --name <CONATINER_APP_NAME> --resource-group <RESOURCE_GROUP> --image <NEW_IMAGE>
    # The cpu and memory values will be adjusted, too
    container {
      name   = "backend-default"
      image  = "mcr.microsoft.com/azuredocs/aci-helloworld:latest" # Placeholder Hello World image
      cpu    = 0.25
      memory = "0.5Gi"
    }
  }

  tags = {
    environment = "demo"
    project     = "RAG Chatbot"
  }
}

# -- Outputs
output "openai_service" {
  value = {
    name     = azurerm_cognitive_account.openai.name
    endpoint = azurerm_cognitive_account.openai.endpoint
    key      = azurerm_cognitive_account.openai.primary_access_key
  }
  sensitive = true
}

output "ai_search_service" {
  value = {
    name       = azurerm_search_service.ai_search.name
    id         = azurerm_search_service.ai_search.id
    query_keys = azurerm_search_service.ai_search.query_keys
    api_key    = azurerm_search_service.ai_search.primary_key
  }
  sensitive = true
}

output "backend_container_app" {
  value = {
    name     = azurerm_container_app.backend_container.name
    fqdn     = azurerm_container_app.backend_container.latest_revision_fqdn  # Fully Qualified Domain Name
    #image    = "mcr.microsoft.com/azuredocs/aci-helloworld:latest"
  }
  sensitive = true
}
