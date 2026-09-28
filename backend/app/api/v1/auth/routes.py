from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.v1.auth.schemas import LoginIn, RegisterIn, TokenOut, UserOut
from app.api.v1.dependencies import CurrentUser, get_authenticate_user, get_register_reviewer
from app.auth.application.use_cases import AuthenticateUser, RegisterReviewer

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
async def login(
    credentials: LoginIn,
    use_case: Annotated[AuthenticateUser, Depends(get_authenticate_user)],
) -> TokenOut:
    token = await use_case.execute(email=credentials.email, password=credentials.senha)
    return TokenOut.from_token(token)


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    payload: RegisterIn,
    use_case: Annotated[RegisterReviewer, Depends(get_register_reviewer)],
) -> TokenOut:
    token = await use_case.execute(name=payload.nome, email=payload.email, password=payload.senha)
    return TokenOut.from_token(token)


@router.get("/me")
async def me(user: CurrentUser) -> UserOut:
    return UserOut.from_user(user)
