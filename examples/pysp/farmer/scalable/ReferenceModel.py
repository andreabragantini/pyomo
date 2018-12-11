#  ___________________________________________________________________________
#
#  Pyomo: Python Optimization Modeling Objects
#  Copyright 2018 National Technology and Engineering Solutions of Sandia, LLC
#  Under the terms of Contract DE-NA0003525 with National Technology and 
#  Engineering Solutions of Sandia, LLC, the U.S. Government retains certain 
#  rights in this software.
#  This software is distributed under the 3-clause BSD License.
#  ___________________________________________________________________________
#
# special scalable farmer for stress-testing

import networkx 
import numpy as np
import re

# Farmer: NetworkX to create tree & gratitiously using indexed cost expressions
# unlimited crops
CropsMult = 30  # there will be three times this many crops
ScenMult = 50 # There will be three times this many scenarios
randseed = 1134 # not used for the first three scenarios (so it matches the book)
np.random.seed(randseed)

import pyomo.environ as pyo

def pysp_instance_creation_callback(scenario_name, node_names):
    # long function to create the entire model

    # scenarios come in groups of three
    scengroupnum = int(re.compile(r'(\d+)$').search(scenario_name).group(1))
    scenario_base_name = scenario_name.rstrip("0123456789")
    
    model = pyo.ConcreteModel()

    def crops_init(m):
        retval = []
        for i in range(CropsMult):
            retval.append("WHEAT"+str(i))
            retval.append("CORN"+str(i))
            retval.append("SUGAR_BEETS"+str(i))
        return retval

    model.CROPS = pyo.Set(initialize=crops_init)

    #
    # Parameters
    #

    model.TOTAL_ACREAGE = 500.0 * CropsMult

    def _scale_up_data(indict):
        outdict = {}
        for i in range(CropsMult):
           for crop in ['WHEAT', 'CORN', 'SUGAR_BEETS']:
               outdict[crop+str(i)] = indict[crop]
        return outdict
        
    model.PriceQuota = _scale_up_data(
        {'WHEAT':100000.0,'CORN':100000.0,'SUGAR_BEETS':6000.0})

    model.SubQuotaSellingPrice = _scale_up_data(
        {'WHEAT':170.0,'CORN':150.0,'SUGAR_BEETS':36.0})

    model.SuperQuotaSellingPrice = _scale_up_data(
        {'WHEAT':0.0,'CORN':0.0,'SUGAR_BEETS':10.0})

    model.CattleFeedRequirement = _scale_up_data(
        {'WHEAT':200.0,'CORN':240.0,'SUGAR_BEETS':0.0})

    model.PurchasePrice = _scale_up_data(
        {'WHEAT':238.0,'CORN':210.0,'SUGAR_BEETS':100000.0})

    model.PlantingCostPerAcre = _scale_up_data(
        {'WHEAT':150.0,'CORN':230.0,'SUGAR_BEETS':260.0})

    #
    # Stochastic Data
    #
    Yield = {}
    Yield['BelowAverageScenario'] = \
        {'WHEAT':2.0,'CORN':2.4,'SUGAR_BEETS':16.0}
    Yield['AverageScenario'] = \
        {'WHEAT':2.5,'CORN':3.0,'SUGAR_BEETS':20.0}
    Yield['AboveAverageScenario'] = \
        {'WHEAT':3.0,'CORN':3.6,'SUGAR_BEETS':24.0}

    def Yield_init(m, cropname):
        # yield as in "crop yield"
        crop_base_name = cropname.rstrip("0123456789")
        if scengroupnum != 0:
            return Yield[scenario_base_name][crop_base_name] + np.random.rand()
        else:
            return Yield[scenario_base_name][crop_base_name]

    model.Yield = pyo.Param(model.CROPS,
                            within=pyo.NonNegativeReals,
                            initialize=Yield_init,
                            mutable=True)

    #
    # Variables
    #

    model.DevotedAcreage = pyo.Var(model.CROPS, bounds=(0.0, model.TOTAL_ACREAGE))

    model.QuantitySubQuotaSold = pyo.Var(model.CROPS, bounds=(0.0, None))
    model.QuantitySuperQuotaSold = pyo.Var(model.CROPS, bounds=(0.0, None))
    model.QuantityPurchased = pyo.Var(model.CROPS, bounds=(0.0, None))

    #
    # Constraints
    #

    def ConstrainTotalAcreage_rule(model):
        return pyo.sum_product(model.DevotedAcreage) <= model.TOTAL_ACREAGE

    model.ConstrainTotalAcreage = pyo.Constraint(rule=ConstrainTotalAcreage_rule)

    def EnforceCattleFeedRequirement_rule(model, i):
        return model.CattleFeedRequirement[i] <= (model.Yield[i] * model.DevotedAcreage[i]) + model.QuantityPurchased[i] - model.QuantitySubQuotaSold[i] - model.QuantitySuperQuotaSold[i]

    model.EnforceCattleFeedRequirement = pyo.Constraint(model.CROPS, rule=EnforceCattleFeedRequirement_rule)

    def LimitAmountSold_rule(model, i):
        return model.QuantitySubQuotaSold[i] + model.QuantitySuperQuotaSold[i] - (model.Yield[i] * model.DevotedAcreage[i]) <= 0.0

    model.LimitAmountSold = pyo.Constraint(model.CROPS, rule=LimitAmountSold_rule)

    def EnforceQuotas_rule(model, i):
        return (0.0, model.QuantitySubQuotaSold[i], model.PriceQuota[i])

    model.EnforceQuotas = pyo.Constraint(model.CROPS, rule=EnforceQuotas_rule)

    # Stage-specific cost computations;

    def ComputeFirstStageCost_rule(model):
        return pyo.sum_product(model.PlantingCostPerAcre, model.DevotedAcreage)
    model.FirstStageCost = pyo.Expression(rule=ComputeFirstStageCost_rule)

    def ComputeSecondStageCost_rule(model):
        expr = pyo.sum_product(model.PurchasePrice, model.QuantityPurchased)
        expr -= pyo.sum_product(model.SubQuotaSellingPrice, model.QuantitySubQuotaSold)
        expr -= pyo.sum_product(model.SuperQuotaSellingPrice, model.QuantitySuperQuotaSold)
        return expr
    model.SecondStageCost = pyo.Expression(rule=ComputeSecondStageCost_rule)

    # Gratitiously using an indexed cost Expression
    # (you really could/should use the two you already have)
    StageSet = pyo.RangeSet(2)
    def cost_rule(m, stage):
        # Just assign the expressions to the right stage
        if stage == 1:
            return model.FirstStageCost
        if stage == 2:
            return model.SecondStageCost
    model.CostExpressions = pyo.Expression(StageSet, rule=cost_rule)

    def total_cost_rule(model):
        return model.FirstStageCost + model.SecondStageCost
    model.Total_Cost_Objective = pyo.Objective(rule=total_cost_rule, sense=pyo.minimize)

    return model

