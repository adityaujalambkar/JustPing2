from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

app = FastAPI()

class Message(BaseModel):
    message: str
    sender: str
    timestamp: datetime

class MessageHistory:
    def _init_(self):
        self.history = []

    def add_message(self, message: str, sender: str, timestamp: datetime):
        self.history.append({
            "message": message,
            "sender": sender,
            "timestamp": timestamp
        })

    def get_history(self, start_time: Optional[datetime] = None, end_time: Optional[datetime] = None, sender: Optional[str] = None):
        filtered_history = self.history
        if start_time:
            filtered_history = [msg for msg in filtered_history if msg["timestamp"] >= start_time]
        if end_time:
            filtered_history = [msg for msg in filtered_history if msg["timestamp"] <= end_time]
        if sender:
            filtered_history = [msg for msg in filtered_history if msg["sender"] == sender]
        return filtered_history

history = MessageHistory()

@app.post("/messages/")
async def post_message(msg: Message):
    history.add_message(msg.message, msg.sender, msg.timestamp)
    return {"status": "message added"}

@app.get("/messages/", response_model=List[Message])
async def get_messages(
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
    sender: Optional[str] = Query(None)
):
    msgs = history.get_history(start_time=start_time, end_time=end_time, sender=sender)
    return msgs