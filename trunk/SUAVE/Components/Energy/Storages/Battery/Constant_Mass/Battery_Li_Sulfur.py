#Battery.py
# 
# Created:  Michael Vegh, November 2014
# Modified:  

# ----------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------

# suave imports
import SUAVE

# package imports
import numpy as np
import scipy as sp
from SUAVE.Attributes                          import Units
from SUAVE.Components.Energy.Storages.Battery  import Battery
# ----------------------------------------------------------------------
#  Battery Class
# ----------------------------------------------------------------------    

class Battery_Li_Sulfur(Battery):
    
    def __defaults__(self):
        self.specific_energy=500*Units.Wh/Units.kg
        self.specific_power=1*Units.kW/Units.kg
        self.ragone.const_1=245.848*Units.kW/Units.kg
        self.ragone.const_2=-.00478/(Units.Wh/Units.kg)
       