import asyncio
from contextlib import aclosing


class LegacyNetworkSocket:
    def __init__(self, host):
        self.host = host

    async def connect(self):
        print(f"Socket: [CONNECTING] {self.host} এর সাথে কানেক্ট করা হচ্ছে...")
        await asyncio.sleep(0.1)
        print(f"Socket: [OPENED] Socket Opened For {self.host}")
        return self

    async def send_data(self, message):
        print(f"Socket: [SENDING] Sending: {message}")
        await asyncio.sleep(0.05)
        print(f"Socket: [SENT] Successfully sent: {message}")

    async def aclose(self):
        print(f"Socket: [CLOSING] এসিনক্রোনাস ক্লিনআপ অপারেশন শুরু হচ্ছে...")
        await asyncio.sleep(0.1)
        print(f"Socket: [CLOSED] Socket for {self.host} has been explicitly closed via aclose().")


async def main():
    print("--- Main Task Start ---")

    socket_instance = LegacyNetworkSocket("api.example.com")
    await socket_instance.connect()

    print("\n--- async with Block Entry ---")

    async with aclosing(socket_instance) as socket:
        await socket.send_data("Data Payload 1")
        await socket.send_data("Data Payload 2")

        print("Main Loop: Inside the block - Task processing is about to end.")

    print("\n--- async with Came out of the block. ---")
    print("Main: async with Normal code outside the block is running...")
    print("--- Main Task End ---")


asyncio.run(main())
