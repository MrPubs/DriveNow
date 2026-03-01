
from pydantic import BaseModel
from typing import List, Optional, Literal
from .items import Rental, RentalStatusEnum, Car

# Rental Responses
class GetAllRentalsResponse(BaseModel):
    length: int
    rentals: List[Rental]

# Car Responses
class GetAllCarsResponse(BaseModel):
    length: int
    filter: Optional[RentalStatusEnum] = None
    cars: List[Car]

# Health Responses
class PingResp(BaseModel):
    msg: Literal["pong"]

class DBHealthCheckResp(BaseModel):
    msg: Literal["ok"]

# Metric Responses
class GetActiveCarsResp(BaseModel):
    active_cars: int

class GetOngoingRentalsResp(BaseModel):
    ongoing_rentals: int

class GetAverageResponseTimeResp(BaseModel):
    average_response_time_in_ms: float
    hit_count: int