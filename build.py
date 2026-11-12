# /// script
# requires-python = ">=3.9"
# dependencies = ["pyyaml", "jinja2"]
# ///
"""Genera PDF (LaTeX) e sito web del CV a partire da cv.yaml.

Uso:   uv run build.py            (PDF + sito)
       uv run build.py --no-pdf   (solo sito, non serve LaTeX)

Output:  pdf/Daniele_Trisotto_CV_{IT,EN}.pdf
         site/index.html (IT), site/en/index.html (EN) + copia di PDF e foto

Se esiste private.yaml (non versionato) i dati privati, es. il telefono,
finiscono solo nel PDF generato in locale; mai sul sito.
"""
import datetime
import html
import re
import shutil
import subprocess
import sys
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader

ROOT = Path(__file__).resolve().parent
LANGS = ("it", "en")
PDF_NAME = "Daniele_Trisotto_CV_{}.pdf"

TEX_ESC = {
    "\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#",
    "_": r"\_", "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}", "“": "``", "”": "''", "–": "--", "—": "---",
}


def localize(value, lang):
    return value.get(lang, "") if isinstance(value, dict) else value


def to_tex(value, lang):
    s = str(localize(value, lang))
    s = "".join(TEX_ESC.get(c, c) for c in s)
    s = re.sub(r"\*\*(.+?)\*\*", r"\\cvstrong{\1}", s)
    s = re.sub(r"\*(.+?)\*", r"\\textit{\1}", s)
    return s.replace("LaTeX", r"\LaTeX{}")


def to_html(value, lang):
    s = html.escape(str(localize(value, lang)), quote=False)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    return re.sub(r"\*(.+?)\*", r"<em>\1</em>", s)


def make_env(fmt, lang):
    opts = {}
    if fmt == "tex":  # delimitatori che non confliggono con LaTeX
        opts = dict(block_start_string=r"\BLOCK{", block_end_string="}",
                    variable_start_string=r"\VAR{", variable_end_string="}",
                    comment_start_string=r"\#{", comment_end_string="}")
    env = Environment(loader=FileSystemLoader(ROOT / "templates"),
                      trim_blocks=True, lstrip_blocks=True, **opts)
    conv = to_tex if fmt == "tex" else to_html
    env.filters["t"] = lambda v: conv(v, lang)
    return env


def build_pdf(cv, lang, photo):
    build = ROOT / "build"
    build.mkdir(exist_ok=True)
    tex = build / f"cv_{lang}.tex"
    tex.write_text(make_env("tex", lang).get_template("cv.tex.j2").render(
        cv=cv, lang=lang, photo=f"../{photo}" if photo else ""), encoding="utf-8")
    for _ in range(2):  # due passate: la banda colorata in alto usa le coordinate di pagina
        r = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error",
                            tex.name], cwd=build, capture_output=True, text=True,
                           errors="replace")
        if r.returncode != 0:
            sys.exit(f"Errore LaTeX ({lang}):\n{r.stdout[-2500:]}")
    out = ROOT / "pdf"
    out.mkdir(exist_ok=True)
    dest = out / PDF_NAME.format(lang.upper())
    shutil.copyfile(build / f"cv_{lang}.pdf", dest)
    pages = len(re.findall(rb"/Type\s*/Page[^s]", dest.read_bytes()))
    print(f"PDF  {dest.relative_to(ROOT)}" + (f"  (ATTENZIONE: {pages} pagine)" if pages > 1 else ""))


def build_site(cv, lang, photo):
    site = ROOT / "site"
    target = site if lang == "it" else site / lang
    target.mkdir(parents=True, exist_ok=True)
    page = make_env("html", lang).get_template("index.html.j2").render(
        cv=cv, lang=lang, other="en" if lang == "it" else "it",
        root="" if lang == "it" else "../",
        other_href="en/" if lang == "it" else "../",
        pdf=PDF_NAME.format(lang.upper()), photo=photo,
        today=datetime.date.today().strftime("%d/%m/%Y"))
    (target / "index.html").write_text(page, encoding="utf-8")
    print(f"WEB  {(target / 'index.html').relative_to(ROOT)}")
    for src in (ROOT / "pdf" / PDF_NAME.format(lang.upper()), ROOT / photo if photo else None):
        if src and src.exists():
            shutil.copyfile(src, site / src.name)


def main():
    cv = yaml.safe_load((ROOT / "cv.yaml").read_text(encoding="utf-8"))
    private = ROOT / "private.yaml"
    cv["private"] = yaml.safe_load(private.read_text(encoding="utf-8")) if private.exists() else {}
    photo = cv["meta"].get("photo") or ""
    if photo and not (ROOT / photo).exists():
        print(f"(foto '{photo}' non trovata: CV senza foto)")
        photo = ""
    for lang in LANGS:
        if "--no-pdf" not in sys.argv:
            build_pdf(cv, lang, photo)
        build_site(cv, lang, photo)


if __name__ == "__main__":
    main()
