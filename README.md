# Words and Money at ECOSOC

**Do international institutions' stated priorities match where their money actually flows?**

A text-as-data study of 26 years of UN Economic and Social Council proceedings, testing whether what ECOSOC *talks about* predicts what the UN system and the World Bank *fund*.

**Course:** BUSN 20800 — Big Data, University of Chicago (Spring 2026)
**Team:** La'Tahvia Williams, Ada Meltzer, Vadim Rudic, Enrico Madani

---

## Research questions

| | Question |
|---|---|
| **Q1 — Alignment** | Do the themes ECOSOC emphasizes in a given year line up with that year's funding allocations? |
| **Q2 — Prediction** | Do text features from the transcripts improve prediction of UN agency revenue over macro controls alone? |
| **Q3 — Comparison** | Does ECOSOC discourse track UN-internal spending more closely than World Bank lending? |

## Data

| Source | Scope | Retrieved via |
|---|---|---|
| ECOSOC summary records | ~1,200 PDFs, 2000–2026 | `documents.un.org` symbol-access API |
| UN agency revenue | 19 ECOSOC-relevant agencies | CEB Financial Statistics (`pivot.csv`) |
| World Bank projects | ~22,700 projects — sector, country, amount, approval date | Projects API |
| Controls | 8 WDI macro indicators, UN ideal-point estimates | World Bank WDI |

## Method

Text is cleaned with a boilerplate regex filter, sentence-split, and aggregated into `(year, segment)` blocks. Features are then built in tiers so each tier's marginal contribution can be isolated:

- **Tier 1** — document length, VADER sentiment, and 7 policy lexicons
- **Tier 2** — TF-IDF over 2,000 unigrams and bigrams
- **Tier 3** — `all-MiniLM-L6-v2` mean-pooled sentence embeddings

Five model classes (OLS, Ridge, Lasso, Random Forest, Gradient Boosting) are fit against each feature set. **Hyperparameters are held fixed across tiers on purpose** — the goal is a clean ablation showing what the text adds, not a tuned leaderboard.

## Headline result

Adding text features produces a large, monotonic drop in out-of-sample error on the UN revenue target:

| Feature set | OLS RMSE |
|---|---|
| `numeric_only` | 9.079 |
| `+tier1` | 2.824 |
| `+tier2` | **0.094** |

A total reduction of 8.985 — the largest tier gain of any model class. Full figures and per-model comparisons are in [`notebooks/03_supervised.ipynb`](notebooks/03_supervised.ipynb).

## Repository layout

```
notebooks/
  harvest_ecosoc.ipynb     Pull ECOSOC summary records from the UN API
  build_un_panel.ipynb     CEB revenue → (agency, year) panel
  fetch_wb_projects.ipynb  Paginate World Bank Projects API → yearly aggregates
  01_corpus_eda.ipynb      Corpus statistics, coverage, Table 1
  label_transcripts.ipynb  Theme labelling
  text_features.ipynb      Tier 1 / 2 / 3 feature construction
  topic_model.ipynb        Topic modelling
  topic_helpers.py         Shared topic-model utilities
  models.ipynb             Model fitting across feature tiers
  03_supervised.ipynb      Supervised results and figures

output/figures/            Generated charts (PNG + interactive HTML)
paper/outline.md           Paper structure and section ownership
```

## Reproducing

Notebooks are numbered in dependency order. Run the three harvest notebooks first — each caches raw responses to disk and skips work that already exists, so reruns are cheap.

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install pandas numpy scikit-learn statsmodels altair matplotlib seaborn requests vaderSentiment sentence-transformers
jupyter lab
```

Then execute in this order:

1. `harvest_ecosoc.ipynb` → `build_un_panel.ipynb` → `fetch_wb_projects.ipynb`
2. `01_corpus_eda.ipynb`
3. `label_transcripts.ipynb` → `text_features.ipynb` → `topic_model.ipynb`
4. `models.ipynb` → `03_supervised.ipynb`
