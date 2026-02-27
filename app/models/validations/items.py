
# Types
from pydantic import BaseModel, create_model
from typing import Optional, Literal
from enum import Enum
from uuid import UUID
from datetime import datetime

# Schemas
from ..orm import CarTableSchema

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

    @classmethod
    def from_orm(cls, orm_obj: CarTableSchema) -> "Car":
        """
        Converts an ORM object to a nested Pydantic Car model.
        """
        return cls.model_validate({
            "id": orm_obj.id,
            "model": {
                "company": orm_obj.company,
                "name": orm_obj.name,
                "year": orm_obj.year
            },
            "status": {
                "status": orm_obj.status
            }
        })

    def to_orm(self) -> CarTableSchema:
        """
        Converts a nested Pydantic Car model to an ORM object
        """
        return CarTableSchema(
            id=self.id,
            company=self.model.company,
            name=self.model.name,
            year=self.model.year,
            status=self.status.status  # convert RentalStatus BaseModel to string
        )

    def update_from_req(self, update_req: "CarUpdateReq") -> None:
        data = update_req.model_dump(exclude_unset=True)

        # Update the nested model if present
        if "model" in data:
            for k, v in data["model"].items():
                setattr(self.model, k, v)

        # Update status if present
        if "status" in data:
            self.status.status = data["status"]["status"]

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

