from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from config.database import get_db
from models.railcar import RailCar

router = APIRouter()

@router.get("/{destination_id}")
def get_railcars_by_destination(
    destination_id: str,
    db: Session = Depends(get_db)
):
    railcars = db.query(RailCar)\
        .filter(RailCar.destination_id == destination_id)\
        .filter(RailCar.status == "AVAILABLE")\
        .all()
    
    return [
        {
            "railcar_id": r.railcar_id,
            "railcar_type": r.railcar_type,
            "max_gross_weight_lb": r.max_gross_weight_lb,
            "status": r.status,
            "destination_id": r.destination_id,
            "train_order": r.train_order
        }
        for r in railcars
    ]
