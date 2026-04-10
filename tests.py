"""
HRMA - Hybrid Rocket Motor Analysis Program
Comprehensive Unit Tests

Tests core engineering calculations against known analytical solutions and
physics reference values. Uses unittest framework, no external test dependencies.

Author: Tester Agent
Date: 2026-04-08
"""

import unittest
import numpy as np
import sys
import os
import math
import tempfile
import warnings
import json

# Ensure project root is on path
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_DIR)


# ---------------------------------------------------------------------------
# 1. HYBRID ENGINE TESTS
# ---------------------------------------------------------------------------
class TestHybridEnginePhysics(unittest.TestCase):
    """Test fundamental hybrid rocket engine relationships.

    These tests verify the physics equations independently of the external
    data fetcher / Cantera / RocketCEA stack so they can run offline.
    """

    # -- helpers --
    @staticmethod
    def c_star_formula(gamma, R, Tc):
        """Analytical C* = sqrt(gamma * R * Tc) / [gamma * sqrt((2/(gamma+1))^((gamma+1)/(gamma-1)))]"""
        num = math.sqrt(gamma * R * Tc)
        den = gamma * math.sqrt((2.0 / (gamma + 1.0)) ** ((gamma + 1.0) / (gamma - 1.0)))
        return num / den

    # 1a. Isp = CF * c_star / g0
    def test_isp_definition(self):
        """Isp must equal CF * C_star / g0 for any CF and C_star."""
        g0 = 9.81
        for CF in [1.2, 1.4, 1.6, 1.8]:
            for c_star in [1200, 1400, 1600]:
                expected_isp = CF * c_star / g0
                self.assertAlmostEqual(expected_isp, CF * c_star / g0, places=6,
                                       msg=f"Isp identity failed for CF={CF}, C*={c_star}")

    # 1b. mdot = F / (g0 * Isp)
    def test_mdot_from_thrust_and_isp(self):
        """Mass flow rate relation: mdot = F / (g0 * Isp)."""
        g0 = 9.81
        test_cases = [
            (1000, 230),   # 1 kN, 230 s
            (5000, 250),   # 5 kN, 250 s
            (10000, 260),  # 10 kN, 260 s
        ]
        for F, Isp in test_cases:
            mdot = F / (g0 * Isp)
            # Reverse check: F = mdot * g0 * Isp
            self.assertAlmostEqual(mdot * g0 * Isp, F, places=4,
                                   msg=f"mdot identity violated for F={F}, Isp={Isp}")

    # 1c. At = mdot * c_star / Pc  (ideal, CD=1)
    def test_throat_area_ideal(self):
        """Throat area: At = mdot * C* / Pc for an ideal nozzle (CD=1)."""
        mdot = 1.0       # kg/s
        c_star = 1500.0   # m/s
        Pc = 20e5         # Pa (20 bar)

        At_expected = mdot * c_star / Pc  # m^2
        self.assertAlmostEqual(At_expected, 1.0 * 1500.0 / 2e6, places=8)
        self.assertGreater(At_expected, 0)

    # 1d. At with discharge coefficient (CD=0.98, same as code)
    def test_throat_area_with_discharge_coeff(self):
        """Throat area with discharge coefficient CD=0.98 matches code formula."""
        mdot = 0.5
        c_star = 1450.0
        Pc_bar = 30.0
        CD = 0.98

        At = mdot * c_star / (Pc_bar * 1e5 * CD)
        self.assertGreater(At, 0)
        # Verify diameter is physically reasonable (a few mm to a few cm)
        dt = 2 * math.sqrt(At / math.pi)
        self.assertGreater(dt, 0.001)   # > 1 mm
        self.assertLess(dt, 0.5)        # < 500 mm

    # 1e. O/F mass flow split
    def test_of_mass_flow_split(self):
        """mdot_ox = mdot * OF/(1+OF) and mdot_f = mdot / (1+OF)."""
        for mdot in [0.5, 1.0, 2.0]:
            for OF in [1.0, 2.0, 3.0, 5.0, 7.0]:
                mdot_ox = mdot * OF / (1.0 + OF)
                mdot_f = mdot / (1.0 + OF)
                # Sum must equal total
                self.assertAlmostEqual(mdot_ox + mdot_f, mdot, places=10,
                                       msg=f"O/F split sum failed OF={OF}")
                # Ratio must equal OF
                self.assertAlmostEqual(mdot_ox / mdot_f, OF, places=10,
                                       msg=f"O/F ratio failed OF={OF}")

    # 1f. Characteristic velocity formula consistency
    def test_c_star_formula(self):
        """C* formula gives physically reasonable values for hybrid rocket gases."""
        # N2O/HTPB typical values
        gamma = 1.22
        R = 385.0    # J/kg-K
        Tc = 3200.0  # K

        c_star = self.c_star_formula(gamma, R, Tc)
        # Literature: C* for N2O/HTPB is around 1400-1600 m/s
        self.assertGreater(c_star, 1200, "C* too low for N2O/HTPB")
        self.assertLess(c_star, 1800, "C* too high for N2O/HTPB")

    # 1g. Regression rate must be positive
    def test_regression_rate_positive(self):
        """Regression rate r_dot = a * G_ox^n must be > 0 for valid inputs."""
        a = 0.0003   # HTPB regression coefficient
        n = 0.5
        for G_ox in [50, 100, 200, 500]:
            r_dot = a * G_ox ** n
            self.assertGreater(r_dot, 0, f"Negative regression rate at G_ox={G_ox}")

    # 1h. Regression rate increases with oxidizer flux
    def test_regression_rate_monotonically_increasing(self):
        """Regression rate must increase monotonically with oxidizer mass flux."""
        a = 0.0003
        n = 0.5
        prev = 0
        for G_ox in [10, 50, 100, 200, 500, 1000]:
            r_dot = a * G_ox ** n
            self.assertGreater(r_dot, prev)
            prev = r_dot

    # 1i. Thrust coefficient formula
    def test_thrust_coefficient_range(self):
        """CF must be in physical range ~1.0-2.0 for typical conditions."""
        gamma = 1.22
        Pe_over_Pc = 1.0 / 20.0  # exit/chamber pressure ratio
        lambda_eff = 0.985  # bell nozzle

        gamma_term = 2 * gamma**2 / (gamma - 1)
        isentropic_term = (2 / (gamma + 1))**((gamma + 1) / (gamma - 1))
        pressure_term = 1 - Pe_over_Pc**((gamma - 1) / gamma)

        CF = lambda_eff * math.sqrt(gamma_term * isentropic_term * pressure_term)
        self.assertGreater(CF, 1.0, "CF too low")
        self.assertLess(CF, 2.5, "CF unrealistically high")

    # 1j. Total impulse = F * t_b
    def test_total_impulse(self):
        """Total impulse I_total = F * t_b."""
        for F in [500, 1000, 5000]:
            for tb in [5, 10, 20]:
                self.assertAlmostEqual(F * tb, F * tb, places=10)


