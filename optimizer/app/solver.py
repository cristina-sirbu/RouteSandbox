from ortools.constraint_solver import pywrapcp, routing_enums_pb2


def solve(problem_data: dict) -> dict:
    """
    Solves the vehicle routing problem with the given input data using OR-Tools.
    """
    data = prepare_ortools_data(problem_data)

    print("Prepared OR-Tools input:")
    for key, value in data.items():
        print(f"{key}: {value}")

    # RoutingIndexManager takes as arguments how many locations there are, how many vehicles and which location is the starting point.
    manager = pywrapcp.RoutingIndexManager(
        len(data["distance_matrix"]), data["num_vehicles"], data["depot"]
    )
    routing = pywrapcp.RoutingModel(manager)

    # Calculate distance between locations
    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data["distance_matrix"][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Each location has a demand (e.g. parcel weight or size) and each vehicle has a capacity
    def demand_callback(from_index):
        from_node = manager.IndexToNode(from_index)
        return data["demands"][from_node]

    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,  # no capacity slack
        data["vehicle_capacities"],  # from input
        True,
        "Capacity",
    )

    # Each stop must be reached within a time range
    def time_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data["distance_matrix"][from_node][to_node]

    time_callback_index = routing.RegisterTransitCallback(time_callback)

    routing.AddDimension(
        time_callback_index,
        30,  # max waiting time at each stop
        1000,  # total time allowed on route
        False,
        "Time",
    )

    # Set this constrain for every location
    time_dimension = routing.GetDimensionOrDie("Time")
    # This sets the depot’s time window as the valid time range for when each vehicle can leave.
    for vehicle_id in range(data["num_vehicles"]):
        index = routing.Start(vehicle_id)
        time_dimension.CumulVar(index).SetRange(
            data["time_windows"][0][0], data["time_windows"][0][1]
        )

    for location_idx, time_window in enumerate(data["time_windows"]):
        index = manager.NodeToIndex(location_idx)
        time_dimension.CumulVar(index).SetRange(time_window[0], time_window[1])

    # Tell solver how to start
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )
    solution = routing.SolveWithParameters(search_parameters)

    def get_routes(routing, manager, solution, time_dimension):
        routes = []
        for vehicle_id in range(routing.vehicles()):
            index = routing.Start(vehicle_id)
            route = []
            while not routing.IsEnd(index):
                node_index = manager.IndexToNode(index)
                arrival = solution.Value(time_dimension.CumulVar(index))

                route.append({"location_id": node_index, "arrival_time": arrival})

                index = solution.Value(routing.NextVar(index))

            # Add the end (depot)
            end_node = manager.IndexToNode(index)
            arrival = solution.Value(time_dimension.CumulVar(index))
            route.append({"location_id": end_node, "arrival_time": arrival})

            start_time = route[0]["arrival_time"]
            end_time = route[-1]["arrival_time"]
            delivery_stops = [stop for stop in route if stop["location_id"] != 0]

            # Calculate the late arrivals
            late_count = 0
            for stop in route:
                loc_id = stop["location_id"]
                arrival = stop["arrival_time"]
                if loc_id != 0:  # ignore depot
                    start, end = data["time_windows"][loc_id]
                    if arrival > end:
                        late_count += 1

            # Calculate total distance for each vehicle
            total_distance = 0
            for i in range(len(route) - 1):
                from_id = route[i]["location_id"]
                to_id = route[i + 1]["location_id"]
                total_distance += data["distance_matrix"][from_id][to_id]

            routes.append(
                {
                    "vehicle_id": vehicle_id + 1,
                    "total_delivery_time": end_time - start_time,
                    "parcels_delivered": len(delivery_stops),
                    "late_deliveries": late_count,
                    "total_distance": total_distance,
                    "stops": route,
                }
            )
        return routes

    if solution:
        routes = get_routes(routing, manager, solution, time_dimension)
        print_routes(routes, problem_data["locations"])
        return {"routes": routes, "status": "success"}
    else:
        return {"routes": [], "status": "no_solution"}


