# catio — Transport Specification v1.0

## Overview

**catio** (catalog I/O) is the transport contract for OpenThing and OpenCatalog objects. It defines how things and catalogs move between systems — import, export, sync, stream, and API exchange.

A catio document is a JSON envelope that carries one or more OpenThing or OpenCatalog payloads. The `.thingalog` file format is a catio document. An MCP tool call that creates an item is a catio operation. A ZIP export is a catio bundle. A browser plugin that captures a webpage is producing a catio message.

catio does not define what a thing *is* (that's OpenThing) or how a catalog *behaves* (that's OpenCatalog). catio defines how they travel.

## Design Principles

1. **Envelope, not content.** catio wraps OpenThing and OpenCatalog payloads without constraining them. New field types or settings don't require catio changes.
2. **One thing is enough.** A valid catio document can contain a single OpenThing with no catalog context. Opening one thing implies a schema; a schema implies a catalog.
3. **Idempotent operations.** Importing the same catio document twice produces the same result. Deduplication is by identity, not by position.
4. **Machine-native.** Every catio operation is expressible as an MCP tool call, a REST API call, or a file exchange. The transport is the same regardless of wire protocol.
5. **Streamable.** catio documents can be produced incrementally — one thing at a time — for pipelines that analyze photos, scrape pages, or read sensors.

## Document Types

### Single Thing

The minimal catio document: one real-world object, described.

```json
{
  "catio": "1.0",
  "type": "thing",

  "thing": {
    "template": "Vintage Watch",
    "fields": {
      "Title": "Omega Speedmaster Professional 145.022",
      "Brand": "Omega",
      "Reference": "145.022-69 ST",
      "Year": 1969,
      "Movement": "Manual",
      "Case Diameter": {"value": 42, "unit": "mm"},
      "Condition": "Very Good"
    },
    "photos": [
      {"filename": "speedy_front.jpg", "slot": 1},
      {"filename": "speedy_caseback.jpg", "slot": 2}
    ]
  }
}
```

A single thing is a complete, portable descriptor of a real-world object. It can be:
- Opened to view the object
- Used to infer a template (the fields imply the schema)
- Imported into any catalog that accepts compatible templates
- Shared, embedded, or archived independently

### Thing Collection

Multiple things, optionally with shared schema.

```json
{
  "catio": "1.0",
  "type": "collection",

  "schema": {
    "templates": [
      {
        "name": "Vintage Watch",
        "field_defs": [
          {"label": "Title", "type": "String", "sort_order": 10, "required": true},
          {"label": "Brand", "type": "Enumerated", "sort_order": 20, "target": "Brand"},
          {"label": "Year", "type": "Integer", "sort_order": 30}
        ]
      }
    ],
    "values": {
      "Brand": ["Omega", "Rolex", "Tudor", "Seiko"]
    }
  },

  "things": [
    {
      "template": "Vintage Watch",
      "fields": {"Title": "Omega Speedmaster", "Brand": "Omega", "Year": 1969}
    },
    {
      "template": "Vintage Watch",
      "fields": {"Title": "Rolex Submariner 5513", "Brand": "Rolex", "Year": 1972}
    }
  ]
}
```

When `schema` is present, it declares the shared template and value set. When absent, each thing is self-describing (fields imply types).

### Full Catalog

A complete OpenCatalog with OpenThing data — the `.thingalog` file.

```json
{
  "catio": "1.0",
  "type": "catalog",

  "catdef": "1.1",
  "product": { ... },
  "requires": { ... },
  "hints": { ... },
  "templates": [ ... ],
  "settings": { ... },

  "data": {
    "values": { ... },
    "items": [ ... ],
    "photos": [ ... ]
  }
}
```

This is the existing `.thingalog` format, now formally identified as a catio document of type `catalog`. Backward-compatible: existing `.thingalog` files that lack the `catio` envelope are treated as `type: "catalog"` with `catio: "1.0"` implied.

### Catalog Schema (Starter Kit)

Template definitions only, no data. The `.catdef.json` format.

```json
{
  "catio": "1.0",
  "type": "schema",

  "catdef": "1.1",
  "templates": [ ... ]
}
```

