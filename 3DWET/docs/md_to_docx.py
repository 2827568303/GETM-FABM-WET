"""Convert markdown to Word document with proper formatting."""
import re
import sys
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn

def add_formatted_runs(paragraph, text):
    """Parse inline markdown (bold, italic, code, links) and add runs."""
    # Pattern: **bold**, *italic*, `code`, [text](url)
    pattern = r'(\*\*(.+?)\*\*|\*(.+?)\*|`(.+?)`|\[([^\]]+)\]\(([^)]+)\))'
    last_end = 0
    for match in re.finditer(pattern, text):
        # Add preceding plain text
        if match.start() > last_end:
            paragraph.add_run(text[last_end:match.start()])
        if match.group(2):  # bold
            run = paragraph.add_run(match.group(2))
            run.bold = True
        elif match.group(3):  # italic
            run = paragraph.add_run(match.group(3))
            run.italic = True
        elif match.group(4):  # code
            run = paragraph.add_run(match.group(4))
            run.font.name = 'Consolas'
            run.font.size = Pt(9)
            run.font.color.rgb = RGBColor(0xC7, 0x25, 0x4E)
        elif match.group(5):  # link - show text only
            run = paragraph.add_run(match.group(5))
            run.font.color.rgb = RGBColor(0x05, 0x63, 0xC1)
            run.underline = True
        last_end = match.end()
    if last_end < len(text):
        paragraph.add_run(text[last_end:])


def parse_table(lines, start_idx):
    """Parse a markdown table starting at start_idx. Returns (rows, next_idx)."""
    rows = []
    i = start_idx
    while i < len(lines) and '|' in lines[i]:
        line = lines[i].strip()
        if line.startswith('|'):
            line = line[1:]
        if line.endswith('|'):
            line = line[:-1]
        cells = [c.strip() for c in line.split('|')]
        # Skip separator row (---)
        if all(re.match(r'^[-:]+$', c) for c in cells):
            i += 1
            continue
        rows.append(cells)
        i += 1
    return rows, i


def add_table_to_doc(doc, rows):
    """Add a table to the document."""
    if not rows:
        return
    n_cols = max(len(r) for r in rows)
    table = doc.add_table(rows=len(rows), cols=n_cols)
    table.style = 'Light Grid Accent 1'
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, row in enumerate(rows):
        for j, cell_text in enumerate(row):
            if j < n_cols:
                cell = table.cell(i, j)
                cell.text = ''
                p = cell.paragraphs[0]
                add_formatted_runs(p, cell_text)
                if i == 0:  # header
                    for run in p.runs:
                        run.bold = True
                for run in p.runs:
                    run.font.size = Pt(9)


