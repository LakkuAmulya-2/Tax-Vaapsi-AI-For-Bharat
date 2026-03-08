"""
Tax Vaapsi v3.0 - Local Development Server
Starts all services in correct order
"""
import subprocess
import sys
import os
import time


def run_local():
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║   TAX VAAPSI v3.0 - Starting All Services                           ║
╚══════════════════════════════════════════════════════════════════════╝

📋 Start Order:
  1. DynamoDB Local (optional): docker run -p 8000:8000 amazon/dynamodb-local
  2. GST Portal:  python dummy_portals/gst_portal/app.py   → :8001
  3. IT Portal:   python dummy_portals/it_portal/app.py    → :8002
  4. MCP GST:     python mcp_servers/gst_mcp_server.py     → :9001
  5. MCP IT:      python mcp_servers/it_mcp_server.py      → :9002
  6. MCP Law:     python mcp_servers/tax_law_mcp_server.py → :9003
  7. Main API:    python main.py                           → :8080

🚀 Quick Start (Windows - open 7 terminals):
  Terminal 1: cd dummy_portals/gst_portal && python app.py
  Terminal 2: cd dummy_portals/it_portal && python app.py
  Terminal 3: python mcp_servers/gst_mcp_server.py
  Terminal 4: python mcp_servers/it_mcp_server.py
  Terminal 5: python mcp_servers/tax_law_mcp_server.py
  Terminal 6: python main.py

📡 URLs:
  Main API:    http://localhost:8080
  API Docs:    http://localhost:8080/docs
  Demo:        http://localhost:8080/demo/quick-start
  A2A Card:    http://localhost:8080/.well-known/agent.json
  MCP GST:     http://localhost:9001/mcp/tools
  MCP IT:      http://localhost:9002/mcp/tools
  GST Portal:  http://localhost:8001
  IT Portal:   http://localhost:8002
    """)

    # Start main server
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True, log_level="info")


if __name__ == "__main__":
    run_local()
