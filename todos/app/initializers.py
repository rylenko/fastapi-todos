from fastapi import FastAPI, Response, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from tortoise.exceptions import ValidationError
from tortoise.contrib.fastapi import register_tortoise
from starlette.middleware.sessions import SessionMiddleware
from traceback import format_exc, format_exception

from . import main, accounts, todos
from .settings import get_settings


settings = get_settings()


def register_database(app: FastAPI, /) -> None:
	register_tortoise(app, settings.TORTOISE_ORM, add_exception_handlers=True)


def add_middlewares(app: FastAPI, /) -> None:
	app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)
	app.add_middleware(
		CORSMiddleware,
		allow_origins=settings.ALLOW_ORIGINS,
		allow_credentials=True,
		allow_methods=("*",),
		allow_headers=("*",),
	)


def include_routers(app: FastAPI, /) -> None:
	app.include_router(main.router)
	app.include_router(accounts.router, prefix="/accounts")
	app.include_router(todos.router, prefix="/todos")


def add_exception_handlers(app: FastAPI, /) -> None:
	@app.exception_handler(ValidationError)
	def handle_validation_error(
		_: Request,
		exc: ValidationError,
	) -> JSONResponse:
		return JSONResponse({'detail': str(exc)}, status_code=400)

	if settings.DISPLAY_TRACEBACK_ON_500:
		@app.exception_handler(Exception)
		async def handle_exception(_: Request, exc: Exception):
			f = format_exception(Exception, value=exc, tb=exc.__traceback__)
			return Response(content="".join(f))
