from fastapi import FastAPI, Request
from solver import solve, solve_greedy

app = FastAPI()

@app.post("/optimize")
async def optimize(request: Request, solver: str = "ortools"):
    data = await request.json()
    if solver == "greedy":
        result = solve_greedy(data)
    else:
        result = solve(data)
    return result