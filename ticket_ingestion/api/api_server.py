from fastapi import FastAPI
from api.routers.tickets import router as tickets_router

def create_api_server(ticket_ingester_service):
    app = FastAPI()
    app.ticket_ingester = ticket_ingester_service
    app.include_router(tickets_router)
    return app
