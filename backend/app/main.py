"""Точка входа API. Тонкий слой: валидация, маршруты, обработка ошибок."""

from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

load_dotenv()

from .auth import (  # noqa: E402
    COOKIE_NAME,
    CurrentUser,
    get_current_user,
    issue_token,
    verify_password,
)
from .config import get_settings  # noqa: E402
from .db import create_pool  # noqa: E402
from .errors import AssistantError, Unauthorized  # noqa: E402
from .schemas import (  # noqa: E402
    AskRequest,
    AskResponse,
    ErrorResponse,
    LoginRequest,
    MeResponse,
    TicketListResponse,
)
from .services.ask import ask  # noqa: E402
from .services.tickets import insert_ticket, list_tickets  # noqa: E402

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.settings = settings
    app.state.db = await create_pool(settings.database_url)
    try:
        yield
    finally:
        await app.state.db.close()


app = FastAPI(
    title="Ассистент дежурной смены",
    description="Мини-дашборд для команды поддержки хостинга",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.allowed_origins),
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
    allow_credentials=True,
)


@app.exception_handler(AssistantError)
async def assistant_error_handler(_: Request, exc: AssistantError) -> JSONResponse:
    """Любая доменная ошибка превращается в понятный JSON, а не в 500."""

    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(error=exc.message).model_dump(),
    )


@app.get("/api/health")
async def health() -> dict:
    """Фронтенд дергает на старте, чтобы честно показать статус подключения."""

    return {
        "status": "ok",
        "llm_configured": settings.is_configured,
        "provider": settings.provider,
        "model": settings.model,
    }


@app.post("/api/auth/login")
async def login(payload: LoginRequest, request: Request, response: Response) -> MeResponse:
    row = await request.app.state.db.fetchrow(
        "SELECT id, password_hash FROM users WHERE login = $1", payload.login
    )
    if row is None or not verify_password(payload.password, row["password_hash"]):
        raise Unauthorized("Неверный логин или пароль.")

    token = issue_token(row["id"], payload.login, settings.jwt_secret)
    response.set_cookie(
        COOKIE_NAME,
        token,
        httponly=True,
        samesite="lax",
        secure=False,  # локальная разработка по http; на проде за https переключить в true
        max_age=30 * 24 * 60 * 60,
    )
    return MeResponse(login=payload.login)


@app.post("/api/auth/logout")
async def logout(response: Response) -> dict:
    response.delete_cookie(COOKIE_NAME)
    return {"status": "ok"}


@app.get("/api/auth/me")
async def me(user: CurrentUser = Depends(get_current_user)) -> MeResponse:
    return MeResponse(login=user.login)


@app.post("/api/ask", response_model=AskResponse)
async def ask_endpoint(
    payload: AskRequest, request: Request, user: CurrentUser = Depends(get_current_user)
) -> AskResponse:
    if len(payload.question) > settings.max_question_chars:
        raise AssistantError(
            f"Вопрос длиннее {settings.max_question_chars} символов. Сократите его."
        )
    result = await ask(settings, payload.question, payload.mode)

    try:
        await insert_ticket(
            request.app.state.db, user.user_id, payload.question, payload.mode, result.answer, result.meta
        )
    except Exception:
        # Ответ важнее факта его архивации: не роняем запрос из-за сбоя записи в БД.
        pass

    return result


@app.get("/api/tickets", response_model=TicketListResponse)
async def tickets_endpoint(
    request: Request,
    limit: int = 20,
    offset: int = 0,
    q: str | None = None,
    _: CurrentUser = Depends(get_current_user),
) -> TicketListResponse:
    limit = max(1, min(limit, 100))
    offset = max(0, offset)
    items = await list_tickets(request.app.state.db, limit, offset, q)
    return TicketListResponse(items=items, limit=limit, offset=offset)
