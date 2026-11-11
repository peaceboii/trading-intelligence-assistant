from pydantic import BaseModel,Field
from typing import Annotated,List,Optional
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

class ResearchArtifact(BaseModel):
    worker_id:str
    source_type:str
    findings:str
    references: List[str] =Field(default_factory=list)

class AnalysisArtifact(BaseModel):
    sentiment_bias:str
    calculated_risk_usd:float
    recommended_position_size:float
    confidence_score:float
    rationale:str
    asset_class:str

class CriticArtifact(BaseModel):
    is_approved:bool
    score:float
    feedback:str
    remediation_required:Optional[str]=None

class TradingAgentState(TypedDict):
    messages:Annotated[List[BaseMessage],add_messages]
    symbol:str
    account_balance:float
    stop_distance:float
    research_a_data:Optional[ResearchArtifact]
    research_b_data:Optional[ResearchArtifact]
    analysis_data:Optional[AnalysisArtifact]
    critique_data:Optional[CriticArtifact]
    final_report:Optional[str]
    next_step:str
    iterations:int
