from __future__ import annotations

import jwt
from tortoise.exceptions import DoesNotExist
from fastapi import Form, status, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from .settings import get_settings


settings = get_settings()
token_scheme = OAuth2PasswordBearer(tokenUrl=settings.TOKEN_URL)


async def _get_user_from_token(token: str, /) -> User:
	algorithms = (settings.JWT_ALGORITHM,)

	try:
		token_data = jwt.decode(
			token,
			settings.SECRET_KEY,
			algorithms=algorithms,
		)
		return await User.get(id=token_data['id'], is_active=True)
	except (jwt.DecodeError, jwt.ExpiredSignatureError, DoesNotExist):
		raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid token.")


async def get_user_from_token(token: str = Depends(token_scheme)) -> User:
	return await _get_user_from_token(token)


async def get_not_confirmed_user_from_token(
	token: str = Depends(token_scheme),
) -> User:
	rv = await _get_user_from_token(token)
	if rv.phone_number_is_confirmed:
		raise HTTPException(
			status.HTTP_403_FORBIDDEN,
			"Your phone is already confirmed.",
		)
	return rv


async def get_confirmed_user_from_token(
	token: str = Depends(token_scheme),
) -> User:
	rv = await _get_user_from_token(token)
	if not rv.phone_number_is_confirmed:
		raise HTTPException(
			status.HTTP_403_FORBIDDEN,
			"Your phone number is not confirmed.",
		)
	return rv


async def get_user_from_form_data(
	phone_number: str = Form(..., min_length=10, max_length=17),
	password: str = Form(..., min_length=6, max_length=255),
) -> User:
	rv = await User.get_or_none(phone_number=phone_number, is_active=True)
	if rv is not None and rv.check_password(password):
		return rv

	raise HTTPException(
		status.HTTP_400_BAD_REQUEST,
		"Invalid phone number or password.",
	)


# Circular imports
from .accounts.models import User
