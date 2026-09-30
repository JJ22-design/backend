from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from config.database import get_db
from models.locomotive import Locomotive

router = APIRouter()

@router.get("/{destination_id}")
def get_locomotives_by_destination(
    destination_id: str,
    db: Session = Depends(get_db)
):
    locomotives = db.query(Locomotive)\
        .filter(Locomotive.destination_id == destination_id)\
        .filter(Locomotive.status == "AVAILABLE")\
        .all()
    
    return [
        {
            "locomotive_id": l.locomotive_id,
            "destination_id": l.destination_id,
            "status": l.status,
            "xcoord": float(l.xcoord),
            "ycoord": float(l.ycoord)
        }
        for l in locomotives
    ]
