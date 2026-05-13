"""Shared helpers for topic_model.ipynb and label_transcripts.ipynb.

Drop this file in the same folder as the notebooks. Both notebooks import
from it so the boilerplate filter, lexicons, and topic-to-theme mapping
are defined exactly once.
"""

from pathlib import Path
import numpy as np

# ---------------------------------------------------------------------------
# Project root. Override by setting the env var PROJECT_ROOT before launching
# Jupyter, e.g. `export PROJECT_ROOT=/Users/latahviawilliams/BUSN-...`.
# Falls back to the parent of this file so it works in any clone of the repo.
# ---------------------------------------------------------------------------
import os
PROJECT_ROOT = Path(os.environ.get(
    "PROJECT_ROOT",
    Path(__file__).resolve().parent,
))

DATA = PROJECT_ROOT / "data"
FIG_DIR = PROJECT_ROOT / "output" / "figures"

# ---------------------------------------------------------------------------
# Boilerplate filter. The raw tier2 TF-IDF has ~22 n-grams from the ECOSOC
# meeting-record header template. Drop them here so LDA learns substance.
# Tighten this list (or push it upstream into text_features.ipynb) if you
# spot more procedural strings in the top-words output.
# ---------------------------------------------------------------------------
BOILERPLATE = [
    "provisional", "records editing", "editing section", "section room",
    "room dc2", "dc2 750", "750 united", "nations plaza", "plaza",
    "chief official", "official records", "corrections record",
    "council provisional", "record submitted", "sent week", "week date",
    "date document", "document chief", "editing", "contents agenda",
    "panellist said",
]


def is_boilerplate(col: str) -> bool:
    """True if a TF-IDF column name contains a header-template phrase."""
    name = col[2:] if col.startswith("t_") else col
    return any(sub in name for sub in BOILERPLATE)


def filter_vocab(cols):
    """Return (kept, dropped) lists of TF-IDF column names."""
    kept = [c for c in cols if not is_boilerplate(c)]
    dropped = [c for c in cols if is_boilerplate(c)]
    return kept, dropped


# ---------------------------------------------------------------------------
# Lexicons. Used to map LDA topics to UN agencies and WB sectors via cosine
# similarity. These are deliberately short (5-7 tokens each) so each lexicon
# vector is a clean signal.
# ---------------------------------------------------------------------------
AGENCY_LEXICONS = {
    "FAO":       ["food", "agriculture", "fisheries", "nutrition", "crops", "hunger"],
    "IFAD":      ["rural", "smallholder", "agriculture", "poverty", "lending", "farmer"],
    "ILO":       ["labor", "employment", "workers", "wages", "decent", "rights"],
    "UNAIDS":    ["hiv", "aids", "epidemic", "prevention", "treatment", "stigma"],
    "UNCCD":     ["desertification", "land", "drought", "degradation", "soil", "drylands"],
    "UNCDF":     ["finance", "microfinance", "capital", "investment", "ldc", "inclusion"],
    "UNDP":      ["development", "poverty", "governance", "capacity", "sustainability"],
    "UNEP":      ["environment", "climate", "pollution", "biodiversity", "ecosystem"],
    "UNESCO":    ["education", "culture", "science", "heritage", "knowledge", "literacy"],
    "UNFCCC":    ["climate", "emissions", "carbon", "temperature", "mitigation", "paris"],
    "UNFPA":     ["population", "reproductive", "family", "maternal", "fertility", "sexual"],
    "UNHABITAT": ["urban", "housing", "cities", "slums", "shelter", "land"],
    "UNHCR":     ["refugees", "displacement", "asylum", "protection", "stateless", "return"],
    "UNICEF":    ["children", "child", "education", "vaccination", "nutrition", "immunization"],
    "UNIDO":     ["industry", "manufacturing", "trade", "technology", "energy", "production"],
    "UNRWA":     ["palestine", "refugees", "gaza", "west bank", "relief", "works"],
    "UNWOMEN":   ["gender", "women", "equality", "empowerment", "violence", "discrimination"],
    "WFP":       ["food", "hunger", "emergency", "nutrition", "assistance", "relief"],
    "WHO":       ["health", "disease", "pandemic", "medicine", "mortality", "epidemics"],
}

SECTOR_LEXICONS = {
    "health":      ["health", "disease", "hospital", "medicine", "nutrition", "pandemic"],
    "education":   ["education", "school", "literacy", "learning", "teacher", "university"],
    "agriculture": ["agriculture", "food", "farming", "rural", "crops", "irrigation"],
    "energy":      ["energy", "electricity", "renewable", "solar", "power", "grid"],
    "transport":   ["transport", "roads", "infrastructure", "bridges", "logistics", "highway"],
    "water":       ["water", "sanitation", "sewage", "irrigation", "drinking", "hygiene"],
    "finance":     ["finance", "banking", "credit", "microfinance", "fiscal", "budget"],
    "environment": ["environment", "climate", "forest", "biodiversity", "pollution", "carbon"],
}


# ---------------------------------------------------------------------------
# Direct topic -> theme mapping. Hand-judged from the top-10 words of the
# current LDA run. RE-JUDGE THIS DICT if you retrain LDA at a different k
# or change the boilerplate filter.
# ---------------------------------------------------------------------------
TOPIC_TO_THEME = {
    0: "development",   # resident coordinator, aid, oda, humanitarian assistance, 2030 agenda
    1: "development",   # developed countries, climate change, summit, world bank
    2: "climate",       # summit, climate change, forests, ministerial
    3: "development",   # developed countries, climate, mdgs, employment
    4: "governance",    # developed countries, capacity building, palestinian, monetary
    5: "health",        # unaids, epidemic, pandemic, peacekeeping
}

THEME_COLORS = {
    "development":  "#3b82f6",
    "humanitarian": "#f97316",
    "climate":      "#10b981",
    "gender":       "#ec4899",
    "conflict":     "#ef4444",
    "health":       "#a855f7",
    "governance":   "#6b7280",
    "finance":      "#eab308",
    "other":        "#9ca3af",
}


# ---------------------------------------------------------------------------
# Vector helpers for the topic->agency/sector cosine mapping.
# ---------------------------------------------------------------------------
def lexicon_vector(tokens, vocab):
    """Binary vector over `vocab` for any vocab word containing a lexicon token."""
    vec = np.zeros(len(vocab))
    for i, word in enumerate(vocab):
        if any(tok in word for tok in tokens):
            vec[i] = 1.0
    return vec


def topic_vector(lda_model, topic_id, vocab, topn=30):
    """Weighted vector over `vocab` for a topic's top-N words."""
    vec = np.zeros(len(vocab))
    vocab_idx = {w: i for i, w in enumerate(vocab)}
    for word, weight in lda_model.show_topic(topic_id, topn=topn):
        if word in vocab_idx:
            vec[vocab_idx[word]] = weight
    return vec


def year_to_top3_themes(assignments):
    """Map each year to the unique themes covered by its top-3 LDA topics."""
    out = {}
    for _, row in assignments.iterrows():
        mixture = row["topic_mixture"]
        top3 = sorted(range(len(mixture)), key=lambda i: -mixture[i])[:3]
        out[row["year"]] = sorted({TOPIC_TO_THEME[i] for i in top3})
    return out
