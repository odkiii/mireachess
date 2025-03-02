from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from stockfish import Stockfish

stockfish = Stockfish(path="stockfish/stockfish-windows-x86-64-avx2")

app = FastAPI()

# Настройка CORS для Vue приложения
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class move(BaseModel):
    fen: str

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
async def chat_with_gpt(move: move):
    try:
        global stockfish
        stockfish.set_fen_position(move.fen)
        best_move = stockfish.get_best_move()
        return {"best_move": best_move}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "ok"}