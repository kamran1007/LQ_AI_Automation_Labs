import asyncio

from app.db.database import AsyncSessionLocal
import app.models

from app.services.medicine_order_service import (
    create_order,
    add_order_item,
    get_order,
    update_order_status,
)


async def main():

    async with AsyncSessionLocal() as db:

        # Create order
        order = await create_order(
            db=db,
            user_id=1,
            latitude=24.7955,
            longitude=85.0002,
            delivery_address="Gaya",
        )

        print("ORDER CREATED:")
        print(order.id)
        print(order.status)

        # Add medicine
        item = await add_order_item(
            db=db,
            order_id=order.id,
            medicine_name="Dolo 650",
            quantity=2,
        )

        print("ITEM CREATED:")
        print(item.id)
        print(item.medicine_name)
        print(item.quantity)

        # Get order
        saved_order = await get_order(
            db=db,
            order_id=order.id,
        )

        print("ORDER FOUND:")
        print(saved_order.id)

        # Update status
        updated_order = await update_order_status(
            db=db,
            order_id=order.id,
            status="broadcasted",
        )

        print("ORDER STATUS:")
        print(updated_order.status)


if __name__ == "__main__":
    asyncio.run(main())