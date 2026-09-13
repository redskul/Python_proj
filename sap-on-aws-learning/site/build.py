#!/usr/bin/env python3
"""Static-site generator for the SAP-on-AWS learning project.

Renders every Markdown file in the project into a browsable, theme-aware static
site under ../public/ (with a sidebar nav), and copies source files (.py/.tf/.txt)
so in-page links to them resolve. The output is pure static HTML/CSS/JS -- no
runtime, no framework -- so Vercel (or any static host) serves it directly with
no build step.

Build-time dependency: the `markdown` package (pip install markdown).

Usage
-----
    pip install markdown
    python site/build.py            # run from the project root (sap-on-aws-learning/)
"""
from __future__ import annotations

import html
import re
import shutil
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent.parent          # sap-on-aws-learning/
OUT = ROOT / "public"
SITE_TITLE = "SAP on AWS — Learning"

# Directories we never publish.
SKIP_DIRS = {"public", "site", ".git", ".terraform", "__pycache__", ".venv", ".idea"}
# Non-markdown source files we copy verbatim so links to them work.
COPY_SUFFIXES = {".py", ".tf", ".txt", ".json", ".cfg", ".ini", ".sh"}

# Pretty labels for the top-level sections in the sidebar.
SECTION_LABELS = {
    "": "Overview",
    "00-getting-started": "0 · Getting Started",
    "01-aws-fundamentals": "1 · AWS Fundamentals",
    "02-sap-fundamentals": "2 · SAP Fundamentals",
    "03-sap-on-aws": "3 · SAP on AWS",
    "labs": "Labs",
    "automation": "Automation",
    "exercises": "Exercises",
}
SECTION_ORDER = list(SECTION_LABELS.keys())

MD_EXTENSIONS = ["tables", "fenced_code", "toc", "attr_list", "sane_lists", "md_in_html"]


def rel_out_path(md_path: Path) -> Path:
    """Map a source .md path to its output .html path (relative to OUT)."""
    rel = md_path.relative_to(ROOT)
    if rel.name.lower() == "readme.md" and rel.parent == Path("."):
        return Path("index.html")
    return rel.with_suffix(".html")


def title_from_md(md_text: str, fallback: str) -> str:
    for line in md_text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def prettify(name: str) -> str:
    stem = Path(name).stem
    stem = re.sub(r"^\d+[-_]?", "", stem)          # drop numeric prefix
    stem = stem.replace("-", " ").replace("_", " ").strip()
    return stem.title() if stem else name


def collect_md() -> list[Path]:
    out = []
    for p in ROOT.rglob("*.md"):
        if any(part in SKIP_DIRS for part in p.relative_to(ROOT).parts):
            continue
        out.append(p)
    return sorted(out, key=lambda x: str(x.relative_to(ROOT)).lower())


def build_nav(md_files: list[Path]) -> list[tuple[str, list[tuple[str, str]]]]:
    """Return [(section_label, [(href, label), ...]), ...] in a sensible order."""
    sections: dict[str, list[tuple[str, str]]] = {}
    for md in md_files:
        rel = md.relative_to(ROOT)
        top = "" if rel.parent == Path(".") else rel.parts[0]
        href = str(rel_out_path(md)).replace("\\", "/")
        md_text = md.read_text(encoding="utf-8")
        if rel.name.lower() == "readme.md":
            label = "Overview" if top == "" else "Introduction"
        else:
            label = title_from_md(md_text, prettify(rel.name))
            # keep labels short in the sidebar
            label = re.sub(r"^\d+\s*[—-]\s*", "", label)
        sections.setdefault(top, []).append((href, label))

    ordered = []
    for key in SECTION_ORDER:
        if key in sections:
            items = sections.pop(key)
            # README/overview first within a section
            items.sort(key=lambda t: (not t[0].endswith(("index.html", "README.html")), t[0]))
            ordered.append((SECTION_LABELS.get(key, prettify(key) or "Overview"), items))
    for key in sorted(sections):
        ordered.append((prettify(key) or key, sorted(sections[key])))
    return ordered


def rewrite_links(html_body: str) -> str:
    """Point .md links at their generated .html equivalents (README.md -> index only at root)."""
    def repl(m: re.Match) -> str:
        target, frag = m.group(1), m.group(2) or ""
        # root README link -> index.html
        if target.lower() in ("readme", "./readme"):
            return f'href="index.html{frag}"'
        return f'href="{target}.html{frag}"'

    return re.sub(r'href="(?!https?:)([^"#]+)\.md(#[^"]*)?"', repl, html_body)


