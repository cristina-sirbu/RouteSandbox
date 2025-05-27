def solve(problem_data: dict) -> dict:
    """
    Solves the vehicle routing problem with the given input data.
    """
    print("DEBUG: Received problem data:", problem_data)
    # Dummy result to simulate routing
    return {
        "routes": [
            {"vehicle_id": 1, "stops": [0, 1, 2, 0]},
            {"vehicle_id": 2, "stops": [0, 3, 4, 0]}
        ],
        "status": "ok"
    }