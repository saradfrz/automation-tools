# pdf-notes-builder

Extracts text from every PDF in `input/` and joins it all into a single
timestamped `.txt` file in `output/`.

## Structure

```
pdf-notes-builder/
├── app
│   ├── pdf_text_extractor.py   # PdfTextExtractor: core extraction logic
│   └── utils
│       ├── config.py           # config.json loader (SimpleNamespace)
│       ├── directory.py        # file discovery helpers
│       ├── file.py             # read/write/delete helpers
│       ├── logger.py           # logging setup (info.log / error.log)
│       ├── retry.py            # retry decorator w/ exponential backoff
│       └── string.py           # text cleanup helpers
├── input/                      # place your PDFs here
├── logs/                       # info.log, error.log (recreated each run)
├── models/                     # reserved for future use
├── output/                     # class_notes_{timestamp}.txt is written here
├── .env                        # secrets (currently none required)
├── config.json                 # parametrized, commitable config
├── main.py                     # entry point
└── requirements.txt
```

## Setup

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

1. Drop your `.pdf` files into `input/`.
2. Run:
   ```bash
   python main.py
   ```
3. The combined text file is written to `output/class_notes_<timestamp>.txt`.
   Logs are written to `logs/info.log` and `logs/error.log`.

## Configuration (`config.json`)

| Key | Purpose |
|---|---|
| `dir.input` | Folder scanned for PDFs |
| `dir.output` / `dir.output_html` | Folder for the generated .txt output |
| `dir.logs` | Folder for log files |
| `extraction.output_filename_prefix` | Prefix of the output filename |
| `extraction.timestamp_format` | `strftime` pattern used in the filename |
| `extraction.file_extension` | Extension used to discover input files |
| `extraction.page_separator` | Text inserted between pages of a PDF |
| `extraction.document_separator` | Text inserted between different PDFs |
| `extraction.encoding` | Encoding used for reading/writing text |
| `retry.*` | Retry attempts/backoff applied per-PDF extraction |

## Notes

- No secrets are currently required, but `.env` (via `python-dotenv`) is
  wired in as the place to add any in the future — never in `config.json`.
- Failed PDFs (e.g. corrupted files) are retried per `retry.*`, logged,
  and skipped so the rest of the batch still completes.
