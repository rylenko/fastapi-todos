import pytest
from fastapi import status
from httpx import AsyncClient

from app import app
from app.accounts.models import User
from .utils import make_auth_header


@pytest.mark.asyncio
async def test_create_user(client: AsyncClient) -> None:
	url = app.url_path_for("create_user")

	async with client:
		response = await client.post(url, json={
			'phone_number': "+12223334455",
			'password': "test-password",
		})

	assert response.status_code == status.HTTP_201_CREATED
	assert response.json()['phone_number'] == "+12223334455"

	created_user = await User.first()
	assert created_user is not None
	assert created_user.phone_number == "+12223334455"
	assert created_user.password != "test-password"
	assert created_user.check_password("test-password")


@pytest.mark.asyncio
async def test_generate_token_and_get_profile(
	client: AsyncClient, test_user: User,
) -> None:
	# Test token generation
	url = app.url_path_for("generate_token")
	async with client:
		response = await client.post(url, data={
			'phone_number': test_user.phone_number,
			'password': "test-password",
		})
	assert response.status_code == status.HTTP_200_OK
	access_token = response.json().get("access_token")
	assert access_token is not None

	# Validate token
	url = app.url_path_for("get_profile")
	async with client:
		response = await client.get(url, headers={
			'Authorization': "Bearer " + access_token,
		})
	assert response.status_code == status.HTTP_200_OK
	assert response.json()['phone_number'] == test_user.phone_number


@pytest.mark.asyncio
async def test_change_password(client: AsyncClient, test_user) -> None:
	url = app.url_path_for("change_password")

	headers = make_auth_header(test_user)
	json = {'new_password': "new-password",
			'new_password_confirm': "new-password"}

	async with client:
		response = await client.post(url, headers=headers, json=json)

	assert response.status_code == status.HTTP_200_OK
	assert (await User.get(id=test_user.id)).check_password("new-password")


@pytest.mark.asyncio
async def test_update_profile(
	client: AsyncClient,
	test_confirmed_user: User,
) -> None:
	url = app.url_path_for("update_profile")

	headers = make_auth_header(test_confirmed_user)
	json = {'phone_number': "+23334445566"}

	async with client:
		response = await client.put(url, headers=headers, json=json)

	assert response.status_code == status.HTTP_200_OK
	assert response.json()['phone_number'] == "+23334445566"

	updated_user = await User.get(id=test_confirmed_user.id)
	assert updated_user.phone_number == "+23334445566"
	assert not updated_user.phone_number_is_confirmed


@pytest.mark.asyncio
async def test_deactivate_user(client: AsyncClient, test_user) -> None:
	url = app.url_path_for("deactivate_user")

	async with client:
		response = await client.post(
			url,
			headers=make_auth_header(test_user),
			json={'password': "test-password"},
		)

	assert response.status_code == status.HTTP_200_OK
	assert "message" in response.json()
	assert not (await User.get(id=test_user.id)).is_active
