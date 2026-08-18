# ============================================================
# SYNTHETIC INDIC MANUSCRIPT GENERATOR
# STREAMLIT VERSION
# ============================================================
#
# Supported:
#   Devanagari
#   Modi
#   Sharada
#
# Input:
#   Unicode text
#   TXT
#   PDF
#   DOCX / Word
#
# Output:
#   Manuscript PNG
#   Markdown annotation
#
# ============================================================

import os
import random
import requests
import io

import numpy as np
import streamlit as st

from PIL import Image, ImageDraw, ImageFont, ImageFilter

# PDF
import PyPDF2

# Word
from docx import Document


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Synthetic Indic Manuscript Generator",
    page_icon="📜",
    layout="wide"
)


# ============================================================
# PROJECT DIRECTORIES
# ============================================================

BASE_DIR = "manuscript_project"

FONT_DIR = os.path.join(BASE_DIR, "fonts")

DEVANAGARI_DIR = os.path.join(
    FONT_DIR,
    "devanagari"
)

MODI_DIR = os.path.join(
    FONT_DIR,
    "modi"
)

SHARADA_DIR = os.path.join(
    FONT_DIR,
    "sharada"
)

OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "output"
)

ANNOTATION_DIR = os.path.join(
    BASE_DIR,
    "annotations"
)


# Create directories

for folder in [
    BASE_DIR,
    FONT_DIR,
    DEVANAGARI_DIR,
    MODI_DIR,
    SHARADA_DIR,
    OUTPUT_DIR,
    ANNOTATION_DIR
]:

    os.makedirs(
        folder,
        exist_ok=True
    )


# ============================================================
# FONT PATHS
# ============================================================

DEVANAGARI_FONT = os.path.join(
    DEVANAGARI_DIR,
    "NotoSansDevanagari-Regular.ttf"
)

MODI_FONT = os.path.join(
    MODI_DIR,
    "NotoSansModi-Regular.ttf"
)

SHARADA_FONT = os.path.join(
    SHARADA_DIR,
    "NotoSansSharada-Regular.ttf"
)


FONT_PATHS = {

    "Devanagari":
        DEVANAGARI_FONT,

    "Modi":
        MODI_FONT,

    "Sharada":
        SHARADA_FONT
}


# ============================================================
# FONT DOWNLOAD URLS
# ============================================================

FONT_URLS = {

    "Devanagari": [

        "https://notofonts.github.io/devanagari/fonts/NotoSansDevanagari/full/ttf/NotoSansDevanagari-Regular.ttf",

        "https://raw.githubusercontent.com/notofonts/devanagari/main/fonts/ttf/NotoSansDevanagari/NotoSansDevanagari-Regular.ttf",

        "https://raw.githubusercontent.com/openmaptiles/fonts/master/noto-sans/NotoSansDevanagari-Regular.ttf"
    ],

    "Modi": [

        "https://notofonts.github.io/modi/fonts/NotoSansModi/full/ttf/NotoSansModi-Regular.ttf",

        "https://raw.githubusercontent.com/notofonts/modi/main/fonts/ttf/NotoSansModi/NotoSansModi-Regular.ttf"
    ],

    "Sharada": [

        "https://notofonts.github.io/sharada/fonts/NotoSansSharada/full/ttf/NotoSansSharada-Regular.ttf",

        "https://raw.githubusercontent.com/notofonts/sharada/main/fonts/ttf/NotoSansSharada/NotoSansSharada-Regular.ttf"
    ]
}


# ============================================================
# VALIDATE FONT
# ============================================================

def validate_font_file(file_path):

    if not os.path.exists(file_path):
        return False

    try:

        file_size = os.path.getsize(file_path)

        if file_size < 10000:
            return False

        test_font = ImageFont.truetype(
            file_path,
            32
        )

        return test_font is not None

    except Exception:
        return False


# ============================================================
# DOWNLOAD FONT
# ============================================================

