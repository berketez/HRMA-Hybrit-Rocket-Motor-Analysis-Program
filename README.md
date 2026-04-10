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
    <img src="https://img.shields.io/badge/CAD-STL_Export-FF6B35?style=flat-square" alt="CAD">
    <img src="https://img.shields.io/badge/License-Educational-blue?style=flat-square" alt="License">
  </p>
</p>

---

A comprehensive rocket propulsion analysis tool with real-time interactive visualizations, 3D CAD model generation (STL export), and physics-validated engineering calculations.

```
       ╔══════════════════════════════════════════════════════╗
       ║                                                      ║
       ║    Injector   ┌──────────────┐   Convergent          ║
       ║    ████████   │              │   Section    ╲        ║
       ║    ████████   │  Combustion  │              ─╲       ║
       ║    ████████   │   Chamber    │   Throat      ─╱      ║
       ║    ████████   │              │              ╱        ║
       ║    ████████   └──────────────┘   Divergent           ║
       ║                                  Nozzle              ║
       ║   Oxidizer     Fuel Grain         Exit               ║
       ║    Feed        (HTPB/Wax)        Plane               ║
       ╚══════════════════════════════════════════════════════╝
                    F = mdot * Ve + (Pe - Pa) * Ae
```

## Engine Types

| Type | Fuels | Oxidizers | Capabilities |
|:----:|:------|:----------|:------------|
| **Hybrid** | HTPB, Paraffin, ABS, PMMA | N2O, LOX, H2O2 | Regression rate, grain geometry, injector design |
| **Solid** | APCP, Black powder, Sugar | — | BATES / Star / Wagon grain, burn rate curves |
| **Liquid** | RP-1, LH2 | LOX | Regenerative cooling, turbopump / pressure-fed |

## Analysis Modules

| Module | What It Computes |
|:------:|:----------------|
| **Combustion** | Flame temperature, species composition, stoichiometric O/F, characteristic velocity c* |
| **Nozzle Design** | Throat/exit sizing, bell/conical contours, Mach number (Newton-Raphson solver) |
| **Heat Transfer** | Bartz correlation for gas-side h_g, thermal resistance network, wall temperatures |
| **Trajectory** | ISA atmosphere, gravity model, powered / coasting / descent phases, drag |
| **Structural** | Chamber stress, safety factors, material selection |
| **CFD** | Flow field visualization, pressure / temperature distributions |
| **CAD Export** | 3D STL generation — chamber, nozzle, injector, fuel grain, full assembly |

## Key Physics

```
Thrust          F  = mdot * Ve + (Pe - Pa) * Ae
Specific Imp.   Isp = CF * c* / g0
Nozzle Flow     A/A* = f(M, gamma)  →  Newton-Raphson solver
Heat Transfer   h_g  = Bartz correlation (primary) | Dittus-Boelter (fallback)
Regression      r_dot = a * G_ox^n   (Marxman / Altman model)
Atmosphere      ISA standard: troposphere lapse + stratosphere exponential
```

## Quick Start

```bash
# Clone
git clone https://github.com/berketez/HRMA-Hybrit-Rocket-Motor-Analysis-Program.git
cd HRMA-Hybrit-Rocket-Motor-Analysis-Program

# Install dependencies
pip install -r requirements.txt

# Launch
python app.py
```

Then open **http://localhost:5000** in your browser.

## Testing

73 tests covering engine physics, nozzle design, combustion, heat transfer, trajectory, CAD generation, Flask integration, and physics consistency:

```bash
python -m pytest tests.py -v
```

```
============================= 73 passed in 11s ==============================
```

| Test Suite | Count | Verifies |
|:----------:|:-----:|:---------|
| Engine Physics | 10 | Isp, thrust, throat sizing, O/F split, regression rate |
| Nozzle Design | 9 | Isentropic relations, bell geometry, flow properties |
| Combustion | 10 | Stoichiometry, exit temperature, species |
| Heat Transfer | 10 | Re, Pr, Nu, Bartz, thermal resistance |
| Trajectory | 10 | ISA atmosphere, gravity model, density |
| CAD Generation | 6 | STL creation, mesh validation, dimensions |
| Flask Integration | 8 | Routes, endpoints, error handling |
| Physics Consistency | 10 | Reference values, conservation laws |

## Architecture

```
app.py (Flask)
  │
  ├─── Engine Simulation ──────────────────────────────────
  │    ├── hybrid_rocket_engine.py     Hybrid motor + grain design
  │    ├── solid_rocket_engine.py      Solid motor burn analysis
  │    └── liquid_rocket_engine.py     Liquid engine cycle analysis
  │
  ├─── Analysis Modules ───────────────────────────────────
  │    ├── combustion_analysis.py      Thermochemistry + flame temp
  │    ├── nozzle_design.py            Nozzle sizing + flow properties
  │    ├── heat_transfer_analysis.py   Bartz + thermal network
  │    ├── structural_analysis.py      Chamber stress + safety
  │    ├── trajectory_analysis.py      Flight sim + ISA atmosphere
  │    └── cfd_analysis.py             Flow field computation
  │
  ├─── CAD / Export ───────────────────────────────────────
  │    ├── cad_design.py               3D assembly (trimesh + plotly)
  │    ├── cad_generator.py            Tank CAD generation
  │    └── detailed_cad_generator.py   Component-level CAD
  │
  ├─── Web Interface ──────────────────────────────────────
  │    ├── templates/                  HTML pages
  │    └── static/                     CSS, JS, assets
  │
  └─── tests.py                        73 unit tests
```

## CAD Export

The platform generates production-ready STL files:

```
cad_exports/
  ├── liquid_hybrid_assembly.stl      Full motor assembly
  ├── liquid_hybrid_chamber.stl       Combustion chamber (watertight, 3D-print ready)
  ├── liquid_hybrid_nozzle.stl        Convergent-divergent nozzle
  ├── liquid_hybrid_injector.stl      Injector head
  ├── liquid_hybrid_gimbal.stl        Gimbal mount
  └── ...
```

Compatible with **Fusion 360**, **SolidWorks**, **FreeCAD**, and 3D printers.

## Requirements

| Package | Purpose |
|:--------|:--------|
| Flask | Web application server |
| NumPy, SciPy | Numerical computation |
| Matplotlib, Plotly | Visualization |
| trimesh | 3D mesh / STL generation |
| CoolProp *(optional)* | Fluid properties |
| Cantera *(optional)* | Advanced thermochemistry |

## Version

**HRMA v2.0** — Professional Rocket Propulsion Design Tool

| | |
|:--|:--|
| **Developed by** | Berke Tezgocen |
| **Idea & Testing** | Ayberk Cem Aksoy |
| **Last Updated** | 2026 |

## License

Educational and research use. Free for academic research and amateur rocketry.

---

<p align="center">
  <strong>Ready to Design?</strong><br><br>
  <code>git clone</code> &rarr; <code>pip install -r requirements.txt</code> &rarr; <code>python app.py</code> &rarr; <a href="http://localhost:5000">localhost:5000</a><br><br>
  <strong>Start designing rockets!</strong>
</p>
