"""
Colour Space Conversion Utilities

Step-by-step conversion traces for the Equation Demonstrator tab.
Single-pixel conversion functions for computing final results.
All single-pixel functions take float inputs normalised to [0, 1] for RGB.
"""

import numpy as np

# CONSTANTS
# YCbCr BT.601 coefficients (standard definition)
_KR_601 = 0.299
_KB_601 = 0.114

# YCbCr BT.709 coefficients (high definition)
_KR_709 = 0.2126
_KB_709 = 0.0722

# CIE standard illuminant D65 (the white point sRGB is defined against)
_D65_X = 0.95047
_D65_Y = 1.00000
_D65_Z = 1.08883

# sRGB → CIE XYZ linear transform matrix (IEC 61966-2-1)
_RGB_TO_XYZ = np.array([
    [0.4124564, 0.3575761, 0.1804375],
    [0.2126729, 0.7151522, 0.0721750],
    [0.0193339, 0.1191920, 0.9503041]
], dtype=np.float64)

# LAB epsilon and kappa (CIE 1976 standard)
_LAB_EPSILON = 0.008856   # (6/29)^3
_LAB_KAPPA   = 903.3      # (29/3)^3


# Convert a single RGB colour → HSV
def rgb_to_hsv(r: float, g: float, b: float) -> tuple[float, float, float]:
    cmax = max(r, g, b)
    cmin = min(r, g, b)
    chroma = cmax - cmin

    v = cmax
    s = 0.0 if cmax == 0.0 else chroma / cmax

    if chroma == 0.0:
        h = 0.0
    elif cmax == r:
        h = 60.0 * (((g - b) / chroma) % 6)
    elif cmax == g:
        h = 60.0 * ((b - r) / chroma + 2.0)
    else:
        h = 60.0 * ((r - g) / chroma + 4.0)

    return h, s, v


# Convert a single RGB colour → YCbCr
def rgb_to_ycbcr(r: float, g: float, b: float, standard: str = "BT.601") -> tuple[float, float, float]:
    R = r * 255.0
    G = g * 255.0
    B = b * 255.0

    if standard == "BT.601":
        y  =  0.299  * R + 0.587  * G + 0.114  * B + 16
        cb = -0.1687 * R - 0.3313 * G + 0.500  * B + 128
        cr =  0.500  * R - 0.4187 * G - 0.0813 * B + 128
    else:  # BT.709
        y  =  0.2126 * R + 0.7152 * G + 0.0722 * B + 16
        cb = -0.1146 * R - 0.3854 * G + 0.500  * B + 128
        cr =  0.500  * R - 0.4542 * G - 0.0458 * B + 128

    return y, cb, cr


# Apply sRGB gamma linearisation to a single channel
def _srgb_to_linear(c: float) -> float:

    if c <= 0.04045:
        return c / 12.92
    return ((c + 0.055) / 1.055) ** 2.4

# CIE LAB cube-root compression
def _f_lab(t: float) -> float:
    if t > _LAB_EPSILON:
        return t ** (1.0 / 3.0)
    return (_LAB_KAPPA * t + 16.0) / 116.0


# Convert a single sRGB colour → CIE L*a*b*
def rgb_to_lab(r: float, g: float, b: float) -> tuple[float, float, float]:
    r_lin = _srgb_to_linear(r)
    g_lin = _srgb_to_linear(g)
    b_lin = _srgb_to_linear(b)

    rgb_lin = np.array([r_lin, g_lin, b_lin])
    xyz = _RGB_TO_XYZ @ rgb_lin

    xn = xyz[0] / _D65_X
    yn = xyz[1] / _D65_Y
    zn = xyz[2] / _D65_Z

    fx = _f_lab(xn)
    fy = _f_lab(yn)
    fz = _f_lab(zn)

    L  = 116.0 * fy - 16.0
    a  = 500.0 * (fx - fy)
    b_ = 200.0 * (fy - fz)

    return L, a, b_


# Step-by-step conversion traces for the Equation Demonstrator tab

