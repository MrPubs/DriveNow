
from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import declarative_base

import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import ForeignKey

from sqlalchemy.orm import Mapped, mapped_column
from uuid import UUID as uuid_UUID


Base = declarative_base()

class CarTableSchema(Base):
    __tablename__ = "cars"

    id: Mapped[uuid_UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    company: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)

class RentalTableSchema(Base):
    __tablename__ = "rentals"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    car_id = Column(UUID(as_uuid=True), ForeignKey('cars.id'), nullable=False)
    customer_name = Column(String, nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    end_date = Column(DateTime(timezone=True), nullable=True)