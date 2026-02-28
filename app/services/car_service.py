
# Response
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

# Models and Types
from typing import List
from uuid import UUID
from app.models.validations.items import CarUpdateReq, RentalStatusEnum, Car

# Session
from sqlalchemy.ext.asyncio import AsyncSession

# Schemas
from app.models.orm import CarTableSchema, deep_update_orm

# Query
from sqlalchemy import select

class CarService:

    @staticmethod
    async def get_one_by_id(db: AsyncSession, car_id: UUID):

        # Make Query
        query = select(CarTableSchema).where(CarTableSchema.id == car_id)

        result = await db.execute(query)
        car_orm = result.scalar_one_or_none()
        if not car_orm:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Car with id {car_id} not found."
            )
        car = Car.from_orm(car_orm)
        return car

    @staticmethod
    async def get_all(db: AsyncSession, status_filter: RentalStatusEnum | None = None) -> List[Car]:

        # Make Query
        query = select(CarTableSchema)
        if status_filter:
            query = query.where(CarTableSchema.status == status_filter.value)

        # Send Query and return
        result = await db.execute(query)
        cars_orm = result.scalars().all()
        cars = [Car.from_orm(c) for c in cars_orm if c is not None]
        return cars

    @staticmethod
    async def add_one(db: AsyncSession, car: Car) -> Car:

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
        return car

    @staticmethod
    async def update_one_by_id(db: AsyncSession, car_id: UUID, update_req: CarUpdateReq) -> Car:

        # Fetch existing car
        query = select(CarTableSchema).where(CarTableSchema.id == car_id)
        result = await db.execute(query)
        car_orm = result.scalar_one_or_none()

        # no record to update!
        if not car_orm:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Car with id {car_id} not found."
            )

        # Apply updates from CarUpdateReq
        car = Car.from_orm(car_orm)
        car.reconcile_req_diff(update_req)

        # Push back to ORM for update only if changes made
        updated_orm = car.to_orm()
        changed = deep_update_orm(car_orm, updated_orm)

        # Try to update
        if changed:
            try:
                await db.commit()
                await db.refresh(car_orm)
            except IntegrityError:
                await db.rollback()
                raise HTTPException(
                    status_code=409,
                    detail=f"Update caused conflict."
                )

            # Return updated car
            return Car.from_orm(car_orm)

        else:
            return car # no update!

    @staticmethod
    async def delete_one_by_id(db: AsyncSession, car_id: UUID) -> None:

        # Fetch the existing record
        query = select(CarTableSchema).where(CarTableSchema.id == car_id)
        result = await db.execute(query)
        car_orm = result.scalar_one_or_none()

        # no record exists
        if not car_orm:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Car with id {car_id} not found."
            )

        # Delete record
        try:
            await db.delete(car_orm)
            await db.commit()

        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Cannot delete car {car_id} due to database constraints."
            )

        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Unexpected error occurred while deleting car {car_id}."
            )

        return