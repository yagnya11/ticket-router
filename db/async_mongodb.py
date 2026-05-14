from typing import Optional
from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase
from pymongo.asynchronous.collection import AsyncCollection
from pymongo.server_api import ServerApi


class AsyncMongoDB:
    """
    Shared async MongoDB client using PyMongo Async API.
    One client per event loop.
    """

    _client: Optional[AsyncMongoClient] = None

    def __init__(self, uri: str, database: str):
        self.uri = uri
        self.database_name = database

    async def connect(self) -> None:
        if not AsyncMongoDB._client:
            AsyncMongoDB._client = AsyncMongoClient(
                self.uri,
                server_api=ServerApi("1"),
                appname="ticketing-platform",
            )
            await AsyncMongoDB._client.admin.command("ping")

    @property
    def db(self) -> AsyncDatabase:
        if not AsyncMongoDB._client:
            raise RuntimeError("MongoDB not connected. Call connect() first.")
        return AsyncMongoDB._client[self.database_name]

    def collection(self, name: str) -> AsyncCollection:
        return self.db[name]

    async def close(self) -> None:
        if AsyncMongoDB._client:
            await AsyncMongoDB._client.close()
            AsyncMongoDB._client = None