
from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import declarative_base

import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import ForeignKey

Base = declarative_base()

class CarTableSchema(Base):
    __tablename__ = "cars"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company = Column(String, nullable=False)
    name = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    status = Column(String, nullable=False)

class RentalTableSchema(Base):
    __tablename__ = "rentals"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    car_id = Column(UUID(as_uuid=True), ForeignKey('cars.id'), nullable=False)
    customer_name = Column(String, nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    end_date = Column(DateTime(timezone=True), nullable=True)