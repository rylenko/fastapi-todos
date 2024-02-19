from typing import Any, Dict, Tuple, Optional

from fastapi import Form, File, UploadFile
from tortoise.contrib.pydantic import pydantic_model_creator

from .models import Todo
from .. import schemas as common_schemas


TodoOut = pydantic_model_creator(Todo, name="TodoOut")


class TodoInForm:
	def __init__(
		self,
		title: str = Form(..., min_length=4, max_length=140),
		text: str = Form(..., min_length=5, max_length=1000),
		image: Optional[UploadFile] = File(None),
	) -> None:
		self.title = title
		self.text = text
		self.image = image

	def dict(self, *, exclude: Tuple[str, ...] = ()) -> Dict[str, Any]:
		return {
			key: value
			for key, value in self.__dict__.items()
			if key not in exclude
		}


class TodosOut(common_schemas.Pagination[TodoOut]):  # type: ignore
	pass