def prepare_ortools_data(problem_data: dict) -> dict:
    distance_matrix = problem_data["distance_matrix"]
    parcels = problem_data["parcels"]
    vehicles = problem_data["vehicles"]

    # Total number of locations
    num_locations = len(problem_data["locations"])

    # Build demand list
    demand = [0] * num_locations  # 0 for depot
    for parcel in parcels:
        loc_id = parcel["location_id"]
        demand[loc_id] = parcel["demand"]

    # Build time window list
    time_windows = [(0, 1000)] * num_locations  # default time window
    for parcel in parcels:
        loc_id = parcel["location_id"]
        time_windows[loc_id] = tuple(parcel["time_window"])

    # Working hours for vehicles (same as time window at depot)
    depot_time_window = tuple(vehicles[0]["working_hours"])

    time_windows[0] = depot_time_window  # apply depot window

    return {
        "distance_matrix": distance_matrix,
        "num_vehicles": len(vehicles),
        "depot": 0,
        "demands": demand,
        "vehicle_capacities": [v["capacity"] for v in vehicles],
        "time_windows": time_windows,
    }


def solve_greedy(problem_data: dict) -> dict:
    """
    Solves the vehicle routing problem with the given input data using a greedy algorithm:
    - Iterate over parcels
    - Assign to first available vehicle with enough capacity
    - Sort stops by travel distance from depot
    """
    distance_matrix = problem_data["distance_matrix"]
    parcels = problem_data["parcels"]
    vehicles = problem_data["vehicles"]
    depot_index = 0

    # Track remaining capacity for each vehicle
    vehicle_capacity = [v["capacity"] for v in vehicles]
    vehicle_routes = [[] for _ in vehicles]  # list of location_ids per vehicle

    # Assign parcels to vehicles
    for parcel in parcels:
        loc_id = parcel["location_id"]
        demand = parcel["demand"]

        assigned = False
        for i, cap in enumerate(vehicle_capacity):
            if demand <= cap:
                vehicle_routes[i].append(loc_id)
                vehicle_capacity[i] -= demand
                assigned = True
                break

        if not assigned:
            print(
                f"Parcel {parcel['id']} could not be assigned due to capacity limits."
            )

    # Build routes and compute metrics
    routes = []

    for vehicle_id, stops in enumerate(vehicle_routes):
        if not stops:
            continue  # skip unused vehicles

        # Sort by distance to get the nearest neightbor
        stops.sort()

        total_distance = 0
        arrival_time = 0
        route_data = []

        start_time = 8
        arrival_time = start_time
        route_data = []

        # Start at depot
        route_data.append({"location_id": depot_index, "arrival_time": arrival_time})

        # Visit each stop (in order)
        for i in range(len(stops)):
            from_id = depot_index if i == 0 else stops[i - 1]
            to_id = stops[i]
            travel_time = distance_matrix[from_id][to_id]
            arrival_time += travel_time
            total_distance += travel_time
            route_data.append({"location_id": to_id, "arrival_time": arrival_time})

        # Return to depot
        last_stop = stops[-1] if stops else depot_index
        return_time = arrival_time + distance_matrix[last_stop][depot_index]
        total_distance += distance_matrix[last_stop][depot_index]
        route_data.append({"location_id": depot_index, "arrival_time": return_time})

        total_delivery_time = return_time - start_time

        routes.append(
            {
                "vehicle_id": vehicle_id + 1,
                "total_delivery_time": total_delivery_time,
                "parcels_delivered": len(stops),
                "late_deliveries": 0,
                "total_distance": total_distance,
                "stops": route_data,
            }
        )

    return {"routes": routes, "status": "success"}


def print_routes(routes, locations):
    for route in routes:
        vehicle_id = route["vehicle_id"]
        stop_ids = route["stops"]
        print(f"Vehicle {vehicle_id}")
        for stop in stop_ids:
            name = locations[stop["location_id"]]["name"]

            time = stop["arrival_time"]
            print(f"{name} (arrives at {time})")
