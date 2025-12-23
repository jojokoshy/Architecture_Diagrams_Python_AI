"""Generate Contoso architecture diagram from instructions.md

Produces: diagrams/contoso_from_instructions.dot, .png and .drawio (if graphviz2drawio present)

Run (from Arch_Diagrams):
  .\venv\Scripts\Activate.ps1
  $env:PATH += ';C:\Program Files\Graphviz\bin'
  python contoso_from_instructions.py
"""
from diagrams import Diagram, Cluster, Edge
from diagrams.azure.compute import AppServices, FunctionApps
from diagrams.azure.network import (
    VirtualNetworks, ApplicationGateway, FrontDoors,
    NetworkSecurityGroupsClassic, Firewall, RouteTables,
    PublicIpAddresses
)
from diagrams.azure.database import SQLServers, SQLDatabases
from diagrams.azure.storage import StorageAccounts
from diagrams.azure.security import KeyVaults
from diagrams.azure.integration import ServiceBus
from diagrams.azure.analytics import LogAnalyticsWorkspaces
from diagrams.azure.devops import ApplicationInsights
from diagrams.onprem.client import Users
import subprocess

graph_attr = {
    "splines": "ortho",
    "nodesep": "0.8",
    "ranksep": "1.2",
    "fontsize": "12",
    "bgcolor": "white",
    "pad": "0.5",
}

OUT_BASE = "diagrams/contoso_from_instructions"

with Diagram("Contoso Architecture — From instructions.md", filename=OUT_BASE, outformat=["png", "dot"], graph_attr=graph_attr, show=False):
    users = Users("Users")

    # Top: Front Door
    afd = FrontDoors("afd-contoso")

    # VNet container with subnets
    with Cluster("vnet-contoso-auea-001\n10.10.0.0/16"):
        with Cluster("snet-frontend\n10.10.1.0/24"):
            agw = ApplicationGateway("agw-contoso")
            web_app = AppServices("app-frontend-portal")
            asp_front = AppServices("asp-contoso-prod")

        with Cluster("snet-backend\n10.10.2.0/24"):
            api = AppServices("app-order-api")
            asp_back = AppServices("asp-contoso-backend")
            func = FunctionApps("func-order-processor")
            sb = ServiceBus("sb-contoso-orders")

        with Cluster("snet-data\n10.10.3.0/24"):
            sql_srv = SQLServers("sqlsrv-contoso")
            sql_db = SQLDatabases("sqldb-orders")
            storage = StorageAccounts("stcontosodata001")
            kv = KeyVaults("kv-contoso-prod")
            pe_sql = PublicIpAddresses("pe-sql")
            pe_storage = PublicIpAddresses("pe-storage")
            pe_kv = PublicIpAddresses("pe-kv")

        # Bottom-left: Firewall + route table + NSGs
        firewall = Firewall("azfw-contoso")
        rtb = RouteTables("rtb-default")
        nsg_front = NetworkSecurityGroupsClassic("nsg-frontend")
        nsg_back = NetworkSecurityGroupsClassic("nsg-backend")
        nsg_data = NetworkSecurityGroupsClassic("nsg-data")

    # Monitoring (bottom-centre)
    law = LogAnalyticsWorkspaces("law-contoso-prod")
    appi = ApplicationInsights("appi-contoso")

    # Connections per instructions
    users >> afd
    afd >> agw
    agw >> web_app
    web_app >> api
    api >> [sql_db, storage]
    func >> sb
    sb >> sql_db

    # All apps -> Key Vault
    for app in (web_app, api, func):
        app >> kv

    # Private endpoints in data subnet
    sql_db >> pe_sql
    storage >> pe_storage
    kv >> pe_kv

    # Outbound to firewall
    for r in (web_app, api, func, storage, sql_db):
        r >> Edge(label="outbound") >> firewall

    # Monitoring connections
    for r in (web_app, api, func, storage, sql_db, sb):
        r >> law
    api >> appi

    # Route table attachment visual
    rtb >> firewall

# Attempt to convert DOT -> draw.io (if graphviz2drawio is available)
try:
    subprocess.run([
        "graphviz2drawio",
        f"{OUT_BASE}.dot",
        "-o",
        f"{OUT_BASE}.drawio"
    ], check=False)
except Exception:
    pass

print(f"Wrote {OUT_BASE}.dot and {OUT_BASE}.png (if diagrams and graphviz installed).")
