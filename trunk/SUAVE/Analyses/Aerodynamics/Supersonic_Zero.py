# Supersonic_Zero.py
# 
# Created:  Tim MacDonald, based on Fidelity_Zero
# Modified: Tim MacDonald, 1/29/15
#
# Updated for new optimization structure


# ----------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------

import SUAVE
from SUAVE.Core import Data, Data_Exception, Data_Warning
from Markup import Markup
from SUAVE.Analyses import Process

# default Aero Results
from Results import Results

from Vortex_Lattice import Vortex_Lattice
from Process_Geometry import Process_Geometry
from SUAVE.Methods.Aerodynamics import Supersonic_Zero as Methods

#from SUAVE.Attributes.Aerodynamics.Aerodynamics_1d_Surrogate import Aerodynamics_1d_Surrogate

# ----------------------------------------------------------------------
#  Class
# ----------------------------------------------------------------------

class Supersonic_Zero(Markup):
    """ SUAVE.Attributes.Aerodynamics.Fidelity_Zero
        aerodynamic model that builds a surrogate model for clean wing 
        lift, using vortex lattic, and various handbook methods
        for everything else
        
        this class is callable, see self.__call__
        
    """
    
    def __defaults__(self):
        
        self.tag = 'Fidelity_Zero_Supersonic'
        
        #self.geometry      = Geometry()
        #self.configuration = Configuration()
        #self.geometry = Data()
        #self.settings = Data()

        # correction factors
        settings =  self.settings
        settings.fuselage_lift_correction           = 1.14
        settings.trim_drag_correction_factor        = 1.02
        settings.wing_parasite_drag_form_factor     = 1.1
        settings.fuselage_parasite_drag_form_factor = 2.3
        settings.aircraft_span_efficiency_factor    = 0.78
        settings.drag_coefficient_increment         = 0.0000
        
        # vortex lattice configurations
        settings.number_panels_spanwise = 5
        settings.number_panels_chordwise = 1
        
        
        # build the evaluation process
        compute = self.process.compute
        
        ##self.conditions_table = Conditions(
            ##angle_of_attack = np.array([-10,-5,0,5,10.0]) * Units.deg ,
        ##)
        #self.training = Data()        
        #self.training.angle_of_attack  = np.array([-10.,-5.,0.,5.,10.]) * Units.deg
        #self.training.lift_coefficient = None
        
        ##self.models = Data()
        ## surrogoate models
        #self.surrogates = Data()
        #self.surrogates.lift_coefficient = None    
        
        compute.lift = Process()

        compute.lift.inviscid_wings                = Vortex_Lattice()
        
        #compute.lift.parasite.wings                = Process_Geometry('wings')
        #compute.drag.parasite.wings.wing           = Methods.Lift.vortex_lift
        compute.lift.vortex                        = Methods.Lift.vortex_lift
        
        compute.lift.compressible_wings            = Methods.Lift.wing_compressibility
        compute.lift.fuselage                      = Methods.Lift.fuselage_correction
        compute.lift.total                         = Methods.Lift.aircraft_total
        
        compute.drag = Process()
        compute.drag.parasite                      = Process()
        compute.drag.parasite.wings                = Process_Geometry('wings')
        compute.drag.parasite.wings.wing           = Methods.Drag.parasite_drag_wing 
        compute.drag.parasite.fuselages            = Process_Geometry('fuselages')
        compute.drag.parasite.fuselages.fuselage   = Methods.Drag.parasite_drag_fuselage
        compute.drag.parasite.propulsors           = Process_Geometry('propulsors')
        compute.drag.parasite.propulsors.propulsor = Methods.Drag.parasite_drag_propulsor
        #compute.drag.parasite.pylons               = Methods.Drag.parasite_drag_pylon
        compute.drag.parasite.total                = Methods.Drag.parasite_total
        compute.drag.induced                       = Methods.Drag.induced_drag_aircraft
        compute.drag.compressibility               = Process()
        compute.drag.compressibility.total         = Methods.Drag.compressibility_drag_total
        compute.drag.miscellaneous                 = Methods.Drag.miscellaneous_drag_aircraft
        compute.drag.untrimmed                     = Methods.Drag.untrimmed
        compute.drag.trim                          = Methods.Drag.trim
        compute.drag.total                         = Methods.Drag.total_aircraft
        
        
    def initialize(self):
        self.process.compute.lift.inviscid_wings.geometry = self.geometry
        self.process.compute.lift.inviscid_wings.initialize()
        
    finalize = initialize        
