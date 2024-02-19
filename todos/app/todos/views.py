from typing import Any, Dict

from fastapi import Query, status, Depends, Request, Response

from . import router, schemas
from .models import Todo
from ..helpers import paginate
from ..settings import get_settings
from ..dependencies import get_confirmed_user_from_token
from ..accounts.models import User


settings = get_settings()


@router.get("/", response_model=schemas.TodosOut)
async def get_todos(
	request: Request,
	page: int = Query(1, ge=1, alias="page"),
	user: User = Depends(get_confirmed_user_from_token),
) -> schemas.TodosOut:
	queryset = user.todos.all()  # type: ignore
	pagination = await paginate(
		queryset,
		request.url_for("get_todos"),
		page,
		settings.TODOS_PER_PAGE,
	)
	results = await schemas.TodoOut.from_queryset(pagination['queryset'])
	return schemas.TodosOut(
		pages_count=pagination['pages_count'],
		previous_page_url=pagination['previous_page_url'],
		next_page_url=pagination['next_page_url'],
		results=results,
	)


@router.post(
	"/",
	response_model=schemas.TodoOut,
	status_code=status.HTTP_201_CREATED,
)
async def create_todo(
	data: schemas.TodoInForm = Depends(),
	user: User = Depends(get_confirmed_user_from_token),
) -> schemas.TodoOut:  # type: ignore
	new_todo = Todo(owner=user, **data.dict(exclude=("image",)))

	if data.image is not None:
		new_todo.set_image(data.image)

	await new_todo.save()
	return await schemas.TodoOut.from_tortoise_orm(new_todo)


@router.get("/{id}/", response_model=schemas.TodoOut)
async def get_todo(
	id: int,
	user: User = Depends(get_confirmed_user_from_token),
) -> schemas.TodoOut:  # type: ignore
	todo = await user.todos.all().get(id=id)  # type: ignore
	return await schemas.TodoOut.from_tortoise_orm(todo)


@router.put("/{id}/", response_model=schemas.TodoOut)
async def update_todo(
	id: int,
	data: schemas.TodoInForm = Depends(),
	user: User = Depends(get_confirmed_user_from_token),
) -> schemas.TodoOut:  # type: ignore
	todo = await user.todos.all().get(id=id)  # type: ignore
	todo.update_from_dict(data.dict(exclude=("image",)))

	if data.image is not None:
		todo.set_image(data.image)

	await todo.save()
	return await schemas.TodoOut.from_tortoise_orm(todo)


@router.delete(
	"/{id}/",
	response_class=Response,
	status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_todo(
	id: int,
	user: User = Depends(get_confirmed_user_from_token),
) -> Response:
	await (await user.todos.all().get(id=id)).delete()  # type: ignore
	return Response(status_code=status.HTTP_204_NO_CONTENT)
