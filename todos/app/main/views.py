from fastapi import status, Depends, HTTPException
from fastapi.responses import FileResponse

from . import router
from ..settings import get_settings
from ..dependencies import get_confirmed_user_from_token
from ..accounts.models import User


settings = get_settings()


@router.get("/media/images/{filename}/", response_class=FileResponse)
async def get_image(
	filename: str,
	user: User = Depends(get_confirmed_user_from_token),
) -> FileResponse:
	image_path = settings.IMAGES_DIR.joinpath(filename)
	if not (
		image_path.exists()
		and user.todos.filter(image_filename=filename).exists()  # type: ignore
	):
		raise HTTPException(status.HTTP_404_NOT_FOUND, "Image not found.")

	return FileResponse(str(image_path))
