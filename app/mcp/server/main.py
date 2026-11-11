from tools import resgister_tools

from mcp.server.fastmcp import FastMCP

mcp=FastMCP("news-mcp")

resgister_tools(mcp)

if __name__ =="__main__":
    mcp.run(transport="stdio")