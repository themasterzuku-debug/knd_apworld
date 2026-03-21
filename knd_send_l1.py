import asyncio
import json

import dolphin_memory_engine as dme
import websockets

SERVER = "ws://archipelago.gg:65345"
SLOT = "Zuku"
PASSWORD = "None"
GAME = "Codename: Kids Next Door (GC)"

L1_FLAG_ADDR = 0x8076F54F
L1_LOCATION_NAME = "Stage_01_Tutorial_Complete"

async def main():
    # Hook Dolphin and confirm the flag
    dme.hook()
    v = dme.read_bytes(L1_FLAG_ADDR, 1)[0]
    print(f"L1 flag @ {hex(L1_FLAG_ADDR)} = {v}")
    if v != 1:
        print("L1 flag is not 1 yet. Beat Stage 1 and return to menu, then run again.")
        return

    # Connect to AP server
    async with websockets.connect(SERVER) as ws:
        await ws.send(json.dumps([{
            "cmd": "Connect",
            "password": PASSWORD,
            "game": GAME,
            "name": SLOT,
            "uuid": "knd-l1-manual-check",
            "version": {"major": 0, "minor": 6, "build": 4, "class": "Version"},
            "tags": ["KNDManual"],
            "items_handling": 0
        }]))

        # Ask for DataPackage so we can map name -> id
        await ws.send(json.dumps([{"cmd": "GetDataPackage"}]))

        datapkg = None
        while datapkg is None:
            packets = json.loads(await ws.recv())
            for p in packets:
                if p.get("cmd") == "DataPackage":
                    datapkg = p["data"]
                    break

        game_dp = datapkg["games"][GAME]
        loc_id = game_dp["location_name_to_id"].get(L1_LOCATION_NAME)

        if loc_id is None:
            print(f"Could not find location in DataPackage: {L1_LOCATION_NAME}")
            print("That means the server's seed/world doesn't have that location name.")
            return

        # Send the check
        await ws.send(json.dumps([{"cmd": "LocationChecks", "locations": [loc_id]}]))
        print(f"SENT LocationCheck: {L1_LOCATION_NAME} -> {loc_id}")

if __name__ == "__main__":
    asyncio.run(main())
