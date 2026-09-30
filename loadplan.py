from sqlalchemy import Column, String, Integer, Numeric, DateTime, BigInteger
from config.database import Base

class LoadPlanHeader(Base):
    __tablename__ = "LoadPlanHeader"
    __table_args__ = {"schema": "dbo"}

    plan_id = Column(BigInteger, primary_key=True)
    destination_id = Column(String(10), nullable=False)
    locomotive_id = Column(String(12), nullable=False)
    requested_rail_car_count = Column(Integer, nullable=False)
    plan_status = Column(String(10), nullable=False, default='DRAFT')
    created_at_utc = Column(DateTime, nullable=False)

class LoadPlanLine(Base):
    __tablename__ = "LoadPlanLine"
    __table_args__ = {"schema": "dbo"}

    plan_line_id = Column(BigInteger, primary_key=True)
    plan_id = Column(BigInteger, nullable=False)
    container_id = Column(String(12), nullable=False)
    railcar_id = Column(String(12), nullable=False)
    well_id = Column(Integer, nullable=False)
    slot_id = Column(Integer, nullable=False)
    assignment_score = Column(Numeric(10,4), nullable=False)
    move_distance = Column(Numeric(10,2), nullable=False)
    score_breakdown = Column(String(500), nullable=True)

class LoadPlanKPI(Base):
    __tablename__ = "LoadPlanKPI"
    __table_args__ = {"schema": "dbo"}

    plan_id = Column(BigInteger, primary_key=True)
    total_slots = Column(Integer, nullable=False)
    filled_slots = Column(Integer, nullable=False)
    slot_utilization_pct = Column(Numeric(5,2), nullable=False)
    containers_loaded = Column(Integer, nullable=False)
    containers_set_aside = Column(Integer, nullable=False)
    containers_unassigned = Column(Integer, nullable=False)
    crane_move_distance = Column(Numeric(12,2), nullable=False)
