from fastapi import FastAPI
from twilio.rest import Client as TwilioClient

from .settings import get_settings
from .initializers import (
	register_database,
	add_middlewares,
	add_exception_handlers,
	include_routers,
)


settings = get_settings()

app = FastAPI()
register_database(app)
add_middlewares(app)
add_exception_handlers(app)
include_routers(app)

app.state.twilio_client = TwilioClient(
	settings.TWILIO_ACCOUNT_SID,
	settings.TWILIO_AUTH_TOKEN,
)
