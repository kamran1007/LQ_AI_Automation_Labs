import asyncio

from app.db.database import engine
from app.db.base import Base

# Import ALL models here
from app.models.conversation import Conversation
from app.models.user import User
from app.models.merchant import Merchant
from app.models.merchant_branch import MerchantBranch
from app.models.medicine_order import MedicineOrder
from app.models.medicine_order_item import MedicineOrderItem
from app.models.merchant_response import MerchantResponse

async def init_db():

    async with engine.begin() as conn:

        await conn.run_sync(
            Base.metadata.create_all
        )

    print("Database tables created successfully")


if __name__ == "__main__":
    asyncio.run(init_db())