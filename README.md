# RouteSandbox

**RouteSandbox** is a backend-driven route optimization simulator designed to explore real-world logistics challenges through code.This project simulates parcel deliveries across a virtual city and applies constraint-based algorithms to optimize delivery routes.

This project is a personal learning initiative.

---

## Project Goals

- Build a realistic simulation of parcel delivery routing under constraints (time windows, vehicle capacity).
- Implement and compare routing algorithms (greedy, optimization via OR-Tools).
- Deploy and orchestrate microservices in a local Minikube Kubernetes cluster.

---

## Tech Stack

| Area                    | Technology Used                                    |
|-------------------------|----------------------------------------------------|
| **Backend API**         | Java (Spring Boot)                                 |
| **Optimization Engine** | Python (FastAPI) with Google OR-Tools              |
| **Containerization**    | Docker                                             |
| **Local Orchestration** | Kubernetes (via Minikube)                          |
| **API Communication**   | REST (HTTP/JSON)                                   |
| **CI/CD**               | GitHub Actions (build, lint, test)                 |
| **Simulation Data**     | JSON files (in-memory, no external DB)             |
| **Ingress & Routing**   | Minikube Ingress addon *or* `kubectl port-forward` |

---

## Instructions

To build the optimizer app Docker image run:

```shell
docker build -t routesandbox-optimizer optimizer/
```

To run the image:

```shell
docker run -p 8000:8000 routesandbox-optimizer
```

To check locally if the image works:

```shell
curl -X POST http://localhost:8000/optimize\?solver\=greedy \
  -H "Content-Type: application/json" \
  --data-binary @data/sample_problems/example.json
```
<details>
<summary>Example input file:</summary>

   ```json
   {
     "locations": [
       { "id": 0, "name": "Depot" },
       { "id": 1, "name": "Customer A" },
       { "id": 2, "name": "Customer B" },
       { "id": 3, "name": "Customer C" }
     ],
     "distance_matrix": [
       [0, 2, 3, 4],
       [2, 0, 1, 3],
       [3, 1, 0, 2],
       [4, 3, 2, 0]
     ],
     "parcels": [
       { "id": 1, "location_id": 1, "time_window": [9, 12], "demand": 1 },
       { "id": 2, "location_id": 2, "time_window": [10, 13], "demand": 1 },
       { "id": 3, "location_id": 3, "time_window": [11, 14], "demand": 1 }
     ],
     "vehicles": [
       { "id": 1, "start_index": 0, "capacity": 2, "working_hours": [8, 15] },
       { "id": 2, "start_index": 0, "capacity": 2, "working_hours": [8, 15] }
     ]
   }
   ```
</details>

<details>
<summary>Example output:</summary>

   ```json
   {
      "routes": [
         {
            "vehicle_id": 1,
            "total_delivery_time": 6,
            "parcels_delivered": 2,
            "late_deliveries": 0,
            "total_distance": 6,
            "stops": [
               {
                  "location_id": 0,
                  "arrival_time": 8
               },
               {
                  "location_id": 1,
                  "arrival_time": 10
               },
               {
                  "location_id": 2,
                  "arrival_time": 11
               },
               {
                  "location_id": 0,
                  "arrival_time": 14
               }
            ]
         },
         {
            "vehicle_id": 2,
            "total_delivery_time": 8,
            "parcels_delivered": 1,
            "late_deliveries": 0,
            "total_distance": 8,
            "stops": [
               {
                  "location_id": 0,
                  "arrival_time": 8
               },
               {
                  "location_id": 3,
                  "arrival_time": 12
               },
               {
                  "location_id": 0,
                  "arrival_time": 16
               }
            ]
         }
      ],
      "status": "success"
   }
   ```
</details>

---

### Debugging the route

`visualize.py` is a small tool designed to help during development to visually inspect and compare delivery routes produced
by the optimizer service.

It generates a simple directed graph of each vehicle's route using `networkx` and `matplotlib`.

#### How to run the debug tool?

Under `/optimizer` there is a `sample_output.json` file. Update it with the result you've got from the `backend` service.
To start the visualizing tool:

```shell
python optimizer/visualize.py
```

Before running the script, make sure you've installed the required libraries:

```shell
pip install matplotlib networkx
```

---

### Optimizer visualization

The file `optimizer/analyze_routes.ipynb` provides a visual comparison between the OR-Tools and Greedy solvers.

This notebook lets you:

* Load and compare optimizer output from both solvers
* Analyze total delivery time, distance, and constraint violations
* Visualize metrics with bar charts using pandas, matplotlib, and seaborn


#### How to use it

1. Install required Python packages

    ```shell
    pip install notebook pandas matplotlib seaborn
    ```

2. Start Jupyter:

    ```shell
    jupyter notebook
    ```

3. Open the notebook `optimizer/analyze_routes.ipynb`.
   Make sure you have result files in optimizer/:
* sample_output.json — output from the OR-Tools solver
* sample_output_greedy.json — output from the Greedy solver

You can generate these by calling the API with `?solver=ortools` or `?solver=greedy`.

Run all cells to view tables and comparison charts.

#### Sample Output

![1](./imgs/1.png)

![2](./imgs/2.png)

![3](./imgs/3.png)

![4](./imgs/4.png)

---

## Docs & Architecture

> Coming soon:
> - ADRs (Architectural Decision Records)
> - Architecture diagrams (services, data flow)

---

## Contributions

This project is personal, but contributions, suggestions and feedback are welcome!
