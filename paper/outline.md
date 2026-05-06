# Words and Money at ECOSOC

**Authors:** Tahvia Williams, Ada Meltzer, Vadim Rudic, Enrico Madani
**Course:** BUSN 20800 — Big Data
**Submit:** May 26, 2026

---

## Abstract  *(150 words — Enrico drafts last)*

Question, data, method, headline result, one sentence on limitations.

## 1. Introduction  *(Enrico, ~1 page)*

- The puzzle: do international institutions' stated priorities match where their money flows?
- Why ECOSOC: focused mandate, accessible transcripts, parallel UN-internal vs. World Bank money.
- Three questions (Q1 alignment, Q2 prediction, Q3 comparison).
- Headline finding placeholder.

## 2. Data  *(Vadim, ~1 page)*

### 2.1 ECOSOC summary records
Source `documents.un.org`, 2000–2026, ~1,200 PDFs harvested via the symbol-access API. Cite [UN Digital Library].

### 2.2 UN agency revenue
CEB Financial Statistics (`pivot.csv`), 19 ECOSOC-relevant agencies. Cite UN System Chief Executives Board.

### 2.3 World Bank projects
Projects API (`search.worldbank.org/api/v2/projects`), ~22,700 projects. Sector / theme / country / amount / approval date.

### 2.4 Controls
WDI macro indicators (8 variables), UN ideal-point estimates.

Table 1: corpus size, year coverage, total commitments. *(Vadim: produce in `01_corpus_eda.ipynb`.)*

## 3. Methods  *(Enrico, ~1.5 pages, with Tahvia + Ada filling subsections)*

### 3.1 Text preprocessing
Boilerplate regex filter; sentence split; aggregation to (year, segment) blocks.

### 3.2 Feature tiers
- Tier 1: length + VADER sentiment + 7 lexicons.
- Tier 2: TF-IDF (2,000 × 1–2 grams).
- Tier 3: `all-MiniLM-L6-v2` mean-pooled embeddings.

### 3.3 Topic model  *(Tahvia)*
LDA, k chosen by coherence over {6, 10, 15}. Topic→sector / topic→agency mapping by cosine similarity over top-30 topic words.

### 3.4 Supervised setup  *(Ada)*
T1 regression `log(spend_t / spend_{t-1})`; T2 classification `1{>10% YoY}`.
Time-based split: train ≤ 2019, val 2020–2021, test 2022–2024.
Ablation across `numeric_only / +tier1 / +tier2 / +tier3`.
Models: OLS, Ridge, Lasso, Logistic, RF, GBM, MLP.

### 3.5 Validation
50-transcript human-labeled sample; agreement rate vs. LDA top-3 reported.

## 4. Results

### 4.1 Q1 — Alignment  *(Tahvia, ~1 page)*
- Heatmap: yearly topic share × yearly UN spending share by mapped agency. Same against WB sector share.
- Two paragraphs: where topics and money agree, where they diverge.
- Figure: `topic_heatmap.png`, `archetype_umap.png`.

### 4.2 Q2 — Prediction  *(Ada, ~1 page)*
- Ablation table (Table 2): RMSE/MAE for T1, AUC/F1 for T2, by feature tier and model.
- Headline: best model + uplift over numeric-only baseline.
- Figure: `ablation_bars.png`.

### 4.3 Q3 — Comparison  *(Ada + Tahvia, ~½ page)*
- Compare R² uplift from text features when target is UN-agency revenue vs. when target is WB-sector commitments. Which institution's money tracks ECOSOC text better?

## 5. Discussion + limitations  *(Enrico, ~½ page)*

- Three honest cautions:
  1. Summary records summarize — boilerplate dominance risk; mitigated by filter + human validation.
  2. UN agency mandates are legally fixed → some misalignment is structural.
  3. WB is not under ECOSOC authority → Q3 is descriptive, not normative.
- External validity: 25-year T-axis is short; effect sizes vs. p-values.
- Future work.

## 6. Conclusion  *(Enrico, 1 paragraph)*

## References

UN Digital Library. CEB Financial Statistics. World Bank Projects API. World Development Indicators (Bailey, Strezhnev & Voeten 2017 for ideal points). Tools: gensim, scikit-learn, sentence-transformers, VADER.

---

## Section ownership recap

| Section | Lead | Backup |
|---|---|---|
| §0 Abstract | Enrico | Tahvia |
| §1 Intro | Enrico | — |
| §2 Data | Vadim | Enrico |
| §3 Methods | Enrico (assembler) | Tahvia §3.3, Ada §3.4 |
| §4.1 Q1 results | Tahvia | — |
| §4.2 Q2 results | Ada | — |
| §4.3 Q3 results | Ada + Tahvia | — |
| §5 Discussion | Enrico | Vadim |
| §6 Conclusion | Enrico | — |

## Deadlines

- **May 20** — outline locked, all section owners have stub paragraphs in place.
- **May 24** — full draft circulated for group review.
- **May 26** — submit.
- **May 27** — present.
