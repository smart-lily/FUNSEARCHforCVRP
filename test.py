# Test for vrplib formatted file reading
# Needs to install vrplib first
import vrplib

# Read VRPLIB formatted instances (default)
instance = vrplib.read_instance("DATA/E/E-n51-k5.vrp")
solution = vrplib.read_solution("DATA/E/E-n51-k5.sol")

print(instance)
print(solution)

# ————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————

from verypy.cvrp_io import read_TSPLIB_CVRP
# Import the Clarke & Wright (1964) Savings heuristic
from verypy.classic_heuristics.parallel_savings import parallel_savings_init
from verypy.util import sol2routes

E_n51_k5_path = r"DATA/E/E-n51-k5.vrp"

problem = read_TSPLIB_CVRP(E_n51_k5_path)

solution = parallel_savings_init(
    D=problem.distance_matrix, 
    d=problem.customer_demands, 
    C=problem.capacity_constraint)

for route_idx, route in enumerate(sol2routes(solution)):
    print("Route #%d : %s"%(route_idx+1, route))

# ————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————

import lkh

problem_str = r"DATA/E/E-n51-k5.vrp"
with open(problem_str, "r") as fh:
    problem = lkh.LKHProblem.parse(fh.read())

solver_path = 'pylkh/LKH-3.0.7/LKH'
lkh.solve(solver_path, problem=problem, max_trials=1000, runs=10)