# notes-builder

Extracts text from screen-printed presentation slides (PNG/JPG screenshots
of professors' `.pptx` slides) via OCR and compiles it into a single
timestamped `.txt` file.

## How it works

1. Drop your screenshots into `input/`.
2. Run `python main.py`.
3. `easyocr` reads each image (models are downloaded once into `models/`
   and cached there for subsequent runs).
4. Extracted text is appended, per image, into
   `output/class_notes_{timestamp}.txt`, in filename order, with a header
   separating each slide's content.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env  # no secrets currently required, kept for convention
python main.py
```

## Configuration (`config.json`)

| Key | Meaning |
|---|---|
| `dir.input` | Folder scanned for screenshots. |
| `dir.output_html` | Folder the final `.txt` file is written to. **Note:** this key is named `output_html` only because `main.py`'s skeleton hardcodes that attribute name and wasn't to be modified — its value points at the real text-output folder (`output/`). |
| `dir.logs` | Folder for `info.log` / `error.log`. |
| `dir.models` | Where OCR model weights are cached. Not wiped between runs. |
| `ocr.languages` | Language codes passed to `easyocr.Reader` (e.g. `en`, `pt`). |
| `ocr.gpu` | Whether to use GPU acceleration. |
| `ocr.detail` | `0` = text only, `1` = include bounding boxes/confidence. |
| `ocr.paragraph` | Whether `easyocr` should merge nearby text into paragraphs. |
| `output.filename_prefix` | Prefix for the generated notes file. |
| `retry.max_attempts` / `retry.delay_seconds` | Retry behavior for OCR calls on transient failures. |
| `supported_extensions` | Image extensions scanned in `input/`. |

Every run **wipes and recreates** `output/` and `logs/` (per `main.py`),
but leaves `input/` and `models/` untouched.

## Project layout

```
notes-builder/
├── app/
│   ├── downloader/     # reserved for future use (not used yet)
│   ├── ocr/
│   │   └── notes_builder.py   # NotesBuilder - the OCR pipeline
│   └── utils/
│       ├── config.py   # config.json -> SimpleNamespace loader
│       ├── directory.py
│       ├── file.py
│       ├── logger.py
│       ├── retry.py    # parametrized retry decorator
│       └── string.py
├── input/               # your screenshots go here
├── logs/
├── models/              # cached OCR model weights
├── output/              # generated class_notes_{timestamp}.txt
├── .env / .env.example
├── config.json
├── main.py
└── requirements.txt
```

## Known limitations / next steps

- `easyocr` pulls in `torch`; first run downloads model weights (~100s of
  MB) and can take a while depending on connection.
- Slide order is inferred from filename sort — name your screenshots
  sequentially (`slide_01.png`, `slide_02.png`, ...) for a coherent notes
  file.
- OCR quality depends on screenshot resolution/crop; no image
  preprocessing (deskew, contrast boost) is applied yet — a natural next
  step if accuracy is inconsistent.
