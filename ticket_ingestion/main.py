import asyncio
import uvicorn

from api.api_server import create_api_server
from services.ticket_ingester import TicketIngester
from db.async_mongodb import AsyncMongoDB

async def start_fastapi(app):
  config = uvicorn.Config(
      app=app,
      host="0.0.0.0",
      port=5000,
      log_level="info",
  )
  server = uvicorn.Server(config)
  await server.serve()

async def main():
  client = AsyncMongoDB(
    uri = "mongodb://localhost:27017",
    database = "ticket_router"
  )
  await client.connect()
  tickets_collection = client.collection("tickets")

  service = TicketIngester(
    collection = tickets_collection
  )

  app = create_api_server(service)
  await start_fastapi(app)

if __name__ == "__main__":
  asyncio.run(main())