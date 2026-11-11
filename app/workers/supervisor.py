from typing import Literal
from app.state import TradingAgentState

def supervisor_node(state:TradingAgentState):
    """supervisor orchestrator: manages state, task delegation, and convergence"""

    res_a = state.get("research_a_data")
    res_b=state.get("research_b_data")
    analysis=state.get("analysis_data")
    critic=state.get("critique_data")

    if not res_a:
        return {"next_step":"research_a"}
    if not res_b:
        return {"next_step": "research_b"}

    if not analysis:
        return { "next_step":"analysis"}

    if not critic:
        return {"next_step":"critic"}

    if critic.is_approved:
        return {"next_step":"report_generator"}
    else:
        if state.get("iterations",0)>=2:
            return{"next_step":"report_generator"}
        return {
            "next_step":"analysis",
            "iterations":state.get("iterations",0)+1,
            "critique_data":None,
        }

def route_supervisor(state:TradingAgentState
                     ) ->Literal[
                        "research_a",
                        "research_b",
                        "analysis",
                        "critic",
                        "report_generator",
                        "__end__",
                     ]:
    next_step=state.get("next_step")
    if next_step=="complete":
        return "__end__"
    return next_step
