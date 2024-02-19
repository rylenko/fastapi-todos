from __future__ import annotations

from typing import Any, Type

from fastapi import UploadFile
from tortoise import fields, Tortoise
from tortoise.signals import pre_delete

from ..helpers import BaseModel, delete_image, save_image


class Todo(BaseModel):
	owner = fields.ForeignKeyField(
		"models.User", related_name="todos",
		on_delete=fields.CASCADE,
	)
	image_filename = fields.CharField(40, null=True)
	title = fields.CharField(140, index=True)
	text = fields.TextField()

	class Meta:
		ordering = ("-created_at",)

	class PydanticMeta:
		exclude = ("owner", "owner_id")

	def __repr__(self) -> str:
		return "<Todo title=\"%s\">" % self.title

	def set_image(self, image: UploadFile, /) -> None:
		if self.image_filename is not None:
			delete_image(self.image_filename)

		self.image_filename = save_image(image)  # type: ignore


@pre_delete(Todo)
async def _delete_image_before_delete(
	sender: Type[Todo], instance: Todo, *args: Any,
) -> None:
	if instance.image_filename is not None:
		delete_image(instance.image_filename)


from ..accounts.models import User  # noqa
Tortoise.init_models(("app.todos.models",), "models")
