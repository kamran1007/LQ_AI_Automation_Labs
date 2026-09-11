import asyncio

from app.services.otp_service import send_otp


async def main():

    mobile = "+918797283371"

    result = await send_otp(mobile)

    print("MSG91 RESPONSE:")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())