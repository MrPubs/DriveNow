
# Types
from pydantic import BaseModel, create_model
from typing import Optional, Literal
from enum import Enum
from uuid import UUID
from datetime import datetime

# Schemas
from ..orm import CarTableSchema, RentalTableSchema


class RentalStatus(BaseModel):
    status: Literal["available", "in use", "under maintenance"] # TODO: Change to use the rental enum.
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
            status=self.status.status
        )

    def reconcile_req_diff(self, update_req: "CarUpdateReq") -> None:
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

    model_config = {
        "from_attributes": True
    }

    @classmethod
    def from_orm(cls, orm_obj: RentalTableSchema) -> "Rental":
        """
        Converts an ORM object to a nested Pydantic Rental model.
        """
        return cls.model_validate({
            "id": orm_obj.id,
            "car_id": orm_obj.car_id,
            "customer_name": orm_obj.customer_name,
            "start_date": orm_obj.start_date,
            "end_date": orm_obj.end_date
        })

    def to_orm(self) -> RentalTableSchema:
        """
        Converts a nested Pydantic Rental model to an ORM object
        """
        return RentalTableSchema(
            id=self.id,
            car_id=self.car_id,
            customer_name=self.customer_name,
            start_date=self.start_date,
            end_date=self.end_date
        )

RentalUpdateReq = create_model(
    'RentalUpdateReq',
    **{k: (Optional[v], None) for k, v in Rental.__annotations__.items() if k != "id"}
)

