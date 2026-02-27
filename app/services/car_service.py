# Models and types
from uuid import UUID
from app.models.validations.items import CarUpdateReq, RentalStatusEnum, Car, RentalStatus, CarModel

# Session
from sqlalchemy.ext.asyncio import AsyncSession

# Schemas
from app.models.orm import CarTableSchema

# Functionality
from sqlalchemy import select

class CarService:

    @staticmethod
    async def get_one_by_id(db: AsyncSession, id: UUID):

        # Make Query
        query = select(CarTableSchema).where(CarTableSchema.id == id)

        result = await db.execute(query)
        car_orm = result.scalar_one_or_none()
        car = Car(
                id=car_orm.id,
                model=CarModel(
                    company=car_orm.company,
                    name=car_orm.name,
                    year=car_orm.year
                ),
                status=RentalStatus(status=car_orm.status)
        )
        return car

    @staticmethod
    async def get_all(db: AsyncSession, status_filter: RentalStatusEnum | None = None):

        # Make Query
        query = select(CarTableSchema)
        if status_filter:
            query = query.where(CarTableSchema.status == status_filter.value)

        # Send Query and return
        result = await db.execute(query)
        cars_orm = result.scalars().all()
        cars = [
            Car(
                id=c.id,
                model=CarModel(
                    company=c.company,
                    name=c.name,
                    year=c.year
                ),
                status=RentalStatus(status=c.status)
            ) for c in cars_orm
        ]

        return cars

    @staticmethod
    async def update_one_by_id(db: AsyncSession, id: UUID, update_req: CarUpdateReq):
        pass

    @staticmethod
    async def delete_one_by_id(db: AsyncSession, id: UUID):
        pass