
# Response
from fastapi import HTTPException, status

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
        cars = [Car.from_orm(c) for c in cars_orm]
        return cars

    @staticmethod
    async def add_one(db: AsyncSession, car: Car):

        # Convert Pydantic model to ORM
        car_orm = car.to_orm()

        # Add record to session
        db.add(car_orm)
        try:
            await db.commit() # Commit transaction
            await db.refresh(car_orm) # Refresh to get any defaults from DB
        except Exception:
            # Rollback on error
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Car with id {car.id} already exists."
            )
        return Car.from_orm(car_orm)

    @staticmethod
    async def update_one_by_id(db: AsyncSession, id: UUID, update_req: CarUpdateReq):
        return

    @staticmethod
    async def delete_one_by_id(db: AsyncSession, id: UUID):
        return