def convert_md_to_docx(md_file, docx_file):
    """Convert markdown file to docx."""
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')
    doc = Document()

    # Set default font
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Calibri'
    font.size = Pt(10.5)
    # Set Chinese font
    rPr = style.element.get_or_add_rPr()
    rFonts = rPr.find(qn('w:rFonts'))
    if rFonts is None:
        rFonts = rPr.makeelement(qn('w:rFonts'), {})
        rPr.append(rFonts)
    rFonts.set(qn('w:eastAsia'), '宋体')

    i = 0
    in_code_block = False
    code_lines = []
    code_lang = ''

    while i < len(lines):
        line = lines[i]

        # Code block fence
        if line.strip().startswith('```'):
            if in_code_block:
                # End code block
                code_text = '\n'.join(code_lines)
                if code_text:
                    p = doc.add_paragraph()
                    p.paragraph_format.left_indent = Inches(0.3)
                    p.paragraph_format.space_before = Pt(6)
                    p.paragraph_format.space_after = Pt(6)
                    run = p.add_run(code_text)
                    run.font.name = 'Consolas'
                    run.font.size = Pt(9)
                    run.font.color.rgb = RGBColor(0x33, 0x33, 0x33)
                    # Shading
                    pPr = p._p.get_or_add_pPr()
                    shd = pPr.makeelement(qn('w:shd'), {
                        qn('w:val'): 'clear',
                        qn('w:color'): 'auto',
                        qn('w:fill'): 'F5F5F5'
                    })
                    pPr.append(shd)
                in_code_block = False
                code_lines = []
                code_lang = ''
            else:
                # Start code block
                in_code_block = True
                code_lang = line.strip()[3:]
                code_lines = []
            i += 1
            continue

        if in_code_block:
            code_lines.append(line)
            i += 1
            continue

        # Table detection
        if '|' in line and i + 1 < len(lines) and '|' in lines[i + 1] and re.match(r'^\s*\|[-:|\s]+\|?\s*$', lines[i + 1]):
            rows, next_i = parse_table(lines, i)
            add_table_to_doc(doc, rows)
            i = next_idx = next_i
            continue

        # Headings
        heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)
        if heading_match:
            level = len(heading_match.group(1))
            text = heading_match.group(2)
            h = doc.add_heading(level=level)
            add_formatted_runs(h, text)
            i += 1
            continue

        # Horizontal rule
        if re.match(r'^---+\s*$', line) or re.match(r'^\*\*\*+\s*$', line):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(6)
            p.paragraph_format.space_after = Pt(6)
            pPr = p._p.get_or_add_pPr()
            pBdr = pPr.makeelement(qn('w:pBdr'), {})
            bottom = pBdr.makeelement(qn('w:bottom'), {
                qn('w:val'): 'single',
                qn('w:sz'): '6',
                qn('w:space'): '1',
                qn('w:color'): 'auto'
            })
            pBdr.append(bottom)
            pPr.append(pBdr)
            i += 1
            continue

        # Blockquote
        if line.startswith('>'):
            text = line.lstrip('>').strip()
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.3)
            p.paragraph_format.space_before = Pt(3)
            p.paragraph_format.space_after = Pt(3)
            add_formatted_runs(p, text)
            for run in p.runs:
                run.italic = True
                run.font.color.rgb = RGBColor(0x66, 0x66, 0x66)
            # Left border
            pPr = p._p.get_or_add_pPr()
            pBdr = pPr.makeelement(qn('w:pBdr'), {})
            left = pBdr.makeelement(qn('w:left'), {
                qn('w:val'): 'single',
                qn('w:sz'): '12',
                qn('w:space'): '4',
                qn('w:color'): 'CCCCCC'
            })
            pBdr.append(left)
            pPr.append(pBdr)
            i += 1
            continue

        # Unordered list
        list_match = re.match(r'^(\s*)[-*]\s+(.+)$', line)
        if list_match:
            indent = len(list_match.group(1))
            text = list_match.group(2)
            level = indent // 2
            p = doc.add_paragraph(style='List Bullet')
            p.paragraph_format.left_indent = Inches(0.25 + level * 0.25)
            add_formatted_runs(p, text)
            i += 1
            continue

        # Ordered list
        ol_match = re.match(r'^(\s*)(\d+)\.\s+(.+)$', line)
        if ol_match:
            indent = len(ol_match.group(1))
            text = ol_match.group(3)
            level = indent // 2
            p = doc.add_paragraph(style='List Number')
            p.paragraph_format.left_indent = Inches(0.25 + level * 0.25)
            add_formatted_runs(p, text)
            i += 1
            continue

        # Empty line
        if not line.strip():
            i += 1
            continue

        # Regular paragraph
        p = doc.add_paragraph()
        add_formatted_runs(p, line)
        i += 1

    doc.save(docx_file)
    print(f'Converted: {md_file} -> {docx_file}')
    print(f'Paragraphs: {len(doc.paragraphs)}, Tables: {len(doc.tables)}')


if __name__ == '__main__':
    md_file = '/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/3DWET/docs/WET_CARBON_CYCLE.md'
    docx_file = '/mnt/c/Users/dinod/Desktop/WET_CARBON_CYCLE.docx'
    convert_md_to_docx(md_file, docx_file)
