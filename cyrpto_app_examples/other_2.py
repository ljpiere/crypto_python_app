import rx
from rx import operators as ops
import asyncio
import websockets
import json

async def price_feed():
    uri = "wss://ws.coincap.io/prices?assets=bitcoin,ethereum,dogecoin"
    async with websockets.connect(uri) as websocket:
        while True:
            message = await websocket.recv()
            yield json.loads(message)

def create_price_observable():
    return rx.from_async(price_feed())

async def main():
    price_observable = create_price_observable()

    price_observable.pipe(
        ops.flat_map(lambda x: rx.from_iterable(x.items())),
        ops.group_by(lambda x: x[0]),
        ops.flat_map(lambda group: group.pipe(
            ops.map(lambda x: (x[0], float(x[1]))),
            ops.distinct_until_changed(lambda x: x[1])
        ))
    ).subscribe(
        on_next=lambda x: print(f"{x[0].capitalize()}: ${x[1]:.2f}"),
        on_error=lambda e: print(f"Error: {e}"),
        on_completed=lambda: print("Completed")
    )

    await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())