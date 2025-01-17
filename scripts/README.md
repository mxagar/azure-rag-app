# Scripts and Commands

```
az containerapp show --name <your-container-app-name> --resource-group <your-resource-group-name> --query "properties.template.containers"
az containerapp show --name "demo-coursera-rag-backend" --resource-group "rg-demo-coursera-rag-app" --query "properties.template.containers"

az containerapp restart --name <your-container-app-name> --resource-group <your-resource-group-name>
az containerapp restart --name "demo-coursera-rag-backend" --resource-group "rg-demo-coursera-rag-app"

az containerapp ingress show --name <your-container-app-name> --resource-group <your-resource-group-name>
az containerapp ingress show --name "demo-coursera-rag-backend" --resource-group "rg-demo-coursera-rag-app"

```