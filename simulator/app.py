"""
Colour Models and Colour Spaces — Interactive Simulator
ARI 2129 | Group 1

Run with:
    streamlit run app.py
"""

import base64
import io
import os
import sys

import cv2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from PIL import Image
from streamlit_image_coordinates import streamlit_image_coordinates

# 
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import (
    rgb_to_hsv as _utils_hsv,
    rgb_to_ycbcr as _utils_ycbcr,
    rgb_to_lab as _utils_lab,
    rgb_to_hsv_steps,
    rgb_to_ycbcr_steps,
    rgb_to_lab_steps,
)

# Page Config
st.set_page_config(
    page_title="Colour Spaces Explorer",
    page_icon="🎨",
    layout="wide",
)


# Global Styles — light theme
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
h1, h2, h3 { font-family: 'Space Mono', monospace !important; }
.block-container { padding-top: 2rem; padding-bottom: 2rem; }

.stTabs [data-baseweb="tab-list"] {
    gap: 2px; background: #f0f0f0; border-radius: 8px; padding: 4px;
    width: fit-content;
}
.stTabs [data-baseweb="tab"] {
    background: transparent; border-radius: 6px; color: #666;
    font-family: 'Space Mono', monospace; font-size: 0.8rem; padding: 8px 16px;
}
.stTabs [aria-selected="true"] { background: #ffffff !important; color: #111 !important; }

.info-box {
    background: #f0faf8; border-left: 3px solid #00a893;
    border-radius: 0 8px 8px 0; padding: 1rem 1.2rem; margin: 1rem 0;
    font-size: 0.9rem; color: #333;
}
.warn-box {
    background: #fff5f0; border-left: 3px solid #ff6b35;
    border-radius: 0 8px 8px 0; padding: 1rem 1.2rem; margin: 1rem 0;
    font-size: 0.9rem; color: #333;
}
.metric-pill {
    display: inline-block; background: #e8f5f2; border-radius: 20px;
    padding: 4px 14px; font-family: 'Space Mono', monospace;
    font-size: 0.8rem; color: #007a6b; margin: 2px;
}
.section-label {
    font-family: 'Space Mono', monospace; font-size: 0.7rem;
    letter-spacing: 0.15em; color: #999; text-transform: uppercase;
    margin-bottom: 0.5rem;
}
div[data-baseweb="select"] > div:focus-within,
div[data-baseweb="select"] > div[aria-expanded="true"] {
    border-color: #00a893 !important;
    box-shadow: 0 0 0 1px #00a893 !important;
}
</style>
""", unsafe_allow_html=True)


# Shared Utilities

# Return an RGB uint8 numpy array from a Streamlit uploaded file
def load_image(upload) -> np.ndarray:
    return np.array(Image.open(upload).convert("RGB"))


# Four-panel matplotlib figure: original RGB + three individual channel maps
def channel_figure(img_rgb: np.ndarray, img_space: np.ndarray, channel_names: list, cmaps: list) -> io.BytesIO:
    fig, axes = plt.subplots(1, 4, figsize=(14, 3.5), facecolor="white")
    axes[0].imshow(img_rgb)
    axes[0].set_title("Original", color="black", fontsize=9)
    for i, (name, cmap) in enumerate(zip(channel_names, cmaps)):
        axes[i + 1].imshow(img_space[:, :, i], cmap=cmap)
        axes[i + 1].set_title(name, color="black", fontsize=9)
    for ax in axes:
        ax.axis("off")
        ax.set_facecolor("white")
    fig.tight_layout(pad=0.5)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=110, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    buf.seek(0)
    return buf


# Render a solid-colour block with the hex code centred inside it
def colour_swatch(r: int, g: int, b: int, width = 400, height: int = 180, top_margin: str = "0px") -> None:
    hex_col = f"#{int(r):02X}{int(g):02X}{int(b):02X}"
    luminance = 0.299 * r + 0.587 * g + 0.114 * b
    text_color = "#111111" if luminance > 128 else "#ffffff"
    css_width = f"{width}px" if isinstance(width, int) else width
    st.markdown(
        f"<div style='margin-top:{top_margin};'>"
        f"<div style='"
        f"background:{hex_col}; width:{css_width}; height:{height}px; "
        f"border-radius:8px; display:flex; align-items:center; "
        f"justify-content:center; font-family:Space Mono,monospace; "
        f"font-size:1rem; font-weight:bold; color:{text_color}; "
        f"letter-spacing:0.05em;'>"
        f"{hex_col}"
        f"</div>"
        f"</div>",
        unsafe_allow_html=True,
    )


def pills(html_str: str) -> None:
    st.markdown(f"<div style='margin-top:0.5rem;'>{html_str}</div>",
                unsafe_allow_html=True)


def pill(label: str, value) -> str:
    return f"<span class='metric-pill'>{label}: {value}</span>"


# Header
st.markdown("# 🎨 Colour Spaces Explorer")
st.markdown(
    "<p style='color:#666; font-family:DM Sans; margin-top:-0.5rem;'>"
    "ARI 2129 — Principles of Computer Vision for AI &nbsp;|&nbsp; Group 1</p>",
    unsafe_allow_html=True,
)
st.divider()

# Tabs
tab_rgb, tab_hsv, tab_ycbcr, tab_lab, tab_eq = st.tabs([
    "  RGB  ", "  HSV  ", "  YCbCr  ", "  LAB  ", "  Equation Demonstrator  ",
])



# TAB 1 — RGB
with tab_rgb:
    st.markdown("## RGB — Red, Green, Blue")
    st.markdown("""
    <div class='info-box'>
    RGB encodes colour as three independent light intensities — one per primary colour.
    It is the native format for screens and cameras, but mixes colour and brightness
    together in every channel, making colour-based operations harder than they need to be.
    </div>
    """, unsafe_allow_html=True)

    # ── Colour builder ─────────────────────────────────────────────────────
    st.markdown("### Build a colour in RGB")
    col_ctrl, _, col_vis = st.columns([1, 0.1, 1.7])
    with col_ctrl:
        r = st.slider("Red (R)", 0, 255, 180, key="rgb_r")
        g = st.slider("Green (G)", 0, 255, 60, key="rgb_g")
        b = st.slider("Blue (B)", 0, 255, 60, key="rgb_b")
        st.markdown(f"""
        <div style='margin-top:1rem;'>
        {pill('R', r)} {pill('G', g)} {pill('B', b)}
        </div>
        """, unsafe_allow_html=True)
    with col_vis:
        st.markdown("Resulting colour:")
        colour_swatch(r, g, b)

    st.divider()

    # ── Channel decomposition ──────────────────────────────────────────────
    st.markdown("### Channel decomposition")
    st.markdown(
        "<div class='info-box'>Upload an image to see how much information each "
        "channel carries independently.</div>", unsafe_allow_html=True
    )
    upload_rgb = st.file_uploader(
        "Upload an image", type=["jpg", "jpeg", "png", "webp"], key="rgb_upload"
    )
    if upload_rgb:
        img_rgb = load_image(upload_rgb)
        st.image(
            channel_figure(img_rgb, img_rgb,
                           ["R channel", "G channel", "B channel"],
                           ["Reds", "Greens", "Blues"]),
            use_container_width=True,
        )
        st.markdown(
            "<div class='warn-box'><b>Notice:</b> brightness affects all three channels "
            "simultaneously. A pixel in shadow has lower R, G <i>and</i> B — you cannot "
            "separate 'red object' from 'dark object' using RGB alone.</div>",
            unsafe_allow_html=True,
        )


# TAB 2 — HSV
with tab_hsv:
    st.markdown("## HSV — Hue, Saturation, Value")
    st.markdown("""
    <div class='info-box'>
    HSV reorganises colour into three perceptually meaningful axes.
    <b>Hue</b> encodes colour type as an angle (0–360°).
    <b>Saturation</b> encodes purity — how far from grey.
    <b>Value</b> encodes brightness. Hue is largely invariant to illumination
    intensity changes, making HSV the preferred space for colour-based segmentation.<br><br>
    <b>OpenCV ranges:</b> H 0–179 (standard H ÷ 2), S 0–255, V 0–255.
    OpenCV models HSV as a <i>cylinder</i>, not a cone — dark pixels can still
    report high S values, unlike a cone model.
    </div>
    """, unsafe_allow_html=True)

    # ── Colour builder ─────────────────────────────────────────────────────
    st.markdown("### Build a colour in HSV")
    col_ctrl, _, col_vis = st.columns([1, 0.1, 1.7])
    with col_ctrl:
        h_val = st.slider("Hue (H) — colour type", 0, 360, 0, key="hsv_h",
                          help="0°=Red, 120°=Green, 240°=Blue")
        s_val = st.slider("Saturation (S) — colour purity", 0, 255, 200, key="hsv_s",
                          help="0 = grey, 255 = fully vivid")
        v_val = st.slider("Value (V) — brightness", 0, 255, 200, key="hsv_v",
                          help="0 = black, 255 = full brightness")

        hsv_pixel = np.uint8([[[min(h_val // 2, 179), s_val, v_val]]])
        rgb_pixel = cv2.cvtColor(hsv_pixel, cv2.COLOR_HSV2RGB)[0][0]

        st.markdown(f"""
        <div style='margin-top:1rem;'>
        {pill('H', f'{h_val}° (OpenCV: {min(h_val // 2, 179)})')}
        {pill('S', s_val)} {pill('V', v_val)}
        </div>
        """, unsafe_allow_html=True)

        if s_val < 30:
            st.markdown(
                "<div class='warn-box'>⚠️ <b>Hue instability:</b> saturation is very low. "
                "The hue value shown is unreliable — this pixel is near-grey and has "
                "no meaningful colour direction.</div>",
                unsafe_allow_html=True,
            )
    with col_vis:
        st.markdown("Resulting colour:")
        colour_swatch(rgb_pixel[0], rgb_pixel[1], rgb_pixel[2])
        st.markdown(f"""
        <div style='margin-top:2.8rem;'>
        {pill('RGB', f'({rgb_pixel[0]}, {rgb_pixel[1]}, {rgb_pixel[2]})')}
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # ── Channel decomposition ──────────────────────────────────────────────
    st.markdown("### Channel decomposition")
    upload_hsv = st.file_uploader(
        "Upload an image", type=["jpg", "jpeg", "png", "webp"], key="hsv_upload"
    )

    if upload_hsv:
        img_rgb = load_image(upload_hsv)
        img_hsv = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2HSV)

        st.image(
            channel_figure(img_rgb, img_hsv,
                           ["H (hue)", "S (saturation)", "V (brightness)"],
                           ["hsv", "gray", "gray"]),
            use_container_width=True,
        )

        st.divider()

        # ── Colour masking ─────────────────────────────────────────────────
        st.markdown("### Colour masking")
        st.markdown(
            "<div class='info-box'>Define a hue range. Pixels whose hue falls within "
            "that range (and whose S and V meet the minimums) will be isolated. "
            "This is the core of HSV-based object segmentation.</div>",
            unsafe_allow_html=True,
        )

        _PRESETS = {
            "Custom":          None,
            "Red":             (340, 20),
            "Orange":          (10,  45),
            "Yellow":          (45,  75),
            "Green":           (85, 155),
            "Cyan":            (155, 200),
            "Blue":            (200, 260),
            "Pink / Magenta":  (260, 340),
        }

        def _apply_preset():
            p = st.session_state.hsv_preset
            if p != "Custom":
                st.session_state.h_min, st.session_state.h_max = _PRESETS[p]

        # Row 1 — hue strip | preset selector
        hdr_l, _, hdr_r = st.columns([1, 0.1, 1])
        with hdr_l:
            st.markdown("""
                <div style="margin-top:1.4rem; margin-bottom:0.5rem;">
                <div style="height:14px; border-radius:4px; border:1px solid #e0e0e0;
                    background:linear-gradient(to right,
                    hsl(0,100%,50%) 0%, hsl(60,100%,50%) 16.7%, hsl(120,100%,50%) 33.3%,
                    hsl(180,100%,50%) 50%, hsl(240,100%,50%) 66.7%,
                    hsl(300,100%,50%) 83.3%, hsl(360,100%,50%) 100%);"></div>
                <div style="position:relative; height:2.2rem; margin-top:5px;
                    font-size:0.5rem; line-height:1.35; color:#888; font-family:Space Mono,monospace;">
                    <span style="position:absolute; left:0%; text-align:left;">Red<br>0°</span>
                    <span style="position:absolute; left:16.7%; transform:translateX(-50%); text-align:center;">Yellow<br>60°</span>
                    <span style="position:absolute; left:33.3%; transform:translateX(-50%); text-align:center;">Green<br>120°</span>
                    <span style="position:absolute; left:50%;   transform:translateX(-50%); text-align:center;">Cyan<br>180°</span>
                    <span style="position:absolute; left:66.7%; transform:translateX(-50%); text-align:center;">Blue<br>240°</span>
                    <span style="position:absolute; left:83.3%; transform:translateX(-50%); text-align:center;">Pink<br>300°</span>
                    <span style="position:absolute; left:100%;  transform:translateX(-100%); text-align:right;">Red<br>360°</span>
                </div>
                </div>
            """, unsafe_allow_html=True)
        with hdr_r:
            st.selectbox(
                "Quick-select colour preset",
                list(_PRESETS.keys()),
                key="hsv_preset",
                on_change=_apply_preset,
            )

        # Row 2 — sliders (separate column group guarantees pixel-perfect alignment)
        col_m1, _, col_m2 = st.columns([1, 0.1, 1])
        with col_m1:
            h_min = st.slider("H min (°)", 0, 360, 120, key="h_min")
            h_max = st.slider("H max (°)", 0, 360, 180, key="h_max")
        with col_m2:
            s_min = st.slider("S min", 0, 255, 50, key="s_min",
                              help="Raise to exclude grey/white pixels")
            v_min = st.slider("V min", 0, 255, 40, key="v_min",
                              help="Raise to exclude very dark pixels")

        lower = np.array([h_min // 2, s_min, v_min])
        upper = np.array([min(h_max // 2, 179), 255, 255])

        if h_min <= h_max:
            mask = cv2.inRange(img_hsv, lower, upper)
        else:
            # Red wraps around 0° — requires two inRange calls combined with bitwise_or
            mask_a = cv2.inRange(img_hsv, lower, np.array([179, 255, 255]))
            mask_b = cv2.inRange(img_hsv, np.array([0, s_min, v_min]), upper)
            mask = cv2.bitwise_or(mask_a, mask_b)

        result = cv2.bitwise_and(img_rgb, img_rgb, mask=mask)
        coverage = 100 * np.mean(mask > 0)

        _, col_r1, col_r2, col_r3, _ = st.columns([0.3, 1, 1, 1, 0.3])
        col_r1.image(img_rgb, caption="Original", use_container_width=True)
        col_r2.image(mask, caption="HSV mask", use_container_width=True, clamp=True)
        col_r3.image(result, caption="Isolated result", use_container_width=True)

        pills(
            pill("Mask coverage", f"{coverage:.1f}%") +
            pill("H range", f"{h_min}°–{h_max}° → OpenCV {h_min//2}–{min(h_max//2, 179)}")
        )

        if h_min > h_max:
            st.markdown(
                "<div class='warn-box'>⚠️ <b>Hue wrap-around active:</b> H min > H max, "
                "so the selection spans the 360°/0° boundary (the red region). "
                "Two <code>inRange</code> calls are combined with <code>bitwise_or</code>.</div>",
                unsafe_allow_html=True,
            )

        st.divider()

        # ── Hue instability overlay ────────────────────────────────────────
        st.markdown("### Hue instability — when HSV breaks")
        st.markdown(
            "<div class='warn-box'>When saturation is near zero, the pixel is grey. "
            "Hue becomes geometrically undefined — there is no colour direction to "
            "measure. OpenCV assigns H=0 by convention, but that is arbitrary. "
            "The red overlay marks every pixel whose hue you should never trust.</div>",
            unsafe_allow_html=True,
        )

        s_thresh = st.slider(
            "Saturation threshold — mark pixels below this as unreliable",
            0, 80, 30, key="s_thresh",
        )

        S_ch = img_hsv[:, :, 1].astype(np.float32)
        low_sat = S_ch < s_thresh
        low_s_hues = img_hsv[:, :, 0][low_sat]

        overlay = img_rgb.copy()
        overlay[low_sat] = [220, 40, 40]

        _, col_i1, _, col_i2, _ = st.columns([0.5, 1, 0.1, 1, 0.5])
        col_i1.image(img_rgb, caption="Original", use_container_width=True)
        col_i2.image(overlay,
                     caption=f"Pixels with S < {s_thresh} marked red (unreliable hue)",
                     use_container_width=True)

        if len(low_s_hues) > 0:
            pills(
                pill("Unreliable pixels", f"{low_sat.sum():,} ({100*low_sat.mean():.1f}%)") +
                pill("Hue std in these pixels", f"{low_s_hues.std():.1f}°")
            )


# TAB 3 — YCbCr
with tab_ycbcr:
    st.markdown("## YCbCr — Luma + Chrominance")
    st.markdown("""
    <div class='info-box'>
    YCbCr separates <b>luminance (Y)</b> from <b>chrominance (Cb, Cr)</b>.
    Human vision is far more sensitive to brightness differences than colour
    differences — YCbCr exploits this. It is used inside JPEG compression and
    broadcast television (BT.601 standard: Kr=0.299, Kg=0.587, Kb=0.114).
    </div>
    """, unsafe_allow_html=True)

    # ── Colour builder ─────────────────────────────────────────────────────
    st.markdown("### Build a colour in YCbCr")
    col_ctrl, _, col_vis = st.columns([1, 0.1, 1.7])
    with col_ctrl:
        y_v  = st.slider("Y — luma (brightness)", 16, 235, 128, key="y_v",
                         help="Broadcast valid range: 16–235")
        cb_v = st.slider("Cb — blue chrominance", 16, 240, 128, key="cb_v")
        cr_v = st.slider("Cr — red chrominance",  16, 240, 128, key="cr_v")

        Y_b  = y_v - 16
        Cb_b = cb_v - 128
        Cr_b = cr_v - 128
        R_f = np.clip(1.164 * Y_b + 1.596 * Cr_b,                  0, 255)
        G_f = np.clip(1.164 * Y_b - 0.392 * Cb_b - 0.813 * Cr_b,   0, 255)
        B_f = np.clip(1.164 * Y_b + 2.017 * Cb_b,                  0, 255)
        rgb_from_ycbcr = (int(R_f), int(G_f), int(B_f))

        st.markdown(f"""
        <div style='margin-top:1rem;'>
        {pill('Y', y_v)} {pill('Cb', cb_v)} {pill('Cr', cr_v)}
        </div>
        """, unsafe_allow_html=True)

    with col_vis:
        st.markdown("Resulting colour:")
        colour_swatch(*rgb_from_ycbcr)
        st.markdown(f"""
        <div style='margin-top:2.8rem;'>
        {pill('RGB', rgb_from_ycbcr)}
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # ── Channel decomposition ──────────────────────────────────────────────
    st.markdown("### Channel decomposition")
    upload_ycbcr = st.file_uploader(
        "Upload an image", type=["jpg", "jpeg", "png", "webp"], key="ycbcr_upload"
    )

    if upload_ycbcr:
        img_rgb = load_image(upload_ycbcr)
        # OpenCV cv2.COLOR_RGB2YCrCb returns channels in Y, Cr, Cb order — reorder
        img_ycrcb = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2YCrCb)
        img_ycbcr_disp = img_ycrcb[:, :, [0, 2, 1]]   # Y, Cb, Cr

        st.image(
            channel_figure(img_rgb, img_ycbcr_disp,
                           ["Y (luma)", "Cb (blue chroma)", "Cr (red chroma)"],
                           ["gray", "Blues", "Reds"]),
            use_container_width=True,
        )

        st.markdown(
            "<div class='info-box'><b>Key insight:</b> Y looks like a greyscale "
            "photograph — it carries almost all structural detail. JPEG stores Cb and Cr "
            "at half the resolution of Y (4:2:0 chroma subsampling), saving space with "
            "minimal visible quality loss.</div>",
            unsafe_allow_html=True,
        )

        st.divider()

        # ── Chrominance suppression ────────────────────────────────────────
        st.markdown("### What happens when you discard chrominance?")
        st.markdown(
            "<div class='info-box'>Drag sliders to suppress Cb and Cr independently. "
            "This shows exactly what information each channel contributes.</div>",
            unsafe_allow_html=True,
        )

        cb_scale = st.slider("Cb scale (1.0 = full, 0.0 = suppressed)", 0.0, 1.0, 1.0,
                             key="cb_scale", step=0.05)
        cr_scale = st.slider("Cr scale (1.0 = full, 0.0 = suppressed)", 0.0, 1.0, 1.0,
                             key="cr_scale", step=0.05)

        img_mod = img_ycrcb.astype(np.float32)
        # In OpenCV YCrCb: index 1 = Cr, index 2 = Cb
        img_mod[:, :, 2] = 128 + (img_mod[:, :, 2] - 128) * cb_scale
        img_mod[:, :, 1] = 128 + (img_mod[:, :, 1] - 128) * cr_scale
        img_mod = np.clip(img_mod, 0, 255).astype(np.uint8)
        img_recon = cv2.cvtColor(img_mod, cv2.COLOR_YCrCb2RGB)

        _, col_y1, _, col_y2, _ = st.columns([0.5, 1, 0.1, 1, 0.5])
        col_y1.image(img_rgb, caption="Original", use_container_width=True)
        col_y2.image(img_recon,
                     caption=f"Cb × {cb_scale:.2f}  |  Cr × {cr_scale:.2f}",
                     use_container_width=True)


# TAB 4 — LAB
with tab_lab:
    st.markdown("## LAB — Perceptually Uniform Colour")
    st.markdown("""
    <div class='info-box'>
    CIELAB is designed so a fixed numerical distance between two colours corresponds
    to a fixed <i>perceptual</i> difference. <b>L*</b> is lightness (0=black, 100=white).
    <b>a*</b> runs from green (−) to red (+). <b>b*</b> runs from blue (−) to yellow (+).<br><br>
    OpenCV encodes L* as L*×255/100, a* and b* as value+128 — all decoded correctly here.
    </div>
    """, unsafe_allow_html=True)

    # ── Colour builder ─────────────────────────────────────────────────────
    st.markdown("### Build a colour in LAB")
    col_ctrl, _, col_vis = st.columns([1, 0.1, 1.7])
    with col_ctrl:
        l_v = st.slider("L* — lightness",     0, 100, 50, key="lab_l")
        a_v = st.slider("a* — green ↔ red",  -128, 127,  0, key="lab_a")
        b_v = st.slider("b* — blue ↔ yellow", -128, 127,  0, key="lab_b")

        lab_pixel = np.uint8([[[
            int(l_v * 255 / 100),
            int(a_v + 128),
            int(b_v + 128),
        ]]])
        rgb_from_lab = cv2.cvtColor(lab_pixel, cv2.COLOR_Lab2RGB)[0][0]

        st.markdown(f"""
        <div style='margin-top:1rem;'>
        {pill('L*', l_v)} {pill('a*', a_v)} {pill('b*', b_v)}
        </div>
        """, unsafe_allow_html=True)

    with col_vis:
        st.markdown("Resulting colour:")
        colour_swatch(rgb_from_lab[0], rgb_from_lab[1], rgb_from_lab[2])
        st.markdown(f"""
        <div style='margin-top:2.8rem;'>
        {pill('RGB', f'({rgb_from_lab[0]}, {rgb_from_lab[1]}, {rgb_from_lab[2]})')}
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # ── Channel decomposition ──────────────────────────────────────────────
    st.markdown("### Channel decomposition")
    upload_lab = st.file_uploader(
        "Upload an image", type=["jpg", "jpeg", "png", "webp"], key="lab_upload"
    )

    if upload_lab:
        img_rgb = load_image(upload_lab)
        img_lab = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2Lab)

        st.image(
            channel_figure(img_rgb, img_lab,
                           ["L* (lightness)", "a* (green↔red)", "b* (blue↔yellow)"],
                           ["gray", "RdYlGn_r", "RdYlBu_r"]),
            use_container_width=True,
        )

        st.divider()

        # ── ΔE heatmap ────────────────────────────────────────────────────
        st.markdown("### Perceptual colour difference (ΔE)")
        st.markdown(
            "<div class='info-box'>Click anywhere on the image to sample a colour. "
            "The heatmap shows the Euclidean distance from that colour in LAB space (ΔE). "
            "Because LAB is perceptually uniform, ΔE correlates with how different two "
            "colours <i>look</i> to a human observer. ΔE &lt; 10 is often considered a "
            "close match.</div>",
            unsafe_allow_html=True,
        )

        img_h, img_w = img_rgb.shape[:2]
        DISPLAY_W = 360

        # Read the previous click from session state BEFORE rendering the widget,
        # so we can draw the yellow circle onto the image that the user clicks on.
        prev_coords = st.session_state.get("lab_click")
        if prev_coords is not None:
            scale    = img_w / DISPLAY_W
            sample_x = int(np.clip(prev_coords["x"] * scale, 0, img_w - 1))
            sample_y = int(np.clip(prev_coords["y"] * scale, 0, img_h - 1))
        else:
            sample_x, sample_y = img_w // 2, img_h // 2

        # Draw the circle on the image before passing it to the click widget
        img_marked = img_rgb.copy()
        cv2.circle(img_marked, (sample_x, sample_y), max(8, img_w // 60), (255, 255, 0), 2)

        # Compute ΔE — done before rendering so the heatmap is ready for the right column
        sampled_lab = img_lab[sample_y, sample_x].astype(np.float32)
        sampled_rgb = img_rgb[sample_y, sample_x]
        delta_e = np.sqrt(
            np.sum((img_lab.astype(np.float32) - sampled_lab) ** 2, axis=2)
        )

        # Derive a figsize that matches DISPLAY_W × (same aspect as the image)
        # so the heatmap renders at the same pixel dimensions as the clickable image.
        DPI = 110
        fig_w = DISPLAY_W / DPI
        fig_h = fig_w * (img_h / img_w)

        col_click, col_heat = st.columns(2)

        with col_click:
            st.markdown(
                "<p class='section-label'>Click on the image to pick a sample point</p>",
                unsafe_allow_html=True,
            )
            streamlit_image_coordinates(
                Image.fromarray(img_marked), width=DISPLAY_W, key="lab_click"
            )

        with col_heat:
            st.markdown(
                "<p class='section-label' style='visibility:hidden;'>placeholder</p>",
                unsafe_allow_html=True,
            )
            fig, ax = plt.subplots(1, 1, figsize=(fig_w, fig_h), facecolor="white")
            im = ax.imshow(delta_e, cmap="plasma", vmin=0, vmax=100)
            ax.set_title("ΔE from sampled colour (LAB distance)", color="black", fontsize=9)
            ax.axis("off")
            plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
            fig.tight_layout(pad=0)
            de_buf = io.BytesIO()
            fig.savefig(de_buf, format="png", dpi=DPI, bbox_inches="tight", facecolor="white")
            plt.close(fig)
            de_buf.seek(0)
            img_b64 = base64.b64encode(de_buf.read()).decode()
            st.markdown(
                f"<div style='display:flex;justify-content:center;'>"
                f"<img src='data:image/png;base64,{img_b64}' width='{DISPLAY_W}'/>"
                f"</div>",
                unsafe_allow_html=True,
            )

        pills(
            pill("Sampled pixel", f"({sample_x}, {sample_y})") +
            pill("RGB", f"({sampled_rgb[0]}, {sampled_rgb[1]}, {sampled_rgb[2]})") +
            pill("LAB", f"({sampled_lab[0]:.1f}, {sampled_lab[1]:.1f}, {sampled_lab[2]:.1f})")
        )

        st.divider()

        # ── Y vs L* comparison ────────────────────────────────────────────
        st.markdown("### Y (YCbCr) vs L* (LAB) — what is the difference?")
        st.markdown(
            "<div class='info-box'>Both Y and L* capture brightness, but L* applies "
            "an additional cube-root nonlinearity to match the eye's logarithmic response "
            "to light. Equal L* steps feel equally bright; equal Y steps do not. "
            "This matters for perceptual image quality measurement.</div>",
            unsafe_allow_html=True,
        )

        img_ycrcb_cmp = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2YCrCb)
        y_ch = img_ycrcb_cmp[:, :, 0]
        # Decode L* from OpenCV encoding (L*×255/100) back to 0–255 display range
        l_ch = np.clip(
            img_lab[:, :, 0].astype(np.float32) * 100 / 255, 0, 255
        ).astype(np.uint8)

        _, col_c1, col_c2, col_c3, _ = st.columns([0.3, 1, 1, 1, 0.3])
        col_c1.image(img_rgb, caption="Original (RGB)", use_container_width=True)
        col_c2.image(y_ch, caption="Y channel (YCbCr BT.601 via OpenCV)",
                     use_container_width=True, clamp=True)
        col_c3.image(l_ch, caption="L* channel (LAB, cube-root compressed)",
                     use_container_width=True, clamp=True)


# TAB 5 — EQUATION DEMONSTRATOR
with tab_eq:
    st.markdown("## Equation Demonstrator")
    st.markdown("""
    <div class='info-box'>
    Pick a colour and a target space. Every conversion step is shown with its
    formula and the computed value at that stage — tracing exactly how RGB
    coordinates are transformed into the target representation.
    </div>
    """, unsafe_allow_html=True)

    _WHY = {
        "HSV": (
            "**Why HSV exists:** RGB encodes colour and brightness together. "
            "HSV reorganises them into a cylinder matching human intuition: "
            "*which* colour (hue), *how vivid* (saturation), *how bright* (value). "
            "To isolate red objects, threshold H alone — not a mix of R, G, and B."
        ),
        "YCbCr": (
            "**Why YCbCr exists:** Broadcast television needed colour to be "
            "backward-compatible with black-and-white sets. Separating luma (Y) from "
            "chroma (Cb, Cr) means an old TV reads only Y. BT.601 coefficients are "
            "tuned for standard-definition content. JPEG also uses this separation."
        ),
        "CIE LAB": (
            "**Why LAB exists:** RGB and HSV distances are not perceptually uniform. "
            "Two colours that look nearly identical can have a large RGB distance. "
            "LAB was designed so equal Euclidean distances (ΔE) correspond to equal "
            "*perceived* colour differences — the standard for colour quality assessment."
        ),
    }

    col_in, _, col_sp = st.columns([2, 0.1, 1])
    with col_in:
        st.markdown("### Input colour (RGB 0–255)")
        r_eq = st.slider("R", 0, 255, 140, key="eq_r")
        g_eq = st.slider("G", 0, 255, 60,  key="eq_g")
        b_eq = st.slider("B", 0, 255, 140, key="eq_b")
    with col_sp:
        st.markdown("### Target space")
        space = st.selectbox(
            "Convert to",
            ["HSV", "YCbCr", "CIE LAB"],
            key="eq_space",
        )
        colour_swatch(r_eq, g_eq, b_eq, width="100%", height=120, top_margin="1.3rem")

    # Normalise to [0, 1] for utils functions
    r_f, g_f, b_f = r_eq / 255.0, g_eq / 255.0, b_eq / 255.0

    st.divider()
    st.markdown(_WHY[space])
    st.markdown(f"### Step-by-step: RGB → {space}")

    if space == "HSV":
        steps = rgb_to_hsv_steps(r_f, g_f, b_f)
    elif space == "YCbCr":
        steps = rgb_to_ycbcr_steps(r_f, g_f, b_f, "BT.601")
    else:
        steps = rgb_to_lab_steps(r_f, g_f, b_f)

    # Column headers
    h1, h2, h3 = st.columns([2, 4, 2])
    with h1: st.markdown("**Step**")
    with h2: st.markdown("**Formula**")
    with h3: st.markdown("**Value**")
    st.divider()

    for step in steps:
        s1, s2, s3 = st.columns([2, 4, 2])
        with s1: st.markdown(f"`{step['step']}`")
        with s2: st.code(step["formula"], language=None)
        with s3: st.markdown(f"**{step['value']}**")

    st.divider()

    st.markdown("### Result:")
    r1, r2, r3 = st.columns(3)
    if space == "HSV":
        h_r, s_r, v_r = _utils_hsv(r_f, g_f, b_f)
        r1.success(f"H = {h_r:.2f}°")
        r2.success(f"S = {s_r:.4f}")
        r3.success(f"V = {v_r:.4f}")
        if s_r < 0.1:
            st.warning("⚠️ Saturation near zero — Hue is unreliable (grey-singularity problem).")
    elif space == "YCbCr":
        y_r, cb_r, cr_r = _utils_ycbcr(r_f, g_f, b_f, "BT.601")
        r1.success(f"Y  = {y_r:.4f}")
        r2.success(f"Cb = {cb_r:.4f}")
        r3.success(f"Cr = {cr_r:.4f}")
    else:
        L_r, a_r, b_r = _utils_lab(r_f, g_f, b_f)
        r1.success(f"L* = {L_r:.2f}")
        r2.success(f"a* = {a_r:.2f}")
        r3.success(f"b* = {b_r:.2f}")
