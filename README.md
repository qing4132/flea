# flea

`flea` is a minimal static site generator, with no config files, no plugins, no JavaScript.

Just write, then get your site.

## Quickstart

Install dependencies:

```bash
pip3 install mistune python-frontmatter
```

Create a folder, like `my-blog`, write your posts in `my-blog/content`, then run:

```bash
python3 flea.py /path/to/my-blog
```

Your site will be generated at `my-blog/output`.

## Rules

`flea` favors convention over configuration, and enforces a minimal set of rules on folder structure, special filenames, and frontmatter metadata.

Follow this structure for your folders and Markdown files:

```
my-blog/
└── content/                            # required
    ├── index.md                        # required – site metadata & homepage
    ├── travel/                         # category
    │   ├── index.md                    # optional – category intro, no metadata
    │   ├── a-trip-to-kyoto.md          # regular post
    │   └── why-i-love-nyc.md
    ├── recipes/
    │   ├── easy-sandwich.md
    │   └── quick-pasta.md
    └──  drafts/                        # optional – drafts
        └── soy-sauce-noodles.md
```

Here’s an example of `content/index.md`:

```markdown
---
lang: en-US
title: Jane's Blog
author: Jane Doe
nav:
  - Home: /
  - Travel: /travel
  - Recipes: /recipes
footer: Generated by flea
---

Hi! This is my new blog...
```

A regular post must include these two metadata fields: `title` and `date`. For example:

```markdown
---
title: Why I Love NYC
date: 2025-07-30
---

My first time in New York City was during a winter...
```

These core rules cover most use cases.

For a full guide and example article, see [this post](https://qing4132.pages.dev/projects/flea-a-minimal-static-site-generator) .
