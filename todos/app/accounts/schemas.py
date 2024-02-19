from typing import Any, Dict

from tortoise.contrib.pydantic import pydantic_model_creator
from pydantic import BaseModel, Field, root_validator

from .models import User
from ..settings import get_settings


settings = get_settings()

UserOut = pydantic_model_creator(User, name="UserOut", exclude=("password",))


class UserInBase(BaseModel):
	phone_number: str = Field(..., min_length=10, max_length=17)


class UserInCreate(UserInBase):
	password: str = Field(..., min_length=6, max_length=255)


class UserInUpdate(UserInBase):
	pass


class Token(BaseModel):
	access_token: str
	token_type: str


class PhoneNumberConfirm(BaseModel):
	code: str = Field(..., min_length=6, max_length=6)


class PasswordChange(BaseModel):
	new_password: str = Field(..., min_length=6, max_length=255)
	new_password_confirm: str = Field(...)

	@root_validator
	def validate_passwords_match(
		cls,
		values: Dict[str, Any],
	) -> Dict[str, Any]:
		if values['new_password'] != values['new_password_confirm']:
			raise ValueError("Passwords must match.")
		return values
