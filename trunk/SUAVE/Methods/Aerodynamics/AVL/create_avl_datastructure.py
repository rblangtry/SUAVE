# Tim Momose, October 2014

# ----------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------
import scipy
import numpy as np
from copy import deepcopy
# SUAVE Imports
from SUAVE.Structure import Data, Data_Exception, Data_Warning
#from SUAVE.Methods.Aerodynamics.Fidelity_Zero.Drag.parasite_drag_aircraft import parasite_drag_aircraft
# SUAVE-AVL Imports
from AVL_Data.AVL_Inputs   import AVL_Inputs
from AVL_Data.AVL_Wing     import AVL_Wing, AVL_Section, AVL_Control_Surface
from AVL_Data.AVL_Body     import AVL_Body
from AVL_Data.AVL_Aircraft import AVL_Aircraft
from AVL_Data.AVL_Cases    import AVL_Cases,AVL_Run_Case
from AVL_Data.AVL_Configuration import AVL_Configuration


def create_avl_datastructure(geometry,configuration,conditions):
	
	avl_aircraft      = translate_avl_geometry(geometry)
	avl_configuration = translate_avl_configuration(geometry,configuration,conditions)
	#avl_cases         = translate_avl_cases(geometry,configuration,conditions)
	avl_cases         = setup_test_cases(conditions)

	# pack results in a new AVL inputs structure
	avl_inputs = AVL_Inputs()
	avl_inputs.aircraft      = avl_aircraft
	avl_inputs.configuration = avl_configuration
	avl_inputs.cases         = avl_cases
	return avl_inputs


def translate_avl_geometry(geometry):

	aircraft = AVL_Aircraft()
	aircraft.tag = geometry.tag
	
	# FOR NOW, ASSUMING THAT CONTROL SURFACES ARE NOT ALIGNED WITH WING SECTIONS (IN THIS CASE, ROOT AND TIP SECTIONS)
	for wing in geometry.wings:
		w = AVL_Wing()
		w.tag       = wing.tag
		w.symmetric = wing.symmetric
		w.vertical  = wing.vertical
		w.sweep     = wing.sweep
		w.dihedral  = wing.dihedral
		w = populate_wing_sections(w,wing)
		aircraft.append_wing(w)
	
	for body in geometry.fuselages:
		b = AVL_Body()
		b.tag       = body.tag
		b.symmetric = True#body.symmetric
		b.lengths.total = body.lengths.total
		b.lengths.nose  = body.lengths.nose
		b.lengths.tail  = body.lengths.tail
		b.widths.maximum = body.width
		b.heights.maximum = body.heights.maximum
		b = populate_body_sections(b,body)
		aircraft.append_body(b)
	
	return aircraft


def populate_wing_sections(avl_wing,suave_wing):
	symm     = avl_wing.symmetric
	sweep    = avl_wing.sweep
	dihedral = avl_wing.dihedral
	span     = suave_wing.spans.projected
	semispan = suave_wing.spans.projected * 0.5 * (2 - symm)
	origin   = suave_wing.origin
	root_section = AVL_Section()
	root_section.tag    = 'Root_Section'
	root_section.origin = origin
	root_section.chord  = suave_wing.chords.root
	root_section.twist  = suave_wing.twists.root
	
	tip_section = AVL_Section()
	tip_section.tag  = 'Tip_Section'
	tip_section.chord = suave_wing.chords.tip
	tip_section.twist = suave_wing.twists.tip
	tip_section.origin = [origin[0]+semispan*np.tan(sweep),origin[1]+semispan,origin[2]+semispan*np.tan(dihedral)]
	
	if avl_wing.vertical:
		temp = tip_section.origin[2]
		tip_section.origin[2] = tip_section.origin[1]
		tip_section.origin[1] = temp
	
	avl_wing.append_section(root_section)
	avl_wing.append_section(tip_section)
	
	if suave_wing.control_surfaces:
		for ctrl in suave_wing.control_surfaces:
			num = 1
			for section in ctrl.sections:
				semispan_fraction = (span/semispan) * section.origins.span_fraction
				s = AVL_Section()
				s.chord  = scipy.interp(semispan_fraction,[0.,1.],[root_section.chord,tip_section.chord])
				s.tag    = '{0}_Section{1}'.format(ctrl.tag,num)
				s.origin = section.origins.dimensional
				s.origin[0] = s.origin[0] - s.chord*section.origins.chord_fraction
				s.twist  = scipy.interp(semispan_fraction,[0.,1.],[root_section.twist,tip_section.twist])
				c = AVL_Control_Surface()
				c.tag     = ctrl.tag
				c.x_hinge = 1. - section.chord_fraction
				c.sign_duplicate = ctrl.deflection_symmetry
				
				s.append_control_surface(c)
				avl_wing.append_section(s)
				num += 1
	
	return avl_wing


