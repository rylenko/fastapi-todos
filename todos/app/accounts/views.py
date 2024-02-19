import secrets
from typing import Dict

from fastapi import Body, status, Depends, Request, HTTPException, \
	BackgroundTasks
from . import router, schemas
from .models import User
from .. import schemas as common_schemas
from ..settings import get_settings
from ..dependencies import (
	get_user_from_form_data,
	get_user_from_token,
	get_not_confirmed_user_from_token,
)


settings = get_settings()


async def _validate_phone_number_unique(phone_number: str, /) -> None:
	if await User.filter(phone_number=phone_number).exists():
		raise HTTPException(status.HTTP_400_BAD_REQUEST,
							"A user with this phone number already exists.")


@router.post(
	"/",
	response_model=schemas.UserOut,
	status_code=status.HTTP_201_CREATED,
)
async def create_user(
	data: schemas.UserInCreate,
) -> schemas.UserOut:  # type: ignore
	await _validate_phone_number_unique(data.phone_number)

	new_user = User(
		phone_number=data.phone_number,
		phone_number_is_confirmed=True,
	)
	new_user.set_password(data.password)
	await new_user.save()

	return await schemas.UserOut.from_tortoise_orm(new_user)


@router.post("/token/", response_model=schemas.Token)
async def generate_token(
	user: User = Depends(get_user_from_form_data),
) -> Dict[str, str]:
	return {'access_token': user.generate_token(), 'token_type': "bearer"}


@router.get("/profile/", response_model=schemas.UserOut)
async def get_profile(
	user: User = Depends(get_user_from_token),
) -> schemas.UserOut:  # type: ignore
	return await schemas.UserOut.from_tortoise_orm(user)


@router.put("/profile/", response_model=schemas.UserOut)
async def update_profile(
	data: schemas.UserInUpdate,
	user: User = Depends(get_user_from_token),
) -> schemas.UserOut:  # type: ignore
	if data.phone_number != user.phone_number:
		await _validate_phone_number_unique(data.phone_number)

		if user.phone_number_is_confirmed:
			user.phone_number_is_confirmed = False  # type: ignore

	user.update_from_dict(data.dict())
	await user.save()

	return await schemas.UserOut.from_tortoise_orm(user)


@router.post(
	"/phone-number/confirm/ask/",
	response_model=common_schemas.Message,
)
async def ask_confirm_phone_number(
	request: Request,
	background_tasks: BackgroundTasks,
	user: User = Depends(get_not_confirmed_user_from_token),
) -> Dict[str, str]:
	code = request.session['confirm_code'] = secrets.token_hex(3)
	background_tasks.add_task(user.send_sms, "Confirmation code: %s" % code)
	return {'message': "A confirmation code was sent to your phone."}


@router.post("/phone-number/confirm/", response_model=common_schemas.Message)
async def confirm_phone_number(
	request: Request,
	data: schemas.PhoneNumberConfirm,
	user: User = Depends(get_not_confirmed_user_from_token),
) -> Dict[str, str]:
	code = request.session.get("confirm_code")

	if code is None:
		raise HTTPException(status.HTTP_403_FORBIDDEN,
							"You did not ask for phone number confirmation.")
	elif data.code != code:
		raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid code.")

	del request.session['confirm_code']
	user.phone_number_is_confirmed = True  # type: ignore
	await user.save(update_fields=("phone_number_is_confirmed",))

	return {'message': "Your phone number was successfully confirmed."}


@router.post("/password/change/", response_model=common_schemas.Message)
async def change_password(
	data: schemas.PasswordChange,
	user: User = Depends(get_user_from_token),
) -> Dict[str, str]:
	user.set_password(data.new_password)
	await user.save(update_fields=("password",))

	return {'message': "Your password has been successfully changed."}


@router.post("/deactivate/", response_model=common_schemas.Message)
async def deactivate_user(
	password: str = Body(..., embed=True),
	user: User = Depends(get_user_from_token),
) -> Dict[str, str]:
	if not user.check_password(password):
		raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid password.")

	await user.deactivate()
	return {'message': "Your account has been successfully deactivated."}
