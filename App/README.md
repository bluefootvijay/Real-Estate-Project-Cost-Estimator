# TNRERA AVM Dashboard

## What's missing before this runs

This folder has everything except the three model artifact files, because
those only exist after you run the export cell in your own notebook:

1. Open `04_TNRERA_MODELLING.ipynb`, run the export cell at the end (after
   the model comparison + your final selection writeup):

   ```python
   import joblib
   joblib.dump(lgb_model, 'lgbm_avm_model.pkl')
   feature_columns = X.columns.tolist()
   joblib.dump(feature_columns, 'lgbm_avm_features.pkl')
   joblib.dump(categorical_cols, 'lgbm_avm_categorical_cols.pkl')
   ```

2. Move the three resulting `.pkl` files into `models/` in this folder.

The `data/tnrera_projects_for_modelling.csv` is already included.

## Running locally

```bash
cd dashboard
pip install -r requirements.txt
streamlit run app.py
```

This opens the app in your browser at `http://localhost:8501`. The sidebar
lets you switch between the Price Predictor and Model Analysis pages.

## Deploying to Streamlit Community Cloud

1. Push this entire `dashboard/` folder to a GitHub repo (the `.pkl` files
   included — they're small enough; LightGBM models are typically a few MB).
2. Go to [share.streamlit.io](https://share.streamlit.io), connect your
   GitHub account, and point it at this repo with `app.py` as the entry file.
3. Deploy. You'll get a public `*.streamlit.app` URL to put on your resume,
   LinkedIn, and portfolio.

No secrets or API keys are needed — everything runs from the bundled data
and model files.
