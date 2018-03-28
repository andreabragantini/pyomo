#  ___________________________________________________________________________
#
#  Pyomo: Python Optimization Modeling Objects
#  Copyright 2017 National Technology and Engineering Solutions of Sandia, LLC
#  Under the terms of Contract DE-NA0003525 with National Technology and 
#  Engineering Solutions of Sandia, LLC, the U.S. Government retains certain
#  rights in this software.
#  This software is distributed under the 3-clause BSD License.
#  ___________________________________________________________________________
#

import pyomo.environ as pe
from pyomo.core.kernel import ComponentMap, ComponentSet
from pyomo.core.expr import current as EXPR
from pyomo.core.expr import is_variable_type, native_numeric_types

from six import iteritems

def substitute_vardata_in_expression(expr, substitution_map, expressions_to_skip=None):
    substituter = ExpressionSubstitutor(substitution_map=substitution_map, expressions_to_skip=expressions_to_skip)
    new_expr = substituter.dfs_postorder_stack(expr)
    return new_expr

class ExpressionSubstitutor(EXPR.SimpleExpressionReplacementVisitor):
    """
    Expression walker that replaces expressions provided by the substitution_map.
    This class will skip replacement of any expression nodes that are in expressions_to_skip OR
    on the right hand side of the substitution_map (this is to prevent recursive replacement
    of entangled expressions)
    """
    def __init__(self, substitution_map, expressions_to_skip=None):
        super(ExpressionSubstitutor, self).__init__(self)
        self._substitution_map = substitution_map
        self._expressions_to_skip = expressions_to_skip
        if self._expressions_to_skip is None:
            # create an empty component set so that the "in" checks will work later
            self._expressions_to_skip = ComponentSet()
        self._substitution_map_rhs = ComponentSet()
        for k,v in iteritems(self._substitution_map):
            self._substitution_map_rhs.add(v)

    def replace_node(self, node):
        print('*** checking node:', node)
        if node in self._substitution_map \
                and node not in self._expressions_to_skip \
                and node not in self._substitution_map_rhs:
            # this is a node that needs to be replaced
            new_node = self._substitution_map[node]
            print('... replacing node:', node, 'with', new_node)
            return new_node
        print('... not replacing node')
        return None

if __name__ == "__main__":
    model = pe.ConcreteModel()
    model.x = pe.Var()
    model.y = pe.Var()
    model.x2 = pe.Expression(expr=model.x*model.x)
    model.obj = pe.Objective(expr=model.x + model.y*model.x + 2.0*model.x + model.x2 + model.y*model.x2)
    print(model.obj.expr)

    smap = ComponentMap()
    smap[model.x] = 42.0*model.x

    new_expr = substitute_vardata_in_expression(expr=model.obj.expr, substitution_map=smap)
    print(new_expr)
