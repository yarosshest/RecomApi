import uvicorn as uvicorn
from fastapi import Cookie, FastAPI, Response
from database.async_db import asyncHandler as DB
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from database.db_init import db_init
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
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
                           "example": {"id": 8986,
                                       "photo": "https://kinopoiskapiunofficial.tech/images/posters/kp/84674.jpg",
                                       "name": "9 рота",
                                       "description": "СССР, 1988-1989 годы, за несколько месяцев до полного вывода "
                                                      "советских войск из Афганистана. Семеро призывников после "
                                                      "нескольких месяцев адской подготовки в учебке под "
                                                      "командованием беспощадного старшины попадают в горнило "
                                                      "афганской кампании.\n\nГруппа десантников, бойцами которой "
                                                      "стали наши герои, получает задание командования - занять "
                                                      "высоту и держать её до прохождения колонны."}
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
          responses={
              404: {"model": Message, "description": "Need to login"},
              202: {"model": Message, "message": "ok"}
          })
async def rate(prod_id: int, user_rate: bool, user_id: int | None = Cookie(default=None)):
    if user_id is None:
        return JSONResponse(status_code=404, content={"message": "Need to login"})
    else:
        await DB.rate_product(user_id, prod_id, user_rate)
        return {"message": "ok"}


@app.get("/get_film",
         responses={
             404: {"model": Message, "description": "Film not found"},
             202: {"model": Product, "description": "product data",
                   "content": {
                       "application/json": {
                           "example": {"id": 8986,
                                       "photo": "https://kinopoiskapiunofficial.tech/images/posters/kp/84674.jpg",
                                       "name": "9 рота",
                                       "description": "СССР, 1988-1989 годы, за несколько месяцев до полного вывода "
                                                      "советских войск из Афганистана. Семеро призывников после "
                                                      "нескольких месяцев адской подготовки в учебке под "
                                                      "командованием беспощадного старшины попадают в горнило "
                                                      "афганской кампании.\n\nГруппа десантников, бойцами которой "
                                                      "стали наши герои, получает задание командования - занять "
                                                      "высоту и держать её до прохождения колонны."}
                       },
                   },
                   }
         })
async def get_film(prod_id: int):
    film = await DB.get_product_by_id(prod_id)
    if film:
        return film
    else:
        return JSONResponse(status_code=404, content={"message": "Not found"})


@app.get("/get_recommendations",
         responses={
             404: {"model": Message, "description": "Need to login"},
             405: {"model": Message, "description": "less 2 positive rates"},
             406: {"model": Message, "description": "less 2 negative rates"},
             202: {"model": Message, "message": "ok"}
         })
async def get_recommendations(user_id: int | None = Cookie(default=None)):
    if user_id is None:
        return JSONResponse(status_code=404, content={"message": "Need to login"})
    else:
        products = await DB.get_recommend_cat(user_id)

        if products == 'less 2 positive rates':
            return JSONResponse(status_code=405, content={"message": "less 2 positive rates"})
        elif products == 'less 2 negative rates':
            return JSONResponse(status_code=406, content={"message": "less 2 negative rates"})
        else:
            return products


def api_main():
    db_init()
    uvicorn.run(app, host="0.0.0.0", port=8031)


if __name__ == "__main__":
    api_main()
