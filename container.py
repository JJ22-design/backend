from sqlalchemy import Column, String, Integer, CheckConstraint
from config.database import Base

class Container(Base):
    __tablename__ = "Container"
    __table_args__ = {"schema": "dbo"}

    container_id = Column(String(12), primary_key=True)
    length_ft = Column(Integer, nullable=False)
    weight_lb = Column(Integer, nullable=False)
    yard_tier = Column(Integer, nullable=False)
    cargo_status = Column(String(5), nullable=False)
    operational_status = Column(String(10), nullable=False)
    destination_id = Column(String(10), nullable=False)
    zone_id = Column(String(3), nullable=False)
    priority_code = Column(String(20), nullable=False)
