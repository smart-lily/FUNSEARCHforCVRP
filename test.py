import os
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from verypy.cvrp_ops import normalize_solution, recalculate_objective
import verypy.cvrp_io as cvrp_io
from verypy import get_algorithms
import hygese
import jpype
import vrplib

def AILSII_cvrp(file_path):
    readerClass = jpype.JClass('SearchMethod.InputParameters')
    instanceClass = jpype.JClass('Data.Instance')
    AILSIIClass = jpype.JClass('SearchMethod.AILSII')
    result = []
    # Solver initialization
    args = ["-file", file_path, "-rounded", "true", "-best", "10856", "-limit", "100", "-stoppingCriterion", "Time"]
    args = jpype.JArray(jpype.JString)(args)
    reader = readerClass()
    reader.readingInput(args)
    try:
        AILSII = AILSIIClass(instanceClass(reader),reader)
        AILSII.setPrint(False)
        AILSII.search()
        cost = AILSII.getMelhorF()
    except:
        cost = None
    result.append(('AILSII', cost))
    return result

def verypy_cvrp(file_path):
    problem = cvrp_io.read_TSPLIB_CVRP(file_path)
    algos = get_algorithms(['all'])
    result = []
    for _, algo_name, _, algo_f in algos:
        try:
            sol = algo_f(problem.coordinate_points, problem.distance_matrix, problem.customer_demands, problem.capacity_constraint, None, None, "GEO", False, True)
        except:
            sol = algo_f(problem.coordinate_points, problem.distance_matrix, problem.customer_demands, problem.capacity_constraint, None, None, "GEO", False, False)
        sol = normalize_solution(sol)
        obj = recalculate_objective(sol, problem.distance_matrix)
        result.append((algo_name, obj))
    return result

def HGS_cvrp(file_path):
    problem = cvrp_io.read_TSPLIB_CVRP(file_path)
    result = []
    # Solver initialization
    ap = hygese.AlgorithmParameters(timeLimit=5)  # seconds
    hgs_solver = hygese.Solver(parameters=ap,verbose=False)
    data = {}
    data["distance_matrix"] = problem.distance_matrix
    data["demands"] = problem.customer_demands
    data["vehicle_capacity"] = problem.capacity_constraint
    data['depot'] = 0
    obj = hgs_solver.solve_cvrp(data)
    result.append(('HGS', obj.cost))
    return result

def ortools_cvrp(file_path):
    problem = cvrp_io.read_TSPLIB_CVRP(file_path)
    result = []
    data = {}
    data["distance_matrix"] = problem.distance_matrix
    data["demands"] = [int(i) for i in problem.customer_demands]
    data["num_vehicles"] = 10
    data["vehicle_capacity"] = problem.capacity_constraint
    data["depot"] = 0
    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(
        len(data["distance_matrix"]), data["num_vehicles"], data["depot"]
    )
    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)
    # Create and register a transit callback.
    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data["distance_matrix"][from_node][to_node]
    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
    # Add Capacity constraint.
    def demand_callback(from_index):
        """Returns the demand of the node."""
        # Convert from routing variable Index to demands NodeIndex.
        from_node = manager.IndexToNode(from_index)
        return data["demands"][from_node]
    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimension(demand_callback_index,0,data["vehicle_capacity"],True,"Capacity")
    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    search_parameters.local_search_metaheuristic = (routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
    search_parameters.time_limit.FromSeconds(1)
    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)
    # Print solution on console.
    if solution:
        result.append(('OR-Tools', solution.ObjectiveValue()))
    else:
        result.append(('OR-Tools', None))
    return result

def get_datasets(path):
    datasets = [(name,[]) for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))]
    for dataset, datas in datasets:
        for file in os.listdir(os.path.join(path, dataset)):
            if file.endswith(".sol"):
                solution = vrplib.read_solution(os.path.join(path, dataset, file))
                file_prefix, file_extension = os.path.splitext(file)
                datas.append((file_prefix, solution["cost"],[]))
    return datasets

def all_datasets():
    path = r"DATA"
    datasets = get_datasets(path)
    algss = [ortools_cvrp, HGS_cvrp, AILSII_cvrp, verypy_cvrp]
    jarpath = r"AILS-CVRP/AILSII.jar"
    jpype.startJVM(jpype.getDefaultJVMPath(), "-ea", "-Djava.class.path=%s" % jarpath)
    for dataset, datas in datasets:
        for file, cost, algcost in datas:
            file_path = os.path.join(path, dataset, file + ".vrp")
            for algs in algss:
                results = algs(file_path)
                for alg, obj in results:
                    algcost.append((alg, obj)) 
    print(datasets)
    save_path = r"results.txt"
    with open(save_path, 'w') as f:
        for dataset, datas in datasets:
            f.write(f"{dataset}\n")
            for file, cost, algcost in datas:
                f.write(f"{file} {cost}\n")
                for alg, obj in algcost:
                    f.write(f"{alg} {obj}\n")
                f.write("\n")
            f.write("\n")
    jpype.shutdownJVM()

def one_dataset(path):
    cost = []
    jarpath = r"AILS-CVRP/AILSII.jar"
    jpype.startJVM(jpype.getDefaultJVMPath(), "-ea", "-Djava.class.path=%s" % jarpath)
    for file in os.listdir(path):
        if file.endswith(".sol"):
            solution = vrplib.read_solution(os.path.join(path, file))
            file_prefix, file_extension = os.path.splitext(file)
            cost.append((file_prefix, solution["cost"]))
            file_path = os.path.join(path, file_prefix + ".vrp")
            algss = [ortools_cvrp, HGS_cvrp, AILSII_cvrp, verypy_cvrp]
            for algs in algss:
                results = algs(file_path)
                for alg, obj in results:
                    cost.append((alg, obj))
    save_path = f"{path}_result.txt"
    with open(save_path, 'w') as f:
        for alg, obj in cost:
            f.write(f"{alg} {obj}\n")
        f.write("\n")
    jpype.shutdownJVM()

if __name__ == "__main__":
    one_dataset("DATA/A")
    # all_datasets()