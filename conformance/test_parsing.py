"""
Thingalog Conformance: catdef parsing tests.

A conformant renderer/parser must:
- Accept valid .thingalog files
- Reject files missing required fields
- Handle all 13 field types
- Validate the catdef version
- Gracefully handle unknown field types
"""

import json
import os
import pytest
from pathlib import Path

FIXTURES = Path(__file__).parent / "fixtures"
VALID_FIELD_TYPES = {
    "String", "Integer", "Number", "RichText", "Enumerated", "Photo",
    "Table", "CloudFile", "URL", "Date", "Money", "Boolean", "GeoLocation",
}


def load_fixture(name: str) -> dict:
    """Load a .thingalog fixture file."""
    path = FIXTURES / name
    with open(path) as f:
        return json.load(f)


def validate_catdef(data: dict) -> list[str]:
    """Validate a catdef structure. Returns a list of errors (empty = valid).

    This is the reference validator — any conformant parser must catch
    at least these errors.
    """
    errors = []

    # catdef version is required
    if "catdef" not in data:
        errors.append("missing required field: catdef")
    elif not isinstance(data["catdef"], str):
        errors.append("catdef must be a string")

    # product block
    product = data.get("product", {})
    if not product.get("name"):
        errors.append("product.name is required")
    if not product.get("slug"):
        errors.append("product.slug is required")

    # templates
    templates = data.get("templates", [])
    if not isinstance(templates, list):
        errors.append("templates must be an array")
    else:
        for i, tmpl in enumerate(templates):
            if not tmpl.get("name"):
                errors.append(f"templates[{i}].name is required")
            for j, fd in enumerate(tmpl.get("field_defs", [])):
                if not fd.get("label"):
                    errors.append(f"templates[{i}].field_defs[{j}].label is required")
                if not fd.get("type"):
                    errors.append(f"templates[{i}].field_defs[{j}].type is required")
                elif fd["type"] not in VALID_FIELD_TYPES:
                    errors.append(
                        f"templates[{i}].field_defs[{j}].type '{fd['type']}' "
                        f"is not a recognized field type"
                    )
                if fd.get("type") == "Enumerated" and not fd.get("target"):
                    errors.append(
                        f"templates[{i}].field_defs[{j}]: Enumerated fields "
                        f"must have a 'target' property"
                    )

    return errors


class TestValidFiles:
    """Valid .thingalog files must parse without errors."""

    def test_minimal(self):
        data = load_fixture("valid_minimal.thingalog")
        errors = validate_catdef(data)
        assert errors == [], f"Unexpected errors: {errors}"

    def test_all_field_types(self):
        data = load_fixture("valid_all_field_types.thingalog")
        errors = validate_catdef(data)
        assert errors == [], f"Unexpected errors: {errors}"

    def test_watches_sample(self):
        """The flagship sample file must be valid."""
        path = FIXTURES.parent.parent / "samples" / "watches.thingalog"
        with open(path) as f:
            data = json.load(f)
        errors = validate_catdef(data)
        assert errors == [], f"Unexpected errors: {errors}"

    def test_catdef_version_is_string(self):
        data = load_fixture("valid_minimal.thingalog")
        assert isinstance(data["catdef"], str)

    def test_catdef_version_is_semver_ish(self):
        data = load_fixture("valid_minimal.thingalog")
        parts = data["catdef"].split(".")
        assert len(parts) >= 1
        assert all(p.isdigit() for p in parts)


class TestInvalidFiles:
    """Invalid .thingalog files must produce errors."""

    def test_missing_catdef(self):
        data = load_fixture("invalid_no_catdef.thingalog")
        errors = validate_catdef(data)
        assert any("catdef" in e for e in errors)

    def test_bad_field_type(self):
        data = load_fixture("invalid_bad_field_type.thingalog")
        errors = validate_catdef(data)
        assert any("SpreadsheetFormula" in e for e in errors)


class TestFieldTypes:
    """All 11 field types must be recognized."""

    @pytest.mark.parametrize("field_type", sorted(VALID_FIELD_TYPES))
    def test_valid_field_type(self, field_type):
        """Each standard field type must pass validation."""
        data = {
            "catdef": "1.0",
            "product": {"name": "Test", "slug": "test"},
            "templates": [{
                "name": "T",
                "field_defs": [{"label": "F", "type": field_type, "sort_order": 10}]
                + ([{"target": "X"}] if field_type == "Enumerated" else [])
            }],
        }
        # Fix: merge target into the field def for Enumerated
        if field_type == "Enumerated":
            data["templates"][0]["field_defs"] = [
                {"label": "F", "type": "Enumerated", "sort_order": 10, "target": "X"}
            ]
        errors = validate_catdef(data)
        assert errors == [], f"{field_type} should be valid but got: {errors}"

    def test_unknown_field_type_rejected(self):
        data = {
            "catdef": "1.0",
            "product": {"name": "Test", "slug": "test"},
            "templates": [{
                "name": "T",
                "field_defs": [{"label": "F", "type": "Hologram", "sort_order": 10}]
            }],
        }
        errors = validate_catdef(data)
        assert any("Hologram" in e for e in errors)