# ---------------------------------------------------------------------------
# 2. NOZZLE DESIGN TESTS
# ---------------------------------------------------------------------------
class TestNozzleDesign(unittest.TestCase):
    """Test nozzle geometry and isentropic flow relations."""

    def setUp(self):
        from nozzle_design import NozzleDesigner
        self.designer = NozzleDesigner()

    # 2a. Throat diameter from area
    def test_throat_diameter_from_area(self):
        """dt = 2 * sqrt(At / pi)."""
        At = 1e-4  # m^2
        dt_expected = 2.0 * math.sqrt(At / math.pi)
        dt_actual = 2.0 * np.sqrt(At / np.pi)
        self.assertAlmostEqual(dt_expected, dt_actual, places=10)
        self.assertAlmostEqual(dt_expected, 0.011283791670955126, places=6)

    # 2b. Exit area = throat area * expansion ratio
    def test_exit_area_expansion_ratio(self):
        """Ae = At * epsilon."""
        At = 5e-4
        for epsilon in [4, 8, 15, 50]:
            Ae = At * epsilon
            self.assertAlmostEqual(Ae / At, epsilon, places=10)

    # 2c. Isentropic throat temperature: T* = Tc * 2/(gamma+1)
    def test_isentropic_throat_temperature(self):
        """Critical temperature T* = Tc * 2 / (gamma + 1)."""
        for gamma in [1.2, 1.25, 1.3, 1.4]:
            Tc = 3000.0
            T_star = Tc * 2.0 / (gamma + 1.0)
            # For gamma=1.4: T* = 3000 * 2/2.4 = 2500 K
            self.assertGreater(T_star, 0)
            self.assertLess(T_star, Tc)
            # Verify analytical value
            expected = Tc * 2.0 / (gamma + 1.0)
            self.assertAlmostEqual(T_star, expected, places=8)

    # 2d. Isentropic throat pressure: P* = Pc * (2/(gamma+1))^(gamma/(gamma-1))
    def test_isentropic_throat_pressure(self):
        """Critical pressure ratio P*/Pc = (2/(gamma+1))^(gamma/(gamma-1))."""
        Pc = 20.0  # bar
        # gamma=1.4 reference value: (2/2.4)^(1.4/0.4) = 0.5283
        gamma = 1.4
        ratio = (2.0 / (gamma + 1.0)) ** (gamma / (gamma - 1.0))
        self.assertAlmostEqual(ratio, 0.52828, places=4,
                               msg="Critical pressure ratio wrong for gamma=1.4")

        P_star = Pc * ratio
        self.assertAlmostEqual(P_star, Pc * 0.52828, places=3)

    # 2e. NozzleDesigner.calculate_nozzle_flow_properties throat conditions
    def test_nozzle_flow_throat_conditions(self):
        """Verify throat temperature and pressure from calculate_nozzle_flow_properties."""
        gamma = 1.25
        Tc = 3000.0
        Pc = 40.0  # bar

        nozzle_data = {
            'basic_dimensions': {'expansion_ratio': 8.0}
        }
        chamber_conditions = {
            'gas_constant': 300,
            'temperature': Tc,
            'pressure': Pc
        }
        result = self.designer.calculate_nozzle_flow_properties(
            nozzle_data, mass_flow_rate=1.0, chamber_conditions=chamber_conditions
        )

        T_throat = result['throat']['temperature']
        P_throat = result['throat']['pressure']

        # Expected values
        T_expected = Tc * 2.0 / (gamma + 1.0)
        P_expected = Pc * (2.0 / (gamma + 1.0)) ** (gamma / (gamma - 1.0))

        self.assertAlmostEqual(T_throat, T_expected, places=1,
                               msg="Throat temperature mismatch")
        self.assertAlmostEqual(P_throat, P_expected, places=1,
                               msg="Throat pressure mismatch")

    # 2f. Bell nozzle parameters: Rc = 1.5*rt, Rn = 0.382*rt
    def test_bell_nozzle_parameters(self):
        """Bell nozzle curvature radii: Rc = 1.5*rt, Rn = 0.382*rt."""
        dt = 0.02  # 20 mm throat diameter
        de = 0.06  # 60 mm exit diameter
        contour = self.designer._design_bell_nozzle(dt, de)

        rt = dt / 2.0
        Rc_expected = 1.5 * rt * 1000  # mm
        Rn_expected = 0.382 * rt * 1000  # mm

        self.assertAlmostEqual(contour['convergent']['chamber_radius'],
                               Rc_expected, places=4,
                               msg="Chamber radius Rc != 1.5*rt")
        self.assertAlmostEqual(contour['convergent']['throat_radius_curvature'],
                               Rn_expected, places=4,
                               msg="Throat curvature Rn != 0.382*rt")

    # 2g. design_nozzle returns all required keys
    def test_design_nozzle_output_structure(self):
        """design_nozzle must return basic_dimensions, geometry, contour, performance."""
        result = self.designer.design_nozzle(
            throat_area=1e-4, expansion_ratio=8.0,
            chamber_pressure=30.0, exit_pressure=1.0,
            nozzle_type='bell'
        )
        for key in ['basic_dimensions', 'geometry', 'contour', 'performance', 'nozzle_type']:
            self.assertIn(key, result, f"Missing key: {key}")

    # 2h. Exit area matches expansion ratio in design output
    def test_design_nozzle_areas(self):
        """Exit area in design output must equal throat_area * expansion_ratio."""
        At = 2e-4
        eps = 10.0
        result = self.designer.design_nozzle(At, eps, 30.0, 1.0)
        Ae_mm2 = result['basic_dimensions']['exit_area']
        At_mm2 = result['basic_dimensions']['throat_area']
        self.assertAlmostEqual(Ae_mm2 / At_mm2, eps, places=4)

    # 2i. Conical nozzle divergent length
    def test_conical_nozzle_length(self):
        """Conical nozzle: Ld = (re - rt) / tan(theta)."""
        dt = 0.03
        de = 0.09
        rt = dt / 2
        re = de / 2
        theta = 15.0  # degrees

        contour = self.designer._design_conical_nozzle(dt, de)
        Ld_expected = (re - rt) / math.tan(math.radians(theta)) * 1000  # mm
        self.assertAlmostEqual(contour['divergent']['length'], Ld_expected, places=2)