def nav_html(nav, depth: int, current_href: str) -> str:
    prefix = "../" * depth
    parts = ['<nav class="sidebar-nav">']
    for label, items in nav:
        parts.append(f'<div class="nav-section"><span class="nav-section-title">{html.escape(label)}</span><ul>')
        for href, item_label in items:
            active = " class=\"active\"" if href == current_href else ""
            parts.append(f'<li><a href="{prefix}{href}"{active}>{html.escape(item_label)}</a></li>')
        parts.append("</ul></div>")
    parts.append("</nav>")
    return "\n".join(parts)


PAGE_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{page_title}</title>
<meta name="description" content="A hands-on curriculum for learning SAP on AWS: AWS fundamentals, SAP fundamentals, and SAP-on-AWS architecture, with Terraform labs and Python automation.">
<style>{css}</style>
</head>
<body>
<header class="topbar">
  <button id="menuBtn" class="menu-btn" aria-label="Toggle menu">☰</button>
  <a class="brand" href="{root}index.html">SAP&nbsp;on&nbsp;AWS <span>Learning</span></a>
  <button id="themeBtn" class="theme-btn" aria-label="Toggle theme">◐</button>
</header>
<div class="layout">
  <aside class="sidebar" id="sidebar">
    {nav}
    <div class="sidebar-foot">Educational material · not affiliated with SAP or AWS</div>
  </aside>
  <main class="content">
    <article class="markdown-body">
      {body}
    </article>
    <footer class="page-foot">
      <span>SAP on AWS learning project</span>
    </footer>
  </main>
