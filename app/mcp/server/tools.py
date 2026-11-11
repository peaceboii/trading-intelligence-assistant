from mcp.server.fastmcp import FastMCP
from fetch_news import fetch_market_news
mcp = FastMCP(
    "news-fetcher-server",
    instructions="Provides clean macroeconomic and ticker-specific news data."
)
def resgister_tools(mcp):
    @mcp.tool()
    async def get_macro_news(symbol:str,count:int=10)->str:
        articles= await fetch_market_news(symbol=symbol,limit=count)

        formatted_output=[]

        for i,article in enumerate(articles,1):
            formatted_output.append(
                f"[{i}] {article['title']}\n"
                f"    Date: {article['published']}\n"
                f"    Summary: {article['summary']}\n"
                f"    Source: {article['source']} ({article['url']})"

            )
        return "\n\n".join(formatted_output)

    
