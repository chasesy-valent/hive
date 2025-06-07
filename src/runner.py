from hive import ComponentFactory

from dotenv import load_dotenv
import asyncio


load_dotenv()

async def main():
    # initialize component factory
    factory = ComponentFactory()

    # create necessary components

    # define agent orchestration pattern and run agentic system

    # cleanup
    await factory.close()

if __name__ == "__main__":
    asyncio.run(main())