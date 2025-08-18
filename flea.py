__version__ = "0.2.4"

import re
import shutil
import sys
import textwrap
from pathlib import Path

import frontmatter
import mistune


class ImageRenderer(mistune.HTMLRenderer):
    def image(self, alt, url, title=None):
        return f'<img src="{url}" alt="{title or ""}" title="{title or ""}"{" class=" + alt if alt else ""} />' + (
            f'<span class="image-title">{title}</span>' if title else ""
        )


parse = mistune.create_markdown(renderer=ImageRenderer())


def generate_base_html(blog_folder: Path):
    base_html_template = textwrap.dedent(
        """\
        <!DOCTYPE html>
        <html lang="<!-- CONFIG: lang -->">
        <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <meta name="author" content="<!-- CONFIG: author -->">
        <link rel="icon" href="/static/favicon.png" type="image/png">
        <link rel="stylesheet" href="/static/style.css" type="text/css" />
        <title><!-- CONFIG: title --></title>
        </head>
        <body>
        <div id="top"></div>
        <header>
        <h2><!-- CONFIG: title --></h2>
        <!-- CONFIG: nav -->
        </header>
        <main>
        <!-- post-title -->
        <!-- post-date -->
        <!-- post-content --><!-- entries -->
        </main>
        <!-- CONFIG: footer -->
        </body>
        </html>
        """
    )

    config = frontmatter.loads((blog_folder / "content" / "index.md").read_text(encoding="utf-8")).metadata

    base_html = base_html_template.replace("<!-- CONFIG: lang -->", config.get("lang", "en-US"))
    base_html = base_html.replace("<!-- CONFIG: author -->", config.get("author", "anonymous"))
    base_html = base_html.replace("<!-- CONFIG: title -->", config.get("title", "Untitled"))
    if "footer" in config:
        base_html = base_html.replace("<!-- CONFIG: footer -->", f'<footer>{config["footer"]}</footer>')
    if "nav" in config:
        nav_html = "\n".join(f'<a href="{list(item.values())[0]}">{list(item.keys())[0]}</a>' for item in config["nav"])
        base_html = base_html.replace("<!-- CONFIG: nav -->", nav_html)

    return base_html


def flea(blog_folder: Path):
    content, output = blog_folder / "content", blog_folder / "output"

    if output.exists():
        shutil.rmtree(output)
    output.mkdir()
    shutil.copytree(Path(__file__).parent / "static", output / "static")

    base_html = generate_base_html(blog_folder)

    for folder in content.iterdir():
        if folder.is_dir() and not folder.name.startswith(".") and folder.name != "drafts":
            category = output / folder.name
            category.mkdir()

            entries = []

            for md_file in folder.iterdir():
                if md_file.is_file() and md_file.suffix == ".md" and not md_file.name.startswith(".") and md_file.name != "index.md":
                    post = frontmatter.loads(md_file.read_text(encoding="utf-8"))

                    post_title = post.metadata.get("title")
                    post_date = post.metadata.get("date") or post.metadata.get("updated")
                    post_path = category / md_file.with_suffix(".html").name
                    entries.append((post_title, post_date, post_path))

                    html = base_html.replace("<!-- post-title -->", f"<h1>{post_title}</h1>")
                    html = re.sub(r"<title>.*?</title>", f"<title>{post_title}</title>", html)
                    html = html.replace("<!-- post-date -->", f'<span class="date"><p>{post_date.strftime("%Y-%m-%d")}</p></span>')
                    html = html.replace("<!-- post-content -->", parse(post.content))

                    post_path.write_text(html, encoding="utf-8")

            html = base_html.replace("<!-- post-title -->", f"<h1>{folder.name}/</h1>")
            html = re.sub(r"<title>.*?</title>", f"<title>{folder.name}/</title>", html)

            post_list = "\n".join(
                f'<li><span class="date">{e[1].isoformat()}</span><a href="/{e[2].parent.name}/{e[2].name}">{e[0]}</a></li>'
                for e in sorted(entries, key=lambda e: e[1], reverse=True)
            )
            html = html.replace("<!-- entries -->", f'<ul class="page-list">\n{post_list}\n</ul>')

            folder_index = folder / "index.md"
            if folder_index.exists():
                html = html.replace("<!-- post-content -->", parse(folder_index.read_text(encoding="utf-8")))
            (category / folder_index.with_suffix(".html").name).write_text(html, encoding="utf-8")

    html = base_html.replace("<!-- post-content -->", parse(frontmatter.loads((content / "index.md").read_text(encoding="utf-8")).content))
    (output / "index.html").write_text(html, encoding="utf-8")


if __name__ == "__main__":
    flea(Path(sys.argv[1]).expanduser())
