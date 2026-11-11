import uuid
import re
from typing import Dict,Any,Optional
from fastapi import FastAPI,BackgroundTasks,HTTPException
from pydantic import BaseModel,Field

from app.graph import trading_grapg

app = FastAPI(title="Dynamic Trading intelligence")

TASKS:Dict[str,Dict[str,Any]]={}

class TradeAnalysisRequest(BaseModel):
    symbol:Optional[str]=Field(default=None,description="Direct ticker")
    query:Optional[str]=Field(default=None,description="natural language prompt")
    account_balance: float=Field(default=10000.0)
    stop_distance:float=Field(default=0.0025)

class TaskStatusResponse(BaseModel):
    task_id:str
    symbol:str
    status:str
    result:Optional[str]=None
    error:Optional[str]=None

def extract_and_normalize_symbol(symbol:Optional[str],query:Optional[str])->str:
    """extracts and normalizes a ticker"""
    if symbol:
        return symbol.upper().strip()
    if query:
        match = re.search(r'\b([A-Z]{3,6}|[A-Za-z]{2,5})\b',query.upper())

        if match:
            return match.group(1).upper()
    return "EURUSD"

async def execute_task(task_id:str,symbol:str,balance:float,stop_dist:float):
    TASKS[task_id]["status"]="RUNNING"
    config={"configurable":{"thread_id":task_id}}

    initial_state={
        "messages":[],
        "symbol":symbol,
        "account_balance":balance,
        "stop_distance":stop_dist,
        "research_a_data":None,
        "research_b_data":None,
        "analysis_data":None,
        "critic_data":None,
        "final_report":None,
        "next:step":"supervisor",
        "iterations":0
    }

    try:
        final_state=await trading_grapg.ainvoke(initial_state,config=config)
        TASKS[task_id]["status"]="COMPLETED"
        TASKS[task_id]["result"]=final_state.get("final_report")
    except Exception as exec:
        TASKS[task_id]["status"]="Failed"
        TASKS[task_id]["error"]=str(exec)
@app.post("/tasks/analyze",response_model=TaskStatusResponse,status_code=202)
async def submit_analysis(request:TradeAnalysisRequest,background_tasks:BackgroundTasks):
    target_symbol=extract_and_normalize_symbol(request.symbol,request.query)
    task_id=str(uuid.uuid4())

    TASKS[task_id]={
        "task_id":task_id,
        "symbol":target_symbol,
        "status":"PENDING",
        "result":None,
        "error":None
    }

    background_tasks.add_task(
        execute_task,
        task_id,
        target_symbol,
        request.account_balance,
        request.stop_distance
    )

    return TASKS[task_id]

@app.get("/task/{task_id}",response_model=TaskStatusResponse)
async def get_task_status(task_id:str):
    if task_id not in TASKS:
        raise HTTPException(status_code=404,detail="task not found")
    return TASKS[task_id]