
# Response
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

# Models and Types
from typing import List
from uuid import UUID
from app.models.validations.items import Rental, RentalUpdateReq, RentalStatusEnum, CarUpdateReq
from app.models.orm import RentalTableSchema, deep_update_orm, CarTableSchema

# Session
from sqlalchemy.ext.asyncio import AsyncSession

# Query
from sqlalchemy import select

class RentalService:

    @staticmethod
    async def get_one_by_id(db: AsyncSession, rental_id: UUID) -> Rental:

        # Make Query
        query = select(RentalTableSchema).where(RentalTableSchema.id == rental_id)

        result = await db.execute(query)
        rental_orm = result.scalar_one_or_none()
        if not rental_orm:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Rental with id {rental_id} not found."
            )
        rental = Rental.from_orm(rental_orm)
        return rental


    @staticmethod
    async def get_all(db: AsyncSession) -> List[Rental]:

        # Make Query
        query = select(RentalTableSchema)

        # Send Query and return
        result = await db.execute(query)
        rentals_orm = result.scalars().all()
        rentals = [Rental.from_orm(r) for r in rentals_orm if r is not None]
        return rentals

    @staticmethod
    async def add_one(db: AsyncSession, rental: Rental) -> Rental:

        async with db.begin(): # requires atomic operation since contains read&write operation

            # rental to create
            rental_orm = rental.to_orm()

            # get relevant car
            result = await db.execute(
                select(CarTableSchema)
                .where(CarTableSchema.id == rental_orm.car_id)
                .with_for_update()
            )
            car = result.scalar_one_or_none()

            if not car:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Car {rental_orm.car_id} not found"
                )

            if car.status != RentalStatusEnum.available.value:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Car is not available"
                )

            # Set in use if available ( if in maintenance, no authority to determine its fixed.. )
            if car.status == RentalStatusEnum.available.value:
                car.status = RentalStatusEnum.in_use.value

            # add rental
            db.add(rental_orm)

        await db.refresh(rental_orm)
        return rental

    @staticmethod
    async def delete_one_by_id(db: AsyncSession, rental_id: UUID) -> None:
        async with db.begin():

            # Fetch rental
            result = await db.execute(select(RentalTableSchema).where(RentalTableSchema.id == rental_id))
            rental_orm: RentalTableSchema = result.scalar_one_or_none()
            if not rental_orm:
                raise HTTPException(status_code=404, detail=f"Rental {rental_id} not found.")

            # Fetch car
            result = await db.execute(
                select(CarTableSchema)
                .where(CarTableSchema.id == rental_orm.car_id)
                .with_for_update()
            )
            car: CarTableSchema = result.scalar_one_or_none()

            # Update car status if needed
            if car and car.status == RentalStatusEnum.in_use.value:
                car.status = RentalStatusEnum.available.value

            # Delete rental
            await db.delete(rental_orm)

        # Commit handled by async with db.begin()
        return