import asyncio
from contextlib import asynccontextmanager

import uvicorn
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.api.routes import code, chat, test, code_files, docs, links, process, flag, auth, \
    pdf_handler, collection_data, agent, qdrant
from app.container import container
from app.databases.singletons import get_mongo_db, get_qdrant_db
from app.websocket import websocket
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


logging.basicConfig(level=logging.DEBUG)
logging.getLogger('pymongo').setLevel(logging.WARNING)



@asynccontextmanager
async def lifespan(app: FastAPI):
    await get_mongo_db()
    await get_qdrant_db()
    bot = container.telegram_bot()
    asyncio.create_task(bot.start())
    yield
    # await bot.stop()
    mdb = await get_mongo_db()
    mdb.client.close()
    qdb = await get_qdrant_db()
    await qdb.client.close()


app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:4200",
    "http://localhost:8081",
    "http://localhost:8082",
    "http://localhost:8083",
    "http://mkpatka.duckdns.org:8080",
    "http://mkpatka.duckdns.org:5000",
    "https://nnikolovskiii.ngrok.dev",
    "http://mkpatka.duckdns.org:5000",
    "https://nnikkserver.duckdns.org",
    "https://nnikkserver.duckdns.org:5000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error"}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"message": "Validation error", "details": exc.errors()}
    )
@app.get("/test-cors")
async def test_cors():
    return {"message": "CORS works!"}

# routes
app.include_router(code.router, prefix="/code", tags=["code"])
app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(websocket.router, prefix="/websocket", tags=["websocket"])
app.include_router(test.router, prefix="/test", tags=["test"])
app.include_router(collection_data.router, prefix="/collection_data", tags=["collection_data"])
app.include_router(code_files.router, prefix="/code_files", tags=["code_files"])
app.include_router(docs.router, prefix="/docs", tags=["docs"])
app.include_router(links.router, prefix="/links", tags=["links"])
app.include_router(process.router, prefix="/process", tags=["process"])
app.include_router(flag.router, prefix="/flag", tags=["flag"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(pdf_handler.router, prefix="/pdf", tags=["pdf"])

app.include_router(agent.router, prefix="/agent", tags=["agent"])
app.include_router(qdrant.router, prefix="/qdrant", tags=["qdrant"])



if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=5000,
        reload=False
    )
