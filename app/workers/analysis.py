import re
from app.state import TradingAgentState, AnalysisArtifact

def parse_sentiment(text: str) -> str:
    if not text:
        return "NEUTRAL"
    match = re.search(r"Overall Sentiment:\s*(BULLISH|BEARISH|NEUTRAL)", text, re.IGNORECASE)
    if match:
        return match.group(1).upper()
    lower = text.lower()
    return "BEARISH" if lower.count("bearish") > lower.count("bullish") else ("BULLISH" if "bullish" in lower else "NEUTRAL")

async def analysis_worker(state: TradingAgentState):
    symbol = state.get("symbol", "GBPJPY").upper().strip()
    balance = float(state.get("account_balance", 10000.0))
    stop_dist = float(state.get("stop_distance", 25.0))  # Expected in pips for FX, dollars for Stocks

    # 1. Firm Rule: 2.0% Maximum Risk
    risk_usd = balance * 0.02

    # 2. Asset Classification
    is_jpy_cross = symbol.endswith("JPY")
    is_forex = (len(symbol) == 6 and symbol.isalpha()) or symbol.endswith("=X")

    if is_forex:
        asset_class = "FOREX"
        # If user passed price difference (e.g., 0.25 on GBPJPY or 0.0025 on EURUSD), convert to pips
        if is_jpy_cross and stop_dist < 5.0:
            pips = stop_dist * 100.0  # 0.25 -> 25 pips
        elif not is_jpy_cross and stop_dist < 0.1:
            pips = stop_dist * 10000.0  # 0.0025 -> 25 pips
        else:
            pips = max(stop_dist, 1.0)

        # Pip value per standard lot (~$6.70 for JPY crosses, $10.00 for USD crosses)
        pip_value_std_lot = 6.70 if is_jpy_cross else 10.00
        
        # Formula: Risk_USD / (Stop_Pips * Pip_Value_Per_Lot)
        raw_lots = risk_usd / (pips * pip_value_std_lot)
        position_size = round(raw_lots, 2)
        if position_size < 0.01:
            position_size = 0.01  # Micro-lot floor
        size_label = f"{position_size} Lots ({pips:.1f} pips SL)"
    else:
        asset_class = "EQUITY"
        # Dollar stop distance on share price
        share_stop = max(stop_dist, 0.05)
        position_size = int(risk_usd // share_stop)
        size_label = f"{position_size} Shares (${share_stop:.2f} SL)"

    # 3. Dynamic R:R Targets (1:2 and 1:3 projections)
    rr_1_2_profit = risk_usd * 2.0
    rr_1_3_profit = risk_usd * 3.0

    res_a = state.get("research_a_data")
    sentiment = parse_sentiment(res_a.findings if res_a else "")

    artifact = AnalysisArtifact(
        symbol=symbol,
        asset_class=asset_class,
        sentiment_bias=sentiment,
        calculated_risk_usd=risk_usd,
        recommended_position_size=position_size,
        confidence_score=0.88 if sentiment != "NEUTRAL" else 0.70,
        rationale=(
            f"Sentiment: {sentiment}. Risk envelope capped at ${risk_usd:.2f} (2.0%). "
            f"Sizing: {size_label}. "
            f"R:R Targets -> 1:2 Target: +${rr_1_2_profit:.2f} | 1:3 Target: +${rr_1_3_profit:.2f}."
        )
    )
    return {"analysis_data": artifact, "next_step": "supervisor"}