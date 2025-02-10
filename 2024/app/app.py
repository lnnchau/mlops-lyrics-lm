from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from src.agent import stream_output
from pydantic import BaseModel


app = FastAPI()


class Query(BaseModel):
    content: str


@app.post("/")
async def main(query: Query):
    return StreamingResponse(stream_output(query.content))
