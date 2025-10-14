# tests/test_finance_pack.py
from ner_sdk.labeler import generate_ner_labels

FIN = ["ner_sdk.domains.finance"]

def test_money_percent_ticker():
    s = "AAPL rose 5% to $150 in Q2"
    labels = generate_ner_labels(s, domains=FIN)
    assert "B-TICKER" in labels
    assert "B-PERCENT" in labels
    assert "B-MONEY" in labels
    assert "B-DATE_Q" in labels

def test_percent_range_hook():
    s = "growth at least 4% expected"
    labels = generate_ner_labels(s, domains=FIN)
    assert "B-PERCENT_RANGE" in labels
