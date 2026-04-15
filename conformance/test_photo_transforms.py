"""
Conformance tests for photo transforms (CATDEF_SPEC.md §"Photo Transforms").

A conformant validator must check:
- rotation is one of 0, 90, 180, 270
- crop_mode is one of "none", "freeform", "deskew"
- freeform crop coords are in [0, 1] and x1 < x2, y1 < y2
- deskew has all four corners (tl, tr, br, bl), each with numeric x and y
- slot is a positive integer
"""

import json
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"

VALID_ROTATIONS = {0, 90, 180, 270}
VALID_CROP_MODES = {"none", "freeform", "deskew"}
DESKEW_CORNERS = ("tl", "tr", "br", "bl")


def _is_number(x) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def validate_photo_ref(ref: dict, index: int = 0) -> list[str]:
    """Validate a single photo reference object. Returns a list of errors."""
    errors = []
    prefix = f"photos[{index}]"

    if "filename" not in ref or not isinstance(ref["filename"], str):
        errors.append(f"{prefix}: filename is required and must be a string")

    slot = ref.get("slot")
    if slot is not None and not (isinstance(slot, int)
                                 and not isinstance(slot, bool)
                                 and slot >= 1):
        errors.append(f"{prefix}: slot must be a positive integer, got {slot!r}")

    rotation = ref.get("rotation")
    if rotation is not None and rotation not in VALID_ROTATIONS:
        errors.append(
            f"{prefix}: rotation must be one of {sorted(VALID_ROTATIONS)}, "
            f"got {rotation!r}"
        )

    crop_mode = ref.get("crop_mode")
    if crop_mode is not None and crop_mode not in VALID_CROP_MODES:
        errors.append(
            f"{prefix}: crop_mode must be one of "
            f"{sorted(VALID_CROP_MODES)}, got {crop_mode!r}"
        )

    if crop_mode == "freeform":
        coords = {k: ref.get(k) for k in ("crop_x1", "crop_y1", "crop_x2", "crop_y2")}
        for k, v in coords.items():
            if v is None:
                errors.append(f"{prefix}: {k} required for freeform crop")
            elif not _is_number(v) or not (0 <= v <= 1):
                errors.append(f"{prefix}: {k} must be a number in [0, 1], got {v!r}")
        x1, y1, x2, y2 = coords["crop_x1"], coords["crop_y1"], coords["crop_x2"], coords["crop_y2"]
        if all(_is_number(v) for v in (x1, x2)) and x1 >= x2:
            errors.append(f"{prefix}: crop_x1 ({x1}) must be less than crop_x2 ({x2})")
        if all(_is_number(v) for v in (y1, y2)) and y1 >= y2:
            errors.append(f"{prefix}: crop_y1 ({y1}) must be less than crop_y2 ({y2})")

    if crop_mode == "deskew":
        deskew = ref.get("deskew")
        if not isinstance(deskew, dict):
            errors.append(f"{prefix}: deskew object required for deskew crop_mode")
        else:
            for corner in DESKEW_CORNERS:
                pt = deskew.get(corner)
                if not isinstance(pt, dict):
                    errors.append(f"{prefix}.deskew: missing corner {corner!r}")
                    continue
                x, y = pt.get("x"), pt.get("y")
                if not _is_number(x) or not (0 <= x <= 1):
                    errors.append(
                        f"{prefix}.deskew.{corner}.x must be a number in [0, 1], "
                        f"got {x!r}"
                    )
                if not _is_number(y) or not (0 <= y <= 1):
                    errors.append(
                        f"{prefix}.deskew.{corner}.y must be a number in [0, 1], "
                        f"got {y!r}"
                    )

    return errors


def validate_all_photos(data: dict) -> list[str]:
    """Walk every item.photos entry in a catalog document."""
    errors = []
    for i, item in enumerate(data.get("data", {}).get("items", [])):
        for j, ref in enumerate(item.get("photos", [])):
            for e in validate_photo_ref(ref, j):
                errors.append(f"items[{i}].{e}")
    return errors


def _load(name: str) -> dict:
    with open(FIXTURES / name) as f:
        return json.load(f)


