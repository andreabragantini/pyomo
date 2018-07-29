# Serial knapsack

from pyomo.contrib.bb.knapsack.knapsack import Knapsack
from pyomo.contrib.bb import ParallelBBSolver_serial

problem = Knapsack(filename='scor-500-1.txt')
solver = ParallelBBSolver_serial()
value, solution = solver.solve(problem=problem)
print(value)
problem.print_solution(solution)
