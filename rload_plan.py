from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from config.database import get_db
from models.load_plan import LoadPlanHeader, LoadPlanLine, LoadPlanKPI

router = APIRouter()

@router.get("/")
def get_all_load_plans(db: Session = Depends(get_db)):
    plans = db.query(LoadPlanHeader).all()
    return [
        {
            "plan_id": p.plan_id,
            "destination_id": p.destination_id,
            "locomotive_id": p.locomotive_id,
            "plan_status": p.plan_status,
            "created_at_utc": p.created_at_utc
        }
        for p in plans
    ]

@router.get("/{plan_id}")
def get_load_plan(
    plan_id: int,
    db: Session = Depends(get_db)
):
    plan = db.query(LoadPlanHeader)\
        .filter(LoadPlanHeader.plan_id == plan_id)\
        .first()
    
    if not plan:
        raise HTTPException(
            status_code=404,
            detail=f"Plan {plan_id} not found"
        )
    
    lines = db.query(LoadPlanLine)\
        .filter(LoadPlanLine.plan_id == plan_id)\
        .all()
    
    return {
        "plan_id": plan.plan_id,
        "destination_id": plan.destination_id,
        "locomotive_id": plan.locomotive_id,
        "plan_status": plan.plan_status,
        "assignments": [
            {
                "plan_line_id": l.plan_line_id,
                "container_id": l.container_id,
                "railcar_id": l.railcar_id,
                "well_id": l.well_id,
                "slot_id": l.slot_id,
                "assignment_score": float(l.assignment_score),
                "move_distance": float(l.move_distance),
                "score_breakdown": l.score_breakdown
            }
            for l in lines
        ]
    }

@router.get("/{plan_id}/kpis")
def get_load_plan_kpis(
    plan_id: int,
    db: Session = Depends(get_db)
):
    kpi = db.query(LoadPlanKPI)\
        .filter(LoadPlanKPI.plan_id == plan_id)\
        .first()
    
    if not kpi:
        raise HTTPException(
            status_code=404,
            detail=f"KPIs for plan {plan_id} not found"
        )
    
    return {
        "plan_id": kpi.plan_id,
        "total_slots": kpi.total_slots,
        "filled_slots": kpi.filled_slots,
        "slot_utilization_pct": float(kpi.slot_utilization_pct),
        "containers_loaded": kpi.containers_loaded,
        "containers_set_aside": kpi.containers_set_aside,
        "containers_unassigned": kpi.containers_unassigned,
        "crane_move_distance": float(kpi.crane_move_distance)
    }