def download_font(script, urls, output_path):

    if validate_font_file(output_path):
        return True

    for url in urls:

        try:

            response = requests.get(
                url,
                timeout=60,
                headers={
                    "User-Agent": "Mozilla/5.0"
                }
            )

            if response.status_code != 200:
                continue

            if len(response.content) < 10000:
                continue

            temp_path = output_path + ".tmp"

            with open(
                temp_path,
                "wb"
            ) as file:

                file.write(
                    response.content
                )

            if validate_font_file(temp_path):

                os.replace(
                    temp_path,
                    output_path
                )

                return True

            if os.path.exists(temp_path):
                os.remove(temp_path)

        except Exception:
            continue

    return False


# ============================================================
# FONT SETUP
# ============================================================

@st.cache_resource
def setup_fonts():

    status = {}

    for script in FONT_PATHS:

        status[script] = download_font(
            script,
            FONT_URLS[script],
            FONT_PATHS[script]
        )

    return status


font_status = setup_fonts()


# ============================================================
# EXTRACT TEXT FROM TXT
# ============================================================

def extract_txt(uploaded_file):

    try:

        data = uploaded_file.read()

        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            text = data.decode("utf-16")

        return text

    except Exception as e:

        raise Exception(
            f"Could not read TXT file: {e}"
        )


# ============================================================
# EXTRACT TEXT FROM PDF
# ============================================================

def extract_pdf(uploaded_file):

    try:

        pdf_bytes = uploaded_file.read()

        pdf_file = io.BytesIO(
            pdf_bytes
        )

        reader = PyPDF2.PdfReader(
            pdf_file
        )

        pages = []

        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:
                pages.append(page_text)

        return "\n\n".join(pages)

    except Exception as e:

        raise Exception(
            f"Could not read PDF file: {e}"
        )


# ============================================================
# EXTRACT TEXT FROM WORD DOCX
# ============================================================

def extract_docx(uploaded_file):

    try:

        document = Document(
            uploaded_file
        )

        paragraphs = []

        for paragraph in document.paragraphs:

            if paragraph.text.strip():

                paragraphs.append(
                    paragraph.text
                )

        return "\n\n".join(
            paragraphs
        )

    except Exception as e:

        raise Exception(
            f"Could not read Word file: {e}"
        )


# ============================================================
# EXTRACT TEXT FROM UPLOADED FILE
# ============================================================

def extract_uploaded_text(uploaded_file):

    if uploaded_file is None:
        return ""

    filename = uploaded_file.name.lower()

    if filename.endswith(".txt"):

        return extract_txt(
            uploaded_file
        )

    elif filename.endswith(".pdf"):

        return extract_pdf(
            uploaded_file
        )

    elif filename.endswith(".docx"):

        return extract_docx(
            uploaded_file
        )

    else:

        raise Exception(
            "Unsupported file type."
        )


# ============================================================
# CREATE AGED MANUSCRIPT PAPER
# ============================================================

