from sqlalchemy import Column, String, Integer, Numeric
from config.database import Base

class RailCar(Base):
    __tablename__ = "RailCar"
    __table_args__ = {"schema": "dbo"}

    railcar_id = Column(String(12), primary_key=True)
    destination_id = Column(String(10), nullable=False)
    railcar_type = Column(String(1), nullable=False)
    max_gross_weight_lb = Column(Integer, nullable=False)
    status = Column(String(12), nullable=False)
    train_order = Column(Integer, nullable=True)
    xcoord = Column(Numeric(8,2), nullable=True)
    ycoord = Column(Numeric(8,2), nullable=True)

class RailCarWell(Base):
    __tablename__ = "RailCarWell"
    __table_args__ = {"schema": "dbo"}

    well_id = Column(Integer, primary_key=True)
    railcar_id = Column(String(12), nullable=False)
    well_number = Column(Integer, nullable=False)
    max_length_ft = Column(Integer, nullable=False)
    max_weight_lb = Column(Integer, nullable=False)

class RailCarSlot(Base):
    __tablename__ = "RailCarSlot"
    __table_args__ = {"schema": "dbo"}

    slot_id = Column(Integer, primary_key=True)
    well_id = Column(Integer, nullable=False)
    slot_position = Column(String(6), nullable=False)
    is_occupied = Column(Integer, nullable=False, default=0)
