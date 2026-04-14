"""
Conformance tests for item field values (CATDEF_SPEC.md §"Field Types").

A conformant validator must check that item.fields values match the type
declared in their template's field_def:

- Integer / Number: JSON number
- String / RichText / URL / Date: JSON string
- Boolean: JSON boolean
- Enumerated (single): string that exists in data.values[target]
- Enumerated (multi): array of such strings
- Money: object with numeric 'amount' and 3-letter ISO 'currency'
- GeoLocation: object with numeric 'lat' and 'lng'
"""

import json
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


def _is_number(x) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def _load(name: str) -> dict:
    with open(FIXTURES / name) as f:
        return json.load(f)


def validate_field_value(label: str, value, fd: dict, values_map: dict) -> list[str]:
    """Validate a single item field value against its field_def."""
    errors = []
    ftype = fd.get("type")
    multi = bool(fd.get("multi"))

    def bad(msg):
        errors.append(f"field {label!r}: {msg}")

    if ftype == "Integer":
        if not (isinstance(value, int) and not isinstance(value, bool)):
            bad(f"expected Integer, got {type(value).__name__}={value!r}")
    elif ftype == "Number":
        if not _is_number(value):
            bad(f"expected Number, got {type(value).__name__}={value!r}")
    elif ftype in ("String", "RichText", "URL", "Date"):
        if not isinstance(value, str):
            bad(f"expected {ftype} string, got {type(value).__name__}")
    elif ftype == "Boolean":
        if not isinstance(value, bool):
            bad(f"expected Boolean, got {type(value).__name__}")
    elif ftype == "Money":
        if not isinstance(value, dict):
            bad(f"expected Money object, got {type(value).__name__}")
        else:
            if not _is_number(value.get("amount")):
                bad("Money.amount must be a number")
            currency = value.get("currency")
            if not isinstance(currency, str) or len(currency) != 3:
                bad("Money.currency must be a 3-letter ISO code")
    elif ftype == "GeoLocation":
        if not isinstance(value, dict):
            bad(f"expected GeoLocation object, got {type(value).__name__}")
        else:
            if not _is_number(value.get("lat")):
                bad("GeoLocation.lat must be a number")
            if not _is_number(value.get("lng")):
                bad("GeoLocation.lng must be a number")
    elif ftype == "Enumerated":
        target = fd.get("target")
        allowed = set(values_map.get(target, []))
        if multi:
            if not isinstance(value, list):
                bad("Enumerated multi: expected array")
            else:
                for v in value:
                    if not isinstance(v, str):
                        bad(f"Enumerated value must be string, got {v!r}")
                    elif allowed and v not in allowed:
                        bad(f"{v!r} not in data.values[{target!r}]")
        else:
            if not isinstance(value, str):
                bad("Enumerated single: expected string")
            elif allowed and value not in allowed:
                bad(f"{value!r} not in data.values[{target!r}]")
    # Photo, Table, CloudFile values live outside the fields object and are
    # validated elsewhere (photos handled in test_photo_transforms).

    return errors


def validate_item_field_values(data: dict) -> list[str]:
    """Walk every item.fields entry in a catalog."""
    errors = []
    templates = {t["name"]: t for t in data.get("templates", [])}
    values_map = data.get("data", {}).get("values", {})
    for i, item in enumerate(data.get("data", {}).get("items", [])):
        tmpl = templates.get(item.get("template"))
        if not tmpl:
            continue  # template-existence is covered by test_parsing.TestDataBlock
        fields_by_label = {fd["label"]: fd for fd in tmpl.get("field_defs", [])}
        for label, value in (item.get("fields") or {}).items():
            fd = fields_by_label.get(label)
            if not fd:
                continue  # field-existence is covered elsewhere
            for e in validate_field_value(label, value, fd, values_map):
                errors.append(f"items[{i}] {e}")
    return errors


class TestValidValues:
    def test_minimal_fixture_clean(self):
        data = _load("valid_minimal.thingalog")
        errors = validate_item_field_values(data)
        assert errors == [], f"Unexpected errors: {errors}"

    def test_all_field_types_fixture_clean(self):
        data = _load("valid_all_field_types.thingalog")
        errors = validate_item_field_values(data)
        assert errors == [], f"Unexpected errors: {errors}"


class TestIntegerField:
    def test_fixture_catches_string_in_integer(self):
        data = _load("invalid_integer_field_value.thingalog")
        errors = validate_item_field_values(data)
        assert any("Integer" in e and "Year" in e for e in errors)

    @pytest.mark.parametrize("bad", ["1969", 1969.5, True, None])
    def test_rejects_non_integer(self, bad):
        fd = {"label": "Year", "type": "Integer"}
        errors = validate_field_value("Year", bad, fd, {})
        assert errors, f"value {bad!r} should be rejected"


class TestEnumeratedField:
    def test_fixture_catches_unknown_value(self):
        data = _load("invalid_enumerated_value.thingalog")
        errors = validate_item_field_values(data)
        assert any("Casio" in e and "Brand" in e for e in errors)

    def test_accepts_value_in_map(self):
        fd = {"label": "Brand", "type": "Enumerated", "target": "Brand"}
        errors = validate_field_value("Brand", "Omega", fd, {"Brand": ["Omega"]})
        assert errors == []

    def test_multi_accepts_array_of_known(self):
        fd = {"label": "Tags", "type": "Enumerated", "target": "Tag", "multi": True}
        errors = validate_field_value("Tags", ["a", "b"], fd, {"Tag": ["a", "b", "c"]})
        assert errors == []

    def test_multi_rejects_unknown_entry(self):
        fd = {"label": "Tags", "type": "Enumerated", "target": "Tag", "multi": True}
        errors = validate_field_value("Tags", ["a", "nope"], fd, {"Tag": ["a", "b"]})
        assert any("nope" in e for e in errors)


class TestMoneyField:
    def test_valid_money(self):
        fd = {"label": "Price", "type": "Money"}
        errors = validate_field_value("Price", {"amount": 42.5, "currency": "USD"}, fd, {})
        assert errors == []

    def test_rejects_bad_currency(self):
        fd = {"label": "Price", "type": "Money"}
        errors = validate_field_value("Price", {"amount": 1, "currency": "US"}, fd, {})
        assert any("currency" in e for e in errors)

    def test_rejects_non_numeric_amount(self):
        fd = {"label": "Price", "type": "Money"}
        errors = validate_field_value("Price", {"amount": "forty", "currency": "USD"}, fd, {})
        assert any("amount" in e for e in errors)


class TestGeoLocationField:
    def test_valid_geo(self):
        fd = {"label": "Where", "type": "GeoLocation"}
        errors = validate_field_value("Where", {"lat": 48.8, "lng": 2.3}, fd, {})
        assert errors == []

    def test_rejects_missing_lng(self):
        fd = {"label": "Where", "type": "GeoLocation"}
        errors = validate_field_value("Where", {"lat": 48.8}, fd, {})
        assert any("lng" in e for e in errors)


class TestBooleanField:
    def test_rejects_string_true(self):
        fd = {"label": "InStock", "type": "Boolean"}
        errors = validate_field_value("InStock", "true", fd, {})
        assert errors
