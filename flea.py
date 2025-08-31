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


def flea(blog_folder: Path):
    parse = mistune.create_markdown(renderer=ImageRenderer())

    content = blog_folder / "content"
    public = blog_folder / "public"

    if public.exists():
        shutil.rmtree(public)
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
                {"".join(f'<a href="{url}">{category}</a>' for category, url in config.get("nav", {}).items())}
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

    for folder in content.iterdir():
        if folder.is_dir() and not folder.name.startswith(".") and folder.name != "static" and folder.name != "drafts":
            category = public / folder.name
            category.mkdir()

            post_list = []

            for md_file in folder.iterdir():
                if md_file.is_file() and md_file.suffix == ".md" and not md_file.name.startswith(".") and md_file.name != "index.md":
                    post_metadata, post_content = frontmatter.parse(md_file.read_text(encoding="utf-8"))

                    post_title = post_metadata.get("title")
                    post_date = post_metadata.get("date")
                    post_path = category / md_file.with_suffix(".html").name
                    post_list.append((post_title, post_date, post_path))

                    render(post_path, post_title, title=post_title, date=post_date, content=post_content)

            category_index_content = (folder / "index.md").read_text(encoding="utf-8") if (folder / "index.md").exists() else None
            entries = "".join(
                f'<li><span class="date">{p[1].isoformat()}</span><a href="/{p[2].parent.name}/{p[2].name}">{p[0]}</a></li>'
                for p in sorted(post_list, key=lambda p: p[1], reverse=True)
            )

            render(category / "index.html", f"{folder.name}/", title=f"{folder.name}/", content=category_index_content, entries=entries)


if __name__ == "__main__":
    flea(Path(sys.argv[1]).expanduser())
