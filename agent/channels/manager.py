import asyncio

class ChannelManager:
    def __init__(self, channels):
        assert len(channels) == 1, "Only one channel should be active at a time."
        self.channel = channels[0]

    async def get_query(self):
        return await self.channel.get_query()

    async def send_response(self, message, user_id=None):
        await self.channel.send_response(message, user_id)

    async def start(self):
        await self.channel.start()

    async def stop(self):
        await self.channel.stop()
