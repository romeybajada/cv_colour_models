# Colour Models and Colour Spaces
**ARI 2129 — Principles of Computer Vision for AI**

**Group Members:  Romey Bajada, Mia Busuttil, Julia-Kay Gutiza, Rebecca Hayward, Kyra Talbot**

Block 1 — Image Data: Colour Models and Colour Spaces

A Computer Vision Learning Pack on colour models and colour spaces: RGB, HSV, YCbCr, and CIELAB — covering conversion equations, the purpose of each space, and what breaks when you use the wrong one.

---

## Repository Structure

``` bash
/
├── README.md
├── requirements.txt
├── study_notes.docx
├── study_notes.pdf
├── quiz_with_rationale.docx
├── quiz_with_rationale.pdf
├── quiz_link.txt
├── slides.pptx
├── slides.pdf
├── walkthrough/
│   ├── walkthrough.ipynb
│   ├── test_image.png      # demo image for notebook
│   ├── tulip.png           # demo image
│   └── people.png          # demo image
├── ai_journal.pdf
├── simulator/
│   ├── app.py
│   ├── utils.py            # util functions seperated to keep app.py clean
│   ├── requirements.txt
│   └── README.md
└── further_reading/
    └── *.pdf
```

---

## Quickstart

### 1. Clone the repository

```bash
git clone https://github.com/romeybajada/cv_colour_models.git
cd cv_colour_models
```

### 2. (Recommended) Create a virtual environment

**Conda:**
```bash
conda create -n colour_spaces python=3.10 -y
conda activate colour_spaces
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Launch the simulator

```bash
streamlit run simulator/app.py
```

The app opens automatically at `http://localhost:8501`.

---

## Simulator

The interactive simulator is a Streamlit app covering all four colour spaces. Each tab lets you adjust parameters and see the visual output update in real time.

| Tab | What it covers |
|-----|----------------|
| **RGB** | Build colours with R/G/B sliders; upload an image to see per-channel decomposition and why brightness affects all three channels simultaneously |
| **HSV** | Build colours in HSV; mask by hue range with colour presets; visualise hue instability in low-saturation regions |
| **YCbCr** | Build colours in YCbCr; decompose channels; drag sliders to suppress Cb/Cr independently and see what each channel contributes |
| **LAB** | Build colours in LAB; upload an image and click any pixel to generate a ΔE perceptual-distance heatmap; compare Y vs L* luminance channels |
| **Equation Demonstrator** | Pick any RGB colour and a target space — every conversion step is shown with its formula and computed value, tracing the full pipeline |

---

## Annotated Code Walkthrough

The notebook walks through the full colour-space pipeline in a tutorial style, with code and explanation interleaved.

**Launch:**
```bash
jupyter notebook walkthrough.ipynb
```

**Sections covered:**

1. **RGB** — channel splitting, BGR/RGB ordering in OpenCV, and why RGB struggles with colour-based segmentation
2. **HSV** — channel decomposition, OpenCV-specific range differences (H 0–180, cylinder vs cone), colour masking, hue instability at low saturation
3. **YCbCr** — channel decomposition, chroma subsampling (4:2:0 and extreme), skin detection, colour cast from mismatched BT standards
4. **LAB** — channel splitting, OpenCV encoding/decoding, perceptual uniformity demonstration, ΔE calculation and heatmap, LAB-based vs RGB-based image enhancement
5. **Conversions** — manual NumPy implementations of all six conversions (RGB↔HSV, RGB↔YCbCr, RGB↔LAB) with round-trip verification and common error demonstrations

---

## Deliverables

| # | Component | File(s) |
|---|-----------|---------|
| 1 | Study Notes + Quick Reference + Key Papers | `study_notes.docx`, `study_notes.pdf` |
| 2 | Adversarial Quiz | `quiz_with_rationale.docx`, `quiz_with_rationale.pdf`, `quiz_link.txt` |
| 3 | Presentation Slides | `slides.pptx`, `slides.pdf` |
| 4 | Interactive Simulator | `simulator/` |
| 5 | Annotated Code Walkthrough | `walkthrough.ipynb` |
| 6 | AI Usage Journal | `ai_journal.pdf` |

The quiz is hosted on Google Forms: https://forms.gle/ZRaviPxEhH172LhS9

Further reading papers are in `further_reading/` with citations and summaries in `study_notes.pdf`.

---

## Team Workflow

Work was split along two axes: each member owned one **deliverable** end-to-end, and one **colour space** (or the conversion functions) whose content they were responsible for across all deliverables.

| Member | Topic | Deliverable |
|--------|----------------------|-------------|
| Romey Bajada | HSV | Simulator |
| Mia Busuttil | RGB | Study Notes |
| Julia-Kay Gutiza | Conversion Functions | Annotated Code Walkthrough |
| Kyra Talbot | YCbCr | Adversarial Quiz |
| Rebecca Hayward | LAB | Presentation Slides |

**Collaboration tools:**
- **Google Docs** — drafting the study notes and quiz questions collaboratively 
- **Google Slides** — building the presentation
- **This repository** — all code (simulator and walkthrough notebook)

The colour space assignment meant that, for example, the person responsible for YCbCr wrote that section of the study notes and the presentation, covered it in the walkthrough, set quiz questions on it and contributed the YCbCr tab of the simulator — keeping the content consistent across deliverables.
