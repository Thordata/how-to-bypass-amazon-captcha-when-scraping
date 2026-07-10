"""Tests for JSON/CSV export helpers."""

from __future__ import annotations

import csv
import json

from amazon_captcha.export import PRODUCT_COLUMNS, to_csv, to_json


def test_to_json_writes_pretty(tmp_path):
    data = {"a": 1, "b": [1, 2, {"c": "é"}]}
    path = to_json(data, tmp_path / "out" / "f.json")
    text = path.read_text(encoding="utf-8")
    assert json.loads(text) == data
    # Pretty-printed (2-space indent).
    assert "\n" in text
    # Unicode preserved.
    assert "é" in text


def test_to_csv_writes_header_and_rows(tmp_path):
    rows = [
        {"asin": "B001", "title": "Widget", "final_price": 9.99},
        {"asin": "B002", "title": "Gadget", "final_price": 19.99, "currency": "USD"},
    ]
    path = to_csv(rows, tmp_path / "f.csv")
    with path.open(encoding="utf-8") as f:
        reader = list(csv.DictReader(f))
    assert reader[0]["asin"] == "B001"
    assert reader[1]["currency"] == "USD"
    # Missing key becomes empty cell.
    assert reader[0]["currency"] == ""
    assert len(reader) == 2


def test_to_csv_explicit_columns(tmp_path):
    rows = [{"asin": "A", "title": "T", "extra": "x"}]
    path = to_csv(rows, tmp_path / "f.csv", columns=PRODUCT_COLUMNS)
    with path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        first = next(reader)
    assert list(first.keys())[: len(PRODUCT_COLUMNS)] == PRODUCT_COLUMNS
    assert "extra" not in first  # extrasaction="ignore"


def test_product_columns_has_stable_order():
    assert PRODUCT_COLUMNS[0] == "asin"
    assert "title" in PRODUCT_COLUMNS


def test_to_csv_empty_rows(tmp_path):
    path = to_csv([], tmp_path / "f.csv")
    # Header line only, no data rows.
    text = path.read_text(encoding="utf-8").strip()
    assert text == ""
