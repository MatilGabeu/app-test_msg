from fastapi import FastAPI, WebSocket
import uvicorn

app = FastAPI()

connected_clients = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    print("Client connecté")

    try:
        while True:
            msg = await websocket.receive_text()
            print(f"Client : {msg}")

            # renvoie à tous les clients connectés
            for client in connected_clients:
                await client.send_text(msg)

    except Exception:
        print("Client déconnecté")
        connected_clients.remove(websocket)

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000)
