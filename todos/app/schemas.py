from typing import List, TypeVar, Generic, Optional

from pydantic import BaseModel
from pydantic.generics import GenericModel


Model = TypeVar("Model", bound=BaseModel)


class Message(BaseModel):
	message: str


class Pagination(GenericModel, Generic[Model]):
	pages_count: int
	previous_page_url: Optional[str]
	next_page_url: Optional[str]
	results: List[Model]
