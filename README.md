# 🚀 UZAYTEK Motor Analysis Tool

Modern web-based rocket motor design and analysis platform supporting hybrid, solid, and liquid propulsion systems.

## 🎯 Quick Start

### For macOS Users:

1. **Download & Extract** the ZIP file to your Desktop
2. **Open Terminal** (press `Cmd + Space`, type "Terminal")
3. **Navigate to folder:**
   ```bash
   cd ~/Desktop/HRMA
   ```
4. **Run the application:**
   ```bash
   python3 app.py
   ```
5. **Open browser** and go to: `http://localhost:5000`

### For Windows/Linux Users:

1. **Download & Extract** the ZIP file
2. **Open Command Prompt/Terminal** in the extracted folder
3. **Run:**
   ```bash
   python app.py
   ```
4. **Open browser** and go to: `http://localhost:5000`

## 📋 Requirements

- **Python 3.7+** (comes pre-installed on macOS 10.15+)
- **Web Browser** (Chrome, Firefox, Safari, Edge)
- **Internet connection** (for first-time package installation)

### Check Python Version:
```bash
python3 --version
```

### Install Python (if needed):
- **macOS**: `brew install python3` or download from [python.org](https://python.org)
- **Windows**: Download from [python.org](https://python.org)
- **Linux**: `sudo apt install python3` (Ubuntu/Debian)

## 🛠️ Features

### 🔥 Hybrid Rocket Motors
- **Advanced Analysis**: Parametric analysis, trajectory analysis
- **Altitude Profiles**: Performance vs altitude calculations
- **Total Impulse Design**: Thrust and burn time optimization
- **Fuel Options**: HTPB, Paraffin, ABS, PMMA
- **Oxidizers**: N2O, LOX, H2O2
- **Injector Design**: Showerhead, pintle, swirl injectors

### 🧨 Solid Rocket Motors  
- **Grain Geometries**: BATES, Star, Wagon wheel, End burner
- **Propellants**: APCP, Black powder, Sugar propellants
- **Burn Rate Analysis**: Progressive/regressive thrust curves
- **Nozzle Design**: Conical and bell nozzles

### 💧 Liquid Rocket Motors
- **Propellant Combinations**: LOX/RP-1, LOX/LH2, Hypergolics
- **Cooling Systems**: Regenerative cooling design
- **Feed Systems**: Turbopump and pressure-fed systems
- **Combustion Analysis**: Injector and combustion chamber design

### 📊 Advanced Analysis Tools
- **Interactive Visualizations**: Real-time plots with Plotly
- **3D CAD Integration**: Motor geometry visualization
- **Trajectory Analysis**: Flight performance prediction
- **Parametric Studies**: Multi-variable optimization
- **Export Functions**: PDF reports and data export

## 🏗️ Project Structure

```
HRMA/
├── app.py                    # Main Flask application
├── hybrid_rocket_engine.py   # Hybrid motor calculations
├── solid_rocket_engine.py    # Solid motor calculations  
├── liquid_rocket_engine.py   # Liquid motor calculations
├── trajectory_analysis.py    # Flight trajectory analysis
├── combustion_analysis.py    # Combustion calculations
├── nozzle_design.py         # Nozzle design tools
├── injector_design.py       # Injector optimization
├── structural_analysis.py   # Structural calculations
├── heat_transfer_analysis.py # Thermal analysis
├── cad_design.py           # 3D CAD integration
├── visualization.py        # Plotting and graphics
├── templates/              # HTML templates
│   ├── index.html         # Main page
│   ├── advanced.html      # Hybrid motor interface
│   ├── solid.html         # Solid motor interface
│   └── liquid.html        # Liquid motor interface
├── static/                # CSS, JS, images
│   ├── css/
│   └── js/
└── README.md              # This file
```

## 🎮 How to Use

### 1. Select Motor Type
- **Hybrid Motors**: Click "Design Hybrid Motor" 
- **Solid Motors**: Click "Design Solid Motor"
- **Liquid Motors**: Click "Design Liquid Motor"

### 2. Enter Parameters
- **Basic**: Thrust, burn time, chamber pressure
- **Propellants**: Select fuel and oxidizer types
- **Geometry**: Chamber dimensions, nozzle sizing
- **Advanced**: O/F ratio, combustion efficiency, etc.

### 3. Run Analysis
- **Single Point**: Basic motor design
- **Parametric Analysis**: Multi-variable studies  
- **Trajectory Analysis**: Flight performance
- **Altitude Profile**: Performance vs altitude

### 4. View Results
- **Performance Metrics**: Isp, thrust, burn time
- **Geometry**: Chamber, throat, and nozzle dimensions
- **Plots**: Interactive charts and visualizations
- **3D Models**: Motor cross-sections and geometry

### 5. Export Data
- **PDF Reports**: Complete design documentation
- **CSV Data**: Raw calculation results
- **3D CAD**: STP files for CAD software

## 🔧 Troubleshooting

### Common Issues:

**"Command not found: python3"**
```bash
# Try these alternatives:
python app.py
py app.py
python3.9 app.py
```

**"Module not found" errors**
```bash
# Install required packages:
pip3 install flask numpy scipy matplotlib plotly
```

**"Port already in use"**
- Close other applications using port 5000
- Or change port in `app.py`: `app.run(port=5001)`

**Browser doesn't open automatically**
- Manually open: `http://localhost:5000`
- Check firewall settings
- Try different browser

### Performance Tips:
- Use Chrome or Firefox for best performance
- Close other browser tabs during analysis
- Restart application if it becomes slow

## 📚 Technical Details

### Calculation Methods:
- **Hybrid Motors**: Karabeyoglu regression models
- **Solid Motors**: Saint-Robert's burn rate law  
- **Liquid Motors**: NASA design methodologies
- **Nozzle Design**: Method of characteristics
- **Thermodynamics**: NASA CEA integration

### Validation:
- Compared against experimental data
- Industry standard calculation methods
- Academic literature validation
- Real-world motor test data

### Accuracy:
- ±5% for well-characterized propellants
- ±10% for experimental combinations
- Suitable for preliminary design
- Not for final certification

## 🆘 Getting Help

1. **Check console output** for error messages
2. **Verify all files** are in the same folder
3. **Update Python** to latest version
4. **Try different browser** if interface issues
5. **Restart application** if calculations freeze

## 📄 License

**Educational and Research Use**
- Free for academic research
- Free for amateur rocketry
- Contact for commercial licensing

## 🚀 Version

**UZAYTEK Motor Analysis v1.1**
- Developed by: Berke Tezgöçen
- Idea & Testing: Ayberk Cem Aksoy
- Professional Rocket Propulsion Design Tool
- Last Updated: 2025

---

## 🎯 Ready to Design?

1. **Extract ZIP file**
2. **Open Terminal in folder**  
3. **Run: `python3 app.py`**
4. **Open: `http://localhost:5000`**
5. **Start designing rockets! 🚀**

*For advanced usage and detailed documentation, explore the application interface.*
