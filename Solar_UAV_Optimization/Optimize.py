# Optimize.py
# 
# Created:  Feb 2016, E. Botero
# Modified: 

# ----------------------------------------------------------------------        
#   Imports
# ----------------------------------------------------------------------    

from SUAVE.Core import Units, Data
import numpy as np
import os
import sys
current_directory_path = os.path.dirname(__file__)
sys.path.append(current_directory_path)
import Vehicles
import Analyses
import Missions
import Procedure
import Plot_Mission
import SUAVE.Optimization.Package_Setups.scipy_setup as scipy_setup
import SUAVE.Optimization.Package_Setups.pyopt_setup as pyopt_setup
from SUAVE.Optimization.Nexus import Nexus
import pylab as plt
sys.path.remove(current_directory_path)

# ----------------------------------------------------------------------        
#   Run the whole thing
# ----------------------------------------------------------------------  
def main():
    
    problem = setup()
    output  = scipy_setup.SciPy_Solve(problem)
    
    problem.translate(output)

    Plot_Mission.plot_mission(problem.results.mission)
    
    return

# ----------------------------------------------------------------------        
#   Inputs, Objective, & Constraints
# ----------------------------------------------------------------------  

def setup():

    nexus = Nexus()
    problem = Data()
    nexus.optimization_problem = problem

    # -------------------------------------------------------------------
    # Inputs
    # -------------------------------------------------------------------

    # [ tag , initial, [lb,ub], scaling, units ]
    problem.inputs = np.array([
        [ 'wing_area'       ,    0.5,   0.1,      1.5 ,    0.5, 1*Units.meter      ],
        [ 'aspect_ratio'    ,   10.0,   5.0,     20.0 ,   10.0, 1*Units.less       ], 
        [ 'dynamic_pressure',  125.0,   1.0,   2000.0 ,  125.0, 1*Units.pascals    ], 
        [ 'solar_ratio'     ,    0.0,   0.0,      0.97,    1.0, 1*Units.less       ], 
        [ 'kv'              ,  800.0,  10.0,  10000.0 ,  800.0, 1*Units['rpm/volt']], 
    ],dtype=object)

    # -------------------------------------------------------------------
    # Objective
    # -------------------------------------------------------------------

    # [ tag, scaling, units ]
    problem.objective = np.array([
         [ 'Nothing', 1. , 1*Units.kg],
    ],dtype=object)
    
    # -------------------------------------------------------------------
    # Constraints
    # -------------------------------------------------------------------

    # [ tag, sense, edge, scaling, units ]
    problem.constraints = np.array([
        [ 'energy_constraint', '=', 0.0, 1.0, 1*Units.less],
        [ 'battery_mass'     , '>', 0.0, 1.0, 1*Units.kg  ],       
        [ 'CL'               , '>', 0.0, 1.0, 1*Units.less],
        [ 'Throttle_min'     , '>', 0.0, 1.0, 1*Units.less],
        [ 'Throttle_max'     , '>', 0.0, 1.0, 1*Units.less],
    ],dtype=object)
    
    # -------------------------------------------------------------------
    #  Aliases
    # -------------------------------------------------------------------
    
    # [ 'alias' , ['data.path1.name','data.path2.name'] ]
    problem.aliases = [
        [ 'wing_area'        ,['vehicle_configurations.*.wings.main_wing.areas.reference',
                               'vehicle_configurations.base.reference_area']                                ], 
        [ 'aspect_ratio'     , 'vehicle_configurations.*.wings.main_wing.aspect_ratio'                      ],
        [ 'kv'               , 'vehicle_configurations.*.propulsors.solar_low_fidelity.motor.speed_constant'           ], 
        [ 'battery_mass'     , 'vehicle_configurations.base.propulsors.solar_low_fidelity.battery.mass_properties.mass'],
        [ 'solar_ratio'      , 'vehicle_configurations.*.propulsors.solar_low_fidelity.solar_panel.ratio'              ],
        [ 'dynamic_pressure' , 'missions.mission.segments.cruise.dynamic_pressure'                          ],  
        [ 'Nothing'          , 'summary.nothing'                                                            ],
        [ 'energy_constraint', 'summary.energy_constraint'                                                  ],
        [ 'CL'               , 'summary.CL'                                                                 ],    
        [ 'Throttle_min'     , 'summary.throttle_min'                                                       ],
        [ 'Throttle_max'     , 'summary.throttle_max'                                                       ],
    ]      
    
    # -------------------------------------------------------------------
    #  Vehicles
    # -------------------------------------------------------------------
    nexus.vehicle_configurations = Vehicles.setup()
    
    # -------------------------------------------------------------------
    #  Analyses
    # -------------------------------------------------------------------
    nexus.analyses = Analyses.setup(nexus.vehicle_configurations)
       
    # -------------------------------------------------------------------
    #  Missions
    # -------------------------------------------------------------------
    nexus.missions = Missions.setup(nexus.analyses,nexus.vehicle_configurations)
    
    # -------------------------------------------------------------------
    #  Procedure
    # -------------------------------------------------------------------    
    nexus.procedure = Procedure.setup()
    
    return nexus

if __name__ == '__main__':
    main()
    plt.show()