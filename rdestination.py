from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from config.database import get_db
from models.destination import Destination

router = APIRouter()

@router.get("/")
def get_destinations(db: Session = Depends(get_db)):
    destinations = db.query(Destination).all()
    return [
        {
            "destination_id": d.destination_id,
            "destination_name": d.destination_name
        }
        for d in destinations
    ]
