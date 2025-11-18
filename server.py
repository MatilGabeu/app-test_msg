from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from jose import jwt
import json
import time

SECRET_KEY = "CHANGE_THIS_TO_A_SECRET_KEY"

app = FastAPI()

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# CORS (utile si front séparé)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Utilisateurs stockés dans un JSON simple
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

# WebSocket clients
connected_clients = []

# ----- ROUTES -----

@app.get("/")
def home():
    return HTMLResponse("""
    <h1>Serveur WebSocket opérationnel</h1>
    <a href='/static/login.html'>➡️ Login</a>
    """)

# REGISTER
@app.post("/register")
def register(user: dict):
    users = load_users()
    username = user.get("username")
    password = user.get("password")
    if not username or not password:
        raise HTTPException(400, "Username et password requis")
    if username in users:
        raise HTTPException(400, "Nom d'utilisateur déjà pris")
    users[username] = {"password": password}
    save_users(users)
    return {"status": "ok"}

# LOGIN
@app.post("/login")
def login(user: dict):
    users = load_users()
    username = user.get("username")
    password = user.get("password")
    if username not in users:
        raise HTTPException(400, "Utilisateur introuvable")
    if users[username]["password"] != password:
        raise HTTPException(400, "Mot de passe incorrect")
    
    # Génération du JWT
    token = jwt.encode(
        {"user": username, "exp": time.time() + 3600*24},
        SECRET_KEY,
        algorithm="HS256"
    )
    return {"token": token}

# WEBSOCKET
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close()
        return
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        username = payload["user"]
    except:
        await websocket.close()
        return

    await websocket.accept()
    connected_clients.append((websocket, username))
    print(f"{username} connecté !")

    try:
        while True:
            text = await websocket.receive_text()
            message = {"user": username, "text": text}
            for client, _ in connected_clients:
                await client.send_json(message)
    except WebSocketDisconnect:
        print(f"{username} déconnecté.")
        connected_clients.remove((websocket, username))

# RUN
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000)
