# ECOSOC Transcripts × UN/World Bank Spending

BUSN 20800 final project. Compares what ECOSOC says (summary-record transcripts, 2000–present) with where money actually flows (UN agency revenue from `pivot.csv`; World Bank project commitments from the WB Projects API).

## Layout

```
src/                pipeline scripts
notebooks/          analysis notebooks (01 EDA, 02 alignment, 03 supervised)
data/raw/           raw inputs (gitignored)
data/interim/       cleaned parquet panels
data/features/      tier1/2/3 feature tables
output/             figures and model results
```

## Run order

All work happens in `notebooks/`. Run in this order:

1. `harvest_ecosoc.ipynb` — downloads ECOSOC PDFs, writes `transcripts.parquet`.
2. `fetch_wb_projects.ipynb` — paginates WB Projects API, writes `wb_panel.parquet` + aggregates.
3. `build_un_panel.ipynb` — reshapes `pivot.csv`, writes `un_panel.parquet`.
4. `text_features.ipynb` — builds tier 1/2/3 features.
5. `topic_model.ipynb` — LDA + topic→sector/agency mapping.
6. `models.ipynb` — supervised ablation, writes `model_results.csv`.
7. `01_corpus_eda.ipynb`, `02_alignment_descriptive.ipynb`, `03_supervised.ipynb` — figures + writeup.

## Day-1 parallel bootstrap (so all four leads start at the same time)

Each person, on their own laptop:

1. Sync this folder.
2. `pip install pandas pyarrow requests pypdf pdfplumber scikit-learn vaderSentiment sentence-transformers gensim umap-learn matplotlib altair joblib`
3. Run `harvest_ecosoc.ipynb` with `START_YEAR=2023, END_YEAR=2023, MAX_MEETINGS=60` (~5 min, ~50 PDFs).
4. Run `build_un_panel.ipynb` (instant).
5. Run `text_features.ipynb` with `RUN_TIER3=False`.
6. Run `_make_stubs.ipynb` to create `wb_panel_stub.parquet` and `transcripts_padded_pilot.parquet`.

After step 6 every laptop has identical inputs. Each lead then works in their own lane (see "Workstreams" below) reading only files that already exist; no one is blocked on anyone else.

Vadim runs the full harvest + WB pull in the background; when those finish, replace the stubs and rerun.

## Workstreams (one writer per output)

| Lead | Notebook(s) owned | Reads | Writes (sole owner) |
|---|---|---|---|
| Tahvia | `topic_model.ipynb`, `02_alignment_descriptive.ipynb` | `tier2_tfidf.parquet`, `un_panel.parquet`, `wb_panel_stub.parquet` | `topic_assignments.parquet`, `output/figures/topic_heatmap.png`, `output/figures/archetype_umap.png` |
| Enrico | `models.ipynb`, `03_supervised.ipynb` | `tier{1,2,3}.parquet`, `un_panel.parquet`, `wb_panel_stub.parquet`, `wdi_controls.parquet` | `output/model_results.csv`, `output/figures/ablation_bars.png` |
| Vadim | `01_corpus_eda.ipynb`, full harvest, WB pull, WDI carving | live APIs, `WDICSV.csv` | `transcripts.parquet` (full), `wb_panel.parquet`, `wdi_controls.parquet`, `output/figures/corpus_growth.png` |
| Ada | `label_transcripts.ipynb`, `paper/outline.md` | `transcripts.parquet` | `transcripts_human_labels.csv`, `paper/outline.md`, `paper/draft.md` |

**Rule:** if you need to change a column name in a parquet listed below, ping the group chat first.

## Locked parquet schemas

`data/interim/transcripts.parquet`
- `year:int, meeting_n:int, meeting_id:str (E/{year}/SR.{n}), segment:str (SR), n_pages:int, text:str, n_chars:int, sha256:str, source_pdf:str`

`data/interim/un_panel.parquet`
- `agency:str, year:int, revenue_usd:float, n_subagencies:int, rev_*:float (one column per rev_type)`

`data/interim/wb_panel.parquet` (and `wb_panel_stub.parquet` matches this schema)
- `id:str, project_name:str, country:str, countrycode:str, region:str, sector1:str, theme1:str, sectors:str (semicolon-joined), themes:str (semicolon-joined), boardapprovaldate:datetime, approval_year:int, closingdate:str, status:str, totalamt:float, grantamt:float, lendinginstr:str, lendprojectcost:float`

`data/interim/wb_sector_year.parquet`
- `sector:str, year:int, totalamt_sum:float, grantamt_sum:float, project_count:int`

`data/interim/wb_country_year.parquet`
- `country:str, year:int, totalamt_sum:float, project_count:int`

`data/interim/wdi_controls.parquet`
- `country:str, countrycode:str, year:int, gdp_growth:float, oda_received:float, gov_expenditure_pct_gdp:float, life_expectancy:float, school_enrol_secondary:float, co2_per_capita:float, gini:float, fdi_inflows:float`

`data/features/tier1.parquet`
- `year:int, segment:str, n_meetings:int, n_tokens:int, sentiment:float, lex_development:float, lex_humanitarian:float, lex_climate:float, lex_gender:float, lex_conflict:float, lex_health:float, lex_governance:float`

`data/features/tier2_tfidf.parquet`
- `year:int, segment:str, t_*:float (≤2,000 columns)`

`data/features/tier3_embeddings.parquet`
- `year:int, segment:str, e_0..e_383:float`

## Data sources kept (extracted into `data/raw/`)

- `pivot.csv` — UN agency revenue (primary UN target).
- `un-secretariat-expenses.csv` — secretariat expenses by priority area (supplementary).
- `WDICSV.csv` — World Development Indicators (country-level macro controls).
- `Idealpointestimates1946-2025.csv` — UN voting ideal points (country political-alignment feature).
- `ecosoc_pdfs/` — populated by `harvest_ecosoc.py`.
- `wb_projects/` — populated by `fetch_wb_projects.py`.

## Data dropped from `Data.zip`

These were in the original bundle but are not used by this pivoted project:

- `OECD.SDD.NAD,DSD_NAAG_VI@DF_NAAG_OTEF,...csv` — OECD national-accounts; off-topic for ECOSOC alignment.
- `dataset_..._IMF.STA_QGFS_...csv` — IMF Quarterly Government Finance Statistics; redundant with WDI for our purposes.
- `GEDEvent_v26_01_26_03.csv`, `ged251-csv.zip` — UCDP geo-coded event data; conflict angle was dropped.
- `ucdp-prio-acd-251-csv.zip`, `ucdp-onesided-251-csv.zip`, `ucdp-actor-251-csv.zip`, `ucdp-nonstate-251-csv.zip`, `ucdp-brd-conf-251-csv.zip`, `organizedviolencecy-251-csv.zip` — UCDP/PRIO conflict datasets.
- `dataverse_files/AgreementScores*.Rdata`, `IdealPointDyads1946-2025.csv`, `IdealpointsJuly2025.dta` — redundant with the kept ideal-point CSV; dyad-level data not needed.

≈ 700 MB freed by skipping those.

## Honest cautions (to surface in the paper)

- ECOSOC summary records summarize, they don't transcribe verbatim — boilerplate dominance is a real risk.
- UN agency mandates are legally fixed; some "misalignment" is structural, not interesting.
- WB is not under ECOSOC authority — frame the WB comparison as "does WB *happen to* track" not "should it."
