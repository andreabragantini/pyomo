# MIP_4.py
# another small MIP example

from pyomo.environ import *

m = ConcreteModel()
m.I = Set(initialize=[1,2,3, 4,5,6,7,8])
m.y = Var(m.I, within=NonNegativeReals, initialize=0)

m.obj = Objective(sense=maximize, expr= -10*m.y[1] - 5*m.y[2] - 7*m.y[3] -2*m.y[4] - 8*m.y[5] -11*m.y[6] -4*m.y[7] -12*m.y[8])

@m.Constraint()
def _c1(m):
    return 3*m.y[1] - m.y[2] - 5*m.y[3] -3*m.y[4] +2*m.y[5] +2*m.y[6] +8*m.y[7] + 4*m.y[8] <= -6

@m.Constraint()
def _c2(m):
    return -2*m.y[1] + 3*m.y[2] + 1*m.y[3] - 10*m.y[4] +1*m.y[5] - 4*m.y[6] - 6*m.y[7] + 2*m.y[8] <= -9

@m.Constraint()
def _c3(m):
    return -5*m.y[1] - 4*m.y[2] - 10*m.y[3] + 2*m.y[4] -2*m.y[5] - 3*m.y[6] - 5*m.y[7] - 3*m.y[8] <= -8

@m.Constraint()
def _c4(m):
    return 3*m.y[1] +3*m.y[2] +4*m.y[3] -5*m.y[4] +5*m.y[5] - m.y[6] +8*m.y[7] - 4*m.y[8] <= -4

if __name__ == "__main__":

    m.y.domain = NonNegativeIntegers
    results = SolverFactory('glpk').solve(m, tee=True, keepfiles=True)
    m.display()
