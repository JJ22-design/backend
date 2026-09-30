from sqlalchemy import Column, String
from config.database import Base

class Destination(Base):
    __tablename__ = "Destination"
    __table_args__ = {"schema": "dbo"}

    destination_id = Column(String(10), primary_key=True)
    destination_name = Column(String(100), nullable=False)
