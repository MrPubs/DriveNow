
# Types
from pydantic import BaseModel, create_model
from typing import Optional, Literal
from enum import Enum
from uuid import UUID
from datetime import datetime


class RentalStatus(BaseModel):
    status: Literal["available", "in use", "under maintenance"]
class RentalStatusEnum(str, Enum):
    available = "available"
    in_use = "in use"
    under_maintenance = "under maintenance"

class CarModel(BaseModel):
    company: str
    name: str
    year: int
class Car(BaseModel):
    id: UUID
    model: CarModel
    status: RentalStatus

    model_config = {
        "from_attributes": True
    }
CarUpdateReq = create_model(
    'CarUpdateReq',
    **{k: (Optional[v], None) for k, v in Car.__annotations__.items() if k != "id"}
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
    **{k: (Optional[v], None) for k, v in Rental.__annotations__.items() if k != "id"}
)

