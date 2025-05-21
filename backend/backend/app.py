from fastapi import FastAPI
from backend.routes import routers


app = FastAPI()
 

@app.get("/")
def read_root():
    return {"Hello": "World..."}
 

for router in routers:
    app.include_router(router)


# fastapi dev app.py --host 0.0.0.0
 