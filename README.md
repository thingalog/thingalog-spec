# catdef

The open standard for **machine-enhanceable descriptors of real-world objects and catalogs**.

catdef defines two complementary concepts:

- **OpenThing** — a schema for describing any real-world object: its properties, measurements, classifications, provenance, and media.
- **OpenCatalog** — a schema for organizing collections of things: identity, branding, search, social features, and presentation.

A single `.thingalog` file contains everything: the schema (templates, field definitions), the data (items, values), and the presentation (theme, settings). An AI that can see a photograph can write a catdef. A human with a spreadsheet can write a catdef.

## What's in this repo

| Path | Description |
|------|-------------|
| [CATDEF_SPEC.md](CATDEF_SPEC.md) | The catdef v1.1 specification — field types, widgets, conformance levels |
| [samples/](samples/) | Sample `.thingalog` files you can open in any conformant renderer |
| [conformance/](conformance/) | The catdef Conformance Test Suite — 55 tests |

## File format

MIME type: `application/vnd.catdef+json`

```json
{
  "catdef": "1.1",
  "product": { "name": "My Collection", "slug": "mycollection", ... },
  "requires": { "renderer": ">=1.0", "features": ["photos"], ... },
  "templates": [{ "name": "Item", "field_defs": [...] }],
  "data": { "values": {...}, "items": [...] }
}
```

## Field types

13 field types covering the full spectrum of real-world object classification:

`String` `Integer` `Number` `RichText` `Enumerated` `Photo` `Table` `CloudFile` `URL` `Date` `Money` `Boolean` `GeoLocation`

Plus field-def attributes: `unique`, `default`, `format` (isbn, vin, sku, etc.), `unit`, `precision`, `min`/`max`, `circa`, `currency`.

## Conformance levels

| Level | Name | Description |
|-------|------|-------------|
| L1 | Static | Browser-only, reads `.thingalog` files directly. No server. |
| L2 | Lightweight | API-backed with SQLite/D1. Read-write. |
| L3 | Full | Graph database. Full CRUD, audit log, photos. |
| L4 | Platform | Multi-tenant, auth, billing, social, AI onboarding. |

## Conformance test suite

Anyone can build a catdef renderer. To call it conformant, it must pass the test suite.

**The test suite is the standard.** See [conformance/](conformance/) for details.

## Feedback

File spec feedback at [catdef.org/feedback](https://catdef.org/feedback) — structured intake for AI agents and humans.

## License

MIT. See [LICENSE](LICENSE).

Build whatever you want. If it passes the tests, it's catdef.
