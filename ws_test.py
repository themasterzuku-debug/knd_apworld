import asyncio
import websockets

SERVER = "ws://127.0.0.1:65345"  # we will change this if needed

async def main():
    async with websockets.connect(SERVER):
        print("WEBSOCKET CONNECT OK")

asyncio.run(main())
