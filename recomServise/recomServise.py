import uvicorn as uvicorn
from fastapi import Cookie, FastAPI, Response
from database.db_init import db_init
from database.async_db import asyncHandler as DB
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import requests

app = FastAPI()


class Message(BaseModel):
    message: str


@app.get("/",
         responses={
             404: {"model": Message, "description": "Need to login"},
             405: {"model": Message, "description": "less 2 positive rates"},
             406: {"model": Message, "description": "less 2 negative rates"},
             202: {"model": Message, "message": "ok"}
         })
async def recommendation(user_id: int):
    products = await DB.get_recommend_cat(user_id)

    if products == 'less 2 positive rates':
        return JSONResponse(status_code=405, content={"message": "less 2 positive rates"})
    elif products == 'less 2 negative rates':
        return JSONResponse(status_code=406, content={"message": "less 2 negative rates"})
    else:
        return products


def api_main():
    db_init()
    uvicorn.run(app, host="0.0.0.0", port=8032)


if __name__ == "__main__":
    api_main()
