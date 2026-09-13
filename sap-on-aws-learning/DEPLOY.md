# Deploying the site to Vercel

The curriculum is rendered into a **static website** in [`public/`](public/) by
[`site/build.py`](site/build.py). It's plain HTML/CSS/JS — **no framework, no build step
required on Vercel** — so Vercel just serves the pre-built `public/` folder.

`vercel.json` is already configured:
```json
{ "framework": null, "outputDirectory": "public" }
```

> ⚠️ Deploying to Vercel requires **your** Vercel account login, which I can't do for
> you from here. Pick one of the two paths below — both take about a minute.

## Option A — Import the Git repo (recommended, gives auto-deploys)

1. Push this branch (already done): `redskul/Python_proj @ claude/funny-bell-wike7b`.
2. Go to <https://vercel.com/new> and **Import** the `redskul/Python_proj` repository.
3. In the import settings:
   - **Root Directory:** `sap-on-aws-learning`  ← important (the site lives in a subfolder)
   - **Framework Preset:** *Other* (leave as detected / none)
   - **Build Command:** *(leave empty)*
   - **Output Directory:** `public` (already set by `vercel.json`)
4. Click **Deploy**. You'll get a URL like `https://your-project.vercel.app`.

Every push to the branch will then redeploy automatically.

## Option B — Deploy from your machine with the Vercel CLI

```bash
npm i -g vercel                       # once
git clone https://github.com/redskul/Python_proj
cd Python_proj/sap-on-aws-learning     # the vercel.json lives here
vercel                                 # first run: log in + link project
vercel --prod                          # promote to production
```

## Rebuilding the site after editing the Markdown

The HTML in `public/` is generated. If you change any `.md` file, regenerate:

```bash
cd sap-on-aws-learning
pip install markdown
python site/build.py          # rewrites public/
git add public && git commit -m "Rebuild site" && git push
```

### (Optional) Let Vercel rebuild automatically

If you'd rather not commit `public/` each time, set the Vercel project's **Build
Command** to:

```
pip install markdown && python3 site/build.py
```

Vercel's build image includes Python 3, so this regenerates `public/` on every deploy.
The committed `public/` still guarantees a working deploy if you leave the build command
empty.

## What gets served

- `index.html` — the project overview (the root `README`).
- One page per Markdown file, with a sidebar, light/dark theme toggle, and mobile menu.
- The `.py` / `.tf` source files are copied verbatim so in-page links to them resolve.