def create_aged_paper(
    width=1400,
    height=1800
):

    seed = random.randint(
        1,
        999999
    )

    random.seed(seed)
    np.random.seed(seed)

    base_color = np.array(
        [
            205,
            188,
            150
        ],
        dtype=np.float32
    )

    noise = np.random.normal(
        0,
        10,
        (height, width, 1)
    )

    image_array = (
        base_color + noise
    )

    image_array = np.clip(
        image_array,
        0,
        255
    ).astype(
        np.uint8
    )

    image = Image.fromarray(
        image_array
    )

    # --------------------------------------------------------
    # Stains
    # --------------------------------------------------------

    stains = Image.new(
        "RGBA",
        (width, height),
        (0, 0, 0, 0)
    )

    stain_draw = ImageDraw.Draw(
        stains
    )

    for _ in range(45):

        x = random.randint(
            0,
            width
        )

        y = random.randint(
            0,
            height
        )

        radius = random.randint(
            20,
            120
        )

        alpha = random.randint(
            8,
            40
        )

        stain_draw.ellipse(

            (
                x - radius,
                y - radius,
                x + radius,
                y + radius
            ),

            fill=(
                90,
                60,
                30,
                alpha
            )
        )

    stains = stains.filter(
        ImageFilter.GaussianBlur(
            30
        )
    )

    image = Image.alpha_composite(
        image.convert("RGBA"),
        stains
    )

    # --------------------------------------------------------
    # Dark edges
    # --------------------------------------------------------

    y_grid, x_grid = np.ogrid[
        :height,
        :width
    ]

    distance_left = x_grid

    distance_right = (
        width - 1 - x_grid
    )

    distance_top = y_grid

    distance_bottom = (
        height - 1 - y_grid
    )

    distance = np.minimum(

        np.minimum(
            distance_left,
            distance_right
        ),

        np.minimum(
            distance_top,
            distance_bottom
        )
    )

    edge_strength = np.clip(
        1 - distance / 250,
        0,
        1
    )

    edge_array = (
        edge_strength * 75
    ).astype(
        np.uint8
    )

    edge = Image.fromarray(
        edge_array
    )

    dark_layer = Image.new(
        "RGBA",
        (width, height),
        (70, 45, 20, 0)
    )

    dark_layer.putalpha(
        edge
    )

    image = Image.alpha_composite(
        image,
        dark_layer
    )

    return image.convert(
        "RGB"
    )


# ============================================================
# TEXT WRAPPING
# ============================================================

def wrap_text(
    draw,
    text,
    font,
    max_width
):

    lines = []

    paragraphs = text.split(
        "\n"
    )

    for paragraph in paragraphs:

        paragraph = paragraph.strip()

        if paragraph == "":

            lines.append("")

            continue

        words = paragraph.split()

        # Text with spaces
        if len(words) > 1:

            current_line = ""

            for word in words:

                test_line = (
                    current_line
                    + " "
                    + word
                ).strip()

                bbox = draw.textbbox(
                    (0, 0),
                    test_line,
                    font=font
                )

                text_width = (
                    bbox[2]
                    - bbox[0]
                )

                if text_width <= max_width:

                    current_line = test_line

                else:

                    if current_line:

                        lines.append(
                            current_line
                        )

                    current_line = word

            if current_line:

                lines.append(
                    current_line
                )

        # Text without spaces
        else:

            current_line = ""

            for char in paragraph:

                test_line = (
                    current_line
                    + char
                )

                bbox = draw.textbbox(
                    (0, 0),
                    test_line,
                    font=font
                )

                text_width = (
                    bbox[2]
                    - bbox[0]
                )

                if text_width <= max_width:

                    current_line = test_line

                else:

                    if current_line:

                        lines.append(
                            current_line
                        )

                    current_line = char

            if current_line:

                lines.append(
                    current_line
                )

    return lines


# ============================================================
# CREATE MARKDOWN ANNOTATION
# ============================================================

def create_annotation(
    script,
    text,
    image_filename,
    image_width,
    image_height
):

    annotation_filename = (
        os.path.splitext(
            image_filename
        )[0]
        + ".md"
    )

    annotation_path = os.path.join(
        ANNOTATION_DIR,
        annotation_filename
    )

    clean_text = text.strip()

    content = f"""# Synthetic Manuscript Annotation

## Image

`{image_filename}`

## Script

{script}

## Image Dimensions

- Width: {image_width}px
- Height: {image_height}px

## Text

{clean_text}

## Dataset Type

Synthetic historical manuscript

## Generator

Synthetic Indic Manuscript Generator
"""

    with open(
        annotation_path,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            content
        )

    return annotation_path


# ============================================================
# GENERATE MANUSCRIPT
# ============================================================

