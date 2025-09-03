__version__ = "0.3.0"

import shutil
import sys
from pathlib import Path

import frontmatter
import mistune


class ImageRenderer(mistune.HTMLRenderer):
    def image(self, alt, url, title=None):
        class_attribute = f' class="{alt}"' if alt else ""
        title_span = f'<span class="image-title">{title}</span>' if title else ""
        return f'<img src="{url}" alt=""{class_attribute} />{title_span}'


def flea(root: Path):
    parse = mistune.create_markdown(renderer=ImageRenderer())

    content, public = root / "content", root / "public"
    shutil.rmtree(public) if public.exists() else None
    shutil.copytree(Path(__file__).parent / "public", public)

    config, index_content = frontmatter.parse((content / "index.md").read_text(encoding="utf-8"))

    base_html = f"""\
        <!DOCTYPE html>
        <html lang="{config.get('lang','en-US')}">
        <head>
            <meta charset="utf-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1.0" />
            <meta name="author" content="{config.get('author', 'anonymous')}">
            <link rel="icon" href="/static/favicon.png" type="image/png">
            <link rel="stylesheet" href="/static/style.css" type="text/css" />
            <!-- $titlebar -->
        </head>
        <body>
            <div id="top"></div>
            <header>
                <h2>{config.get('title', 'Untitled')}</h2>
                {"".join(f'<a href="{url}">{cat}</a>' for cat, url in config.get("nav", {}).items())}
            </header>
            <main>
                <!-- $title -->
                <!-- $date -->
                <!-- $content -->
                <!-- $entries -->
            </main>
            <footer>{config.get('footer','')}</footer>
        </body>
        </html>"""

    def render(path: Path, titlebar, title=None, date=None, content=None, entries=None):
        path.write_text(
            base_html.replace("<!-- $titlebar -->", f"<title>{titlebar}</title>")
            .replace("<!-- $title -->", f"<h1>{title}</h1>" if title else "")
            .replace("<!-- $date -->", f'<span class="date"><p>{date.isoformat()}</p></span>' if date else "")
            .replace("<!-- $content -->", parse(content) if content else "")
            .replace("<!-- $entries -->", f'<ul class="entries">{entries}</ul>' if entries else ""),
            encoding="utf-8",
        )

    render(public / "index.html", config.get("title", "Untitled"), content=index_content)

    for d in content.iterdir():
        if d.is_dir() and not d.name.startswith(".") and d.name not in {"static", "drafts"}:
            cat = public / d.name
            cat.mkdir()

            posts = []

            for f in d.iterdir():
                if f.is_file() and f.suffix == ".md" and not f.name.startswith(".") and f.name != "index.md":
                    post_metadata, post_content = frontmatter.parse(f.read_text(encoding="utf-8"))

                    post_title = post_metadata.get("title")
                    post_date = post_metadata.get("date")
                    post_path = cat / f.with_suffix(".html").name
                    posts.append((post_title, post_date, post_path))

                    render(post_path, post_title, title=post_title, date=post_date, content=post_content)

            cat_index_content = (d / "index.md").read_text(encoding="utf-8") if (d / "index.md").exists() else None
            entries = "".join(
                f'<li><span class="date">{date.isoformat()}</span>'
                f'<a href="/{path.parent.name}/{path.name}">{title}</a></li>'
                for title, date, path in sorted(posts, key=lambda p: p[1], reverse=True)
            )

            render(cat / "index.html", f"{d.name}/", title=f"{d.name}/", content=cat_index_content, entries=entries)


if __name__ == "__main__":
    flea(Path(sys.argv[1]).expanduser())
