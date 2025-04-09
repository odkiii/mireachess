from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from stockfish import Stockfish
import asyncpg
from fastapi import Depends
import os
from asyncpg.pool import Pool

# Меняем если запуск на iOS или Windows
stockfish = Stockfish(path="stockfish/stockfish-windows-x86-64-avx2")
# stockfish = Stockfish(path="/opt/homebrew/Cellar/stockfish/17/bin/stockfish")


# DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:12345678@localhost:5432/mireachessdb")
DATABASE_URL = "postgresql://postgres:12345678@localhost:5432/mireachessdb"
db_pool: Pool = None

async def create_db_pool():
    global db_pool
    db_pool = await asyncpg.create_pool(
        DATABASE_URL,
        min_size=1,
        max_size=10,
        command_timeout=60
    )
    
app = FastAPI()


@app.on_event("startup")
async def startup():
    await create_db_pool()

@app.on_event("shutdown")
async def shutdown():
    if db_pool:
        await db_pool.close()


# Настройка CORS для Vue приложения
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://infallibly-refined-shark.cloudpub.ru/", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# async def get_db():
#     return await asyncpg.create_pool(DATABASE_URL)


class move(BaseModel):
    fen: str
    telegram_id: int

class start(BaseModel):
    diff: int

@app.post("/api/start")
async def start_game(diff: start):
    try:
        global stockfish
        stockfish.set_skill_level(diff.diff)
        return {"message": "Difficult is set"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/move")
async def make_move(move: move):
    try:
        if not db_pool:
            raise HTTPException(status_code=500, detail="Database not connected")
        
        async with db_pool.acquire() as conn:
            # Проверяем существование пользователя
            user_exists = await conn.fetchval(
                "SELECT EXISTS(SELECT 1 FROM users WHERE telegram_id = $1)",
                move.telegram_id
            )
            
            if not user_exists:
                # Создаем временного пользователя для тестов
                if move.telegram_id == 0:
                    await conn.execute(
                        "INSERT INTO users (telegram_id, username) VALUES (0, 'temp_user') "
                        "ON CONFLICT (telegram_id) DO NOTHING"
                    )
                else:
                    raise HTTPException(status_code=400, detail="User not found")

            stockfish.set_fen_position(move.fen)
            best_move = stockfish.get_best_move()
            
            await conn.execute(
                "INSERT INTO game_sessions (telegram_id, fen) VALUES ($1, $2)",
                move.telegram_id, move.fen
            )
            
        return {"best_move": best_move}
        
    except Exception as e:
        print(f"Error in /api/move: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/health")
async def health_check():
    return {"status": "ok"}

async def get_db():
    return db_pool