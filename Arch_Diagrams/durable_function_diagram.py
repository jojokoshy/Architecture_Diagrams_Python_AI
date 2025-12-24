"""Generate Azure Durable Function architecture diagram from durablefunction.md

Produces: diagrams/durable_function_arch.dot, .png and .drawio (if graphviz2drawio present)

Run (from Arch_Diagrams):
  .\\venv\\Scripts\\Activate.ps1
  $env:PATH += ';C:\\Program Files\\Graphviz\\bin'
  python durable_function_diagram.py
"""
from diagrams import Diagram, Cluster, Edge
from diagrams.azure.compute import FunctionApps
from diagrams.azure.network import VirtualNetworks
from diagrams.azure.database import SQLDatabases
from diagrams.azure.storage import StorageAccounts, TableStorage, QueuesStorage
from diagrams.azure.security import KeyVaults
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

# Cluster colors for different tiers
function_cluster_attr = {
    "fontsize": "13",
    "bgcolor": "#E3F2FD",  # Light Blue
    "style": "rounded",
    "margin": "15"
}

backend_cluster_attr = {
    "fontsize": "13",
    "bgcolor": "#F3E5F5",  # Light Purple
    "style": "rounded",
    "margin": "15"
}

data_cluster_attr = {
    "fontsize": "13",
    "bgcolor": "#FFF3E0",  # Light Orange
    "style": "rounded",
    "margin": "15"
}

OUT_BASE = "diagrams/durable_function_arch"

with Diagram("Azure Durable Function Architecture", filename=OUT_BASE, outformat=["png", "dot"], graph_attr=graph_attr, show=False, direction="TB"):
    users = Users("Users")

    # VNet container with subnets
    with Cluster("vnet-namescreening\n10.10.0.0/16"):
        
        # Durable Function Subnet
        with Cluster("snet-durablefunction\n10.10.1.0/24", graph_attr=function_cluster_attr):
            func = FunctionApps("clm-ns-durable-function")
        
        # Backend Subnet
        with Cluster("snet-backend\n10.10.2.0/24", graph_attr=backend_cluster_attr):
            storage_queue = QueuesStorage("sq-namescreening-\norchestration")
            storage_tables = TableStorage("Storage Tables")
        
        # Data Tier Subnet
        with Cluster("snet-data\n10.10.3.0/24", graph_attr=data_cluster_attr):
            sql_db = SQLDatabases("sqldb-ns")
            storage_acct = StorageAccounts("ns-storage")
            kv = KeyVaults("kv-ns")

    # Monitoring (bottom-centre, outside VNet)
    with Cluster("Monitoring"):
        law = LogAnalyticsWorkspaces("law-ns")
        appi = ApplicationInsights("appi-ns")

    # Main flow connections
    users >> Edge(label="HTTPS") >> func
    func >> Edge(label="enqueue") >> storage_queue
    storage_queue >> Edge(label="process") >> storage_tables
    func >> storage_tables
    
    # Function to data tier
    func >> sql_db
    func >> storage_acct
    func >> Edge(label="secrets") >> kv
    
    # Monitoring connections
    func >> Edge(style="dotted") >> law
    func >> Edge(style="dotted") >> appi
    storage_queue >> Edge(style="dotted") >> law
    storage_tables >> Edge(style="dotted") >> law
    sql_db >> Edge(style="dotted") >> law
    storage_acct >> Edge(style="dotted") >> law
    kv >> Edge(style="dotted") >> law

# Attempt to convert DOT -> draw.io (if graphviz2drawio is available)
try:
    import os
    venv_path = os.path.join(os.path.dirname(__file__), "venv", "Scripts", "graphviz2drawio.exe")
    if os.path.exists(venv_path):
        subprocess.run([
            venv_path,
            f"{OUT_BASE}.dot",
            "-o",
            f"{OUT_BASE}.drawio"
        ], check=True)
        print(f"✓ Successfully converted to draw.io format")
    else:
        subprocess.run([
            "graphviz2drawio",
            f"{OUT_BASE}.dot",
            "-o",
            f"{OUT_BASE}.drawio"
        ], check=True)
        print(f"✓ Successfully converted to draw.io format")
except FileNotFoundError:
    print("⚠ graphviz2drawio not found - skipping draw.io conversion")
except Exception as e:
    print(f"⚠ Draw.io conversion failed: {e}")

print(f"✓ Created {OUT_BASE}.dot")
print(f"✓ Created {OUT_BASE}.png")
print(f"✓ Outputs saved to diagrams/ folder")
