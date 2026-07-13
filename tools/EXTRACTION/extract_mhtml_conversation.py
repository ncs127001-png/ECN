#!/usr/bin/env python3
import re
import sys
import html
import os
import quopri

def extract_body_from_mhtml(text):
    # Try to find the HTML part by searching for first <html
    m = re.search(r"<html[\s\S]*</html>", text, flags=re.I)
    if m:
        return m.group(0)
    # fallback: find first <body...> to </body>
    m = re.search(r"<body[\s\S]*?</body>", text, flags=re.I)
    if m:
        return m.group(0)
    # fallback: find Content-Type: text/html then the subsequent HTML
    idx = text.find("Content-Type: text/html")
    if idx != -1:
        # attempt to find first <html after this
        m = re.search(r"<html[\s\S]*</html>", text[idx:], flags=re.I)
        if m:
            return m.group(0)
    # last resort: return entire file
    return text


def clean_html_to_text(html_text):
    # remove script/style/pre/code blocks entirely
    html_text = re.sub(r"<(?:(?:script)|(?:style)|(?:pre)|(?:code))[\s\S]*?</(?:(?:script)|(?:style)|(?:pre)|(?:code))>", "", html_text, flags=re.I)

    # ensure some block-level tags produce newlines
    block_tags = ["</div>", "</p>", "<br", "</li>", "</tr>", "</section>", "</article>", "</h1>", "</h2>", "</h3>", "</h4>", "</h5>", "</h6>"]
    for tag in block_tags:
        html_text = html_text.replace(tag, tag + "\n")

    # remove all remaining tags
    text = re.sub(r"<[^>]+>", "", html_text)

    # unescape html entities
    text = html.unescape(text)

    # normalize line endings and whitespace
    # remove leading/trailing spaces on each line
    lines = [ln.strip() for ln in text.splitlines()]
    # drop consecutive empty lines
    out_lines = []
    prev_empty = False
    for ln in lines:
        if ln == "":
            if not prev_empty:
                out_lines.append("")
            prev_empty = True
        else:
            out_lines.append(ln)
            prev_empty = False
    # join
    cleaned = "\n".join(out_lines).strip() + "\n"
    return cleaned


def guess_interlocutors_and_mark(text):
    # Try to detect common speaker labels and ensure they appear at line start.
    # We'll look for patterns like "Qwen", "You", "Assistant", "User", "System".
    speakers = ["Qwen", "You", "Assistant", "User", "System", "Tú", "Usuario", "Asistente"]
    # If some lines contain 'Qwen' or 'Assistant' inline, leave them. Otherwise attempt no aggressive changes.
    # We'll return text unchanged (safe), but include a brief header describing any detected names.
    found = set()
    for sp in speakers:
        if re.search(r"\b" + re.escape(sp) + r"\b", text):
            found.add(sp)
    header = """
# Conversación extraída desde MHTML
# Archivo original: {orig}
# Detectados (coincidencias heurísticas): {found}

"""
    return header, found


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: extract_mhtml_conversation.py <archivo.mhtml> [salida.txt]")
        sys.exit(2)
    infile = sys.argv[1]
    if not os.path.exists(infile):
        print("Archivo no encontrado:", infile)
        sys.exit(2)
    outpath = None
    if len(sys.argv) >= 3:
        outpath = sys.argv[2]
    else:
        base = os.path.basename(infile)
        name, _ = os.path.splitext(base)
        outpath = os.path.join(os.path.dirname(infile), f"{name}_conversation.txt")

    with open(infile, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()

    # If file is quoted-printable encoded (common in MHTML), decode it to clean =XX tokens
    # Heuristic: presence of common quoted-printable markers like "=20" or "=3D"
    if "=20" in content or "=3D" in content or re.search(r"=\r?\n", content):
        try:
            # quopri expects bytes
            content = quopri.decodestring(content.encode('utf-8', errors='replace')).decode('utf-8', errors='replace')
        except Exception:
            # if decoding fails, keep original
            pass

    html_part = extract_body_from_mhtml(content)
    cleaned = clean_html_to_text(html_part)

    header, found = guess_interlocutors_and_mark(cleaned)
    header = header.format(orig=infile, found=(', '.join(sorted(found)) if found else 'Ninguno detectado'))

    with open(outpath, 'w', encoding='utf-8') as out:
        out.write(header)
        out.write(cleaned)

    print("Archivo de salida creado:", outpath)
    # print small stats
    lines = cleaned.count('\n')
    print(f"Líneas extraídas (aprox): {lines}")
