# Test for vrplib formatted file reading
# Needs to install vrplib first
import vrplib

# Read VRPLIB formatted instances (default)
instance = vrplib.read_instance("DATA/A/A-n32-k5.vrp")
solution = vrplib.read_solution("DATA/A/A-n32-k5.sol")

print(instance)
print(solution)