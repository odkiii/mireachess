from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole
import requests
import os
from dotenv import load_dotenv
import httpx
import json

load_dotenv()

app = FastAPI()

# Настройка CORS для Vue приложения
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    user_id: str = None  # Для сохранения контекста диалога

@app.post("/api/chat")
async def chat_with_gpt(request: ChatRequest):
    try:
        # Получение Access Token
        url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
        auth_key = "OTAyZjAzNTctMTVhOC00M2YzLTkyMmQtNDY0MzRiMGNhMzQ2OjkxNzlmNGExLTE5YzgtNDUwZS04ZjVhLWE3NDEwNjVlZTlkNQ=="

        payload = {
            'scope': 'GIGACHAT_API_PERS'
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
            'RqUID': '4f7b26d4-2fea-486e-a6fd-375881330ba2',  # Уникальный идентификатор запроса
            'Authorization': f'Basic {auth_key}'  # Используем ваш секретный ключ
        }

        async with httpx.AsyncClient(verify=False) as client:  # Отключаем проверку SSL
            response = await client.post(url, headers=headers, data=payload)


        # Проверка на успешное получение токена
        if response.status_code != 200:
            raise HTTPException(status_code=401, detail="Failed to obtain access token")

        access_token = response.json().get('access_token')

        # Создаем экземпляр GigaChat с полученным токеном
        giga = GigaChat(
            access_token=access_token,
            verify_ssl_certs=False
        )

        messages = [
            Messages(
                role=MessagesRole.USER,
                content=request.message
            )
        ]
        chat = Chat(messages=messages)  # Убираем указание модели

        # Отправляем запрос и получаем ответ
        response = await giga.achat(chat)

        # Проверяем, есть ли ответ
        if response.choices:
            lenMyJson = len(response.choices[0].message.content)
            myJson = response.choices[0].message.content[8:lenMyJson-3]
            return {"response": myJson}
        else:
            return {"response": "Нет ответа от GigaChat."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "ok"}