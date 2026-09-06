import re


class StringUtils:

    @staticmethod
    def replace_multiple_spaces(text):
        return re.sub(r'\s+', ' ', text).strip()

    @staticmethod
    def normalize_line_breaks(text):
        """
        Collapse 3+ consecutive newlines into a double newline,
        while preserving intentional paragraph breaks.
        """
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        return re.sub(r'\n{3,}', '\n\n', text).strip()

    @staticmethod
    def clean_page_text(text):
        """
        Apply the standard cleanup pipeline to text extracted from a PDF page:
        strip trailing whitespace per line, then normalize blank lines.
        """
        if not text:
            return ""
        lines = [line.rstrip() for line in text.split('\n')]
        cleaned = '\n'.join(lines)
        return StringUtils.normalize_line_breaks(cleaned)
