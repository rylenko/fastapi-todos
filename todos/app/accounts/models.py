from __future__ import annotations

from typing import Any
from datetime import datetime

import jwt
from tortoise import fields, Tortoise
from tortoise.validators import MinLengthValidator, RegexValidator
from bcrypt import hashpw, checkpw, gensalt

from ..settings import get_settings
from ..helpers import BaseModel, send_sms


settings = get_settings()


class User(BaseModel):
	phone_number = fields.CharField(
		max_length=17,
		unique=True,
		index=True,
		validators=[RegexValidator(r"^\+?\d\d{9,15}$", 0)],
	)
	password = fields.CharField(
		max_length=255,
		validators=[MinLengthValidator(6)],
	)
	is_active = fields.BooleanField(default=True)
	phone_number_is_confirmed = fields.BooleanField(default=False)

	# todos: fields.ReverseRelation[Todo]

	class Meta:
		ordering = ("-created_at",)

	def __repr__(self) -> str:
		return "<User phone_number=\"%s\">" % self.phone_number

	async def delete(*args: Any, **kwargs: Any) -> None:
		raise RuntimeError(
			"You cannot delete a user. Use `.deactivate` instead.",
		)

	async def deactivate(self) -> None:
		self.is_active = False  # type: ignore
		await self.save(update_fields=("is_active",))

	def set_password(self, password: str, /) -> None:
		self.password \
			= hashpw(password.encode(), gensalt()).decode()  # type: ignore

	def check_password(self, password: str, /) -> bool:
		return checkpw(password.encode(), self.password.encode())

	def generate_token(self) -> str:
		expires_at = datetime.utcnow() + settings.TOKEN_MAX_AGE
		data = {'id': self.id, 'exp': expires_at}

		return jwt.encode(
			data,
			settings.SECRET_KEY,
			settings.JWT_ALGORITHM,
		).decode()

	def send_sms(self, message: str, /) -> None:
		send_sms(self.phone_number, message)


from ..todos.models import Todo  # noqa
Tortoise.init_models(("app.accounts.models",), "models")
