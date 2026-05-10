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

| Tab | What it does |
|---|---|
| **RGB** | Build colours with R/G/B sliders, upload an image to see per-channel decomposition |
| **HSV** | Build colours in HSV, mask by hue range with colour presets and a hue reference strip, visualise hue instability |
| **YCbCr** | Build colours in YCbCr, see channel decomposition, suppress Cb/Cr to understand chroma contribution |
| **LAB** | Build colours in LAB, click an image to sample a point and see a ΔE perceptual distance heatmap |
| **Equation Demonstrator** | Pick an RGB colour and a target space — every conversion step is shown with its formula and computed value |

---

## Files

```
simulator/
├── app.py            # Main Streamlit application
├── utils.py          # Pure-NumPy colour space conversion functions (used by Equation Demonstrator)
├── requirements.txt  # Python dependencies
└── README.md         # This file
```
