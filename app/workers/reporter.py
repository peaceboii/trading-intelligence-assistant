from datetime import datetime
from app.state import TradingAgentState

async def report_generator(state: TradingAgentState):
    symbol = state.get("symbol", "UNKNOWN")
    res_a = state.get("research_a_data")
    res_b = state.get("research_b_data")
    analysis = state.get("analysis_data")
    critique = state.get("critique_data")

    is_fx = analysis and analysis.asset_class == "FOREX"
    unit = "Lots" if is_fx else "Shares"

    risk_usd = analysis.calculated_risk_usd if analysis else 200.0
    rr_1_2 = risk_usd * 2.0
    rr_1_3 = risk_usd * 3.0

    report = f"""
# TRADING INTELLIGENCE DOSSIER: {symbol}
**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}  
**Audit Status:** {'PASSED' if critique and critique.is_approved else 'REJECTED'} (Score: {critique.score if critique else 0})

---

## 1. Executive Summary & Strategy
* **Directional Bias:** {analysis.sentiment_bias if analysis else 'NEUTRAL'}
* **Recommended Volume:** {analysis.recommended_position_size if analysis else 0.0} {unit}
* **Risk Envelope:** ${risk_usd:.2f} (2.0% Maximum)
* **Risk/Reward Scenarios:**
  * **Conservative (1:2 R:R):** Target Return = **+${rr_1_2:.2f}**
  * **Asymmetric (1:3 R:R):** Target Return = **+${rr_1_3:.2f}**
* **Confidence Rating:** {analysis.confidence_score * 100 if analysis else 0:.1f}%

## 2. Evidence Interpretation
{analysis.rationale if analysis else 'No rationale provided.'}

## 3. Independent Source Retrieval
### Worker A (Macro & News Intelligence):
{res_a.findings if res_a else 'No data.'}
*References: {', '.join(res_a.references) if res_a else 'None'}*

### Worker B (Trading Rule & Protocol Retrieval):
{res_b.findings if res_b else 'No data.'}
*References: {', '.join(res_b.references) if res_b else 'None'}*

## 4. Compliance & Critic Audit
> {critique.feedback if critique else 'No critique recorded.'}
"""
    return {"final_report": report.strip(), "next_step": "complete"}