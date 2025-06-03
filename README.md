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

## Features (Planned)

- [x] Parcel and vehicle simulation with delivery constraints
- [ ] Greedy baseline and advanced optimization strategies
- [x] Python microservice for solving VRPs using OR-Tools
- [ ] REST APIs for submitting and retrieving route plans
- [ ] Simulation metrics (delivery success, total distance, time)
- [ ] Cloud deployment via Kubernetes and GitHub Actions
- [ ] Optional dashboard for visualizing routes and KPIs

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
curl -X POST http://localhost:8000/optimize \
  -H "Content-Type: application/json" \
  --data-binary @data/sample_problems/example.json
```

---

## Docs & Architecture

> Coming soon:
> - ADRs (Architectural Decision Records)
> - Architecture diagrams (services, data flow)
> - Example API requests and JSON payloads

---

## Contributions

This project is personal, but contributions, suggestions and feedback are welcome!
