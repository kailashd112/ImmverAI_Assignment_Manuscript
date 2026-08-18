import os
import random
import requests
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import streamlit as st

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(BASE_DIR, "fonts")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
ANNOTATION_DIR = os.path.join(BASE_DIR, "annotations")

FONT_PATHS = {
    "Devanagari": os.path.join(FONT_DIR, "devanagari", "NotoSansDevanagari-Regular.ttf"),
    "Modi": os.path.join(FONT_DIR, "modi", "NotoSansModi-Regular.ttf"),
    "Sharada": os.path.join(FONT_DIR, "sharada", "NotoSansSharada-Regular.ttf"),
}

FONT_URLS = {
    "Devanagari": [
        "https://notofonts.github.io/devanagari/fonts/NotoSansDevanagari/full/ttf/NotoSansDevanagari-Regular.ttf",
        "https://raw.githubusercontent.com/notofonts/devanagari/main/fonts/ttf/NotoSansDevanagari/NotoSansDevanagari-Regular.ttf",
    ],
    "Modi": [
        "https://notofonts.github.io/modi/fonts/NotoSansModi/full/ttf/NotoSansModi-Regular.ttf",
        "https://raw.githubusercontent.com/notofonts/modi/main/fonts/ttf/NotoSansModi/NotoSansModi-Regular.ttf",
    ],
    "Sharada": [
        "https://notofonts.github.io/sharada/fonts/NotoSansSharada/full/ttf/NotoSansSharada-Regular.ttf",
        "https://raw.githubusercontent.com/notofonts/sharada/main/fonts/ttf/NotoSansSharada/NotoSansSharada-Regular.ttf",
    ],
}

