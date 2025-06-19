from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from typing import List, Dict
from pydantic import BaseModel

app = FastAPI()

class Message(BaseModel):
    id: int
    sender: str
    content: str

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str, sender_ws: WebSocket = None):
        for connection in self.active_connections:
            if sender_ws and connection == sender_ws:
                continue
            await connection.send_text(message)

connectionmanager = ConnectionManager()
chat_messages: Dict[int, Message] = {}
message_id_counter = 1

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    global message_id_counter
    await connectionmanager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = Message(id=message_id_counter, sender=f"Client #{client_id}", content=data)
            chat_messages[message_id_counter] = message
            message_id_counter += 1

            await connectionmanager.send_personal_message(f"You: {data}", websocket)
            await connectionmanager.broadcast(f"{message.sender}: {data}", websocket)
    except WebSocketDisconnect:
        connectionmanager.disconnect(websocket)
        await connectionmanager.broadcast(f"Client #{client_id} left the chat")

# GET all messages
@app.get("/messages", response_model=List[Message])
def get_all_messages():
    return list(chat_messages.values())

# PUT update a message
@app.put("/messages/{message_id}", response_model=Message)
def update_message(message_id: int, new_data: Message):
    if message_id not in chat_messages:
        raise HTTPException(status_code=404, detail="Message not found")
    chat_messages[message_id] = new_data
    return new_data

# DELETE a message
@app.delete("/messages/{message_id}")
def delete_message(message_id: int):
    if message_id not in chat_messages:
        raise HTTPException(status_code=404, detail="Message not found")
    del chat_messages[message_id]
    return {"message": "Deleted successfully"}


# ✅ New Root Endpoint (optional but useful)
@app.get("/")
def root():
    return {"message": "FastAPI Chat Service is running!"}
