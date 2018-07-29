# Serial knapsack
  
from mpi4py import MPI
from mpi4py.futures import MPICommExecutor

if __name__ == '__main__':
    import sys
    from pyomo.contrib.bb.knapsack.knapsack import Knapsack
    from pyomo.contrib.bb import ParallelBBSolver_mpi_async as PBB

    problem = Knapsack(filename='scor-500-1.txt')
    solver = PBB()

    rank = MPI.COMM_WORLD.Get_rank()
    size = MPI.COMM_WORLD.Get_size()

    with MPICommExecutor(MPI.COMM_WORLD, 0) as executor:
        if executor is not None:
            value, solution = solver.solve(problem=problem, executor=executor, greedy=True)
            print(value)
            problem.print_solution(solution)

