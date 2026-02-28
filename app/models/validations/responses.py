
from pydantic import BaseModel
from typing import List, Optional
from .items import Rental, RentalStatusEnum, Car

class GetAllRentalsResponse(BaseModel):
    length: int
    rentals: List[Rental]

class GetAllCarsResponse(BaseModel):
    length: int
    filter: Optional[RentalStatusEnum] = None
    cars: List[Car]