def pysp_scenario_tree_model_callback():
    # Return a NetworkX scenario tree.
    g = networkx.DiGraph()

    ce1 = "CostExpressions[1]"
    g.add_node("Root",
               cost = ce1,
               variables = ["DevotedAcreage[*]"],
               derived_variables = [])

    ce2 = "CostExpressions[2]"
    wgt = 1. / (3.0 * ScenMult)  # with a big scenmult, we might have troubles
    for s in range(ScenMult):
        g.add_node("BelowAverageScenario"+str(s),
                   cost = ce2,
                   variables = ["QuantitySubQuotaSold[*]",
                                "QuantitySuperQuotaSold[*]",
                                "QuantityPurchased[*]"],
                   derived_variables = [])
        g.add_edge("Root", "BelowAverageScenario"+str(s), weight=wgt)

        g.add_node("AverageScenario"+str(s),
                   cost = ce2,
                   variables = ["QuantitySubQuotaSold[*]",
                                "QuantitySuperQuotaSold[*]",
                                "QuantityPurchased[*]"],
                   derived_variables = [])
        g.add_edge("Root", "AverageScenario"+str(s), weight=wgt)

        g.add_node("AboveAverageScenario"+str(s),
                   cost = ce2,
                   variables = ["QuantitySubQuotaSold[*]",
                                "QuantitySuperQuotaSold[*]",
                                "QuantityPurchased[*]"],
                   derived_variables = [])
        g.add_edge("Root", "AboveAverageScenario"+str(s), weight=wgt)

    return g