def populate_body_sections(avl_body,suave_body):

	symm = avl_body.symmetric
	semispan_h = avl_body.widths.maximum * 0.5 * (2 - symm)
	semispan_v = avl_body.heights.maximum * 0.5
	origin = suave_body.origin
	root_section = AVL_Section()
	root_section.tag    = 'Center_Horizontal_Section'
	root_section.origin = origin
	root_section.chord  = avl_body.lengths.total
	
	tip_section = AVL_Section()
	tip_section.tag  = 'Outer_Horizontal_Section'
	nl = avl_body.lengths.nose
	tl = avl_body.lengths.tail
	tip_section.origin = [origin[0]+nl,origin[1]+semispan_h,origin[2]]
	tip_section.chord = root_section.chord - nl - tl
	
	avl_body.append_section(root_section,'Horizontal')
	avl_body.append_section(tip_section,'Horizontal')
	tip_sectionv1 = deepcopy(tip_section)
	tip_sectionv1.origin[1] = origin[1]
	tip_sectionv1.origin[2] = origin[2] - semispan_v
	tip_sectionv1.tag       = 'Lower_Vertical_Section'
	avl_body.append_section(tip_sectionv1,'Vertical')
	avl_body.append_section(root_section,'Vertical')
	tip_sectionv2 = deepcopy(tip_section)
	tip_sectionv2.origin[1] = origin[1]
	tip_sectionv2.origin[2] = origin[2] + semispan_v
	tip_sectionv2.tag       = 'Upper_Vertical_Section'
	avl_body.append_section(tip_sectionv2,'Vertical')
	
	return avl_body
	

def translate_avl_configuration(geometry,configuration,conditions):
	
	config = AVL_Configuration()
	config.reference_values.sref = geometry.reference_area
	config.reference_values.bref = geometry.wings['Main Wing'].spans.projected
	config.reference_values.cref = geometry.wings['Main Wing'].chords.mean_aerodynamic
	config.reference_values.cg_coords = geometry.mass_properties.center_of_gravity
	
	config.parasite_drag = 0.0177#parasite_drag_aircraft(conditions,configuration,geometry)
	
	config.mass_properties.mass = geometry.mass_properties.max_takeoff ###
	moment_tensor = geometry.mass_properties.moments_of_inertia.tensor
	config.mass_properties.inertial.Ixx = moment_tensor[0][0]
	config.mass_properties.inertial.Iyy = moment_tensor[1][1]
	config.mass_properties.inertial.Izz = moment_tensor[2][2]
	config.mass_properties.inertial.Ixy = moment_tensor[0][1]
	config.mass_properties.inertial.Iyz = moment_tensor[1][2]
	config.mass_properties.inertial.Izx = moment_tensor[2][0]

	#No Iysym, Izsym assumed for now
	
	return config



def translate_avl_cases():
	raise NotImplementedError



def setup_test_cases(conditions):
	
	runcases = AVL_Cases()
	
	alphas = [-10,-5,-2,0,2,5,10,20]
	mach   = conditions.freestream.mach
	v_inf  = conditions.freestream.velocity
	rho    = conditions.density
	g      = conditions.g
	for alpha in alphas:
		case = AVL_Run_Case()
		case.tag = 'Alpha={}'.format(alpha)
		case.conditions.mach  = mach
		case.conditions.v_inf = v_inf
		case.conditions.rho   = rho
		case.conditions.gravitation_acc = g
		case.angles.alpha     = alpha
		runcases.append_case(case)
	
	return runcases
