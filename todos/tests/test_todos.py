from io import BytesIO

import pytest
from fastapi import status
from httpx import AsyncClient

from app import app
from app.settings import get_settings
from app.todos.models import Todo
from app.accounts.models import User
from .utils import make_auth_header


settings = get_settings()


@pytest.mark.asyncio
async def test_get_todos(
	client: AsyncClient,
	test_confirmed_user: User,
) -> None:
	todos_for_create = []
	for i in range(1, 11):
		todos_for_create.append(Todo(
			owner=test_confirmed_user,
			title=str(i) + "-title",
			text=str(i) + "-text",
		))
	await Todo.bulk_create(todos_for_create)

	url = app.url_path_for("get_todos")

	async with client:
		headers = make_auth_header(test_confirmed_user)
		response = await client.get(url + "?page=2", headers=headers)

	assert response.status_code == status.HTTP_200_OK

	full_url = str(client.base_url) + str(url)
	json = response.json()

	assert json['pages_count'] == 3
	assert json['previous_page_url'] == full_url + "?page=1"
	assert json['next_page_url'] == full_url + "?page=3"
	assert json['results'][0]['title'] == "6-title"
	assert json['results'][3]['title'] == "3-title"


@pytest.mark.asyncio
async def test_create_todo(
	client: AsyncClient, test_confirmed_user: User, test_image_io: BytesIO,
) -> None:
	url = app.url_path_for("create_todo")

	data = {'title': "test-todo-title", 'text': "test-todo-text"}
	files = {'image': ("test-image.jpg", test_image_io)}
	headers = make_auth_header(test_confirmed_user)

	async with client:
		response \
			= await client.post(url, data=data, files=files, headers=headers)

	assert response.status_code == status.HTTP_201_CREATED
	created_todo = await Todo.first()
	assert created_todo is not None

	assert (await created_todo.owner).id == test_confirmed_user.id
	assert created_todo.title == "test-todo-title"
	assert settings.IMAGES_DIR.joinpath(created_todo.image_filename).exists()


@pytest.mark.asyncio
async def test_get_todo(client: AsyncClient, test_todo: Todo) -> None:
	url = app.url_path_for("get_todo", id=test_todo.id)  # type: ignore
	headers = make_auth_header(await test_todo.owner)

	async with client:
		response = await client.get(url, headers=headers)

	assert response.status_code == status.HTTP_200_OK
	assert response.json()['title'] == test_todo.title


@pytest.mark.asyncio
async def test_update_todo(client: AsyncClient, test_todo: Todo) -> None:
	"""I have not done any image-related tests here. The reason for this
	is that the `file` attribute of `fastapi.UploadFile` objects breaks
	and becomes `tempfile.SpooledTemporaryFile` when `PUT` requests are
	made, whereas normally they are `io.BytesIO`."""

	url = app.url_path_for("update_todo", id=test_todo.id)  # type: ignore

	data = {'title': "updated-title", 'text': "updated-text"}
	headers = make_auth_header(await test_todo.owner)

	async with client:
		response = await client.put(url, data=data, headers=headers)

	assert response.status_code == status.HTTP_200_OK

	updated_todo = await Todo.get(id=test_todo.id)
	assert updated_todo.title == "updated-title"
	assert updated_todo.text == "updated-text"


@pytest.mark.asyncio
async def test_delete_todo(client: AsyncClient, test_todo: Todo) -> None:
	url = app.url_path_for("delete_todo", id=test_todo.id)  # type: ignore
	headers = make_auth_header(await test_todo.owner)

	async with client:
		response = await client.delete(url, headers=headers)

	assert response.status_code == status.HTTP_204_NO_CONTENT

	assert await Todo.get_or_none(id=test_todo.id) is None
	assert not settings.IMAGES_DIR.joinpath(test_todo.image_filename).exists()
