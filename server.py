from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
import jwt
import time

SECRET_KEY = "TA_CLE_SECRETE_SUPER_SÛRE"   # change-la !

app = FastAPI()

# Héberger /static
app.mount("/static", StaticFiles(directory="static"), name="static")

# Autoriser frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

connected_clients = []


##############################
#   UTILISATEURS JSON
##############################
USERS_FILE = "users.json"

def load_users():
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)


##############################
#       ROUTES LOGIN
##############################

@app.post("/register")
def register(user: dict):
    users = load_users()
    
    if user["username"] in users:
        raise HTTPException(400, "Ce nom d'utilisateur existe déjà.")

    users[user["username"]] = {
        "password": user["password"]
    }
    save_users(users)
    return {"status": "ok"}


@app.post("/login")
def login(user: dict):
    users = load_users()

    if user["username"] not in users:
        raise HTTPException(400, "Utilisateur introuvable.")
    if users[user["username"]]["password"] != user["password"]:
        raise HTTPException(400, "Mot de passe incorrect.")

    # Création du token
    token = jwt.encode(
        {"user": user["username"], "exp": time.time() + 3600 * 24},
        SECRET_KEY,
        algorithm="HS256"
    )

    return {"token": token}


##############################
#          WEBSOCKET
##############################

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):

    # Récupère token dans l’URL
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close()
        return

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        username = payload["user"]
    except Exception:
        await websocket.close()
        return

    await websocket.accept()
    connected_clients.append((websocket, username))
    print(f"{username} connecté !")

    try:
        while True:
            text = await websocket.receive_text()

            # Structure JSON envoyée à tout le monde
            message = {"user": username, "text": text}

            for client, _ in connected_clients:
                await client.send_json(message)

    except WebSocketDisconnect:
        print(f"{username} déconnecté.")
        connected_clients.remove((websocket, username))


##############################
#         PAGE ACCUEIL
##############################
@app.get("/")
def home():
    return HTMLResponse("""
    <h1>Serveur WebSocket opérationnel</h1>
    <a href='/static/chat.html'>➡️ Ouvrir le chat</a>
    """)


if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000)
