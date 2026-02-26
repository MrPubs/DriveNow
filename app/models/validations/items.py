
# Types
from pydantic import BaseModel, create_model
from typing import Optional, Literal
from uuid import UUID
from datetime import datetime

class CarModel(BaseModel):
    company: str
    name: str
    year: int

class RentalStatus(BaseModel):
    status: Literal["available", "in use", "under maintenance"]

class Car(BaseModel):
    id: UUID
    model: CarModel
    status: RentalStatus
CarUpdateReq = create_model(
    'CarUpdateReq',
    **{k: (Optional[v], None) for k, v in Car.__annotations__.items()}
)

# Rentals
class Rental(BaseModel):
    id: UUID
    car_id: UUID
    customer_name: str
    start_date: datetime
    end_date: datetime
RentalUpdateReq = create_model(
    'RentalUpdateReq',
    **{k: (Optional[v], None) for k, v in Rental.__annotations__.items()}
)

