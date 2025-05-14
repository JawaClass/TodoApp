from typing import Annotated, Union
from fastapi import APIRouter, Depends, FastAPI

from backend.services.auth_service import get_current_active_user
from backend.routes import routers
from backend.models import model

app = FastAPI()

test_router = APIRouter(prefix="", dependencies=[Depends(get_current_active_user)])

@test_router.get("/")
def read_root():
    return {"Hello": "World..."}


@test_router.get("/items/{item_id}")
def read_item(current_user: Annotated[model.User, Depends(get_current_active_user)],
              item_id: int, q: Union[str, None] = None,):
    return {"item_id": item_id, "q": q}


app.include_router(test_router)

for router in routers:
    app.include_router(router)


# fastapi dev app.py --host 0.0.0.0