# FINALS PROJECT - Credit Card Fraud Visualization

This finals deliverable uses a two-step workflow:

1. Preprocess the large CSV once with Python.
2. Open a static frontend dashboard that loads compact JSON artifacts.

## Files

- `data/creditcard.csv` - raw dataset
- `preprocess_creditcard.py` - preprocessing pipeline
- `processed/*.json` - generated dashboard data
- `../index.html` - final visualization page (served from repo root)
- `sample/css/dashboard.css` - extracted dashboard styles
- `sample/js/dashboard.js` - extracted dashboard logic

## Generate Processed Data

From `FINALS-PROJECT/` run:

```bash
python preprocess_creditcard.py
```

Optional arguments:

```bash
python preprocess_creditcard.py --max-legit-points 12000 --seed 42
```

## Publish and View on GitHub Pages

This project is static (HTML + JSON), so it can run directly on GitHub Pages with no backend and no localhost database server.

### 1. Make sure processed artifacts exist

From `FINALS-PROJECT/`:

```bash
python preprocess_creditcard.py
```

Confirm these files are present and committed:

- `processed/overview.json`
- `processed/distributions.json`
- `processed/sample_points.json`
- `processed/metrics.json`

### 2. Push to GitHub

Commit and push your repository so the latest `FINALS-PROJECT/processed/*.json` files are available online.

### 3. Enable GitHub Pages

In GitHub:

- Open repository `Settings` -> `Pages`
- Under `Build and deployment`, set `Source` to `Deploy from a branch`
- Select branch `main` (or your active branch) and folder `/ (root)`
- Save

### 4. Open the live dashboard URL

Use the GitHub Pages URL pattern:

- `https://<your-username>.github.io/<your-repo>/`

The dashboard reads data from:

- `../processed/*.json`

which resolves correctly on GitHub Pages.

## Local Preview (Optional)

If you still want to preview before pushing, you can run:

```bash
python -m http.server 8000
```

Then open:

- `http://localhost:8000/`

## Notes

- The metrics section uses a heuristic ranking score to produce a precision-recall curve and AUPRC-oriented interpretation.
- This is for analysis and visualization, not a production fraud detector.
