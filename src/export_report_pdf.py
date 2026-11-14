"""Export docs/TECHNICAL_REPORT.md to docs/TECHNICAL_REPORT.pdf with embedded plots."""
import base64
import os
import re
import subprocess
import tempfile
from pathlib import Path
import markdown


CSS_STYLES = """
@page {
    size: A4;
    margin: 1.8cm 1.5cm;
}
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    color: #24292e;
    line-height: 1.55;
    font-size: 10.5pt;
    padding: 0;
    margin: 0;
}
h1 {
    font-size: 20pt;
    border-bottom: 2px solid #0366d6;
    padding-bottom: 6px;
    margin-top: 0;
    color: #0b3d91;
}
h2 {
    font-size: 14pt;
    border-bottom: 1px solid #eaecef;
    padding-bottom: 4px;
    margin-top: 24px;
    color: #1a1f2c;
    page-break-after: avoid;
}
h3 {
    font-size: 12pt;
    margin-top: 18px;
    color: #24292e;
    page-break-after: avoid;
}
p, ul, ol {
    margin-top: 6px;
    margin-bottom: 10px;
}
table {
    border-collapse: collapse;
    width: 100%;
    margin: 14px 0;
    font-size: 9pt;
    page-break-inside: avoid;
}
th, td {
    border: 1px solid #d0d7de;
    padding: 6px 10px;
    text-align: left;
}
th {
    background-color: #f6f8fa;
    font-weight: 600;
}
tr:nth-child(even) {
    background-color: #fcfcfc;
}
code {
    font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace;
    font-size: 85%;
    background-color: #f6f8fa;
    padding: 2px 4px;
    border-radius: 3px;
}
pre {
    background-color: #f6f8fa;
    padding: 10px;
    border-radius: 4px;
    overflow-x: auto;
    font-size: 8.5pt;
    page-break-inside: avoid;
}
pre code {
    background: none;
    padding: 0;
}
img {
    max-width: 90%;
    height: auto;
    display: block;
    margin: 14px auto;
    border: 1px solid #e1e4e8;
    border-radius: 4px;
    page-break-inside: avoid;
}
hr {
    border: none;
    border-top: 1px solid #eaecef;
    margin: 20px 0;
}
blockquote {
    border-left: 4px solid #0366d6;
    color: #57606a;
    padding-left: 12px;
    margin-left: 0;
}
"""


def find_browser() -> str:
    """Locate Chrome or Edge executable on Windows."""
    candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    raise FileNotFoundError("Neither Google Chrome nor Microsoft Edge was found.")


def image_to_base64(img_path: Path) -> str:
    """Read an image and convert it to a base64 data URI."""
    with open(img_path, "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")
    return f"data:image/png;base64,{data}"


def export_markdown_to_pdf(
    md_path: Path = Path("docs/TECHNICAL_REPORT.md"),
    pdf_path: Path = Path("docs/TECHNICAL_REPORT.pdf"),
) -> None:
    """Convert Markdown report to PDF with base64 embedded images."""
    if not md_path.exists():
        raise FileNotFoundError(f"Markdown file not found: {md_path}")

    with open(md_path, "r", encoding="utf-8") as f:
        md_content = f.read()

    # Convert markdown to HTML
    html_body = markdown.markdown(
        md_content,
        extensions=["tables", "fenced_code"],
    )

    # Embed images as base64 data URIs
    project_root = md_path.resolve().parent.parent

    def replace_img_src(match):
        rel_src = match.group(1)
        # Resolve path relative to docs or project root
        candidate = (md_path.parent / rel_src).resolve()
        if not candidate.exists():
            candidate = (project_root / rel_src).resolve()
        if candidate.exists() and candidate.suffix.lower() == ".png":
            b64_uri = image_to_base64(candidate)
            return f'src="{b64_uri}"'
        return match.group(0)

    html_body = re.sub(r'src="([^"]+\.png)"', replace_img_src, html_body)

    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Technical Report</title>
<style>
{CSS_STYLES}
</style>
</head>
<body>
{html_body}
</body>
</html>"""

    # Write temporary HTML and render to PDF using headless Chrome/Edge
    browser = find_browser()
    abs_pdf = pdf_path.resolve()
    abs_pdf.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as tmp:
        tmp.write(full_html)
        tmp_path = Path(tmp.name)

    try:
        cmd = [
            browser,
            "--headless=new",
            "--disable-gpu",
            "--no-pdf-header-footer",
            f"--print-to-pdf={abs_pdf}",
            str(tmp_path),
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if res.returncode != 0:
            raise RuntimeError(f"PDF export failed with code {res.returncode}: {res.stderr}")
        if not abs_pdf.exists():
            raise RuntimeError(f"PDF file was not created: {abs_pdf}")
        file_size_kb = abs_pdf.stat().st_size / 1024
        print(f"Successfully generated {pdf_path} ({file_size_kb:.1f} KB)")
    finally:
        if tmp_path.exists():
            os.remove(tmp_path)


if __name__ == "__main__":
    export_markdown_to_pdf()

