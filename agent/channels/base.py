from abc import ABC, abstractmethod

class Channel(ABC):
    @abstractmethod
    async def get_query(self) -> tuple[str, str]:
        """Returns (user_id, query)"""
        pass

    @abstractmethod
    async def send_response(self, message: str, user_id: str):
        pass

    @abstractmethod
    async def start(self):
        pass

    @abstractmethod
    async def stop(self):
        pass
