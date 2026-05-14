import asyncio
from db.ticket_crud import TicketCRUD

class TicketIngester:
  def __init__(self, collection):
    self.ticket_crud = TicketCRUD(collection)


  # async def ingest_ticket(self, ticket):
  #   return f"{ticket.ticket_id} is under process..."

  async def ingest_ticket(self, ticket):
    try:
      existing_ticket = await self.ticket_crud.get_ticket_by_id(ticket.ticket_id)
      if existing_ticket:
        return f"{ticket.ticket_id} already exists"

      inserted_ticket_id = await self.ticket_crud.insert_ticket(ticket)
      saved_ticket = await self.ticket_crud.get_ticket_by_id(
          inserted_ticket_id
      )

      return saved_ticket
    except exception as e:
      raise
