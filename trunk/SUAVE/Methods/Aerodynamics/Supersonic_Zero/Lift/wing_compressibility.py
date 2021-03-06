# compute_aircraft_lift.py
# 
# Created:  Anil V., Dec 2013
# Modified: Anil, Trent, Tarik, Feb 2014 
# Modified: Anil  April 2014 

# ----------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------
import SUAVE
# suave imports

from SUAVE.Core import Data
from SUAVE.Core import Units

from SUAVE.Core import Results

from SUAVE.Methods.Aerodynamics.Supersonic_Zero.Drag import compute_aircraft_drag

from SUAVE.Methods.Aerodynamics.Supersonic_Zero.Lift import weissinger_vortex_lattice
from SUAVE.Methods.Aerodynamics.Supersonic_Zero.Lift.vortex_lift import vortex_lift


# python imports
import os, sys, shutil
from copy import deepcopy
from copy import copy
from warnings import warn

# package imports
import numpy as np
import scipy as sp


# ----------------------------------------------------------------------
#  The Function
# ----------------------------------------------------------------------

#def compute_aircraft_lift(conditions,configuration,geometry):
def wing_compressibility(state,settings,geometry):
    """ SUAVE.Methods.Aerodynamics.compute_aircraft_lift(conditions,configuration,geometry)
        computes the lift associated with an aircraft 
        
        Inputs:
            conditions - data dictionary with fields:
                mach_number - float or 1D array of freestream mach numbers
                angle_of_attack - floar or 1D array of angle of attacks
                
            configuration - data dictionary with fields:
                surrogate_models.lift_coefficient - a callable function or class 
                    with inputs of angle of attack and outputs of lift coefficent
                fuselage_lift_correction - the correction to fuselage contribution to lift
                    
            geometry - used for wing
            
        
        Outputs:
            CL - float or 1D array of lift coefficients of the total aircraft
        
        Updates:
            conditions.lift_breakdown - stores results here
            
        Assumptions:
            surrogate model returns total incompressible lift due to wings
            prandtl-glaurert compressibility correction on this
            fuselage contribution to lift correction as a factor
        
    """    
   
    # unpack
    fus_correction = settings.fuselage_lift_correction
    Mc             = state.conditions.freestream.mach_number
    AoA            = state.conditions.aerodynamics.angle_of_attack
    
    
    wings_lift = state.conditions.aerodynamics.lift_coefficient
    
    # compressibility correction
    compress_corr = np.array([[0.0]] * len(Mc))
    compress_corr[Mc < 0.95] = 1./(np.sqrt(1.-Mc[Mc < 0.95]**2.))
    compress_corr[Mc >= 0.95] = 1./(np.sqrt(1.-0.95**2)) # Values for Mc > 1.05 are update after this assignment 
    compress_corr[Mc > 1.05] = 1./(np.sqrt(Mc[Mc > 1.05]**2.-1.))
    
    
    # correct lift
    wings_lift_comp = wings_lift * compress_corr  
    
    state.conditions.aerodynamics.lift_breakdown.compressible_wings = wings_lift_comp
    state.conditions.aerodynamics.lift_coefficient= wings_lift_comp    
    
    return wings_lift_comp



if __name__ == '__main__':   
    #test()
    raise RuntimeError , 'module test failed, not implemented'


#-------runn this caase  - have a local test case---------------------

