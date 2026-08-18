import os
import random
import requests
import numpy as np
import streamlit as st

from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pypdf import PdfReader
from docx import Document


# ============================================================
# 1. PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Synthetic Indic Manuscript Generator",
    page_icon="📜",
    layout="wide"
)


# ============================================================
# 2. PROJECT DIRECTORIES
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

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
# 3. FONT PATHS
# ============================================================

FONT_PATHS = {

    "Devanagari": os.path.join(
        DEVANAGARI_DIR,
        "NotoSansDevanagari-Regular.ttf"
    ),

    "Modi": os.path.join(
        MODI_DIR,
        "NotoSansModi-Regular.ttf"
    ),

    "Sharada": os.path.join(
        SHARADA_DIR,
        "NotoSansSharada-Regular.ttf"
    )
}


# ============================================================
# 4. FONT DOWNLOAD URLS
# ============================================================

FONT_URLS = {

    "Devanagari": [
        "https://notofonts.github.io/devanagari/fonts/NotoSansDevanagari/full/ttf/NotoSansDevanagari-Regular.ttf",
        "https://raw.githubusercontent.com/notofonts/devanagari/main/fonts/ttf/NotoSansDevanagari/NotoSansDevanagari-Regular.ttf"
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
# 5. FONT VALIDATION
# ============================================================

def validate_font_file(file_path):

    if not os.path.exists(file_path):
        return False

    try:

        if os.path.getsize(file_path) < 10000:
            return False

        font = ImageFont.truetype(
            file_path,
            32
        )

        return font is not None

    except Exception:
        return False


# ============================================================
# 6. DOWNLOAD FONT
# ============================================================

@st.cache_resource
def setup_fonts():

    status = {}

    for script in FONT_PATHS:

        output_path = FONT_PATHS[script]

        if validate_font_file(
            output_path
        ):

            status[script] = True
            continue

        status[script] = False

        for url in FONT_URLS[script]:

            try:

                response = requests.get(
                    url,
                    timeout=60,
                    headers={
                        "User-Agent":
                        "Mozilla/5.0"
                    }
                )

                if response.status_code != 200:
                    continue

                if len(response.content) < 10000:
                    continue

                temp_path = (
                    output_path
                    + ".tmp"
                )

                with open(
                    temp_path,
                    "wb"
                ) as file:

                    file.write(
                        response.content
                    )

                if validate_font_file(
                    temp_path
                ):

                    os.replace(
                        temp_path,
                        output_path
                    )

                    status[script] = True

                    break

                if os.path.exists(
                    temp_path
                ):

                    os.remove(
                        temp_path
                    )

            except Exception:
                continue

    return status


font_status = setup_fonts()


# ============================================================
# 7. CREATE AGED PAPER
# ============================================================

def create_aged_paper(
    width=1400,
    height=1800
):

    random.seed(
        random.randint(
            1,
            999999
        )
    )

    np.random.seed(
        random.randint(
            1,
            999999
        )
    )

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

    return image.convert("RGB")


# ============================================================
# 8. TEXT WRAPPING
# ============================================================

def wrap_text(
    draw,
    text,
    font,
    max_width
):

    lines = []

    paragraphs = text.split("\n")

    for paragraph in paragraphs:

        paragraph = paragraph.strip()

        if paragraph == "":
            lines.append("")
            continue

        words = paragraph.split()

        # ----------------------------------------------------
        # Normal text
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # Text without spaces
        # ----------------------------------------------------

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
# 9. PDF TEXT EXTRACTION
# ============================================================

def extract_pdf_text(
    uploaded_file
):

    try:

        reader = PdfReader(
            uploaded_file
        )

        pages = []

        for page in reader.pages:

            text = page.extract_text()

            if text:
                pages.append(
                    text
                )

        return "\n\n".join(
            pages
        ).strip()

    except Exception as e:

        st.error(
            f"PDF reading error: {e}"
        )

        return ""


# ============================================================
# 10. WORD TEXT EXTRACTION
# ============================================================

def extract_docx_text(
    uploaded_file
):

    try:

        document = Document(
            uploaded_file
        )

        paragraphs = []

        for paragraph in document.paragraphs:

            text = paragraph.text.strip()

            if text:
                paragraphs.append(
                    text
                )

        return "\n\n".join(
            paragraphs
        ).strip()

    except Exception as e:

        st.error(
            f"Word file reading error: {e}"
        )

        return ""


# ============================================================
# 11. EXTRACT UPLOADED FILE
# ============================================================

def extract_uploaded_text(
    uploaded_file
):

    if uploaded_file is None:
        return ""

    filename = uploaded_file.name.lower()

    if filename.endswith(".pdf"):

        return extract_pdf_text(
            uploaded_file
        )

    elif filename.endswith(".docx"):

        return extract_docx_text(
            uploaded_file
        )

    else:

        st.error(
            "Only PDF and DOCX files are supported."
        )

        return ""


# ============================================================
# 12. CREATE MARKDOWN ANNOTATION
# ============================================================

def create_annotation(
    script,
    text,
    image_filename,
    source_filename
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

    content = f"""# Synthetic Manuscript Annotation

## Image

`{image_filename}`

## Source File

`{source_filename}`

## Script

{script}

## Image Dimensions

- Width: 1400px
- Height: 1800px

## Text

{text}

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
# 13. GENERATE MANUSCRIPT
# ============================================================

def generate_manuscript(
    script,
    text,
    source_filename
):

    if not text:
        return None, None

    font_path = FONT_PATHS[script]

    if not validate_font_file(
        font_path
    ):

        st.error(
            f"{script} font is not available."
        )

        return None, None

    # --------------------------------------------------------
    # Image settings
    # --------------------------------------------------------

    WIDTH = 1400
    HEIGHT = 1800

    FONT_SIZE = 52

    LEFT_MARGIN = 120
    RIGHT_MARGIN = 120
    TOP_MARGIN = 160

    # --------------------------------------------------------
    # Paper
    # --------------------------------------------------------

    image = create_aged_paper(
        WIDTH,
        HEIGHT
    )

    draw = ImageDraw.Draw(
        image
    )

    # --------------------------------------------------------
    # Font
    # --------------------------------------------------------

    font = ImageFont.truetype(
        font_path,
        FONT_SIZE
    )

    # --------------------------------------------------------
    # Wrap
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
    # Ink
    # --------------------------------------------------------

    ink_colors = [

        (45, 32, 20),
        (50, 35, 22),
        (55, 38, 23),
        (60, 40, 24),
        (65, 43, 25)
    ]

    y_position = TOP_MARGIN

    line_height = 82

    # --------------------------------------------------------
    # Draw
    # --------------------------------------------------------

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

        if y_position >= HEIGHT - 150:
            break

    # ========================================================
    # INK IMPERFECTIONS
    # ========================================================

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
            [1, 1, 1, 2, 2, 3]
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

    # ========================================================
    # SAVE PNG
    # ========================================================

    image_filename = (
        "manuscript_"
        + script.lower()
        + "_"
        + str(
            random.randint(
                10000,
                99999
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
        "PNG"
    )

    # ========================================================
    # ANNOTATION
    # ========================================================

    annotation_path = create_annotation(
        script,
        text,
        image_filename,
        source_filename
    )

    return image, annotation_path


# ============================================================
# 14. TITLE
# ============================================================

st.title(
    "📜 Synthetic Indic Manuscript Generator"
)

st.write(
    "Convert Unicode text, PDF files, or Word documents "
    "into synthetic historical-style Indic manuscripts."
)


# ============================================================
# 15. FONT STATUS
# ============================================================

with st.expander(
    "🔤 Font Status",
    expanded=False
):

    for script, ready in font_status.items():

        if ready:
            st.success(
                f"{script}: READY"
            )
        else:
            st.error(
                f"{script}: NOT AVAILABLE"
            )


# ============================================================
# 16. SCRIPT SELECTION
# ============================================================

script = st.selectbox(
    "Select Manuscript Script",
    [
        "Devanagari",
        "Modi",
        "Sharada"
    ]
)


# ============================================================
# 17. FILE UPLOAD
# ============================================================

st.subheader(
    "📂 Upload PDF or Word File"
)

uploaded_file = st.file_uploader(

    "Upload your document",

    type=[
        "pdf",
        "docx"
    ],

    help="Upload a PDF or Microsoft Word DOCX file."
)


# ============================================================
# 18. PROCESS FILE
# ============================================================

if uploaded_file is not None:

    st.info(
        f"Uploaded: {uploaded_file.name}"
    )

    if st.button(
        "📖 Extract Text",
        use_container_width=True
    ):

        extracted_text = extract_uploaded_text(
            uploaded_file
        )

        if extracted_text:

            st.session_state[
                "extracted_text"
            ] = extracted_text

            st.success(
                "Text extracted successfully."
            )

        else:

            st.error(
                "No readable text was found."
            )


# ============================================================
# 19. EXTRACTED TEXT
# ============================================================

if "extracted_text" in st.session_state:

    st.subheader(
        "📖 Extracted Text"
    )

    edited_text = st.text_area(

        "You can edit the extracted text before generating the manuscript.",

        value=st.session_state[
            "extracted_text"
        ],

        height=300
    )


    # ========================================================
    # GENERATE
    # ========================================================

    if st.button(
        "📜 Generate Manuscript",
        type="primary",
        use_container_width=True
    ):

        with st.spinner(
            "Generating manuscript..."
        ):

            image, annotation_path = generate_manuscript(

                script,

                edited_text,

                uploaded_file.name
            )


        if image is not None:

            st.success(
                "Manuscript generated successfully!"
            )

            st.subheader(
                "📜 Generated Manuscript"
            )

            st.image(
                image,
                use_container_width=True
            )


            # ------------------------------------------------
            # Download PNG
            # ------------------------------------------------

            image_filename = (
                os.path.basename(
                    image.filename
                )
                if getattr(
                    image,
                    "filename",
                    None
                )
                else None
            )


            # Save image to memory
            import io

            image_bytes = io.BytesIO()

            image.save(
                image_bytes,
                format="PNG"
            )

            image_bytes.seek(0)


            st.download_button(

                label="⬇️ Download Manuscript PNG",

                data=image_bytes,

                file_name=(
                    "synthetic_manuscript.png"
                ),

                mime="image/png",

                use_container_width=True
            )


            # ------------------------------------------------
            # Download annotation
            # ------------------------------------------------

            with open(
                annotation_path,
                "rb"
            ) as file:

                annotation_data = file.read()


            st.download_button(

                label="⬇️ Download Annotation MD",

                data=annotation_data,

                file_name=os.path.basename(
                    annotation_path
                ),

                mime="text/markdown",

                use_container_width=True
            )


# ============================================================
# 20. DIRECT TEXT INPUT
# ============================================================

st.divider()

st.subheader(
    "✍️ Or Enter Text Directly"
)


direct_text = st.text_area(

    "Enter Unicode text",

    placeholder=(
        "Example:\n"
        "नमस्ते महाराष्ट्र\n"
        "भारत एक महान देश है."
    ),

    height=250
)


if st.button(
    "📜 Generate From Direct Text",
    use_container_width=True
):

    if not direct_text.strip():

        st.warning(
            "Please enter some text."
        )

    else:

        with st.spinner(
            "Generating manuscript..."
        ):

            image, annotation_path = generate_manuscript(

                script,

                direct_text,

                "Direct Text Input"
            )


        if image is not None:

            st.success(
                "Manuscript generated successfully!"
            )

            st.image(
                image,
                use_container_width=True
            )


            # ------------------------------------------------
            # PNG download
            # ------------------------------------------------

            import io

            image_bytes = io.BytesIO()

            image.save(
                image_bytes,
                format="PNG"
            )

            image_bytes.seek(0)


            st.download_button(

                label="⬇️ Download Manuscript PNG",

                data=image_bytes,

                file_name=(
                    "synthetic_manuscript.png"
                ),

                mime="image/png",

                use_container_width=True
            )


            # ------------------------------------------------
            # Annotation download
            # ------------------------------------------------

            with open(
                annotation_path,
                "rb"
            ) as file:

                annotation_data = file.read()


            st.download_button(

                label="⬇️ Download Annotation MD",

                data=annotation_data,

                file_name=os.path.basename(
                    annotation_path
                ),

                mime="text/markdown",

                use_container_width=True
            )


# ============================================================
# 21. INFORMATION
# ============================================================

st.divider()

st.markdown(
    """
### 🔄 Project Workflow

**PDF / DOCX / Text**
↓  
**Text Extraction**
↓  
**Select Indic Script**
↓  
**Create Aged Paper**
↓  
**Render Text**
↓  
**Generate Manuscript PNG**
↓  
**Create Markdown Annotation**

### Supported

- 📄 PDF
- 📝 Word DOCX
- ✍️ Unicode Text
- 🔤 Devanagari
- 🔤 Modi
- 🔤 Sharada
"""
)
