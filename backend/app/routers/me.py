"""Authenticated identity ping."""

from fastapi import APIRouter, Depends

from app.deps import verify_api_key

router = APIRouter(tags=["auth"])


@router.get("/me")
def me(_token: str = Depends(verify_api_key)) -> dict[str, bool]:
    """Validate API key for login flow."""

    return {"ok": True}
