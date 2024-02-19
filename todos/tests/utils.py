from typing import Any, Dict

from app.accounts.models import User


def make_auth_header(user: User) -> Dict[str, str]:
	return {'Authorization': "Bearer " + user.generate_token()}


async def create_test_user(**kwargs: Any) -> User:
	rv = User(phone_number="+12223334455", **kwargs)
	rv.set_password("test-password")
	await rv.save()

	return rv
