__all__ = ["valid_units", "dimensionless_unit"]

import pint

unit_registry = pint.UnitRegistry()
unit_registry.define("@alias week = w")

# Da is defined incorrectly as dimensionless in Pint 0.17
unit_registry.define("dalton = g / mol = Da")

# Workaround for https://github.com/hgrecco/pint/issues/740
unit_registry._build_cache()

time_unit_names = {"fs", "ps", "ns", "us", "ms", "cs", "ds", "s", "min", "hr", "d", "w"}

length_unit_names = {"fm", "pm", "nm", "um", "mm", "cm", "dm", "m"}

mass_unit_names = {"fg", "pg", "ng", "ug", "mg", "cg", "dg", "g", "kg"}

volume_unit_names = {"fL", "pL", "nL", "uL", "mL", "cL", "dL", "L"}

amount_unit_names = {"fmol", "pmol", "nmol", "umol", "mmol", "cmol", "dmol", "mol"}

concentration_unit_names = {"fM", "pM", "nM", "uM", "mM", "cM", "dM", "M"}

molecular_mass_unit_names = {"Da", "kDa", "MDa"}

radioactivity_unit_names = {"fCi", "pCi", "nCi", "uCi", "mCi", "cCi", "dCi", "Ci"}

voltage_unit_names = {"fV", "pV", "nV", "uV", "mV", "cV", "dV", "V"}

all_units_names = (
    time_unit_names
    | length_unit_names
    | mass_unit_names
    | volume_unit_names
    | amount_unit_names
    | concentration_unit_names
    | molecular_mass_unit_names
    | radioactivity_unit_names
    | voltage_unit_names
)

valid_units = {name: unit_registry.Unit(name) for name in all_units_names}

valid_units_error_string = " or ".join(all_units_names)

dimensionless_unit = unit_registry.Unit("1")
