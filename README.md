<p align="center">
  <h1 align="center">HRMA — Hybrid Rocket Motor Analysis</h1>
  <p align="center">
    <strong>Web-based rocket motor design and analysis platform</strong><br>
    Hybrid, solid, and liquid propulsion systems
  </p>
  <p align="center">
    <img src="https://img.shields.io/badge/Python-3.8+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python">
    <img src="https://img.shields.io/badge/Flask-Web_App-000?style=flat-square&logo=flask" alt="Flask">
    <img src="https://img.shields.io/badge/Tests-73_passing-00C853?style=flat-square" alt="Tests">
    <img src="https://img.shields.io/badge/License-Educational-blue?style=flat-square" alt="License">
  </p>
</p>

---

A comprehensive rocket propulsion analysis tool with real-time interactive visualizations, 3D CAD model generation (STL export), and physics-validated engineering calculations.

## Features

### Engine Types

| Type | Fuels | Oxidizers | Capabilities |
|------|-------|-----------|-------------|
| **Hybrid** | HTPB, Paraffin, ABS, PMMA | N2O, LOX, H2O2 | Regression rate, grain geometry, injector design |
| **Solid** | APCP, Black powder, Sugar | — | BATES/Star/Wagon grain, burn rate curves |
| **Liquid** | RP-1, LH2 | LOX | Regenerative cooling, turbopump/pressure-fed |

### Analysis Modules

| Module | What It Computes |
|--------|-----------------|
| **Combustion** | Flame temperature, species composition, stoichiometric O/F, c* |
| **Nozzle Design** | Throat/exit sizing, bell/conical contours, Mach number (Newton-Raphson solver) |
| **Heat Transfer** | Bartz correlation for gas-side h_g, thermal resistance network, wall temperatures |
| **Trajectory** | ISA atmosphere, gravity model, powered/coasting/descent phases, drag |
| **Structural** | Chamber stress, safety factors, material selection |
| **CFD** | Flow field visualization, pressure/temperature distributions |
| **CAD** | 3D STL export — chamber, nozzle, injector, fuel grain, full assembly |

### Key Physics

- **Thrust:** F = mdot * Ve + (Pe - Pa) * Ae (momentum + pressure thrust)
- **Isp:** CF * c* / g0, with validated c* from thermochemistry
- **Nozzle flow:** Isentropic relations with Newton-Raphson area-Mach solver
- **Heat transfer:** Bartz correlation (primary) with Dittus-Boelter fallback
- **Regression rate:** Marxman/Altman model: r_dot = a * G_ox^n
- **Atmosphere:** ISA standard (troposphere lapse + stratosphere exponential)

## Quick Start

```bash
# Clone
git clone https://github.com/berketez/HRMA-Hybrit-Rocket-Motor-Analysis-Program.git
cd HRMA-Hybrit-Rocket-Motor-Analysis-Program

# Install dependencies
pip install -r requirements.txt

# Run
python app.py

# Open browser → http://localhost:5000
```

## Testing

```bash
# Run all 73 tests
python -m pytest tests.py -v

# Test categories:
#   - Engine physics (Isp, thrust, throat sizing, O/F split)
#   - Nozzle design (isentropic relations, bell geometry)
#   - Combustion (stoichiometry, exit temperature)
#   - Heat transfer (Re, Pr, Nu, thermal resistance)
#   - Trajectory (ISA atmosphere, gravity model)
#   - CAD generation (STL file creation, mesh validation)
#   - Flask integration (routes, endpoints)
#   - Physics consistency (reference values, conservation laws)
```

## Architecture

```
app.py (Flask)
  │
  ├── hybrid_rocket_engine.py     Engine simulation & grain design
  ├── solid_rocket_engine.py      Solid motor burn analysis
  ├── liquid_rocket_engine.py     Liquid engine cycle analysis
  │
  ├── combustion_analysis.py      Thermochemistry & flame temperature
  ├── nozzle_design.py            Nozzle sizing & flow properties
  ├── heat_transfer_analysis.py   Bartz correlation, thermal network
  ├── structural_analysis.py      Chamber stress & safety factors
  ├── trajectory_analysis.py      Flight simulation with ISA atmosphere
  ├── cfd_analysis.py             Flow field computation
  │
  ├── cad_design.py               3D motor assembly (trimesh + plotly)
  ├── cad_generator.py            Tank CAD generation
  ├── detailed_cad_generator.py   Component-level CAD
  │
  ├── templates/                  HTML (index, hybrid, solid, liquid)
  ├── static/                     CSS, JS
  └── tests.py                    73 unit tests
```

## CAD Export

The platform generates STL files for all motor components:

```
cad_exports/
  ├── liquid_hybrid_assembly.stl    Full motor assembly
  ├── liquid_hybrid_chamber.stl     Combustion chamber (watertight)
  ├── liquid_hybrid_nozzle.stl      Convergent-divergent nozzle
  ├── liquid_hybrid_injector.stl    Injector head
  └── ...
```

STL files are compatible with Fusion 360, SolidWorks, FreeCAD, and 3D printers.

## Requirements

- Python 3.8+
- Flask, NumPy, SciPy, Matplotlib, Plotly
- trimesh (for CAD/STL export)
- Optional: CoolProp, Cantera (for advanced thermochemistry)

## Authors

- **Berke Tezgöçen** — Development
- **Ayberk Cem Aksoy** — Idea & Testing

## License

Educational and research use. Free for academic research and amateur rocketry.
