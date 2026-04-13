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

## Bundled Transport (ZIP)

Any catio document can be bundled as a ZIP archive alongside its referenced media files. This is the self-contained, portable transport — no network required, no external dependencies.

### Structure

```
catalog-export.zip
├── catalog.opencatalog          # The catio JSON document
├── photos/                      # Referenced photos
│   ├── watch_001.jpg
│   ├── watch_002.jpg
│   └── ...
└── files/                       # Referenced non-photo files (optional)
    ├── manual.pdf
    └── certificate.pdf
```

### Rules

1. **The JSON document MUST be at the root of the ZIP**, with the appropriate extension (`.openthing`, `.opencatalog`, or `.catdef`). If multiple JSON documents exist at the root, the importer SHOULD use the first `.opencatalog` file, then `.openthing`, then `.catdef`.

2. **Photos MUST be in a `photos/` directory** at the ZIP root. Photo references in the JSON use the filename only (no path prefix): `"filename": "watch_001.jpg"`. The importer resolves `photos/{filename}`.

3. **Non-photo files** (CloudFile, attachments) SHOULD be in a `files/` directory. Same filename-only reference rule.

4. **Photo filenames MUST be unique within the bundle.** If the source system has duplicate filenames across different storage paths, it MUST rename them before bundling (e.g. append a suffix: `watch_001.jpg`, `watch_001_2.jpg`).

5. **Photo references** in the JSON support two forms:
   - **Filename only** (for bundled transport): `{"filename": "watch_001.jpg", "slot": 1}`
   - **Filename + URL** (for hybrid transport): `{"filename": "watch_001.jpg", "url": "https://...", "slot": 1}`

   When both are present, the importer SHOULD prefer the local file from the ZIP. The URL is a fallback for cases where the ZIP is incomplete or the file is too large to bundle.

6. **EXIF metadata** embedded in photos SHOULD be preserved. The importer MAY extract photographer, date, and description from EXIF tags (same as direct upload).

7. **File size guidance** (non-normative):
   - Small catalogs (< 100 photos, < 500 MB): bundle everything.
   - Large catalogs: consider URL references with optional selective bundling (bundle thumbnails, reference originals by URL).
   - The ZIP format has no practical size limit, but transfer and storage constraints apply.

### Import Behavior

When importing a ZIP bundle:

1. Parse the JSON document at the root.
2. For each referenced photo:
   a. Look in the `photos/` directory of the ZIP.
   b. If not found and a `url` is present, attempt to download.
   c. If neither, skip the photo and log a warning (do not fail the import).
3. Apply standard catio identity and deduplication rules.
4. Photos are deduplicated by filename within the catalog (same as direct upload).

### Export Behavior

When exporting a catalog as a ZIP bundle:

1. Generate the `.opencatalog` JSON with all items, values, and photo references.
2. For each photo in the catalog, include the original file in `photos/`.
3. Include non-photo files in `files/` if applicable.
4. Photo references in the JSON use filename only (no storage paths or URLs).

### MIME Type

| Format | MIME |
|--------|------|
| ZIP bundle | `application/zip` |

The ZIP bundle is identified by its `.zip` extension and the presence of a catio JSON document at the root. There is no special MIME type — it's a standard ZIP file.

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
