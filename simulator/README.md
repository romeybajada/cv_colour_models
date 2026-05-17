# Colour Spaces Explorer — Simulator

Interactive Streamlit app for ARI 2129

---

## Requirements

- Python 3.10 or higher
- pip
- [Anaconda](https://www.anaconda.com/download) or Miniconda installed (Recommended)

---

## Setup

**1. Navigate to the simulator folder**

```bash
cd path/to/cv_colour_models/simulator
```

**2. (Recommended) Create and Activate a Conda environment**

```bash
conda create -n colour_spaces python=3.10 -y
conda activate colour_spaces
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

---

## Running the app

```bash
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`.

---

## Tabs

The interactive simulator is a Streamlit app covering all four colour spaces. Each tab lets you adjust parameters and see the visual output update in real time.

| Tab | What it covers |
|-----|----------------|
| **RGB** | Build colours with R/G/B sliders; upload an image to see per-channel decomposition and why brightness affects all three channels simultaneously |
| **HSV** | Build colours in HSV; mask by hue range with colour presets; visualise hue instability in low-saturation regions |
| **YCbCr** | Build colours in YCbCr; decompose channels; drag sliders to suppress Cb/Cr independently and see what each channel contributes |
| **LAB** | Build colours in LAB; upload an image and click any pixel to generate a ΔE perceptual-distance heatmap; compare Y vs L* luminance channels |
| **Equation Demonstrator** | Pick any RGB colour and a target space — every conversion step is shown with its formula and computed value, tracing the full pipeline |

---

## Files

``` bash
simulator/
├── app.py            # Main Streamlit application
├── utils.py          # Pure-NumPy colour space conversion functions (used by Equation Demonstrator)
├── requirements.txt  
└── README.md         
```
