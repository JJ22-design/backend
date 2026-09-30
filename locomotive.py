from sqlalchemy import Column, String, Numeric
from config.database import Base

class Locomotive(Base):
    __tablename__ = "Locomotive"
    __table_args__ = {"schema": "dbo"}

    locomotive_id = Column(String(12), primary_key=True)
    xcoord = Column(Numeric(8,2), nullable=False)
    ycoord = Column(Numeric(8,2), nullable=False)
    status = Column(String(12), nullable=False)
    destination_id = Column(String(10), nullable=False)