</div>
<script>{js}</script>
</body>
</html>
"""

CSS = r"""
:root{--bg:#ffffff;--fg:#1f2933;--muted:#647084;--border:#e4e8ef;--card:#f7f9fc;
--accent:#ff9900;--accent2:#232f3e;--link:#0b6bcb;--code-bg:#f2f4f8;--code-fg:#1f2933;
--sidebar-bg:#fafbfd;--th-bg:#eef1f6;}
:root[data-theme="dark"]{--bg:#12161d;--fg:#e7ebf1;--muted:#98a2b3;--border:#2a3140;
--card:#1a2029;--accent:#ff9900;--accent2:#0d1117;--link:#6cb6ff;--code-bg:#1c2230;
--code-fg:#e7ebf1;--sidebar-bg:#151a22;--th-bg:#1c2230;}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#12161d;--fg:#e7ebf1;
--muted:#98a2b3;--border:#2a3140;--card:#1a2029;--accent:#ff9900;--accent2:#0d1117;
--link:#6cb6ff;--code-bg:#1c2230;--code-fg:#e7ebf1;--sidebar-bg:#151a22;--th-bg:#1c2230;}}
*{box-sizing:border-box}
html,body{margin:0;padding:0}
body{background:var(--bg);color:var(--fg);font:15px/1.65 -apple-system,BlinkMacSystemFont,
"Segoe UI",Roboto,Helvetica,Arial,sans-serif;-webkit-font-smoothing:antialiased}
a{color:var(--link);text-decoration:none}
a:hover{text-decoration:underline}
.topbar{position:sticky;top:0;z-index:20;display:flex;align-items:center;gap:12px;
height:54px;padding:0 16px;background:var(--accent2);color:#fff;border-bottom:1px solid var(--border)}
.brand{color:#fff;font-weight:700;font-size:17px;letter-spacing:.2px}
.brand span{color:var(--accent);font-weight:700}
.menu-btn,.theme-btn{background:transparent;border:1px solid rgba(255,255,255,.25);color:#fff;
border-radius:8px;height:34px;min-width:38px;cursor:pointer;font-size:16px}
.theme-btn{margin-left:auto}
.menu-btn{display:none}
.layout{display:flex;align-items:flex-start;max-width:1200px;margin:0 auto}
.sidebar{position:sticky;top:54px;align-self:flex-start;width:290px;flex:0 0 290px;
height:calc(100vh - 54px);overflow-y:auto;background:var(--sidebar-bg);
border-right:1px solid var(--border);padding:18px 14px}
.nav-section{margin-bottom:16px}
.nav-section-title{display:block;font-size:11px;text-transform:uppercase;letter-spacing:.08em;
color:var(--muted);font-weight:700;margin:0 0 6px 8px}
.sidebar-nav ul{list-style:none;margin:0;padding:0}
.sidebar-nav li a{display:block;padding:5px 8px;border-radius:7px;color:var(--fg);font-size:13.5px}
.sidebar-nav li a:hover{background:var(--card);text-decoration:none}
.sidebar-nav li a.active{background:var(--accent);color:#231f00;font-weight:600}
.sidebar-foot{margin-top:20px;padding:10px 8px 0;border-top:1px solid var(--border);
color:var(--muted);font-size:11.5px}
.content{flex:1 1 auto;min-width:0;padding:28px 34px 60px}
.markdown-body{max-width:820px}
.markdown-body h1{font-size:30px;line-height:1.2;margin:.2em 0 .6em;border-bottom:2px solid var(--border);padding-bottom:.3em}
.markdown-body h2{font-size:22px;margin:1.6em 0 .5em;border-bottom:1px solid var(--border);padding-bottom:.25em}
.markdown-body h3{font-size:17px;margin:1.3em 0 .4em}
.markdown-body p,.markdown-body li{color:var(--fg)}
.markdown-body code{background:var(--code-bg);color:var(--code-fg);padding:.15em .4em;
border-radius:5px;font-size:.88em;font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
.markdown-body pre{background:var(--code-bg);border:1px solid var(--border);border-radius:10px;
padding:14px 16px;overflow-x:auto}
.markdown-body pre code{background:transparent;padding:0;font-size:13px;line-height:1.55}
.markdown-body blockquote{margin:1em 0;padding:.5em 1em;border-left:4px solid var(--accent);
background:var(--card);border-radius:0 8px 8px 0;color:var(--fg)}
.markdown-body table{border-collapse:collapse;width:100%;margin:1.1em 0;display:block;overflow-x:auto}
.markdown-body th,.markdown-body td{border:1px solid var(--border);padding:8px 11px;text-align:left;font-size:13.5px}
.markdown-body th{background:var(--th-bg);font-weight:700}
.markdown-body details{background:var(--card);border:1px solid var(--border);border-radius:10px;
padding:10px 14px;margin:1em 0}
.markdown-body summary{cursor:pointer;font-weight:600}
.markdown-body hr{border:0;border-top:1px solid var(--border);margin:2em 0}
.markdown-body img{max-width:100%}
.page-foot{margin-top:48px;padding-top:16px;border-top:1px solid var(--border);
color:var(--muted);font-size:12.5px}
@media (max-width:860px){
 .menu-btn{display:inline-block}
 .sidebar{position:fixed;top:54px;left:0;z-index:15;transform:translateX(-100%);
  transition:transform .2s ease;box-shadow:0 10px 30px rgba(0,0,0,.25)}
 .sidebar.open{transform:translateX(0)}
 .content{padding:20px 18px 50px}
}
"""

JS = r"""
(function(){
 var root=document.documentElement;
 try{var saved=localStorage.getItem('theme');if(saved)root.setAttribute('data-theme',saved);}catch(e){}
 var tb=document.getElementById('themeBtn');
 if(tb)tb.addEventListener('click',function(){
   var cur=root.getAttribute('data-theme');
   var next=cur==='dark'?'light':(cur==='light'?'dark':(matchMedia('(prefers-color-scheme:dark)').matches?'light':'dark'));
   root.setAttribute('data-theme',next);
   try{localStorage.setItem('theme',next);}catch(e){}
 });
 var mb=document.getElementById('menuBtn'),sb=document.getElementById('sidebar');
 if(mb&&sb)mb.addEventListener('click',function(){sb.classList.toggle('open');});
 document.querySelectorAll('.sidebar-nav a').forEach(function(a){
   a.addEventListener('click',function(){if(sb)sb.classList.remove('open');});
 });
})();
"""


def main() -> int:
    md_files = collect_md()
    if not md_files:
        print("No markdown files found."); return 1

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    nav = build_nav(md_files)
    md = markdown.Markdown(extensions=MD_EXTENSIONS)

    for src in md_files:
        rel = src.relative_to(ROOT)
        out_path = OUT / rel_out_path(src)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        depth = len(out_path.relative_to(OUT).parts) - 1
        root_prefix = "../" * depth

        md.reset()
        body = md.convert(src.read_text(encoding="utf-8"))
        body = rewrite_links(body)

        page_title = title_from_md(src.read_text(encoding="utf-8"), SITE_TITLE)
        current_href = str(out_path.relative_to(OUT)).replace("\\", "/")
        page = PAGE_TEMPLATE.format(
            page_title=html.escape(f"{page_title} · {SITE_TITLE}"),
            css=CSS, js=JS, root=root_prefix,
            nav=nav_html(nav, depth, current_href),
            body=body,
        )
        out_path.write_text(page, encoding="utf-8")

    # Copy source files verbatim so in-page links to them resolve.
    copied = 0
    for p in ROOT.rglob("*"):
        if p.is_dir():
            continue
        rel = p.relative_to(ROOT)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        if p.suffix.lower() in COPY_SUFFIXES:
            dest = OUT / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, dest)
            copied += 1

    print(f"Built {len(md_files)} pages + copied {copied} source files -> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
