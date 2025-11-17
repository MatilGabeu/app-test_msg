from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI()

connected_clients = []


# --------------------------
#  PAGE D'ACCUEIL
# --------------------------
@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <h1>Serveur WebSocket opérationnel</h1>
    <p>Bienvenue !</p>
    <a href="/chat">➡️ Ouvrir le chat</a>
    """


# --------------------------
#  PAGE DU CHAT
# --------------------------
@app.get("/chat", response_class=HTMLResponse)
def chat_page():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Chat WebSocket</title>
        <style>
            body { font-family: Arial; padding: 20px; }
            #messages { border: 1px solid #ccc; padding: 10px; height: 300px; overflow-y: scroll; margin-bottom: 10px; }
        </style>
    </head>
    <body>
        <h1>Chat WebSocket</h1>

        <div id="messages"></div>

        <input id="msg" type="text">
        <button onclick="sendMsg()">Envoyer</button>

        <script>
            const ws = new WebSocket("wss://" + location.host + "/ws");

            ws.onmessage = (event) => {
                document.getElementById("messages").innerHTML += "<p>" + event.data + "</p>";
            };

            function sendMsg() {
                const inp = document.getElementById("msg");
                ws.send(inp.value);
                inp.value = "";
            }
        </script>
    </body>
    </html>
    """


# --------------------------
#  WEBSOCKET
# --------------------------
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    print("Client connecté !")

    try:
        while True:
            msg = await websocket.receive_text()
            print("Message reçu :", msg)

            # diffuse à tous les clients
            for client in connected_clients:
                await client.send_text(msg)

    except Exception:
        print("Client déconnecté.")
        connected_clients.remove(websocket)


# --------------------------
#  LANCEMENT LOCAL
# --------------------------
if __name__ == "__main__":
    # pour lancer en local
    uvicorn.run("server:app", host="0.0.0.0", port=8000)
