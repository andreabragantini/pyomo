# MIP_2.py
# small MIP example

from pyomo.environ import *

m = ConcreteModel()
m.I = Set(initialize=[1,2,3, 4, 5])
m.y = Var(m.I, within=NonNegativeReals, initialize=0)

m.obj = Objective(sense=minimize, expr= 2*m.y[1] - 3*m.y[2] - 4*m.y[3] - 2*m.y[4] - 0.5*m.y[5])
@m.Constraint()
def _c1(m):
    return -2*m.y[2] - 3*m.y[3] + 3*m.y[4] >= -12
@m.Constraint()
def _c2(m):
    return m.y[1] + m.y[2] +2*m.y[3] - 2*m.y[4] - 4*m.y[5] <= 16
@m.Constraint()
def _c3(m):
    return m.y[1] + 2*m.y[2] + 1*m.y[3] + m.y[4] + 0.2*m.y[5] <= 9

if __name__ == "__main__":
    m.y.domain = NonNegativeIntegers
    results = SolverFactory('glpk').solve(m, tee=True, keepfiles=False)
    m.display()