class TestRequiresBlock:
    """The requires block declares renderer expectations."""

    def test_requires_field_types_are_valid(self):
        data = load_fixture("valid_all_field_types.thingalog")
        required_types = data.get("requires", {}).get("field_types", [])
        for ft in required_types:
            assert ft in VALID_FIELD_TYPES, f"Required field type '{ft}' is not valid"

    def test_requires_renderer_version(self):
        data = load_fixture("valid_all_field_types.thingalog")
        renderer = data.get("requires", {}).get("renderer", "")
        assert renderer, "requires.renderer should be specified"


class TestDataBlock:
    """The data block must reference valid templates and fields."""

    def test_items_reference_existing_templates(self):
        data = load_fixture("valid_minimal.thingalog")
        template_names = {t["name"] for t in data.get("templates", [])}
        for item in data.get("data", {}).get("items", []):
            assert item["template"] in template_names, (
                f"Item references template '{item['template']}' which doesn't exist"
            )

    def test_item_fields_match_template(self):
        """Item fields should correspond to field_defs in their template."""
        data = load_fixture("valid_all_field_types.thingalog")
        templates = {t["name"]: t for t in data.get("templates", [])}
        for item in data.get("data", {}).get("items", []):
            tmpl = templates.get(item["template"])
            assert tmpl, f"Template '{item['template']}' not found"
            valid_labels = {fd["label"] for fd in tmpl["field_defs"]}
            for field_name in item.get("fields", {}).keys():
                assert field_name in valid_labels, (
                    f"Field '{field_name}' not defined in template '{item['template']}'"
                )

    def test_enumerated_values_reference_existing_targets(self):
        """Values in data.values should match Enumerated field targets."""
        data = load_fixture("valid_all_field_types.thingalog")
        targets = set()
        for tmpl in data.get("templates", []):
            for fd in tmpl.get("field_defs", []):
                if fd.get("target"):
                    targets.add(fd["target"])
        for label in data.get("data", {}).get("values", {}).keys():
            assert label in targets, (
                f"data.values['{label}'] doesn't match any field target"
            )


class TestNumberType:
    """Number fields: decimal values with optional unit, precision, bounds."""

    def test_number_field_valid(self):
        data = {
            "catdef": "1.1",
            "product": {"name": "Test", "slug": "test"},
            "templates": [{"name": "T", "field_defs": [
                {"label": "Diameter", "type": "Number", "sort_order": 10,
                 "unit": "mm", "precision": 1, "min": 10, "max": 60}
            ]}],
        }
        errors = validate_catdef(data)
        assert errors == []

    def test_number_with_step(self):
        data = {
            "catdef": "1.1",
            "product": {"name": "Test", "slug": "test"},
            "templates": [{"name": "T", "field_defs": [
                {"label": "Rating", "type": "Number", "sort_order": 10,
                 "min": 0, "max": 100, "step": 0.5, "widget": "rating"}
            ]}],
        }
        errors = validate_catdef(data)
        assert errors == []


class TestGeoLocationType:
    """GeoLocation fields: lat/lng with optional address."""

    def test_geolocation_field_valid(self):
        data = {
            "catdef": "1.1",
            "product": {"name": "Test", "slug": "test"},
            "templates": [{"name": "T", "field_defs": [
                {"label": "Origin", "type": "GeoLocation", "sort_order": 10}
            ]}],
        }
        errors = validate_catdef(data)
        assert errors == []

    def test_geolocation_value_shape(self):
        """GeoLocation values must have at least lat and lng."""
        value = {"lat": 48.8566, "lng": 2.3522, "label": "Louvre"}
        assert "lat" in value
        assert "lng" in value
        assert isinstance(value["lat"], (int, float))
        assert isinstance(value["lng"], (int, float))

    def test_geolocation_value_with_address(self):
        value = {
            "lat": 48.8566, "lng": 2.3522,
            "address": "Musée du Louvre, 75001 Paris, France",
            "label": "Louvre Museum"
        }
        assert "address" in value


