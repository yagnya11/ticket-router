from models.models import Ticket
from pymongo.asynchronous.collection import AsyncCollection

class TicketCRUD:
    def __init__(self, collection: AsyncCollection):
        self._collection = collection

    async def insert_ticket(self, ticket: Ticket) -> None:
        await self._collection.insert_one(ticket.model_dump())
        return ticket.ticket_id

    async def get_ticket_by_id(self, ticket_id: str) -> dict | None:
        return await self._collection.find_one(
            {"ticket_id": ticket_id},
            {"_id": 0},
        )