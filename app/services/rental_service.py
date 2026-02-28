
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

# Observability
from ..core.logger import logger

class RentalService:

    @staticmethod
    async def get_one_by_id(db: AsyncSession, rental_id: UUID) -> Rental:

        # Make Query
        query = select(RentalTableSchema).where(RentalTableSchema.id == rental_id)

        result = await db.execute(query)
        rental_orm = result.scalar_one_or_none()
        if not rental_orm:
            logger.warning(f"Rental with id {rental_id} not found.")
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

        if not rentals:
            logger.warning("No Rentals found!")
        return rentals

    @staticmethod
    async def add_one(db: AsyncSession, rental: Rental) -> Rental:

        async with db.begin():

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
                logger.warning(f"Car {rental_orm.car_id} not found")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Car {rental_orm.car_id} not found"
                )

            if car.status != RentalStatusEnum.available.value:
                logger.warning("Car is not available")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Car is not available"
                )

            # Set in use if available ( if in maintenance, no authority to determine its fixed.. )
            if car.status == RentalStatusEnum.available.value:
                car.status = RentalStatusEnum.in_use.value
            else:
                logger.warning("Tried renting a Car that's not available - Rental made but car needs to be fixed before rental")
                # TODO: here would be a good area to add a message queue integration to produce an event to fix a car before rental, consumed by a different service

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
                logger.warning(f"Rental {rental_id} not found.")
                raise HTTPException(
                    status_code=404,
                    detail=f"Rental {rental_id} not found."
                )

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
                logger.info(f"Deleted Rental with id: {rental_id}, and set Car with id: {car.id} to status: {car.status}")

            # Delete rental
            await db.delete(rental_orm)
        return