from .base import Channel
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio
import json
from urllib.parse import urlparse

class ChromeChannel(Channel):
    def __init__(self, url="http://localhost:5000", ready_flag=None):
        # Parse the URL to get host and port if needed
        parsed = urlparse(url)
        self.host = parsed.hostname or "0.0.0.0"
        self.port = parsed.port or 5000
        self.app = FastAPI()
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        self.loop = asyncio.get_event_loop()
        self.query_queue = asyncio.Queue()
        self.response_queue = asyncio.Queue()
        self._server = None
        self.ready_flag = ready_flag
        self.response_futures = {}  # user_id -> Future
        self.channel_manager = None

        @self.app.get("/status")
        async def status():
            return {"status": "ready" if self.ready_flag and self.ready_flag.is_set() else "initializing"}

        @self.app.get("/query")
        async def query(request: Request, message: str):
            user_id = "chrome"
            future = asyncio.get_event_loop().create_future()
            self.response_futures[user_id] = future
            await self.query_queue.put((user_id, message))
            try:
                response = await future
                print(f"Returning to Chrome: {response}")
                return JSONResponse({"type": "final", "content": response})
            except Exception as e:
                return JSONResponse({"error": str(e)}, status_code=500)

    def set_channel_manager(self, channel_manager):
        self.channel_manager = channel_manager

    async def get_query(self) -> tuple[str, str]:
        return await self.query_queue.get()

    async def send_response(self, message: str, user_id: str):
        # Set the result for the waiting future
        if user_id in self.response_futures:
            self.response_futures[user_id].set_result(message)
            del self.response_futures[user_id]

    async def start(self):
        config = uvicorn.Config(self.app, host=self.host, port=self.port, log_level="info")
        self._server = uvicorn.Server(config)
        asyncio.create_task(self._server.serve())

    async def stop(self):
        if self._server:
            self._server.should_exit = True
