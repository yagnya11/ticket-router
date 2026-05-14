from models.models import Ticket
from fastapi import APIRouter, HTTPException, status, Request 

router = APIRouter(prefix = "/tickets", tags = ["tickets"])

@router.post("/ingest")
async def ingest_ticket(ticket: Ticket, request: Request):
  try:
    ticket_ingester = request.app.ticket_ingester
    result = await ticket_ingester.ingest_ticket(ticket)
    return {
      "status": "ok",
      "result": result
    }
  except Exception as e:
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=str(e),
    )
