import uvicorn as uvicorn
from fastapi import Cookie, FastAPI, Response
from database.async_db import asyncHandler as DB
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

app = FastAPI()


class Product(BaseModel):
    id: int
    name: str
    photo: str
    description: str


class User(BaseModel):
    user_id: int


class Message(BaseModel):
    message: str


@app.get("/login",
         responses={
             404: {"model": Message, "description": "User not found"},
             200: {"model": User, "description": "ID of user",
                   "content": {
                       "application/json": {
                           "example": {"user_id": 232}
                       },
                   },
                   },
         },
         )
async def login(response: Response, log, password: str):
    user = await DB.get_user(log, password)
    if user is False:
        return JSONResponse(status_code=404, content={"message": "User not found"})
    else:
        response.set_cookie(key="user_id", value=user['id'])
        return {'user_id': int(user['id'])}


@app.get("/register",
         responses={
             405: {"model": Message, "description": "User already exists"},
             200: {"model": User, "description": "ID of user",
                   "content": {
                       "application/json": {
                           "example": {"user_id": 232}
                       },
                   },
                   },
         })
async def register(response: Response, log, password: str):
    user_id = await DB.add_user(log, password)
    if user_id is False:
        return JSONResponse(status_code=405, content={"message": "User already exists"})
    else:
        response.set_cookie(key="user_id", value=str(user_id))
        return {'user_id': int(user_id)}


@app.get("/")
async def main() -> dict:
    return {"msg": "ok"}


@app.get("/find",
         responses={
             404: {"model": Message, "description": "Product not found"},
             200: {"model": list[Product], "description": "list of products",
                   "content": {
                       "application/json": {
                           "example": [{"id": 1, "photo": "зрщещ", "name": "добрый год", "description": "ажлыжаыза"},
                                       {"id": 2, "photo": "выа", "name": "добрый день", "description": "ыавы"}]
                       },
                   },
                   },
         })
async def find(line):
    res = await DB.get_product_by_req(line)
    if res is None:
        return JSONResponse(status_code=404, content={"message": "Object not found"})
    else:
        return res


@app.post("/rate",
          responses={202: {"model": Message, "message": "ok"}})
async def rate(prod_id: int, user_rate: bool):
    await DB.rate_product(prod_id, user_rate)
    return {"message": "ok"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8031)
