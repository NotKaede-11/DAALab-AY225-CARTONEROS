# FINALS PROJECT - Fraud Risk Analysis Dashboard

This folder contains the data pipeline and supporting assets for the fraud-risk dashboard used by the root-level `../index.html`.

The main app is served from the repository root, while `FINALS-PROJECT/` holds the source dataset, preprocessing script, processed JSON files, and extracted sample assets.

## What the Root Dashboard Does

The root `index.html` loads processed transaction points from `FINALS-PROJECT/processed/sample_points.json` and maps them into dashboard-friendly fields in the browser, including:

- `riskScore`
- `amountIndex`
- `timeOfDay`

It then renders:

- descriptive statistics such as min, max, range, variance, and standard deviation
- correlation analysis for `amountIndex -> riskScore` and `timeOfDay -> riskScore`
- a linear regression summary with equation, slope, intercept, `R^2`, and prediction at index `15`
- a narrative insights panel based on the computed results

## Folder Contents

- `data/creditcard.csv` - raw source dataset
- `data-new/` - additional dataset files kept alongside the main input set
- `preprocess_creditcard.py` - preprocessing script for generating processed outputs
- `processed/sample_points.json` - primary dataset consumed by the root dashboard
- `processed/overview.json` - summary metadata
- `processed/distributions.json` - distribution-oriented processed output
- `processed/metrics.json` - metrics-oriented processed output
- `processed/embedded_bundle.js` - generated supporting bundle
- `index.html` - alternate dashboard file inside `FINALS-PROJECT`
- `sample/css/dashboard.css` - extracted styling reference
- `sample/js/dashboard.js` - extracted JavaScript reference

## Generate the Processed Data

From inside `FINALS-PROJECT/`, run:

```bash
python preprocess_creditcard.py
```

Optional example:

```bash
python preprocess_creditcard.py --max-legit-points 12000 --seed 42
```

After preprocessing, make sure `processed/sample_points.json` exists because that is the key file used by the root dashboard.

## How the Root Page Finds the Data

The root dashboard tries a few relative paths so it can work from different locations, but the intended repository layout is:

- root page: `../index.html`
- processed data: `processed/sample_points.json`

When the root page is opened from the repository root, it resolves the dataset from:

- `FINALS-PROJECT/processed/sample_points.json`

When the in-folder `FINALS-PROJECT/index.html` is used, it can resolve:

- `processed/sample_points.json`

## GitHub Pages Notes

This project is static, so it can run on GitHub Pages without a backend.

For the hosted version to work correctly:

- commit the root `index.html`
- commit `FINALS-PROJECT/processed/sample_points.json`
- keep folder names and file casing exactly the same
- publish from the repository root

If the processed JSON is missing from GitHub, the live page will not be able to load the exact processed fraud dataset.

## Local Preview

To preview with fetch requests working, serve the repository through a local web server instead of opening the HTML file directly:

```bash
python -m http.server 8000
```

Then open:

```text
http://localhost:8000/
```

## Summary

Use the root `index.html` as the main dashboard entry point.

Use this `FINALS-PROJECT/` folder for:

- preparing the processed dataset
- storing the JSON artifacts the dashboard reads
- keeping supporting assets and references for the final project
