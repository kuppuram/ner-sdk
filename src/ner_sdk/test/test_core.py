# tests/test_core.py
from ner_sdk.labeler import generate_ner_labels

def test_core_score_date():
    s = "top 10 trends for the last quarter of 2019 with 4 or above score"
    labels = generate_ner_labels(s)
    # sanity checks
    assert "B-TOPK" in labels
    assert "B-DATE" in labels
    assert "B-YEAR" in labels
    assert labels.count("B-SCORE") == 1  # "4 or above" should be a single span

def test_core_month_year():
    s = "analyze reviews from sept 2012 to dec 2013"
    labels = generate_ner_labels(s)
    assert "B-MONTH" in labels
    assert labels.count("B-YEAR") == 2
