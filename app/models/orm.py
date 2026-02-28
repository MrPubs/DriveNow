
from sqlalchemy.inspection import inspect
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
    status: Mapped[str] = mapped_column(String, nullable=False) # TODO: Change to use the rental enum.

class RentalTableSchema(Base):
    __tablename__ = "rentals"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    car_id = Column(UUID(as_uuid=True), ForeignKey('cars.id'), nullable=False)
    customer_name = Column(String, nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    end_date = Column(DateTime(timezone=True), nullable=True)

def deep_update_orm(target, source) -> bool:
    """
    Recursively updates `target` ORM instance with values from `source`.
    Returns True if any field was changed.
    """
    changed = False

    mapper = inspect(target.__class__)

    # --- Update scalar columns ---
    for column in mapper.columns:
        field = column.key

        if not hasattr(source, field):
            continue

        new_value = getattr(source, field)
        old_value = getattr(target, field)

        if new_value != old_value:
            setattr(target, field, new_value)
            changed = True

    # --- Update relationships recursively ---
    for rel in mapper.relationships:
        field = rel.key

        if not hasattr(source, field):
            continue

        new_value = getattr(source, field)
        old_value = getattr(target, field)

        if new_value is None:
            continue

        # One-to-one or many-to-one
        if not rel.uselist:
            if old_value is None:
                setattr(target, field, new_value)
                changed = True
            else:
                if deep_update_orm(old_value, new_value):
                    changed = True

        # One-to-many (list relationships)
        else:
            # Simple strategy: replace if different
            if new_value != old_value:
                setattr(target, field, new_value)
                changed = True

    return changed