Used for template marketplace, starter kits, and "create a catalog like this one."

## Operations

catio defines a standard set of operations for moving things between systems. Each operation maps to both a REST endpoint and an MCP tool call.

### Write Operations

| Operation | Description | REST | MCP Tool |
|-----------|-------------|------|----------|
| `import_thing` | Add a single thing to a catalog | `POST /api/items` + field updates | `create_item` + `update_field` |
| `import_collection` | Add multiple things (with optional schema) | `POST /api/import` | batch `create_item` calls |
| `import_catalog` | Restore a full catalog from backup | `POST /api/import/zip` | — |
| `update_thing` | Modify fields on an existing thing | `PATCH /api/items/{id}/fields/{label}` | `update_field` |
| `classify_thing` | Attach enumerated values to a thing | `POST /api/items/{id}/fields/{label}/values` | `attach_value` |
| `attach_media` | Add a photo to a thing | `POST /api/photos/upload` + `POST /api/items/{id}/photos` | `upload_photo` + `attach_photo` |
| `remove_thing` | Soft-delete a thing (trash) | `DELETE /api/items/{id}` | `trash_item` |

### Read Operations

| Operation | Description | REST | MCP Tool |
|-----------|-------------|------|----------|
| `export_thing` | Export a single thing as a catio document | `GET /api/items/{id}` | `get_item` |
| `export_collection` | Export matching things | `GET /api/items?q=...` | `search_items` |
| `export_catalog` | Full catalog backup | `GET /api/export/zip` | — |
| `export_schema` | Template definitions only | `GET /api/export/templates` | `get_catalog_spec` |
| `list_values` | Available classifications for a field | `GET /api/values?label=...` | `list_values` |

### Inference Operations

These operations produce catio documents from unstructured input. They are not part of the transport spec but are defined here for interoperability.

| Operation | Input | Output | Description |
|-----------|-------|--------|-------------|
| `infer_thing` | Photo(s) | Single thing | AI vision analyzes images and produces a classified thing |
| `infer_schema` | Thing(s) | Schema | Derive a template from one or more example things |
| `infer_catalog` | Photo folder | Full catalog | Group photos by item, classify each, produce a complete catalog |

## Identity and Deduplication

Things are identified by their content, not by position in the document. On import:

1. If the thing has a field marked `unique: true` (e.g. SKU, accession number, ISBN), match by that field's value.
2. If no unique field, match by `Title` (case-insensitive) within the same template.
3. If no match, create a new thing.

When a match is found:
- **Merge mode** (default): update empty fields, skip populated fields.
- **Overwrite mode**: replace all fields with the incoming values.
- **Skip mode**: do nothing if the thing already exists.

The import mode is specified per-operation, not per-document.

## Error Shapes

All catio operations return errors in a standard shape:

```json
{
  "error": "field_not_found",
  "message": "Field 'Caliber' does not exist on template 'Vintage Watch'",
  "thing_index": 3,
  "field": "Caliber",
  "suggestion": "Did you mean 'Reference'?"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `error` | string | Machine-readable error code |
| `message` | string | Human-readable description |
| `thing_index` | integer | Which thing in a batch (0-based), if applicable |
| `field` | string | Which field caused the error, if applicable |
| `suggestion` | string | Suggested fix, if determinable |

## Versioning

catio version follows semver, independent of catdef version. A catio 1.0 envelope can carry a catdef 1.1 payload — the transport doesn't constrain the content.

## MIME Types

| Type | MIME |
|------|------|
| Single thing | `application/vnd.openthing+json` |
| Collection | `application/vnd.opencatalog+json` |
| Catalog | `application/vnd.opencatalog+json` |
| Schema | `application/vnd.catdef+json` |

## File Extensions

| Extension | Contents |
|-----------|----------|
| `.openthing` | A single classified object (minimal: one real-world object, self-describing) |
| `.opencatalog` | A complete catalog (schema + data + values + settings) or a collection of things |
| `.catdef` | Schema only (template definitions, no data) |

These extensions belong to the catdef standard, not to any runtime. Any conformant application reads and writes all three.

---

*Specification version 1.0. April 2026.*
*An open standard. Licensed under MIT.*
