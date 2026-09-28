from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.v1.auth.schemas import AdminOut, LoginIn, TokenOut
from app.api.v1.dependencies import CurrentAdmin, get_authenticate_admin
from app.auth.application.use_cases import AuthenticateAdmin

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
async def login(
    credentials: LoginIn,
    use_case: Annotated[AuthenticateAdmin, Depends(get_authenticate_admin)],
) -> TokenOut:
    token = await use_case.execute(email=credentials.email, password=credentials.senha)
    return TokenOut.from_token(token)


@router.get("/me")
async def me(admin: CurrentAdmin) -> AdminOut:
    return AdminOut.from_admin(admin)
