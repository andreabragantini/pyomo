# Serial knapsack

from pyomo.contrib.bb.knapsack.knapsack import Knapsack
from pyomo.contrib.bb import SerialBBSolver

problem = Knapsack(filename='scor-500-1.txt')
solver = SerialBBSolver()
value, solution = solver.solve(problem=problem)
print(value)
problem.print_solution(solution)
