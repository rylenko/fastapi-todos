import shutil
from io import BytesIO
from typing import Iterator

import pytest
from PIL import Image
from httpx import AsyncClient
from fastapi import UploadFile
from tortoise.contrib.test import initializer, finalizer

from app import app
from app.settings import get_settings
from app.todos.models import Todo
from app.accounts.models import User
from .utils import create_test_user


settings = get_settings()


@pytest.fixture
def client() -> Iterator[AsyncClient]:
	if not settings.IMAGES_DIR.exists():
		settings.IMAGES_DIR.mkdir(parents=True)

	initializer(settings.TORTOISE_ORM['apps']['models']['models'])
	yield AsyncClient(app=app, base_url="http://test")
	finalizer()

	shutil.rmtree(settings.MEDIA_DIR)


@pytest.fixture
async def test_user() -> User:
	return await create_test_user()


@pytest.fixture
async def test_confirmed_user() -> User:
	return await create_test_user(phone_number_is_confirmed=True)


@pytest.fixture
def test_image_io() -> BytesIO:
	image_io = BytesIO()
	image = Image.new("RGB", (512, 512), color="red")
	image.save(image_io, "JPEG", optimize=True, quality=95)
	image_io.seek(0)

	return image_io


@pytest.fixture
async def test_todo(test_confirmed_user: User, test_image_io: BytesIO) -> Todo:
	rv = Todo(owner=test_confirmed_user, title="test-title", text="test-text")
	rv.set_image(UploadFile("test-image.jpg", test_image_io, "image/jpg"))
	await rv.save()

	return rv
