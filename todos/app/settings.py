import os
import sys
from pathlib import Path
from datetime import timedelta
from functools import lru_cache
from typing import Any, Set, Dict, Tuple, Union

from dotenv import load_dotenv
from pydantic import BaseSettings


_TESTING = "pytest" in sys.argv[0]
_BASE_DIR = Path(__file__).resolve().parent
_MODEL_PATHS = (
	"app.accounts.models",
	"app.todos.models",
	"aerich.models",
)

load_dotenv(_BASE_DIR.parent.joinpath(".env"))


def _make_tortoise_orm_config(uri: str) -> Dict[str, Any]:
	return {
		'connections': {'default': uri},
		'apps': {
			'models': {
				'models': _MODEL_PATHS,
				'default_connection': "default",
			}
		},
	}


_POSTGRES_TORTOISE_ORM = _make_tortoise_orm_config(
	"postgres://%s:%s@db:5432/%s" % (
		os.environ['POSTGRES_USER'],
		os.environ['POSTGRES_PASSWORD'],
		os.environ['POSTGRES_DB'],
	),
)


class Settings(BaseSettings):
	TESTING: bool = _TESTING
	DISPLAY_TRACEBACK_ON_500 = True
	SECRET_KEY: str

	BASE_DIR: Path = _BASE_DIR
	MEDIA_DIR: Path = _BASE_DIR.joinpath("media")
	IMAGES_DIR: Path = MEDIA_DIR.joinpath("images")

	TORTOISE_ORM: Dict[str, Any] = _POSTGRES_TORTOISE_ORM
	ALLOW_ORIGINS: Tuple[str, ...] = ("http://localhost:8000",)

	JWT_ALGORITHM: str = "HS256"
	TOKEN_URL: str = "/accounts/token/"
	TOKEN_MAX_AGE: timedelta = timedelta(days=1)

	IMAGES_MAX_SIZE: Tuple[int, int] = (1920, 1080)
	IMAGES_ALLOWED_EXTENSIONS: Set[str] = {"jpeg", "jpg", "png"}
	IMAGES_ALLOWED_CONTENT_TYPES: Set[str] = {
		"image/%s" % ext for ext in IMAGES_ALLOWED_EXTENSIONS
	}

	TODOS_PER_PAGE: int = 4

	TWILIO_ACCOUNT_SID: str
	TWILIO_AUTH_TOKEN: str
	TWILIO_MOBILE_NUMBER: str

	class Config:
		env_file = _BASE_DIR.parent.joinpath(".env")


class TestingSettings(Settings):
	MEDIA_DIR: Path = _BASE_DIR.joinpath("test_media")
	IMAGES_DIR: Path = MEDIA_DIR.joinpath("images")

	TESTING_DIR: Path = _BASE_DIR.parent.joinpath("tests")
	TORTOISE_ORM: Dict[str, Any] \
		= _make_tortoise_orm_config("sqlite://:memory")


@lru_cache()
def get_settings() -> Union[TestingSettings, Settings]:
	return TestingSettings() if _TESTING else Settings()
