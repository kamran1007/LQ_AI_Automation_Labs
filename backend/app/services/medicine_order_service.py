from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.medicine_order import MedicineOrder
from app.models.medicine_order_item import MedicineOrderItem


async def create_order(
    db: AsyncSession,
    user_id: int,
    latitude: float | None = None,
    longitude: float | None = None,
    delivery_address: str | None = None,
):
    order = MedicineOrder(
        user_id=user_id,
        status="pending",
        latitude=latitude,
        longitude=longitude,
        delivery_address=delivery_address,
    )

    db.add(order)

    await db.commit()
    await db.refresh(order)

    return order


async def add_order_item(
    db: AsyncSession,
    order_id: int,
    medicine_name: str,
    quantity: int,
):
    item = MedicineOrderItem(
        order_id=order_id,
        medicine_name=medicine_name,
        quantity=quantity,
    )

    db.add(item)

    await db.commit()
    await db.refresh(item)

    return item


async def get_order(
    db: AsyncSession,
    order_id: int,
):
    result = await db.execute(
        select(MedicineOrder).where(
            MedicineOrder.id == order_id
        )
    )

    return result.scalar_one_or_none()


async def update_order_status(
    db: AsyncSession,
    order_id: int,
    status: str,
):
    order = await get_order(
        db=db,
        order_id=order_id,
    )

    if not order:
        return None

    order.status = status

    await db.commit()
    await db.refresh(order)

    return order