def generate_manuscript(
    script,
    text
):

    if text is None:
        raise ValueError(
            "Please enter some text."
        )

    text = text.strip()

    if text == "":
        raise ValueError(
            "Please enter some text."
        )

    if script not in FONT_PATHS:
        raise ValueError(
            "Invalid script selected."
        )

    font_path = FONT_PATHS.get(
        script
    )

    if not validate_font_file(
        font_path
    ):

        raise ValueError(
            f"{script} font is missing or invalid."
        )

    # --------------------------------------------------------
    # Image configuration
    # --------------------------------------------------------

    WIDTH = 1400
    HEIGHT = 1800

    FONT_SIZE = 52

    LEFT_MARGIN = 120
    RIGHT_MARGIN = 120
    TOP_MARGIN = 160

    # --------------------------------------------------------
    # Create paper
    # --------------------------------------------------------

    image = create_aged_paper(
        WIDTH,
        HEIGHT
    )

    draw = ImageDraw.Draw(
        image
    )

    # --------------------------------------------------------
    # Load font
    # --------------------------------------------------------

    font = ImageFont.truetype(
        font_path,
        FONT_SIZE
    )

    # --------------------------------------------------------
    # Text wrapping
    # --------------------------------------------------------

    max_width = (
        WIDTH
        - LEFT_MARGIN
        - RIGHT_MARGIN
    )

    lines = wrap_text(
        draw,
        text,
        font,
        max_width
    )

    # --------------------------------------------------------
    # Historical ink
    # --------------------------------------------------------

    ink_colors = [

        (45, 32, 20),
        (50, 35, 22),
        (55, 38, 23),
        (60, 40, 24),
        (65, 43, 25)

    ]

    # --------------------------------------------------------
    # Draw text
    # --------------------------------------------------------

    y_position = TOP_MARGIN

    line_height = 82

    for line in lines:

        if line == "":

            y_position += 40

            continue

        x_variation = random.randint(
            -7,
            7
        )

        y_variation = random.randint(
            -3,
            3
        )

        ink_color = random.choice(
            ink_colors
        )

        draw.text(

            (
                LEFT_MARGIN
                + x_variation,

                y_position
                + y_variation
            ),

            line,

            font=font,

            fill=ink_color
        )

        y_position += line_height

        if y_position >= (
            HEIGHT - 150
        ):

            break

    # --------------------------------------------------------
    # Ink imperfections
    # --------------------------------------------------------

    overlay = Image.new(
        "RGBA",
        image.size,
        (0, 0, 0, 0)
    )

    overlay_draw = ImageDraw.Draw(
        overlay
    )

    for _ in range(350):

        x = random.randint(
            80,
            WIDTH - 80
        )

        y = random.randint(
            80,
            HEIGHT - 80
        )

        radius = random.choice(
            [
                1,
                1,
                1,
                2,
                2,
                3
            ]
        )

        alpha = random.randint(
            10,
            65
        )

        overlay_draw.ellipse(

            (
                x - radius,
                y - radius,
                x + radius,
                y + radius
            ),

            fill=(
                40,
                30,
                20,
                alpha
            )
        )

    overlay = overlay.filter(
        ImageFilter.GaussianBlur(
            1
        )
    )

    image = Image.alpha_composite(
        image.convert("RGBA"),
        overlay
    )

    image = image.convert(
        "RGB"
    )

    # --------------------------------------------------------
    # Save image
    # --------------------------------------------------------

    image_filename = (
        "manuscript_"
        + script.lower()
        + "_"
        + str(
            random.randint(
                100000,
                999999
            )
        )
        + ".png"
    )

    image_path = os.path.join(
        OUTPUT_DIR,
        image_filename
    )

    image.save(
        image_path,
        quality=95
    )

    # --------------------------------------------------------
    # Annotation
    # --------------------------------------------------------

    annotation_path = create_annotation(

        script=script,

        text=text,

        image_filename=image_filename,

        image_width=WIDTH,

        image_height=HEIGHT
    )

    return (
        image,
        image_path,
        annotation_path,
        image_filename
    )


# ============================================================
# STREAMLIT USER INTERFACE
# ============================================================

st.title(
    "📜 Synthetic Indic Manuscript Generator"
)

st.write(
    "Generate synthetic historical-style manuscripts "
    "from Unicode text, PDF, Word or TXT files."
)

