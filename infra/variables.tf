# -- Azure Credentials

variable "client_id" {
  description = "The client ID for the Azure Service Principal"
  type        = string
  sensitive   = true
}

variable "client_secret" {
  description = "The client secret for the Azure Service Principal"
  type        = string
  sensitive   = true
}

variable "subscription_id" {
  description = "The Azure Subscription ID"
  type        = string
  sensitive   = true
}

variable "tenant_id" {
  description = "The Azure Tenant ID"
  type        = string
  sensitive   = true
}

# -- Resource Group

variable "resource_group_name" {
  description = "The name of the application resource group"
  type        = string
  default     = "rg-default"
}

variable "resource_group_location" {
  description = "The location of the application resource group"
  type        = string
  default     = "West Europe"
}

# -- Azure OpenAI Service

variable "openai_name" {
  description = "The name of the Azure OpenAI Service"
  type        = string
  default     = "open-ai-default"
}

# -- Azure AI Search

variable "ai_search_name" {
  description = "The name of the Azure AI Search Service"
  type        = string
  default     = "ai-search-default"
}

# -- Azure Container App Environment

variable "backend_container_env_name" {
  description = "The name of the Azure Container App Environment"
  type        = string
  default     = "backend-container-env-default"
}

# -- Azure Container App

variable "backend_container_name" {
  description = "The name of the Azure Container App"
  type        = string
  default     = "backend-container-default"
}
