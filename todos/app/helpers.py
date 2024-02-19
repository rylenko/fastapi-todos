from __future__ import annotations

import secrets
from math import ceil
from typing import Optional, TypedDict

from PIL import Image
from tortoise import models, fields
from tortoise.queryset import QuerySet
from fastapi import status, Request, UploadFile, HTTPException

from . import app
from .settings import get_settings


settings = get_settings()


def send_sms(to: str, message: str) -> None:
	app.state.twilio_client.messages.create(
		to, from_=settings.TWILIO_MOBILE_NUMBER, body=message,
	)


def delete_image(filename: str, /) -> None:
	settings.IMAGES_DIR.joinpath(filename).unlink()


def save_image(image: UploadFile, /) -> str:
	"""Generates a filename for the image and saves the image below it.
	If the size of the transferred image was larger than `IMAGES_MAX_SIZE`,
	then it will be equated to it.

	:return: Generated filename
	"""

	if image.content_type not in settings.IMAGES_ALLOWED_CONTENT_TYPES:
		raise HTTPException(
			status.HTTP_400_BAD_REQUEST,
			"Invalid content type.",
		)

	while True:
		# Generate unique save path for image
		filename = secrets.token_hex(16) + ".jpg"
		save_path = settings.IMAGES_DIR.joinpath(filename)
		if not save_path.exists():
			break

	with Image.open(image.file) as new_image:
		# Small important corrections and saving
		if new_image.mode != "RGB":
			new_image = new_image.convert("RGB")
		new_image.thumbnail(settings.IMAGES_MAX_SIZE, Image.LANCZOS)
		new_image.save(save_path, optimize=True, quality=95)

	return filename


async def paginate(
	queryset: QuerySet, view_url: str, current_page: int, per_page: int,
) -> PaginationResult:
	if current_page < 1:
		raise ValueError("`current_page` must be >= 1.")
	elif per_page < 1:
		raise ValueError("`per_page` must be >= 1.")

	pages_count = ceil(await queryset.count() / per_page)

	offset = (current_page - 1) * per_page
	queryset = queryset.limit(per_page).offset(offset)

	# On the first page, if there are no objects,
	# we can place a corresponding inscription.
	if await queryset.count() < 1 and current_page != 1:
		raise HTTPException(status.HTTP_404_NOT_FOUND, "Page not found.")

	view_url += "?page=%d"
	previous_page_url = view_url % (current_page - 1) \
		if current_page > 1 else None
	next_page_url = view_url % (current_page + 1) \
		if current_page < pages_count else None

	return {
		'queryset': queryset,
		'pages_count': pages_count,
		'previous_page_url': previous_page_url,
		'next_page_url': next_page_url,
	}


class PaginationResult(TypedDict):
	queryset: QuerySet
	pages_count: int
	previous_page_url: Optional[str]
	next_page_url: Optional[str]


class BaseModel(models.Model):
	id = fields.IntField(pk=True)
	created_at = fields.DatetimeField(auto_now_add=True)
	updated_at = fields.DatetimeField(auto_now=True)

	class Meta:
		abstract = True
