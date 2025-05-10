from typing import Annotated, Union

from fastapi import APIRouter, Depends, FastAPI

from auth_route import router as router_auth_route
from auth_model import User
from auth_service import get_current_active_user
app = FastAPI()

router = APIRouter(prefix="", dependencies=[Depends(get_current_active_user)])

@router.get("/")
def read_root():
    return {"Hello": "World..."}


@router.get("/items/{item_id}")
def read_item(current_user: Annotated[User, Depends(get_current_active_user)],
              item_id: int, q: Union[str, None] = None,):
    return {"item_id": item_id, "q": q}


app.include_router(router)
app.include_router(router_auth_route)

# fastapi dev app.py --host 0.0.0.0