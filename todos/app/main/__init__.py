from fastapi import APIRouter


router = APIRouter(tags=["main"])


from . import views  # noqa
