#!/usr/bin/env python3
"""
Simple auto-indenter for HTML and CSS files.

Usage: python auto_indent.py path/to/file1 [path/to/file2 ...]

Rules:
- Normalize tabs to 2 spaces
- For HTML: put one tag or text node per line, indent nested tags by 2 spaces
- Preserve contents of <script> and <style> blocks (they are indented as a whole)
- For CSS: indent by brace depth (2 spaces)

This is a conservative, heuristic formatter (not a full parser). Use with git so you can review.
"""
import re
import sys
from pathlib import Path


VOID_ELEMENTS = set([
    'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'
])


def is_self_closing(tag):
    return tag.endswith('/') or tag.split()[0].lower() in VOID_ELEMENTS


def format_html(text):
    # Normalize line endings and tabs
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    text = text.replace('\t', '  ')

    # Tokenize: capture comments, doctype, tags, and text
    token_re = re.compile(r'(<!--.*?-->|<!DOCTYPE.*?>|<[^>]+>|[^<]+)', re.S | re.I)
    tokens = token_re.findall(text)

    out_lines = []
    indent = 0
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        tok_strip = tok.strip()

        if not tok_strip:
            i += 1
            continue

        # comments and doctype
        if tok_strip.startswith('<!--') or tok_strip.upper().startswith('<!DOCTYPE'):
            out_lines.append('  ' * indent + tok_strip)
            i += 1
            continue

        if tok_strip.startswith('<'):
            # closing tag
            if tok_strip.startswith('</'):
                indent = max(indent - 1, 0)
                out_lines.append('  ' * indent + tok_strip)
                i += 1
                continue

            # opening tag possibly script/style
            tag_name_match = re.match(r'<\s*([a-zA-Z0-9:-]+)', tok_strip)
            tag_name = tag_name_match.group(1).lower() if tag_name_match else ''

            if tag_name in ('script', 'style'):
                # output open tag
                out_lines.append('  ' * indent + tok_strip)
                indent += 1
                # collect everything until the corresponding closing tag
                inner = []
                i += 1
                while i < len(tokens):
                    t = tokens[i]
                    if isinstance(t, str) and re.match(r'\s*</\s*' + tag_name + r'\s*>', t, re.I):
                        break
                    inner.append(t)
                    i += 1
                # add inner block as-is, but indent each line by current indent
                inner_text = ''.join(inner)
                inner_lines = inner_text.split('\n')
                for line in inner_lines:
                    if line.strip() == '':
                        out_lines.append('')
                    else:
                        out_lines.append('  ' * indent + line.rstrip())
                # closing tag
                if i < len(tokens):
                    indent = max(indent - 1, 0)
                    out_lines.append('  ' * indent + tokens[i].strip())
                    i += 1
                continue

            # self-closing or void
            if tok_strip.endswith('/>') or is_self_closing(tok_strip.strip('<>/ ').split()[0] if ' ' in tok_strip else tok_strip.strip('<>/')):
                out_lines.append('  ' * indent + tok_strip)
                i += 1
                continue

            # normal opening tag
            out_lines.append('  ' * indent + tok_strip)
            indent += 1
            i += 1
            continue

        # text node
        # collapse excessive whitespace but preserve single newlines inside
        text_lines = tok.split('\n')
        for line in text_lines:
            if line.strip() == '':
                continue
            out_lines.append('  ' * indent + line.strip())
        i += 1

    # ensure single trailing newline
    return '\n'.join(out_lines).rstrip() + '\n'


def format_css(text):
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    text = text.replace('\t', '  ')
    lines = text.split('\n')
    out = []
    depth = 0
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        # decrease before if line starts with }
        if line.startswith('}'):
            depth = max(depth - 1, 0)
        out.append('  ' * depth + line)
        # increase if line ends with { (but not for single-line rules like @media)
        if line.endswith('{'):
            depth += 1
        # handle lines with both { and } on same line (rare)
        if '{' in line and '}' in line and line.index('{') < line.index('}'):
            # unchanged depth
            pass
    return '\n'.join(out).rstrip() + '\n'


def process_file(path: Path):
    text = path.read_text(encoding='utf-8')
    if path.suffix.lower() in ('.html', '.htm'):
        new = format_html(text)
    elif path.suffix.lower() in ('.css',):
        new = format_css(text)
    else:
        # fallback: normalize tabs to two spaces
        new = text.replace('\t', '  ')

    if new != text:
        path.write_text(new, encoding='utf-8')
        print(f'Formatted: {path}')
    else:
        print(f'Unchanged: {path}')


def main(argv):
    if len(argv) < 2:
        print('Usage: auto_indent.py file1 [file2 ...]')
        return 1
    for p in argv[1:]:
        process_file(Path(p))
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
