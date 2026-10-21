# How hard is this problem?

Paste a Codeforces or AtCoder problem and get its rating. If Codeforces hasn't rated it yet, a small machine-learning model (ridge regression plus gradient boosting) makes an educated guess and says how unsure it is.

- rated Codeforces problem: the official rating
- unrated Codeforces problem: a guess and a likely range
- AtCoder task: difficulty converted to the Codeforces scale (rough)
- CSES: no data, so no guess

The site is static. A GitHub Action retrains every Monday and writes every estimate into `site/data.json`, so there's no server.

## Put it on GitHub

1. Make a new repo and upload everything, including the `.github` folder.
2. Settings, Pages, Source: **GitHub Actions**.
3. Actions tab, "Build and deploy site", Run workflow.
4. A few minutes later it's live at `https://<you>.github.io/<repo>/`.

If the data download fails, run it again. Codeforces sometimes rate-limits cloud machines.

## Run it on your computer

```
pip install -r requirements-train.txt
python train.py --cache-dir data
python build_site_data.py --cache-dir data
python app.py
```

Then open http://127.0.0.1:8000. Needs Python 3.10+. Only training needs numpy and scikit-learn.

## More

`docs/how_it_works.pdf` explains the maths (source in `docs/how_it_works.tex`). `python tests/test_pipeline.py` runs everything on fake data to check the code works; it says nothing about real accuracy.

Guesses are usually off by a couple of hundred points, and the page shows the measured error. MIT licensed.
