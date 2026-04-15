# catdef

The open standard for **machine-enhanceable descriptors of real-world objects and catalogs**.

catdef defines two complementary concepts:

- **OpenThing** — a schema for describing any real-world object: its properties, measurements, classifications, provenance, and media.
- **OpenCatalog** — a schema for organizing collections of things: identity, branding, search, social features, and presentation.

A single `.thingalog` file contains everything: the schema (templates, field definitions), the data (items, values), and the presentation (theme, settings). An AI that can see a photograph can write a catdef. A human with a spreadsheet can write a catdef.

## What's in this repo

| Path | Description |
|------|-------------|
| [CATDEF_SPEC.md](CATDEF_SPEC.md) | The catdef v1.3 specification — field types, subcats, views, inheritance, conformance levels |
| [CATIO_SPEC.md](CATIO_SPEC.md) | The CATIO bundled-transport specification — `.opencatalog` ZIP format |
| [samples/](samples/) | Sample `.thingalog` files you can open in any conformant renderer |
| [conformance/](conformance/) | The catdef Conformance Test Suite — 98 tests |
| [CONTRIBUTING.md](CONTRIBUTING.md) | How to propose changes to the standard |

## File format

MIME type: `application/vnd.catdef+json`

```json
{
  "catdef": "1.3",
  "product": { "name": "My Collection", "slug": "mycollection", ... },
  "inherits_from": "optional_model_slug",
  "views": { "primary_axis": "thing", "modes": ["grid"], "default": "grid" },
  "templates": [{ "name": "Item", "field_defs": [...] }],
  "subcats": { "Brand": { "field_defs": [...], "values": {...} } },
  "themes": { ... },
  "embed": { ... },
  "data": { "values": {...}, "items": [...] }
}
```

## Field types

13 field types covering the full spectrum of real-world object classification:

`String` `Integer` `Number` `RichText` `Enumerated` `Photo` `Table` `CloudFile` `URL` `Date` `Money` `Boolean` `GeoLocation`

Plus field-def attributes: `unique`, `default`, `format` (isbn, vin, sku, etc.), `unit`, `precision`, `min`/`max`, `circa`, `currency`, `range`, `scorable`, `primary`.

## v1.3 highlights

- **Subcats** — enriched Enumerated values with their own field_defs. Stanley (the brand) has Founded/Country/Specialty/Logo. Artists have portraits. Venues have addresses.
- **Inheritance** — `inherits_from` enables partner/model catalogs. A watch-catalog platform publishes `watchomatic_model`; customers create catalogs that inherit schema, themes, and seed data.
- **Views** — `primary_axis` (thing/date/place) tells renderers the dominant organizing principle. A concert calendar declares `"primary_axis": "date"`, gets calendar-first rendering for free.
- **Range types** — `Number`/`Money`/`Date` with `range: true` for case diameter ranges, price ranges, exhibition dates.
- **Context-aware rendering** — `scorable` fields enable geo/time-weighted sorting. Same CATIO file renders differently on kiosks in different locations.
- **Embed declaration** — catalogs can be embedded in any website as iframes with declared defaults.
- **About page** — expanded `product` object (phone, website, address, hours, social, sections) turns every catalog into a proper web destination.

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
