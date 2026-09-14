from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
def chat(req: ChatRequest):

    msg = req.message.lower()

    if "network" in msg:
        reply = "Checking your network connection..."

    elif "renew" in msg:
        reply = "You can renew your package from the services page."

    elif "support" in msg:
        reply = "Connecting you to customer support."

    else:
        reply = "Sorry, I did not understand your request."

    return {"reply": reply}