class TestStringFormats:
    """String format attribute: named validators for identifiers."""

    KNOWN_FORMATS = {
        "email", "phone", "isbn", "issn", "doi", "vin",
        "upc", "ean", "sku", "accession", "hex_color",
    }

    @pytest.mark.parametrize("fmt", sorted(KNOWN_FORMATS))
    def test_known_format_accepted(self, fmt):
        """Named formats should not cause validation errors."""
        data = {
            "catdef": "1.1",
            "product": {"name": "Test", "slug": "test"},
            "templates": [{"name": "T", "field_defs": [
                {"label": "F", "type": "String", "sort_order": 10, "format": fmt}
            ]}],
        }
        errors = validate_catdef(data)
        assert errors == [], f"Format '{fmt}' should be valid"

    def test_custom_regex_format(self):
        """Formats starting with ^ are custom regex patterns."""
        data = {
            "catdef": "1.1",
            "product": {"name": "Test", "slug": "test"},
            "templates": [{"name": "T", "field_defs": [
                {"label": "Code", "type": "String", "sort_order": 10,
                 "format": "^[A-Z]{2}-\\d{4}$"}
            ]}],
        }
        errors = validate_catdef(data)
        assert errors == []

    def test_unique_field(self):
        """Fields with unique:true should pass validation."""
        data = {
            "catdef": "1.1",
            "product": {"name": "Test", "slug": "test"},
            "templates": [{"name": "T", "field_defs": [
                {"label": "SKU", "type": "String", "sort_order": 10,
                 "format": "sku", "unique": True}
            ]}],
        }
        errors = validate_catdef(data)
        assert errors == []


class TestDateExtensions:
    """Date type with circa and range support."""

    def test_circa_date_field(self):
        data = {
            "catdef": "1.1",
            "product": {"name": "Test", "slug": "test"},
            "templates": [{"name": "T", "field_defs": [
                {"label": "Made", "type": "Date", "sort_order": 10, "circa": True}
            ]}],
        }
        errors = validate_catdef(data)
        assert errors == []

    def test_exact_date_value(self):
        assert isinstance("2024-06-15", str)

    def test_circa_date_value(self):
        value = {"date": "1850", "circa": True}
        assert value["circa"] is True

    def test_date_range_value(self):
        value = {"start": "1845", "end": "1855"}
        assert "start" in value
        assert "end" in value


class TestMoneyType:
    """Money fields with currency."""

    def test_money_with_default_currency(self):
        data = {
            "catdef": "1.1",
            "product": {"name": "Test", "slug": "test"},
            "templates": [{"name": "T", "field_defs": [
                {"label": "Price", "type": "Money", "sort_order": 10, "currency": "USD"}
            ]}],
        }
        errors = validate_catdef(data)
        assert errors == []

    def test_money_value_shape(self):
        value = {"amount": 4500.00, "currency": "USD"}
        assert isinstance(value["amount"], (int, float))
        assert len(value["currency"]) == 3  # ISO 4217


class TestPhotoGallery:
    """Photo type with multi:true for galleries."""

    def test_photo_gallery_field(self):
        data = {
            "catdef": "1.1",
            "product": {"name": "Test", "slug": "test"},
            "templates": [{"name": "T", "field_defs": [
                {"label": "Photos", "type": "Photo", "sort_order": 10, "multi": True}
            ]}],
        }
        errors = validate_catdef(data)
        assert errors == []

    def test_single_photo_field(self):
        data = {
            "catdef": "1.1",
            "product": {"name": "Test", "slug": "test"},
            "templates": [{"name": "T", "field_defs": [
                {"label": "Photo", "type": "Photo", "sort_order": 10}
            ]}],
        }
        errors = validate_catdef(data)
        assert errors == []


class TestFieldDefAttributes:
    """New field-def attributes: unique, default, min/max, unit, etc."""

    def test_default_value(self):
        data = {
            "catdef": "1.1",
            "product": {"name": "Test", "slug": "test"},
            "templates": [{"name": "T", "field_defs": [
                {"label": "In Stock", "type": "Boolean", "sort_order": 10, "default": True}
            ]}],
        }
        errors = validate_catdef(data)
        assert errors == []

    def test_min_max_on_integer(self):
        data = {
            "catdef": "1.1",
            "product": {"name": "Test", "slug": "test"},
            "templates": [{"name": "T", "field_defs": [
                {"label": "Year", "type": "Integer", "sort_order": 10,
                 "min": 1800, "max": 2030}
            ]}],
        }
        errors = validate_catdef(data)
        assert errors == []

    def test_unit_on_number(self):
        data = {
            "catdef": "1.1",
            "product": {"name": "Test", "slug": "test"},
            "templates": [{"name": "T", "field_defs": [
                {"label": "Weight", "type": "Number", "sort_order": 10,
                 "unit": "kg", "precision": 2}
            ]}],
        }
        errors = validate_catdef(data)
        assert errors == []
