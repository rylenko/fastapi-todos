from fastapi import APIRouter, Depends

from ..dependencies import get_confirmed_user_from_token


router = APIRouter(tags=["todos"], dependencies=(
	Depends(get_confirmed_user_from_token),
))


from . import views  # noqa