class TestValidPhotoTransforms:
    def test_valid_fixture_has_no_errors(self):
        data = _load("valid_photo_transforms.thingalog")
        errors = validate_all_photos(data)
        assert errors == [], f"Unexpected errors: {errors}"

    @pytest.mark.parametrize("rotation", sorted(VALID_ROTATIONS))
    def test_all_valid_rotations(self, rotation):
        ref = {"filename": "a.jpg", "slot": 1, "rotation": rotation}
        assert validate_photo_ref(ref) == []

    def test_freeform_full_image(self):
        ref = {
            "filename": "a.jpg", "slot": 1, "crop_mode": "freeform",
            "crop_x1": 0, "crop_y1": 0, "crop_x2": 1, "crop_y2": 1,
        }
        assert validate_photo_ref(ref) == []

    def test_deskew_all_corners(self):
        ref = {
            "filename": "a.jpg", "slot": 1, "crop_mode": "deskew",
            "deskew": {
                "tl": {"x": 0.1, "y": 0.1}, "tr": {"x": 0.9, "y": 0.1},
                "br": {"x": 0.9, "y": 0.9}, "bl": {"x": 0.1, "y": 0.9},
            },
        }
        assert validate_photo_ref(ref) == []


class TestInvalidRotation:
    def test_fixture_catches_45_degrees(self):
        data = _load("invalid_photo_rotation.thingalog")
        errors = validate_all_photos(data)
        assert any("rotation" in e for e in errors)

    @pytest.mark.parametrize("bad", [1, 45, 89, 91, 180.5, -90, 360])
    def test_rejects_nonstandard_rotations(self, bad):
        ref = {"filename": "a.jpg", "slot": 1, "rotation": bad}
        errors = validate_photo_ref(ref)
        assert any("rotation" in e for e in errors), (
            f"rotation={bad!r} should be rejected, got {errors}")


class TestInvalidCropMode:
    def test_rejects_unknown_mode(self):
        ref = {"filename": "a.jpg", "slot": 1, "crop_mode": "cartoonify"}
        errors = validate_photo_ref(ref)
        assert any("crop_mode" in e for e in errors)


class TestFreeformCropBounds:
    def test_fixture_catches_inverted_bounds(self):
        data = _load("invalid_photo_crop_bounds.thingalog")
        errors = validate_all_photos(data)
        assert any("crop_x1" in e and "crop_x2" in e for e in errors)

    def test_rejects_coord_out_of_range(self):
        ref = {
            "filename": "a.jpg", "slot": 1, "crop_mode": "freeform",
            "crop_x1": -0.1, "crop_y1": 0, "crop_x2": 1.2, "crop_y2": 1,
        }
        errors = validate_photo_ref(ref)
        assert any("crop_x1" in e for e in errors)
        assert any("crop_x2" in e for e in errors)

    def test_rejects_missing_coord(self):
        ref = {
            "filename": "a.jpg", "slot": 1, "crop_mode": "freeform",
            "crop_x1": 0, "crop_y1": 0, "crop_x2": 1,
        }
        errors = validate_photo_ref(ref)
        assert any("crop_y2" in e for e in errors)


class TestDeskew:
    def test_fixture_catches_missing_corner(self):
        data = _load("invalid_deskew_missing_corner.thingalog")
        errors = validate_all_photos(data)
        assert any("bl" in e for e in errors)

    def test_rejects_non_numeric_coord(self):
        ref = {
            "filename": "a.jpg", "slot": 1, "crop_mode": "deskew",
            "deskew": {
                "tl": {"x": "left", "y": 0.1}, "tr": {"x": 0.9, "y": 0.1},
                "br": {"x": 0.9, "y": 0.9}, "bl": {"x": 0.1, "y": 0.9},
            },
        }
        errors = validate_photo_ref(ref)
        assert any("tl" in e and "x" in e for e in errors)


class TestSlot:
    @pytest.mark.parametrize("bad", [0, -1, 1.5, "1", True])
    def test_rejects_non_positive_integer_slot(self, bad):
        ref = {"filename": "a.jpg", "slot": bad}
        errors = validate_photo_ref(ref)
        assert any("slot" in e for e in errors), (
            f"slot={bad!r} should be rejected, got {errors}")
