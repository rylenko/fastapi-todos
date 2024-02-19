from io import BytesIO

import pytest
from PIL import Image
from fastapi import status
from httpx import AsyncClient

from app import app
from app.settings import get_settings
from app.todos.models import Todo
from .utils import make_auth_header


settings = get_settings()


@pytest.mark.asyncio
async def test_get_image(client: AsyncClient, test_todo: Todo) -> None:
	path = settings.IMAGES_DIR.joinpath(test_todo.image_filename)
	url = app.url_path_for("get_image", filename=test_todo.image_filename)

	async with client:
		response = await client.get(url, headers=make_auth_header(
			await test_todo.owner,
		))

	assert response.status_code == status.HTTP_200_OK

	response_image = BytesIO(response.content)
	with Image.open(response_image) as image:
		with Image.open(path) as original_image:
			assert image == original_image