for p in FONT_PATHS.values():
    os.makedirs(os.path.dirname(p), exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(ANNOTATION_DIR, exist_ok=True)

def validate_font_file(path):
    if not os.path.exists(path) or os.path.getsize(path) < 10000:
        return False
    try:
        ImageFont.truetype(path, 32)
        return True
    except Exception:
        return False

@st.cache_resource(show_spinner=False)
def ensure_fonts():
    status = {}
    for script, path in FONT_PATHS.items():
        if validate_font_file(path):
            status[script] = True
            continue
        status[script] = False
        for url in FONT_URLS[script]:
            try:
                r = requests.get(url, timeout=60, headers={"User-Agent": "Mozilla/5.0"})
                if r.status_code == 200 and len(r.content) >= 10000:
                    tmp = path + ".tmp"
                    with open(tmp, "wb") as f:
                        f.write(r.content)
                    if validate_font_file(tmp):
                        os.replace(tmp, path)
                        status[script] = True
                        break
                    if os.path.exists(tmp):
                        os.remove(tmp)
            except Exception:
                pass
    return status

def create_aged_paper(width=1400, height=1800):
    seed = random.randint(1, 999999)
    random.seed(seed)
    np.random.seed(seed)
    base = np.array([205, 188, 150], dtype=np.float32)
    noise = np.random.normal(0, 10, (height, width, 1))
    arr = np.clip(base + noise, 0, 255).astype(np.uint8)
    image = Image.fromarray(arr).convert("RGBA")

    stains = Image.new("RGBA", (width, height), (0,0,0,0))
    sd = ImageDraw.Draw(stains)
    for _ in range(45):
        x, y = random.randint(0,width), random.randint(0,height)
        radius = random.randint(20,120)
        alpha = random.randint(8,40)
        sd.ellipse((x-radius,y-radius,x+radius,y+radius), fill=(90,60,30,alpha))
    stains = stains.filter(ImageFilter.GaussianBlur(30))
    image = Image.alpha_composite(image, stains)

    yy, xx = np.ogrid[:height,:width]
    distance = np.minimum(np.minimum(xx, width-1-xx), np.minimum(yy, height-1-yy))
    edge_strength = np.clip(1-distance/250,0,1)
    edge = Image.fromarray((edge_strength*75).astype(np.uint8))
    dark = Image.new("RGBA",(width,height),(70,45,20,0))
    dark.putalpha(edge)
    return Image.alpha_composite(image,dark).convert("RGB")

def wrap_text(draw, text, font, max_width):
    lines = []
    for paragraph in text.split("\n"):
        paragraph = paragraph.strip()
        if not paragraph:
            lines.append("")
            continue
        words = paragraph.split()
        if len(words) > 1:
            current = ""
            for word in words:
                test = (current + " " + word).strip()
                if draw.textbbox((0,0), test, font=font)[2] <= max_width:
                    current = test
                else:
                    if current:
                        lines.append(current)
                    current = word
            if current:
                lines.append(current)
        else:
            current = ""
            for char in paragraph:
                test = current + char
                if draw.textbbox((0,0), test, font=font)[2] <= max_width:
                    current = test
                else:
                    if current:
                        lines.append(current)
                    current = char
            if current:
                lines.append(current)
    return lines

def create_annotation(script, text, image_filename, width, height):
    path = os.path.join(ANNOTATION_DIR, os.path.splitext(image_filename)[0] + ".md")
    content = f"""# Synthetic Manuscript Annotation

## Image
`{image_filename}`

## Script
{script}

## Image Dimensions
- Width: {width}px
- Height: {height}px

## Text
{text.strip()}

## Dataset Type
Synthetic historical manuscript

## Generator
Synthetic Indic Manuscript Generator
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path

def generate_manuscript(script, text):
    text = (text or "").strip()
    if not text:
        raise ValueError("Please enter some text.")
    if not validate_font_file(FONT_PATHS[script]):
        raise ValueError(f"{script} font is unavailable. Check your internet connection and restart the app.")

    width, height = 1400, 1800
    image = create_aged_paper(width, height)
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(FONT_PATHS[script], 52)
    lines = wrap_text(draw, text, font, width-240)

    ink_colors = [(45,32,20),(50,35,22),(55,38,23),(60,40,24),(65,43,25)]
    y = 160
    for line in lines:
        if not line:
            y += 40
            continue
        draw.text((120+random.randint(-7,7), y+random.randint(-3,3)),
                  line, font=font, fill=random.choice(ink_colors))
        y += 82
        if y >= height-150:
            break

    overlay = Image.new("RGBA", image.size, (0,0,0,0))
    od = ImageDraw.Draw(overlay)
    for _ in range(350):
        x, yy = random.randint(80,width-80), random.randint(80,height-80)
        r = random.choice([1,1,1,2,2,3])
        od.ellipse((x-r,yy-r,x+r,yy+r), fill=(40,30,20,random.randint(10,65)))
    overlay = overlay.filter(ImageFilter.GaussianBlur(1))
    image = Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB")

    filename = f"manuscript_{script.lower()}_{random.randint(100000,999999)}.png"
    image_path = os.path.join(OUTPUT_DIR, filename)
    image.save(image_path, "PNG")
    annotation_path = create_annotation(script,text,filename,width,height)
    return image, image_path, annotation_path

st.set_page_config(page_title="Synthetic Indic Manuscript Generator", page_icon="📜", layout="centered")
st.title("📜 Synthetic Indic Manuscript Generator")
st.write("Generate synthetic historical-style manuscript images from Unicode text.")

with st.spinner("Checking Indic fonts..."):
    font_status = ensure_fonts()

cols = st.columns(3)
for col, script in zip(cols, FONT_PATHS):
    col.metric(script, "READY" if font_status[script] else "MISSING")

script = st.selectbox("Select Script", list(FONT_PATHS.keys()))
text = st.text_area("Enter Manuscript Text", height=250, placeholder="Enter or paste Unicode text here...")

if st.button("📜 Generate Manuscript", type="primary", use_container_width=True):
    try:
        image, image_path, annotation_path = generate_manuscript(script, text)
        st.success("Manuscript generated successfully.")
        st.image(image, caption=f"{script} manuscript", use_container_width=True)

        with open(image_path, "rb") as f:
            st.download_button("⬇️ Download PNG", f, file_name=os.path.basename(image_path), mime="image/png")

        with open(annotation_path, "rb") as f:
            st.download_button("⬇️ Download Annotation (.md)", f, file_name=os.path.basename(annotation_path), mime="text/markdown")

        st.caption(f"Saved locally: {image_path}")
    except Exception as e:
        st.error(str(e))
