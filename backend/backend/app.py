from fastapi import FastAPI
# from backend.services.api import ServiceType, require_service
# from backend.services.api.user_google_service import UserGoogleService
# from backend.services.auth_service import get_current_active_user
from backend.routes import routers

app = FastAPI()
 
# test_router = APIRouter(prefix="", dependencies=[Depends(get_current_active_user)])

@app.get("/")
def read_root():
    return {"Hello": "World..."}


# @test_router.get("/items/{item_id}")
# def read_item(current_user: Annotated[model.User, Depends(get_current_active_user)],
#               item_id: int, q: Union[str, None] = None,):
#     return {"item_id": item_id, "q": q}


# app.include_router(test_router)

for router in routers:
    app.include_router(router)


# fastapi dev app.py --host 0.0.0.0

# def resolve_field_type(class_: type[BaseModel], field_name: str):
    
#     types = get_type_hints(class_)
    
#     field_type = types[field_name]
    
#     if not issubclass(type(field_type), type):
#         field_type = get_args(field_type)
        
#         field_type = [_ for _ in field_type if _ is not type(None)]
    
#     return field_type
     



# # class A:
# #     x: str
# #     z: int
# #     b: "B"

# # class B:
# #     a: str
# # print("app called")

# from typing import get_args, get_origin, get_type_hints
# # print(A, type(A), type(type(A)))
# # print(None, type(None), type(type(None)), type(type(type(None))))
# # print(get_args(A))
# # print(get_origin(A), A.__type_params__)
# # print(get_type_hints(A))

# # print(get_type_hints(UserOut))
# # print(get_type_hints(TodoItemOut_Detailed))

# # print("field_type...")
# # # types = get_type_hints(TodoItemOut_Detailed)

# # # print(field_type)
# # # print(get_args(field_type))


# from backend.models.api import UserOut, TodoItemOut_Detailed
# from backend.sa_util.relationships import resolve_field_type

# for fname in TodoItemOut_Detailed.model_fields:
#     # print(k, "::", v, type(v), issubclass(type(v), type))
#     # if not issubclass(type(v), type):
#     #     print("  ", get_args(v))
    
#     print(fname, "::", resolve_field_type(TodoItemOut_Detailed, fname))