# Thingalog Conformance Test Suite

This directory contains the official conformance tests for Thingalog renderers.

## Structure

```
conformance/
  fixtures/          .thingalog files: valid, invalid, and edge-case
  test_parsing.py    catdef file parsing + validation
  test_fields.py     field type rendering (all 11 types)
  test_search.py     search, sort, filter behavior
  test_themes.py     theme application
  test_levels.py     conformance level feature gates
```

## Running the tests

```bash
pip install pytest
pytest conformance/ -v
```

## Writing a renderer

Your renderer must:

1. Accept a `.thingalog` file (or URL to one)
2. Parse the catdef JSON according to [CATDEF_SPEC.md](../CATDEF_SPEC.md)
3. Render items in a grid/list with search, sort, and filter
4. Declare its conformance level (L1-L4)
5. Pass all tests for its declared level

## Fixture files

The `fixtures/` directory contains `.thingalog` files designed to exercise every corner of the spec:

- `valid_minimal.thingalog` — smallest possible valid file
- `valid_all_field_types.thingalog` — one field of every type
- `valid_watches.thingalog` — real-world collection (12 items)
- `invalid_no_catdef.thingalog` — missing catdef version
- `invalid_bad_field_type.thingalog` — unrecognized field type
- `invalid_circular_table.thingalog` — recursive Table field

## Status

The conformance suite is under active development. Contributions welcome.