st.markdown(
    """
### Supported Scripts

**Devanagari • Modi • Sharada**

### Supported Input Files

- 📄 PDF
- 📝 Word / DOCX
- 📃 TXT
- ✍️ Direct Unicode text
"""
)


# ============================================================
# FONT STATUS
# ============================================================

with st.expander(
    "🔤 Font Status",
    expanded=False
):

    for script, status in font_status.items():

        if status:

            st.success(
                f"{script}: READY"
            )

        else:

            st.error(
                f"{script}: FONT NOT FOUND"
            )


# ============================================================
# SCRIPT SELECTION
# ============================================================

script = st.selectbox(
    "Select Script",
    [
        "Devanagari",
        "Modi",
        "Sharada"
    ]
)


# ============================================================
# FILE UPLOAD
# ============================================================

uploaded_file = st.file_uploader(

    "Upload PDF / Word / TXT file",

    type=[
        "pdf",
        "docx",
        "txt"
    ]
)


# ============================================================
# EXTRACT FILE TEXT
# ============================================================

extracted_text = ""

if uploaded_file is not None:

    st.info(
        f"Uploaded file: {uploaded_file.name}"
    )

    try:

        extracted_text = extract_uploaded_text(
            uploaded_file
        )

        if extracted_text.strip():

            st.success(
                "Text extracted successfully."
            )

            st.text_area(
                "Extracted Text",
                extracted_text,
                height=250
            )

        else:

            st.warning(
                "No text could be extracted from this file."
            )

    except Exception as e:

        st.error(
            str(e)
        )


# ============================================================
# MANUAL TEXT INPUT
# ============================================================

manual_text = st.text_area(

    "Or enter / paste Unicode text",

    height=250,

    placeholder=(
        "Enter Hindi, Marathi, Sanskrit, "
        "Modi or Sharada Unicode text here..."
    )
)


# ============================================================
# CHOOSE INPUT
# ============================================================

if uploaded_file is not None and extracted_text.strip():

    final_text = extracted_text

else:

    final_text = manual_text


# ============================================================
# GENERATE BUTTON
# ============================================================

generate_button = st.button(

    "📜 Generate Manuscript",

    type="primary",

    use_container_width=True
)


# ============================================================
# GENERATE
# ============================================================

if generate_button:

    if not final_text.strip():

        st.error(
            "Please upload a PDF/Word/TXT file "
            "or enter some Unicode text."
        )

    elif not font_status.get(script, False):

        st.error(
            f"{script} font is not available."
        )

    else:

        with st.spinner(
            "Generating synthetic manuscript..."
        ):

            try:

                (
                    image,
                    image_path,
                    annotation_path,
                    image_filename
                ) = generate_manuscript(
                    script,
                    final_text
                )

                st.success(
                    "Manuscript generated successfully!"
                )

                # ------------------------------------------------
                # Display image
                # ------------------------------------------------

                st.subheader(
                    "🖼️ Generated Manuscript"
                )

                st.image(
                    image,
                    caption=image_filename,
                    use_container_width=True
                )

                # ------------------------------------------------
                # Download PNG
                # ------------------------------------------------

                with open(
                    image_path,
                    "rb"
                ) as image_file:

                    st.download_button(

                        label="⬇️ Download Manuscript PNG",

                        data=image_file.read(),

                        file_name=image_filename,

                        mime="image/png",

                        use_container_width=True
                    )

                # ------------------------------------------------
                # Download Markdown
                # ------------------------------------------------

                with open(
                    annotation_path,
                    "rb"
                ) as annotation_file:

                    st.download_button(

                        label="⬇️ Download Annotation Markdown",

                        data=annotation_file.read(),

                        file_name=os.path.basename(
                            annotation_path
                        ),

                        mime="text/markdown",

                        use_container_width=True
                    )

            except Exception as e:

                st.error(
                    f"Generation failed: {e}"
                )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "Synthetic Indic Manuscript Generator | "
    "Devanagari • Modi • Sharada"
)
