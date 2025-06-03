from fastapi import FastAPI, Request
from solver import solve

app = FastAPI()

@app.post("/optimize")
async def optimize(request: Request):
    data = await request.json()
    return solve(data)