# Return RGB → HSV conversion as an ordered list of steps
def rgb_to_hsv_steps(r: float, g: float, b: float) -> list[dict]:
    cmax = max(r, g, b)
    cmin = min(r, g, b)
    chroma = cmax - cmin
    dominant = "R" if cmax == r else ("G" if cmax == g else "B")

    h, s, v = rgb_to_hsv(r, g, b)

    return [
        {"step": "Inputs",    "formula": "R, G, B",                          "value": f"{r:.3f}, {g:.3f}, {b:.3f}"},
        {"step": "V (Value)", "formula": "V = max(R, G, B)",                  "value": f"{v:.4f}"},
        {"step": "Cmin",      "formula": "Cmin = min(R, G, B)",               "value": f"{cmin:.4f}"},
        {"step": "C (Chroma)","formula": "C = V − Cmin",                      "value": f"{chroma:.4f}"},
        {"step": "S (Sat.)",  "formula": "S = C / V  (0 if V=0)",             "value": f"{s:.4f}"},
        {"step": "Dominant",  "formula": "Which primary = V?",                "value": dominant},
        {"step": "H (Hue)",   "formula": "H = 60 × sector formula (degrees)", "value": f"{h:.2f}°"},
    ]


# Return RGB → YCbCr conversion as step-by-step trace
def rgb_to_ycbcr_steps(r: float, g: float, b: float, standard: str = "BT.601") -> list[dict]:
    R, G, B = r * 255.0, g * 255.0, b * 255.0
    y, cb, cr = rgb_to_ycbcr(r, g, b, standard)

    return [
        {"step": "Inputs",    "formula": "R, G, B (scaled to 0–255)",                    "value": f"{R:.1f}, {G:.1f}, {B:.1f}"},
        {"step": "Y (Luma)",  "formula": "Y = 0.299R + 0.587G + 0.114B + 16",            "value": f"{y:.4f}"},
        {"step": "Cb",        "formula": "Cb = -0.1687R - 0.3313G + 0.500B + 128",       "value": f"{cb:.4f}"},
        {"step": "Cr",        "formula": "Cr = 0.500R - 0.4187G - 0.0813B + 128",        "value": f"{cr:.4f}"},
        {"step": "Note",      "formula": "Cb=Cr=128 when R=G=B (neutral grey)",          "value": f"Cb={cb:.1f}, Cr={cr:.1f}"},
    ]


# Return RGB → LAB conversion as step-by-step trace
def rgb_to_lab_steps(r: float, g: float, b: float) -> list[dict]:
    r_lin = _srgb_to_linear(r)
    g_lin = _srgb_to_linear(g)
    b_lin = _srgb_to_linear(b)

    rgb_lin = np.array([r_lin, g_lin, b_lin])
    xyz = _RGB_TO_XYZ @ rgb_lin

    xn, yn, zn = xyz[0] / _D65_X, xyz[1] / _D65_Y, xyz[2] / _D65_Z
    fx, fy, fz = _f_lab(xn), _f_lab(yn), _f_lab(zn)
    L, a, b_ = rgb_to_lab(r, g, b)

    return [
        {"step": "Inputs",          "formula": "R, G, B (sRGB)",                         "value": f"{r:.3f}, {g:.3f}, {b:.3f}"},
        {"step": "Linearise",       "formula": "Remove sRGB gamma (piecewise)",           "value": f"{r_lin:.4f}, {g_lin:.4f}, {b_lin:.4f}"},
        {"step": "→ XYZ",           "formula": "XYZ = M_rgb2xyz × [R_lin G_lin B_lin]ᵀ", "value": f"X={xyz[0]:.4f}, Y={xyz[1]:.4f}, Z={xyz[2]:.4f}"},
        {"step": "Normalise (D65)", "formula": "xn=X/Xn, yn=Y/Yn, zn=Z/Zn",             "value": f"{xn:.4f}, {yn:.4f}, {zn:.4f}"},
        {"step": "f(t)",            "formula": "Cube-root compression (CIE 1976)",        "value": f"f(xn)={fx:.4f}, f(yn)={fy:.4f}, f(zn)={fz:.4f}"},
        {"step": "L*",              "formula": "L* = 116·f(yn) − 16",                    "value": f"{L:.3f}"},
        {"step": "a*",              "formula": "a* = 500·(f(xn) − f(yn))",               "value": f"{a:.3f}"},
        {"step": "b*",              "formula": "b* = 200·(f(yn) − f(zn))",               "value": f"{b_:.3f}"},
    ]
