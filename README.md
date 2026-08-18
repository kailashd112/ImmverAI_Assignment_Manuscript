# 📜 Synthetic Indic Manuscript Generator

LINK :- https://by-kailashdake.streamlit.app/

A Streamlit application that converts Unicode text into synthetic historical-style manuscript images.

## Supported Scripts
- Devanagari
- Modi
- Sharada

## Features
- Unicode text input
- Automatic Indic font download
- Aged paper texture
- Historical-style ink variation
- PNG manuscript output
- Markdown annotation output
- Streamlit web interface
- GitHub-ready project structure

## Project Structure

```text
synthetic-indic-manuscript/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── fonts/
│   ├── devanagari/
│   ├── modi/
│   └── sharada/
├── output/
└── annotations/
```

## Run Locally

### 1. Clone
```bash
git clone https://github.com/YOUR_USERNAME/synthetic-indic-manuscript.git
cd synthetic-indic-manuscript
```

### 2. Create virtual environment
Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run
```bash
streamlit run app.py
```

The generated images are synthetic historical-style images. They are not scans or reproductions of real historical manuscripts.
