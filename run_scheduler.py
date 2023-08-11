import asyncio
from background.check_battle import check_battle_completion


async def main():
    while True:
        await check_battle_completion()
        await asyncio.sleep(60)


if __name__ == "__main__":
    asyncio.run(main())
