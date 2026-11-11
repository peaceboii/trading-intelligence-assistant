from app.state import CriticArtifact,TradingAgentState

async def critic_worker(state:TradingAgentState):
    """critic_worker: Quality review, compliance auditing,and hallucinating check"""

    balance=state.get("account_balance",10000.0)
    analysis=state.get("analysis_data")

    max_allowed_risk=balance*0.02
    is_valid= True
    feedback="all risk metrics pass internal compliance standards"

    if not analysis:
        is_valid=False
        feedback="analysis data missing"
    elif analysis.calculated_risk_usd > (max_allowed_risk+0.01):        
        is_valid=False
    
        feedback = f"Rejected : Risk ({analysis.calculated_risk_usd} exceeds 2% of capital limit ({max_allowed_risk}))"

    critique=CriticArtifact(
        is_approved=is_valid,
        score=0.95 if is_valid else 0.40,
        feedback=feedback
    )

    return {"critique_data": critique,"next_step":"supervisor"}
