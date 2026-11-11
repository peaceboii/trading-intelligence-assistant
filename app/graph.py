from langgraph.graph import StateGraph,START,END
from langgraph.checkpoint.memory import MemorySaver

from app.state import TradingAgentState
from app.workers.supervisor import supervisor_node,route_supervisor
from app.workers.research import research_worker_a, research_worker_b
from app.workers.analysis import analysis_worker
from app.workers.critic import critic_worker
from app.workers.reporter import report_generator

def build_trading_workflow():
    workflow=StateGraph(TradingAgentState)

    workflow.add_node("supervisor",supervisor_node)
    workflow.add_node("research_a",research_worker_a)
    workflow.add_node("research_b",research_worker_b)
    workflow.add_node("analysis",analysis_worker)
    workflow.add_node("critic",critic_worker)
    workflow.add_node("report_generator",report_generator)

    workflow.add_edge(START,"supervisor")
    workflow.add_conditional_edges(
        "supervisor",route_supervisor,{
            "research_a": "research_a",
            "research_b": "research_b",
            "analysis": "analysis",
            "critic": "critic",
            "report_generator": "report_generator",
            "__end__": END,
        }
    )

    workflow.add_edge("research_a","supervisor")
    workflow.add_edge("research_b","supervisor")
    workflow.add_edge("analysis","supervisor")
    workflow.add_edge("critic","supervisor")
    workflow.add_edge("report_generator",END)

    checkpinter=MemorySaver()
    return workflow.compile(checkpointer=checkpinter)

trading_grapg=build_trading_workflow()