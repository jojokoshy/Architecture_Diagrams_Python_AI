Create an Azure architecture diagram.
Scenario:
One subscription, one VNet, azure durable function, Azure Storage Queue, Azure Storage Tables, Azure Key Vault and Azure SQL DB.

Resources:

1. **Networking**
   - VNet: "vnet-namescreening" (10.10.0.0/16)   

2. **Web Tier**
   - Azure Function App: "clm-ns-durable-function"

3. **Application Tier**
   - Azure Storage Queues: "sq-namescreening-orchestration"

4. **Data Tier**
   - SQL Server: "sqlsrv-namescreening"
   - SQL Database: "sqldb-ns"
   - Storage Account: "ns-storage"
   - Azure Key Vault: "kv-ns"

5. **Monitoring**
   - Log Analytics Workspace: "law-ns"
   - Application Insights: "appi-ns"

Connections:
- Users → Azure Durable Function
- Azure Durable Function → Storage Queues → Storage Tables
- All apps → Key Vault for secrets
- All resources → Log Analytics

Layout rules:
- Top: Azure Durable Function
- Right side: Function App + Storage Queues
- Bottom: Data tier (SQL, Storage, Key Vault)
- Bottom centre: Monitoring resources
- Place everything inside a single VNet box with subnet boundaries.

Output format required:
- List each container (VNet, each subnet)
- List each resource with labels
- List the arrows and connections
- Make the layout instructions clear
- Use icons for every resource following the icon instructions above
