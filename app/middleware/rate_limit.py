import time
from flask import request

LIMIT=100
WINDOW=60
clients={}

def rate_limit(app):

    @app.before_request
    def check():

        ip=request.remote_addr
        now=time.time()

        if ip not in clients:
            clients[ip]=[]

        clients[ip]=[t for t in clients[ip] if now-t<WINDOW]

        if len(clients[ip])>=LIMIT:
            return {"error":"Rate limit exceeded"},429

        clients[ip].append(now)
