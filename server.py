from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

app = FastAPI()

# Sert le dossier /static (pour chat.html)
app.mount("/static", StaticFiles(directory="static"), name="static")

connected_clients = []


# ROUTE : page d'accueil
@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <h1>Serveur WebSocket opérationnel</h1>
    <a href='/static/chat.html'>➡️ Ouvrir le chat</a>
    """


# ROUTE : WebSocket
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    print("Client connecté !")

    try:
        while True:
            msg = await websocket.receive_text()

            # Renvoie à tous les clients connectés
            for client in connected_clients:
                await client.send_text(msg)

    except Exception:
        print("Client déconnecté.")
        connected_clients.remove(websocket)


if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000)
