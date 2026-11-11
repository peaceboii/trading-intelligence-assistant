import sys
from pathlib import Path
from typing import List
from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient

base_dir=Path(__file__).resolve().parent.parent
news_script=str(base_dir/"server"/"main.py")

async def get_all_mcp_tools()->List[BaseTool]:
    """Connects to multiple mcp servers via stdio and extracts callable langchain tools"""
    client= MultiServerMCPClient({
        "news":{
            "command":sys.executable,
            "args":[news_script],
            "transport":"stdio"
        }
    })

    tools= await client.get_tools()
    return tools