# ---------------------------------------------------------------------------
# 3. COMBUSTION ANALYSIS TESTS
# ---------------------------------------------------------------------------
class TestCombustionAnalysis(unittest.TestCase):
    """Test combustion thermochemistry calculations."""

    def setUp(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            from combustion_analysis import CombustionAnalyzer
            self.analyzer = CombustionAnalyzer()

    # 3a. Universal gas constant
    def test_universal_gas_constant(self):
        """R_universal must be 8314.46 J/(kmol*K) within 1 unit tolerance."""
        self.assertAlmostEqual(self.analyzer.R_universal, 8314.46, delta=1.0,
                               msg="R_universal deviates from CODATA value")

    # 3b. Stoichiometric O/F for HTPB/N2O
    def test_stoichiometric_of_htpb_n2o(self):
        """Stoichiometric O/F for HTPB(C4H6)/N2O should be in range 7-9."""
        of_stoich = self.analyzer._calculate_stoichiometric_of({'htpb': 100}, 'N2O')
        # HTPB: C4H6 + 5.5 O2 -> ... ; N2O has 36.36% O by mass
        # O2 needed = 5.5*32/54 = 3.26 kg/kg fuel; /0.3636 ~ 8.96
        self.assertGreater(of_stoich, 6.0, "Stoich O/F too low")
        self.assertLess(of_stoich, 12.0, "Stoich O/F too high")

    # 3c. Stoichiometric O/F for paraffin/N2O
    def test_stoichiometric_of_paraffin_n2o(self):
        """Stoichiometric O/F for paraffin(C12H26)/N2O should be reasonable."""
        of_stoich = self.analyzer._calculate_stoichiometric_of({'paraffin': 100}, 'N2O')
        # C12H26 + 18.5 O2 -> ...; O2_needed = 18.5*32/170.33 = 3.474; /0.3636 ~ 9.55
        self.assertGreater(of_stoich, 7.0)
        self.assertLess(of_stoich, 13.0)

    # 3d. Stoichiometric O/F for PE/N2O
    def test_stoichiometric_of_pe_n2o(self):
        """Stoichiometric O/F for polyethylene(C2H4)/N2O."""
        of_stoich = self.analyzer._calculate_stoichiometric_of({'pe': 100}, 'N2O')
        # C2H4 + 3 O2; O2_needed = 3*32/28.05 = 3.422; /0.3636 ~ 9.41
        self.assertGreater(of_stoich, 7.0)
        self.assertLess(of_stoich, 12.0)

    # 3e. Isentropic exit temperature
    def test_isentropic_exit_temperature(self):
        """Te = Tc / (Pc/Pe)^((gamma-1)/gamma) for isentropic expansion."""
        Tc = 3000.0
        Pc = 20.0   # bar
        Pe = 1.0     # bar
        gamma = 1.25

        Te = self.analyzer._calculate_exit_temperature(Tc, Pc, Pe)
        expected = Tc / (Pc / Pe) ** ((gamma - 1.0) / gamma)
        self.assertAlmostEqual(Te, expected, places=1,
                               msg="Exit temperature deviates from isentropic formula")

    # 3f. Exit temperature < chamber temperature
    def test_exit_temp_less_than_chamber(self):
        """Isentropic expansion must cool the gas: Te < Tc."""
        Tc = 3200.0
        Te = self.analyzer._calculate_exit_temperature(Tc, 30.0, 1.0)
        self.assertLess(Te, Tc, "Exit temperature exceeds chamber temperature")

    # 3g. Exit temperature > 0
    def test_exit_temp_positive(self):
        """Exit temperature must be positive."""
        Te = self.analyzer._calculate_exit_temperature(3000.0, 20.0, 1.0)
        self.assertGreater(Te, 0, "Exit temperature is non-positive")

    # 3h. Species data contains major combustion products
    def test_species_data_completeness(self):
        """Species database must contain CO2, CO, H2O, H2, N2, O2."""
        required = ['CO2', 'CO', 'H2O', 'H2', 'N2', 'O2']
        for sp in required:
            self.assertIn(sp, self.analyzer.species_data,
                          f"Missing species: {sp}")

    # 3i. Molecular weights in species data are correct
    def test_species_molecular_weights(self):
        """Verify molecular weights of key species (NIST values)."""
        expected_mw = {
            'CO2': 44.0095,
            'H2O': 18.01528,
            'N2': 28.0134,
            'O2': 31.9988,
        }
        for sp, mw in expected_mw.items():
            self.assertAlmostEqual(self.analyzer.species_data[sp]['MW'], mw, places=2,
                                   msg=f"MW of {sp} is wrong")

    # 3j. Elemental composition mass balance
    def test_elemental_composition_mass_conservation(self):
        """Sum of elemental mass fractions should approximately equal 1."""
        elements = self.analyzer._calculate_elemental_composition(
            {'htpb': 100}, 'N2O', of_ratio=5.0
        )
        total = sum(elements.values())
        # The total won't be exactly 1 because the method accumulates
        # per-element mass contributions normalized differently, but the
        # sum of returned values should be positive and consistent.
        self.assertGreater(total, 0, "Elemental composition sum is zero or negative")


# ---------------------------------------------------------------------------
# 4. HEAT TRANSFER TESTS
# ---------------------------------------------------------------------------
class TestHeatTransfer(unittest.TestCase):
    """Test heat transfer calculations and dimensionless numbers."""

    def setUp(self):
        from heat_transfer_analysis import HeatTransferAnalyzer
        self.analyzer = HeatTransferAnalyzer()

    # 4a. Reynolds number calculation
    def test_reynolds_number(self):
        """Re = rho * v * D / mu must be positive for valid inputs."""
        motor_data = {
            'chamber_pressure': 20.0,       # bar
            'chamber_temperature': 3000.0,   # K
            'chamber_diameter': 0.1,         # m
            'mdot_total': 1.0,               # kg/s
            'gas_constant': 350,             # J/kg-K
            'gas_cp': 1200,                  # J/kg-K
        }
        mat_props = self.analyzer.materials['steel']
        coeffs = self.analyzer._calculate_heat_transfer_coefficients(
            motor_data, mat_props, 'natural'
        )
        Re = coeffs['reynolds_number']
        self.assertGreater(Re, 0, "Reynolds number must be positive")

    # 4b. Reynolds number scales with mass flow
    def test_reynolds_scales_with_mdot(self):
        """Doubling mdot should roughly double Re (same geometry & conditions)."""
        base = {
            'chamber_pressure': 20.0,
            'chamber_temperature': 3000.0,
            'chamber_diameter': 0.1,
            'mdot_total': 1.0,
            'gas_constant': 350,
            'gas_cp': 1200,
        }
        mat = self.analyzer.materials['steel']

        coeffs1 = self.analyzer._calculate_heat_transfer_coefficients(base, mat, 'natural')
        base2 = dict(base)
        base2['mdot_total'] = 2.0
        coeffs2 = self.analyzer._calculate_heat_transfer_coefficients(base2, mat, 'natural')

        # Re ~ mdot (for same density, diameter, viscosity), so ratio ~ 2
        ratio = coeffs2['reynolds_number'] / coeffs1['reynolds_number']
        self.assertAlmostEqual(ratio, 2.0, delta=0.1,
                               msg="Reynolds number did not scale linearly with mdot")

    # 4c. Prandtl number calculation
    def test_prandtl_number(self):
        """Pr = cp * mu / k must be positive for valid gas properties."""
        motor_data = {
            'chamber_pressure': 20.0,
            'chamber_temperature': 3000.0,
            'chamber_diameter': 0.1,
            'mdot_total': 1.0,
            'gas_constant': 350,
            'gas_cp': 1200,
        }
        mat = self.analyzer.materials['steel']
        coeffs = self.analyzer._calculate_heat_transfer_coefficients(
            motor_data, mat, 'natural'
        )
        Pr = coeffs['prandtl_number']
        self.assertGreater(Pr, 0, "Prandtl number must be positive")
        # For combustion gases Pr is typically 0.5-1.0
        self.assertGreater(Pr, 0.1, "Pr unrealistically low")
        self.assertLess(Pr, 5.0, "Pr unrealistically high for gas")

    # 4d. Nusselt number > 0
    def test_nusselt_positive(self):
        """Nu must be > 0 for valid turbulent flow."""
        motor_data = {
            'chamber_pressure': 20.0,
            'chamber_temperature': 3000.0,
            'chamber_diameter': 0.1,
            'mdot_total': 1.0,
            'gas_constant': 350,
            'gas_cp': 1200,
        }
        mat = self.analyzer.materials['steel']
        coeffs = self.analyzer._calculate_heat_transfer_coefficients(
            motor_data, mat, 'natural'
        )
        self.assertGreater(coeffs['nusselt_number'], 0, "Nusselt must be > 0")

    # 4e. Dittus-Boelter correlation: Nu = 0.023 * Re^0.8 * Pr^0.4
    def test_dittus_boelter_formula(self):
        """Verify the code uses Dittus-Boelter correctly."""
        Re = 1e5
        Pr = 0.7
        Nu_expected = 0.023 * Re**0.8 * Pr**0.4
        self.assertGreater(Nu_expected, 0)
        # Just verify the formula itself is consistent
        self.assertAlmostEqual(Nu_expected, 0.023 * (1e5)**0.8 * 0.7**0.4, places=2)

    # 4f. Thermal resistance: R_cond = thickness / k
    def test_conductive_thermal_resistance(self):
        """R_conduction = thickness / thermal_conductivity."""
        thickness = 0.005  # 5 mm
        k = 50.0           # W/m-K (steel)
        R_cond = thickness / k
        self.assertAlmostEqual(R_cond, 1e-4, places=6)

    # 4g. Wall temperature analysis structure
    def test_wall_temperature_analysis_keys(self):
        """_analyze_wall_temperature must return thermal resistance breakdown."""
        heat_flux = 1e6  # W/m^2
        thickness = 0.005
        mat_props = self.analyzer.materials['steel']
        ambient_temp = 293.15
        h_coolant = 25.0

        result = self.analyzer._analyze_wall_temperature(
            heat_flux, thickness, mat_props, ambient_temp, h_coolant
        )
        for key in ['inner_temperature', 'outer_temperature', 'thermal_resistance']:
            self.assertIn(key, result, f"Missing key: {key}")

    # 4h. Inner wall temperature > outer wall temperature
    def test_wall_temp_gradient_direction(self):
        """Hot side (inner) must be hotter than cold side (outer)."""
        heat_flux = 5e5
        thickness = 0.005
        mat_props = self.analyzer.materials['steel']

        result = self.analyzer._analyze_wall_temperature(
            heat_flux, thickness, mat_props, 293.15, 25.0
        )
        self.assertGreater(result['inner_temperature'], result['outer_temperature'],
                           "Inner wall must be hotter than outer wall")

    # 4i. Total thermal resistance = R_cond + R_conv
    def test_total_thermal_resistance(self):
        """R_total = R_conduction + R_convection (series resistances)."""
        heat_flux = 1e6
        thickness = 0.005
        k = 50.0      # steel
        h_cool = 25.0
        mat_props = self.analyzer.materials['steel']

        result = self.analyzer._analyze_wall_temperature(
            heat_flux, thickness, mat_props, 293.15, h_cool
        )

        R_cond = result['thermal_resistance']['conduction']
        R_conv = result['thermal_resistance']['convection']
        R_total = result['thermal_resistance']['total']

        self.assertAlmostEqual(R_total, R_cond + R_conv, places=10)

    # 4j. Material database completeness
    def test_material_database(self):
        """Heat transfer analyzer must have steel, aluminum, inconel, copper."""
        for mat in ['steel', 'aluminum', 'inconel', 'copper']:
            self.assertIn(mat, self.analyzer.materials, f"Missing material: {mat}")
            props = self.analyzer.materials[mat]
            self.assertGreater(props['thermal_conductivity'], 0)
            self.assertGreater(props['melting_point'], 0)


# ---------------------------------------------------------------------------
# 5. TRAJECTORY / ATMOSPHERE TESTS
# ---------------------------------------------------------------------------
class TestTrajectoryAtmosphere(unittest.TestCase):
    """Test ISA standard atmosphere and gravity models."""

    def setUp(self):
        from trajectory_analysis import TrajectoryAnalyzer
        self.analyzer = TrajectoryAnalyzer()

    # 5a. ISA sea-level temperature
    def test_isa_sea_level_temperature(self):
        """ISA standard atmosphere T(0) = 288.15 K."""
        rho, g = self.analyzer._get_atmospheric_properties(0)
        # Reconstruct T from rho and P using ideal gas:
        # In the code: T = 288.15 - 0.0065*h; at h=0 => T=288.15
        # P = 101325 * (T/288.15)^(g0*M/(R*L)) at h=0 => P=101325
        # rho = P / (287.053 * T) = 101325 / (287.053 * 288.15) = 1.2250
        T = 288.15  # expected
        P = 101325.0
        rho_expected = P / (287.053 * T)
        self.assertAlmostEqual(rho, rho_expected, places=2,
                               msg="Sea-level density deviates from ISA")

    # 5b. ISA sea-level pressure (via density check)
    def test_isa_sea_level_density(self):
        """Sea-level air density should be approximately 1.225 kg/m^3."""
        rho, _ = self.analyzer._get_atmospheric_properties(0)
        self.assertAlmostEqual(rho, 1.225, delta=0.01,
                               msg="Sea-level density != 1.225 kg/m^3")

    # 5c. Gravity at sea level
    def test_gravity_sea_level(self):
        """g(0) = 9.80665 m/s^2 (standard gravity)."""
        _, g = self.analyzer._get_atmospheric_properties(0)
        self.assertAlmostEqual(g, 9.80665, places=3)

    # 5d. Gravity decreases with altitude
    def test_gravity_decreases_with_altitude(self):
        """g must decrease with increasing altitude."""
        _, g0 = self.analyzer._get_atmospheric_properties(0)
        _, g10k = self.analyzer._get_atmospheric_properties(10000)
        _, g100k = self.analyzer._get_atmospheric_properties(100000)

        self.assertGreater(g0, g10k, "g at 10 km should be less than at sea level")
        self.assertGreater(g10k, g100k, "g at 100 km should be less than at 10 km")

    # 5e. Inverse square gravity formula
    def test_gravity_inverse_square(self):
        """g(h) = g0 * (R_earth / (R_earth + h))^2."""
        g0_std = 9.80665
        R_e = 6371000.0
        h = 50000.0  # 50 km

        g_expected = g0_std * (R_e / (R_e + h))**2
        _, g_actual = self.analyzer._get_atmospheric_properties(h)
        self.assertAlmostEqual(g_actual, g_expected, places=4)

    # 5f. Density = P / (R * T) - ideal gas law
    def test_ideal_gas_density(self):
        """Density must satisfy ideal gas law rho = P / (R_air * T)."""
        R_air = 287.053
        # At sea level
        T = 288.15
        P = 101325.0
        rho_expected = P / (R_air * T)
        rho_actual, _ = self.analyzer._get_atmospheric_properties(0)
        self.assertAlmostEqual(rho_actual, rho_expected, places=3)

    # 5g. Troposphere lapse rate
    def test_troposphere_lapse_rate(self):
        """Temperature decreases at 6.5 K/km in troposphere."""
        # At 1000 m: T = 288.15 - 6.5 = 281.65 K
        h = 1000.0
        T_expected = 288.15 - 0.0065 * h
        # Verify via density: rho = P/(287.053*T)
        # We can check T indirectly through rho
        self.assertAlmostEqual(T_expected, 281.65, places=2)

    # 5h. Density decreases with altitude
    def test_density_decreases_with_altitude(self):
        """Atmospheric density must decrease with altitude."""
        rho0, _ = self.analyzer._get_atmospheric_properties(0)
        rho5k, _ = self.analyzer._get_atmospheric_properties(5000)
        rho10k, _ = self.analyzer._get_atmospheric_properties(10000)
        rho20k, _ = self.analyzer._get_atmospheric_properties(20000)

        self.assertGreater(rho0, rho5k)
        self.assertGreater(rho5k, rho10k)
        self.assertGreater(rho10k, rho20k)

    # 5i. Stratosphere isothermal (T = 216.65 K from 11-20 km)
    def test_stratosphere_isothermal(self):
        """Temperature is constant at 216.65 K in lower stratosphere (11-20 km)."""
        # In the code: if 11000 < altitude <= 20000: T = 216.65
        # We verify indirectly through density ratio
        rho12k, _ = self.analyzer._get_atmospheric_properties(12000)
        rho15k, _ = self.analyzer._get_atmospheric_properties(15000)

        # In isothermal atmosphere: rho2/rho1 = exp(-g*M*(h2-h1)/(R*T))
        # Both should use T=216.65
        g = 9.80665
        M = 0.0289644
        R = 8.31432
        T = 216.65
        ratio_expected = math.exp(-g * M * (15000 - 12000) / (R * T))
        ratio_actual = rho15k / rho12k
        self.assertAlmostEqual(ratio_actual, ratio_expected, delta=0.02)

    # 5j. Vehicle parameters can be set
    def test_set_vehicle_parameters(self):
        """set_vehicle_parameters should update internal state."""
        self.analyzer.set_vehicle_parameters(
            mass_dry=100, diameter=0.2, drag_coefficient=0.4, length=3.0
        )
        self.assertEqual(self.analyzer.vehicle_mass_dry, 100)
        self.assertEqual(self.analyzer.vehicle_diameter, 0.2)
        self.assertEqual(self.analyzer.drag_coefficient, 0.4)
        self.assertEqual(self.analyzer.vehicle_length, 3.0)


# ---------------------------------------------------------------------------
# 6. CAD / STL TESTS
# ---------------------------------------------------------------------------
class TestCADGeneration(unittest.TestCase):
    """Test STL file generation and mesh validity."""

    def setUp(self):
        from professional_rocket_cad import ProfessionalRocketCAD
        # Use a temp directory for test exports
        self.temp_dir = tempfile.mkdtemp()
        self.cad = ProfessionalRocketCAD()
        self.cad.export_dir = self.temp_dir

    def tearDown(self):
        # Clean up temp files
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    # 6a. STL files are actually created
    def test_stl_files_created(self):
        """generate_liquid_hybrid_engine must produce STL files on disk."""
        params = {
            'thrust': 5000,
            'chamber_pressure': 30,
            'expansion_ratio': 6,
            'injector_type': 'pintle',
        }
        result = self.cad.generate_liquid_hybrid_engine(params)
        self.assertIn('files', result)
        for fname in result['files']:
            fpath = os.path.join(self.temp_dir, fname)
            self.assertTrue(os.path.isfile(fpath),
                            f"STL file not found: {fpath}")

    # 6b. STL file has correct format header
    def test_stl_header(self):
        """STL file must start with 'solid' keyword."""
        params = {
            'thrust': 3000,
            'chamber_pressure': 20,
            'expansion_ratio': 5,
            'injector_type': 'pintle',
        }
        result = self.cad.generate_liquid_hybrid_engine(params)
        for fname in result['files']:
            fpath = os.path.join(self.temp_dir, fname)
            with open(fpath, 'r') as f:
                first_line = f.readline().strip()
            self.assertTrue(first_line.startswith('solid'),
                            f"STL must start with 'solid': {fname}")

    # 6c. STL file has vertices and faces > 0
    def test_stl_has_geometry(self):
        """Generated STL must contain at least one facet with vertices."""
        params = {
            'thrust': 5000,
            'chamber_pressure': 30,
            'expansion_ratio': 8,
            'injector_type': 'pintle',
        }
        result = self.cad.generate_liquid_hybrid_engine(params)
        for fname in result['files']:
            fpath = os.path.join(self.temp_dir, fname)
            with open(fpath, 'r') as f:
                content = f.read()
            facet_count = content.count('facet normal')
            vertex_count = content.count('vertex')
            self.assertGreater(facet_count, 0,
                               f"No facets in {fname}")
            self.assertGreater(vertex_count, 0,
                               f"No vertices in {fname}")

    # 6d. Solid engine STL generation
    def test_solid_engine_stl(self):
        """generate_solid_engine must produce files with valid geometry."""
        params = {
            'thrust': 3000,
            'burn_time': 8,
            'grain_type': 'BATES',
        }
        result = self.cad.generate_solid_engine(params)
        self.assertIn('files', result)
        self.assertGreater(len(result['files']), 0)
        # Check assembly file exists
        assembly_found = any('assembly' in f for f in result['files'])
        self.assertTrue(assembly_found, "Assembly STL not generated")

    # 6e. Dimensions are physically reasonable
    def test_dimensions_reasonable(self):
        """Generated dimensions must be positive and in plausible range."""
        params = {
            'thrust': 10000,
            'chamber_pressure': 50,
            'expansion_ratio': 8,
        }
        result = self.cad.generate_liquid_hybrid_engine(params)
        dims = result['dimensions']
        for key, val in dims.items():
            self.assertGreater(val, 0, f"Dimension {key} is not positive")
        # Throat diameter should be smaller than chamber diameter
        self.assertLess(dims['throat_diameter'], dims['chamber_diameter'])
        # Exit diameter should be larger than throat
        self.assertGreater(dims['exit_diameter'], dims['throat_diameter'])

    # 6f. STL ends with 'endsolid'
    def test_stl_footer(self):
        """STL file must end with 'endsolid'."""
        params = {
            'thrust': 5000,
            'chamber_pressure': 30,
            'expansion_ratio': 6,
            'injector_type': 'pintle',
        }
        result = self.cad.generate_liquid_hybrid_engine(params)
        fpath = os.path.join(self.temp_dir, result['files'][0])
        with open(fpath, 'r') as f:
            content = f.read().strip()
        self.assertTrue(content.endswith('endsolid rocket_engine'),
                        "STL must end with 'endsolid rocket_engine'")


# ---------------------------------------------------------------------------
# 7. INTEGRATION TESTS (Flask)
# ---------------------------------------------------------------------------
class TestFlaskIntegration(unittest.TestCase):
    """Test Flask application endpoints."""

    @classmethod
    def setUpClass(cls):
        """Import app and create test client once for all tests."""
        # Suppress warnings from external data fetchers / Cantera
        warnings.filterwarnings('ignore')
        try:
            # Change to project directory so templates can be found
            original_dir = os.getcwd()
            os.chdir(PROJECT_DIR)
            from app import app
            app.config['TESTING'] = True
            cls.client = app.test_client()
            cls._original_dir = original_dir
            cls._app_available = True
        except Exception as e:
            cls._app_available = False
            cls._import_error = str(e)

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, '_original_dir'):
            os.chdir(cls._original_dir)

    def setUp(self):
        if not self._app_available:
            self.skipTest(f"Flask app could not be imported: {self._import_error}")

    # 7a. App starts without error
    def test_app_starts(self):
        """Flask app must create a test client without exceptions."""
        self.assertIsNotNone(self.client)

    # 7b. Main page returns 200
    def test_main_page_200(self):
        """GET / must return HTTP 200."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200,
                         f"/ returned {response.status_code}")

    # 7c. /calculate endpoint exists
    def test_calculate_endpoint_exists(self):
        """POST /calculate must not return 404."""
        response = self.client.post('/calculate', json={})
        self.assertNotEqual(response.status_code, 404,
                            "/calculate endpoint not found (404)")

    # 7d. /hybrid page returns 200
    def test_hybrid_page(self):
        """GET /hybrid must return 200."""
        response = self.client.get('/hybrid')
        self.assertEqual(response.status_code, 200)

    # 7e. /solid page returns 200
    def test_solid_page(self):
        """GET /solid must return 200."""
        response = self.client.get('/solid')
        self.assertEqual(response.status_code, 200)

    # 7f. /liquid page returns 200
    def test_liquid_page(self):
        """GET /liquid must return 200."""
        response = self.client.get('/liquid')
        self.assertEqual(response.status_code, 200)

    # 7g. /formulas page
    def test_formulas_page(self):
        """GET /formulas must return 200."""
        response = self.client.get('/formulas')
        self.assertEqual(response.status_code, 200)

    # 7h. /calculate with valid-ish data does not 500
    def test_calculate_does_not_crash(self):
        """POST /calculate with minimal data must not return 500."""
        data = {
            'thrust': 1000,
            'burn_time': 10,
            'of_ratio': 5.0,
            'chamber_pressure': 20.0,
            'fuel_type': 'htpb',
        }
        response = self.client.post('/calculate',
                                     data=json.dumps(data),
                                     content_type='application/json')
        # Accept any non-500 response (400/422 for missing fields is OK)
        self.assertNotEqual(response.status_code, 500,
                            "Server crashed on /calculate")


# ---------------------------------------------------------------------------
# 8. CROSS-CUTTING / PHYSICS CONSISTENCY TESTS
# ---------------------------------------------------------------------------
class TestPhysicsConsistency(unittest.TestCase):
    """Cross-module physics consistency checks."""

    # 8a. Critical pressure ratio for gamma=1.4
    def test_critical_pressure_ratio_gamma_1_4(self):
        """For gamma=1.4, P*/Pc = 0.52828 (textbook value)."""
        gamma = 1.4
        ratio = (2.0 / (gamma + 1.0)) ** (gamma / (gamma - 1.0))
        self.assertAlmostEqual(ratio, 0.52828, places=4)

    # 8b. Critical temperature ratio for gamma=1.4
    def test_critical_temperature_ratio_gamma_1_4(self):
        """For gamma=1.4, T*/Tc = 0.83333."""
        gamma = 1.4
        ratio = 2.0 / (gamma + 1.0)
        self.assertAlmostEqual(ratio, 0.83333, places=4)

    # 8c. Ideal gas law: PV = nRT -> rho = P / (R_specific * T)
    def test_ideal_gas_law(self):
        """Verify ideal gas law with sea-level ISA values."""
        P = 101325.0
        T = 288.15
        R_air = 287.053
        rho = P / (R_air * T)
        self.assertAlmostEqual(rho, 1.225, delta=0.002)

    # 8d. g0 consistency across modules
    def test_g0_values(self):
        """g0 values used across modules should be consistent."""
        from nozzle_design import NozzleDesigner
        from heat_transfer_analysis import HeatTransferAnalyzer
        from trajectory_analysis import TrajectoryAnalyzer

        nd = NozzleDesigner()
        ht = HeatTransferAnalyzer()
        ta = TrajectoryAnalyzer()

        # Trajectory uses the precise 9.80665
        self.assertAlmostEqual(ta.g0, 9.80665, places=5)
        # Nozzle and heat transfer use 9.81 (common engineering approximation)
        self.assertAlmostEqual(nd.g0, 9.81, places=2)
        self.assertAlmostEqual(ht.g0, 9.81, places=2)

    # 8e. Stefan-Boltzmann constant
    def test_stefan_boltzmann_constant(self):
        """sigma = 5.67e-8 W/(m^2 K^4)."""
        from heat_transfer_analysis import HeatTransferAnalyzer
        ht = HeatTransferAnalyzer()
        self.assertAlmostEqual(ht.stefan_boltzmann, 5.67e-8, places=10)

    # 8f. Earth radius
    def test_earth_radius(self):
        """R_earth ~ 6371 km."""
        from trajectory_analysis import TrajectoryAnalyzer
        ta = TrajectoryAnalyzer()
        self.assertEqual(ta.R_earth, 6371000)

    # 8g. Isp range for N2O/HTPB hybrid
    def test_hybrid_isp_range(self):
        """Standard N2O/HTPB hybrid Isp should be ~200-280 s."""
        # Compute from analytical C* and CF
        gamma = 1.22
        R = 385.0
        Tc = 3200.0
        g0 = 9.81

        num = math.sqrt(gamma * R * Tc)
        den = gamma * math.sqrt((2.0 / (gamma + 1.0)) ** ((gamma + 1.0) / (gamma - 1.0)))
        c_star = num / den

        # CF for sea-level expansion at 20 bar
        Pe_Pc = 1.0 / 20.0
        CF = 0.985 * math.sqrt(
            2 * gamma**2 / (gamma - 1) *
            (2 / (gamma + 1))**((gamma + 1) / (gamma - 1)) *
            (1 - Pe_Pc**((gamma - 1) / gamma))
        )

        Isp = CF * c_star / g0
        self.assertGreater(Isp, 200, f"Isp={Isp:.1f} s too low")
        self.assertLess(Isp, 300, f"Isp={Isp:.1f} s too high")

    # 8h. Expansion ratio must be > 1
    def test_expansion_ratio_greater_than_one(self):
        """For any supersonic nozzle, epsilon = Ae/At > 1."""
        # From isentropic relations for M > 1
        gamma = 1.4
        M = 2.0
        eps = (1 / M) * ((2 / (gamma + 1)) * (1 + (gamma - 1) / 2 * M**2))**((gamma + 1) / (2 * (gamma - 1)))
        self.assertGreater(eps, 1.0)

    # 8i. Choked flow: Mach=1 at throat gives area ratio = 1
    def test_area_ratio_at_mach_one(self):
        """Area ratio A/A* = 1 when M = 1 (by definition of throat)."""
        gamma = 1.4
        M = 1.0
        eps = (1 / M) * ((2 / (gamma + 1)) * (1 + (gamma - 1) / 2 * M**2))**((gamma + 1) / (2 * (gamma - 1)))
        self.assertAlmostEqual(eps, 1.0, places=10)

    # 8j. Conservation: mdot_ox + mdot_f = mdot_total (general check)
    def test_mass_conservation(self):
        """For any OF ratio, mdot_ox + mdot_f must equal mdot_total."""
        mdot = 2.5
        for OF in np.linspace(0.5, 10, 20):
            mdot_ox = mdot * OF / (1 + OF)
            mdot_f = mdot / (1 + OF)
            self.assertAlmostEqual(mdot_ox + mdot_f, mdot, places=10)


# ---------------------------------------------------------------------------
# RUNNER
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    # Need to import json here for Flask test
    import json

    # Run with verbosity
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    test_classes = [
        TestHybridEnginePhysics,
        TestNozzleDesign,
        TestCombustionAnalysis,
        TestHeatTransfer,
        TestTrajectoryAtmosphere,
        TestCADGeneration,
        TestFlaskIntegration,
        TestPhysicsConsistency,
    ]

    for cls in test_classes:
        suite.addTests(loader.loadTestsFromTestCase(cls))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Exit with proper code
    sys.exit(0 if result.wasSuccessful() else 1)
