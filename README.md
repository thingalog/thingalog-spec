# Thingalog Spec

The open standard for **live catalogs**.

Thingalog defines a portable, JSON-based format for describing collections of anything — watches, artifacts, books, wines, stamps, boats. A single `.thingalog` file contains everything: the schema (templates, field definitions), the data (items, values), and the presentation (theme, settings).

## What's in this repo

| Path | Description |
|------|-------------|
| [CATDEF_SPEC.md](CATDEF_SPEC.md) | The catdef v1.0 specification — file format, field types, widgets, conformance levels |
| [samples/](samples/) | Sample `.thingalog` files you can open in any conformant renderer |
| [conformance/](conformance/) | The Thingalog Conformance Test Suite (coming soon) |

## File format

A `.thingalog` file is JSON with MIME type `application/vnd.thingalog.catdef+json`.

```json
{
  "catdef": "1.0",
  "product": { "name": "My Collection", "slug": "mycollection", ... },
  "requires": { "renderer": ">=1.0", "features": ["photos"], ... },
  "templates": [{ "name": "Item", "field_defs": [...] }],
  "data": { "values": {...}, "items": [...] }
}
```

## Conformance levels

| Level | Name | Description |
|-------|------|-------------|
| L1 | Static | Browser-only, reads `.thingalog` files directly. No server. |
| L2 | Lightweight | API-backed with SQLite/D1. Read-write. |
| L3 | Full | Graph database (Neo4j). Full CRUD, audit log, photos. |
| L4 | Platform | Multi-tenant, auth, billing, social, AI onboarding. |

A renderer declares which level it supports. Higher levels are supersets of lower levels.

## Conformance test suite

Anyone can build a Thingalog renderer. To call it conformant, it must pass the test suite.

The test suite validates:
- Catdef parsing (valid files accepted, malformed files rejected)
- Field type rendering (all 11 types)
- Widget behavior (autocomplete, dropdown, checkbox-table, etc.)
- Conformance level requirements (L1 features, L2 features, etc.)
- Theme application
- Search, sort, and filter behavior

**The test suite is the standard.** See [conformance/](conformance/) for details.

## License

MIT. See [LICENSE](LICENSE).

Build whatever you want. If it passes the tests, it's Thingalog.
