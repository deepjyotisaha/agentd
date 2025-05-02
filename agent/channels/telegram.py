from .base import Channel
import httpx
import asyncio
import json
from config.log_config import setup_logging

logger = setup_logging(__name__)


class TelegramChannel(Channel):
    def __init__(self, multi_mcp, ready_flag):
        self.multi_mcp = multi_mcp
        self.ready_flag = ready_flag

    async def get_query(self) -> tuple[str, str]:
        if not self.ready_flag.is_set():
            await self.send_response("Agent is initializing, please wait...", "")
            return None
        # Use multi_mcp to call the tool
        result = await self.multi_mcp.call_tool("get-next-telegram-message", {})
        msg = result.content[0].text
        msg_data = json.loads(msg.replace("'", '"'))  # crude fix if needed
        return msg_data["user_id"], msg_data["text"]

    async def send_response(self, message: str, user_id: str):
        await self.multi_mcp.call_tool(
            "send-telegram-message",
            {"text": message, "user_id": user_id}
        )

    async def start(self):
        pass

    async def stop(self):
        pass
