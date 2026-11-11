from app.state import TradingAgentState,ResearchArtifact
from langchain_core.messages import HumanMessage,SystemMessage
from app.mcp.host.adapter import get_all_mcp_tools
from langchain_ollama import ChatOllama
from app.rag.macro_rag import query_fundamental_risk_rules
llm=ChatOllama(model="llama3.2:latest",temperature=0.1)

async def research_worker_a(state:TradingAgentState):
    symbol=state.get("symbol","EURUSD").upper().strip()
    tools= await get_all_mcp_tools()
    print(f"[DEBUG Worker A] Discovered tool names: {[t.name for t in tools]}")
    news_tool= next((t for t in tools if t.name =="get_macro_news"),None)

    if news_tool:
        raw_news=await news_tool.ainvoke({"symbol":symbol,"count":10})
    else:
        raw_news="News mcp is not available"

    system_prompt=(
        "You are Research Worker A (Financial News Specialist).\n"
        "Analyze the provided raw news feed. Identify overall sentiment (BULLISH, BEARISH, NEUTRAL), "
        "highlight immediate high-impact catalysts, and list specific sources."
    )

    user_prompt=f"Assest:{symbol}\n\nFeed data:\n{raw_news}"

    response=await llm.ainvoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ])

    articate =ResearchArtifact(
        worker_id="Research_worker_a",
        symbol=symbol,
        source_type="mcp_news_feed",
        findings=response.content,
        references=[f"{symbol} Yahoo rss Feed","Mcp::fetch_macro_news"]
        )
    return {"research_a_data":articate,"next_step":"supervisor"}

async def research_worker_b(state: TradingAgentState):
    """Worker B: Independent retrieval (Trading handbook rules & liquidity policy)"""
    symbol = state.get("symbol", "AAPL").upper().strip()

    # Generic textbook search query (do not include AAPL/NVDA here)
    rag_query = "margin of safety, financial leverage debt risk, and defensive investing rules"
    retrieved_context = await query_fundamental_risk_rules(rag_query, k=4)

    system_prompt = (
        "You are Research Worker B (Fundamental Risk & Rules Specialist).\n"
        "Your task is to extract 3 concrete risk management and financial health rules "
        "from the provided book excerpts.\n"
        "RULES:\n"
        "- Do NOT introduce yourself or ask the user to provide passages.\n"
        "- Base your rules strictly on the provided retrieved passages.\n"
        "- State each rule clearly with practical risk implications for an investor/trader."
    )
    user_prompt = (
        f"Target Asset: {symbol}\n\n"
        f"Retrieved Passages from 'Fundamental Analysis For Dummies':\n"
        f"{retrieved_context}"
    )

    response = await llm.ainvoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ])

    artifact = ResearchArtifact(
        worker_id="research_worker_b",
        symbol=symbol,
        source_type="RAG::Fundamental_Analysis_For_Dummies",
        findings=response.content,
        references=[
            "Fundamental Analysis For Dummies (ChromaDB)",
            "Ch. 5: Margin of Safety & Capital Preservation"
        ]
    )

    return {"research_b_data": artifact, "next_step": "supervisor"}