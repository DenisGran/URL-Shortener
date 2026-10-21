"""GET / — placeholder until the home page form lands (T14, FR12 home page)."""

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

router = APIRouter()


@router.get("/", response_class=PlainTextResponse)
async def home() -> str:
    return "rapid.codes — coming soon"
