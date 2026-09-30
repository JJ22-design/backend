from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from config.database import get_db
from services.optimizer import run_greedy_optimizer

router = APIRouter()

class OptimizeRequest(BaseModel):
    destination_id: str
    locomotive_id: str
    selected_railcar_ids: List[str]

@router.post("/")
def optimize(
    request: OptimizeRequest,
    db: Session = Depends(get_db)
):
    if not request.selected_railcar_ids:
        raise HTTPException(
            status_code=400,
            detail="No railcars selected"
        )
    
    result = run_greedy_optimizer(
        destination_id=request.destination_id,
        locomotive_id=request.locomotive_id,
        selected_railcar_ids=request.selected_railcar_ids,
        db=db
    )
    
    return result
