from fastapi import APIRouter


router = APIRouter(tags=["accounts"])


from . import views  # noqa
