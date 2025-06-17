from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

app = FastAPI()

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if "typing" in data:
                await manager.broadcast(f"Client #{client_id} is typing...")
            else:
                await manager.send_personal_message(f"You wrote: {data}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")

@app.get("/")
async def get():
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
        <head>
            <title>WebSocket Chat</title>
        </head>
        <body>
            <h1>WebSocket Chat</h1>
            <input type="text" id="messageText" autocomplete="off"/>
            <button onclick="sendMessage()">Send</button>
            <div id="typingIndicator"></div>
            <ul id="messages"></ul>

            <script>
                var ws = new WebSocket("ws://localhost:8000/ws/123");

                ws.onopen = function() {
                    console.log("Connected");
                };

                ws.onmessage = function(event) {
                    var messages = document.getElementById('messages');
                    var message = document.createElement('li');
                    var content = document.createTextNode(event.data);
                    message.appendChild(content);
                    messages.appendChild(message);
                };

                ws.onclose = function() {
                    console.log("Disconnected");
                };

                function sendMessage() {
                    var messageText = document.getElementById('messageText').value;
                    ws.send(messageText);
                    document.getElementById('messageText').value = '';
                }

                var typing = false;
                var typingTimeout = null;

                document.getElementById('messageText').addEventListener('keyup', function(e) {
                    if (!typing) {
                        typing = true;
                        ws.send('typing');
                    }
                    clearTimeout(typingTimeout);
                    typingTimeout = setTimeout(function() {
                        typing = false;
                    }, 1000);
                });
            </script>
        </body>
    </html>
    """)
