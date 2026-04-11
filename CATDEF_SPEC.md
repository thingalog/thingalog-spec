# catdef.json — Specification v1.0

## Overview

A **catdef** (catalog definition) is a single JSON document that fully describes a data application. Any conforming runtime — browser JS, Docker container, Cloudflare Worker, WASM binary, Claude artifact — can read a catdef and render a working, interactive catalog application.

The catdef is to catalog applications what HTML is to documents: a portable, runtime-independent specification that separates content from implementation.

## Design Principles

1. **One file, complete product.** A catdef contains everything needed to go from zero to running application: identity, branding, schema, settings, and runtime hints.
2. **Declarative, not imperative.** The catdef says *what*, never *how*. It never specifies a database engine, a programming language, or a hosting provider.
3. **Forward-compatible.** A v1.0 renderer encountering a v1.3 catdef gracefully ignores fields it doesn't understand. New capabilities degrade, never break.
4. **AI-generable.** Every part of the catdef can be produced by a conversational AI from a natural language description. No field requires technical knowledge to specify.
5. **Human-readable.** The catdef is JSON with clear key names. A non-developer can read it and understand what their catalog will contain.

## Top-Level Structure

```json
{
  "catdef": "1.0",

  "product": { ... },
  "requires": { ... },
  "hints": { ... },
  "templates": [ ... ],
  "settings": { ... }
}
```

### `catdef` (string, required)
Spec version. Semver format. Runtimes use this to determine compatibility.

---

## `product` (object, required)

The identity and branding of the catalog application.

```json
{
  "product": {
    "name": "Scott's Watch Collection",
    "slug": "scottswatches",
    "domain": "scottswatches.thingalog.app",
    "tagline": "Vintage timepieces, documented",
    "description": "A curated catalog of vintage mechanical watches collected over 30 years.",
    "contact_email": "scott@confusedgorilla.com",
    "owner": "Scott Welch",
    "logo_url": "",
    "theme": "Midnight"
  }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | yes | Display name of the catalog |
| `slug` | string | yes | URL-safe identifier. Used for subdomain: `{slug}.thingalog.app` |
| `domain` | string | no | Full domain if custom (e.g., `scottswatches.com`). Defaults to `{slug}.thingalog.app` |
| `tagline` | string | no | Short subtitle, displayed in header |
| `description` | string | no | Longer description, used in meta tags and AI context |
| `contact_email` | string | no | Owner's contact email (captured conversationally during onboarding) |
| `owner` | string | no | Display name of the catalog owner |
| `logo_url` | string | no | URL to a logo image |
| `theme` | string or object | no | Either a theme name (resolved from marketplace) or an inline theme object |

### Inline Theme Object

When `theme` is an object instead of a string:

```json
{
  "theme": {
    "accent": "#1a365d",
    "accent_dim": "#4a7ab5",
    "bg": "#f7fafc",
    "panel": "#ffffff",
    "ink": "#1a202c",
    "muted": "#718096",
    "border": "#e2e8f0",
    "font": "Inter, system-ui, sans-serif",
    "card_radius": "12px",
    "mode": "light"
  }
}
```

All theme fields are optional. The runtime provides sensible defaults for any omitted field.

---

## `requires` (object, optional)

Declares the capabilities the catdef needs from the runtime. Used for compatibility checking and graceful degradation.

```json
{
  "requires": {
    "renderer": ">=1.0",
    "features": ["photos", "social", "embed", "export"],
    "field_types": ["String", "Integer", "RichText", "Enumerated", "Photo", "Table", "CloudFile", "URL"],
    "widgets": ["autocomplete", "dropdown", "checkbox_table", "table"]
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `renderer` | string | Semver range. Minimum renderer version required |
| `features` | string[] | Platform features needed. Known values: `photos`, `social`, `embed`, `export`, `inquire`, `comments`, `health_score`, `history` |
| `field_types` | string[] | Field types used in templates. Known values listed below |
| `widgets` | string[] | Widget types used. Known values listed below |

A runtime that doesn't support a required feature SHOULD still render the catalog, omitting the unsupported feature with a visual indicator.

---

## `hints` (object, optional)

Non-binding guidance to help the runtime choose infrastructure. The runtime MAY ignore hints entirely.

```json
{
  "hints": {
    "expected_items": 100,
    "expected_photos": 400,
    "avg_photo_size_mb": 3,
    "expected_values": 50,
    "primary_media": "photo",
    "update_frequency": "weekly",
    "audience": "private"
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `expected_items` | integer | Approximate number of items the catalog will contain |
| `expected_photos` | integer | Approximate number of photos |
| `avg_photo_size_mb` | number | Average photo file size in megabytes |
| `expected_values` | integer | Approximate number of unique enumerated values |
| `primary_media` | string | Dominant media type: `photo`, `video`, `document`, `url`, `none` |
| `update_frequency` | string | How often data changes: `realtime`, `daily`, `weekly`, `monthly`, `rarely` |
| `audience` | string | Visibility: `private` (owner only), `shared` (invited), `public` (anyone) |

### Runtime Guidance (non-normative)

| Profile | Suggested Runtime |
|---------|-------------------|
| ≤50 items, no photos | Browser-only (in-memory, LocalStorage) |
| ≤500 items, photos | Lightweight server (SQLite + file storage) |
| ≤5000 items, heavy media | Full server (Neo4j/Postgres + object storage) |
| >5000 items or realtime | Scaled infrastructure |

---

## `templates` (array, required)

One or more item templates. Each template defines a kind of thing in the catalog.

```json
{
  "templates": [
    {
      "name": "Vintage Watch",
      "description": "A mechanical or quartz timepiece",
      "icon": "watch",
      "field_defs": [ ... ]
    }
  ]
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | yes | Template name. Unique within the catdef |
| `description` | string | no | Human-readable description of what this template catalogs |
| `icon` | string | no | Icon hint (emoji or icon name) |
| `field_defs` | array | yes | Ordered list of field definitions |

### Field Definition

```json
{
  "label": "Complications",
  "type": "Table",
  "sort_order": 70,
  "target": "Complication",
  "multi": true,
  "required": false,
  "importance": "preferred",
  "filterable": true,
  "widget": "table",
  "placeholder": "Add complications...",
  "help_text": "List the watch's complications (moon phase, chronograph, etc.)",
  "columns": [
    {"label": "Subdial Position", "type": "String"},
    {"label": "Phase Count", "type": "Integer"},
    {"label": "Notes", "type": "String"}
  ]
}
```

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `label` | string | yes | — | Display name and internal identifier for this field |
| `type` | string | yes | — | Field type. See Field Types below |
| `sort_order` | integer | yes | — | Display order (ascending). Gaps allowed (10, 20, 30...) |
| `target` | string | conditional | `""` | For Enumerated/Table types: the label namespace for Value nodes |
| `multi` | boolean | no | `false` | Whether multiple values can be attached |
| `required` | boolean | no | `false` | Whether the field must have a value before save |
| `importance` | string | no | `"optional"` | For health score: `"required"`, `"preferred"`, or `"optional"` |
| `filterable` | boolean | no | `false` | Whether the list view shows a filter dropdown for this field |
| `widget` | string | no | auto | Override the default widget. See Widget Types below |
| `placeholder` | string | no | `""` | Placeholder text in the empty input |
| `help_text` | string | no | `""` | Tooltip or helper text for the field |
| `columns` | array | conditional | — | For Table type: sub-field definitions for each column |

---

## Field Types

| Type | Value Storage | Description |
|------|---------------|-------------|
| `String` | Inline on Field node | Single-line text |
| `Integer` | Inline on Field node | Whole number |
| `RichText` | Inline on Field node | Multi-line formatted text (HTML) |
| `Enumerated` | Edge to `:Value` node | Pick from (or create) shared values. Dedupe by name (case-insensitive) |
| `Photo` | Edge to `:Photo` node | An image with storage path, dimensions, metadata. Single photo per field |
| `Table` | Edges to `:Value` nodes with sub-fields | Structured multi-row data. Each row is a Value node with its own Fields defined by `columns` |
| `CloudFile` | Inline (URL + provider metadata) | Pointer to a file in Dropbox/GDrive/OneDrive/Box. Not downloaded, just referenced |
| `URL` | Inline | A web URL with auto-extracted title, description, og:image |
| `Date` | Inline | ISO 8601 date string |
| `Money` | Inline (amount + currency) | Monetary value with currency code |
| `Boolean` | Inline | True/false toggle |

Runtimes MUST support: `String`, `Integer`, `RichText`, `Enumerated`, `Photo`.
Runtimes SHOULD support: `Table`, `URL`, `Date`, `Money`, `Boolean`.
Runtimes MAY support: `CloudFile`.

---

## Widget Types

Widgets control how a field is presented in the UI. The runtime selects a default widget based on the field type, but the catdef can override it.

| Widget | Best For | Description |
|--------|----------|-------------|
| `text` | String, Integer | Single-line input |
| `textarea` | RichText | Multi-line editor |
| `number` | Integer, Money | Numeric input with validation |
| `autocomplete` | Enumerated (open-ended) | Type-ahead with find-or-create |
| `dropdown` | Enumerated (closed set) | Single or multi select dropdown |
| `checkbox_table` | Enumerated (multi, all visible) | All options displayed with checkboxes |
| `table` | Table | Rows with sub-columns |
| `photo` | Photo | Upload/capture with preview |
| `url` | URL | Input with auto-preview (favicon, og:image) |
| `file_picker` | CloudFile | OAuth-connected cloud file browser |
| `date` | Date | Date picker |
| `toggle` | Boolean | On/off switch |

### Default Widget Selection

| Field Type | Default Widget |
|------------|----------------|
| String | `text` |
| Integer | `number` |
| RichText | `textarea` |
| Enumerated (multi:false) | `autocomplete` |
| Enumerated (multi:true) | `autocomplete` |
| Photo | `photo` |
| Table | `table` |
| CloudFile | `file_picker` |
| URL | `url` |
| Date | `date` |
| Money | `number` |
| Boolean | `toggle` |

---

## `settings` (object, optional)

Catalog-level feature flags and configuration.

```json
{
  "settings": {
    "public": true,
    "embed": {
      "enabled": true,
      "powered_by": true,
      "max_items": null
    },
    "social": {
      "likes": true,
      "favourites": true,
      "comments": false,
      "view_tracking": true
    },
    "inquire": {
      "enabled": true,
      "recipient_email": "scott@confusedgorilla.com",
      "ai_assistant": true
    },
    "export": {
      "pdf": true,
      "excel": true,
      "zip": true
    },
    "health_score": {
      "enabled": true,
      "grading": "letter"
    },
    "history": true,
    "trash": true
  }
}
```

All settings are optional. Omitted settings use the runtime's defaults (which SHOULD be sensible for a personal catalog).

---

## Complete Example: Vintage Watch Catalog

```json
{
  "catdef": "1.0",

  "product": {
    "name": "Scott's Watch Collection",
    "slug": "scottswatches",
    "tagline": "Vintage timepieces, documented",
    "contact_email": "scott@confusedgorilla.com",
    "theme": {
      "accent": "#1a365d",
      "bg": "#0d1117",
      "ink": "#e6edf3",
      "mode": "dark"
    }
  },

  "requires": {
    "renderer": ">=1.0",
    "features": ["photos", "social", "embed", "export"],
    "field_types": ["String", "Integer", "RichText", "Enumerated", "Photo", "Table"]
  },

  "hints": {
    "expected_items": 100,
    "expected_photos": 400,
    "avg_photo_size_mb": 3,
    "primary_media": "photo",
    "update_frequency": "weekly",
    "audience": "public"
  },

  "templates": [
    {
      "name": "Vintage Watch",
      "description": "A mechanical or quartz timepiece",
      "icon": "⌚",
      "field_defs": [
        {"label": "Title",            "type": "String",     "sort_order": 10, "required": true, "importance": "required", "placeholder": "e.g. Omega Speedmaster Professional 145.022"},
        {"label": "Brand",            "type": "Enumerated", "sort_order": 20, "target": "Brand", "filterable": true, "importance": "required", "widget": "autocomplete"},
        {"label": "Reference",        "type": "String",     "sort_order": 30, "importance": "preferred", "placeholder": "e.g. 145.022-69"},
        {"label": "Year",             "type": "Integer",    "sort_order": 40, "importance": "preferred"},
        {"label": "Movement",         "type": "Enumerated", "sort_order": 50, "target": "Movement", "filterable": true, "widget": "dropdown"},
        {"label": "Case Material",    "type": "Enumerated", "sort_order": 60, "target": "Material", "filterable": true},
        {"label": "Case Diameter",    "type": "String",     "sort_order": 70, "placeholder": "e.g. 42mm"},
        {"label": "Complications",    "type": "Table",      "sort_order": 80, "target": "Complication", "multi": true, "widget": "table", "columns": [
          {"label": "Complication", "type": "String"},
          {"label": "Subdial", "type": "String"},
          {"label": "Notes", "type": "String"}
        ]},
        {"label": "Condition",        "type": "Enumerated", "sort_order": 90,  "target": "Grade", "widget": "dropdown"},
        {"label": "Box & Papers",     "type": "Enumerated", "sort_order": 100, "target": "Completeness", "widget": "dropdown"},
        {"label": "Photo (Front)",    "type": "Photo",      "sort_order": 110, "importance": "required"},
        {"label": "Photo (Back)",     "type": "Photo",      "sort_order": 120, "importance": "preferred"},
        {"label": "Photo (Movement)", "type": "Photo",      "sort_order": 130},
        {"label": "Purchase Price",   "type": "Money",      "sort_order": 140},
        {"label": "Purchased From",   "type": "Enumerated", "sort_order": 150, "target": "Dealer"},
        {"label": "Purchase Date",    "type": "Date",       "sort_order": 160},
        {"label": "Service History",  "type": "RichText",   "sort_order": 170, "importance": "preferred"},
        {"label": "Notes",            "type": "RichText",   "sort_order": 180}
      ]
    }
  ],

  "settings": {
    "public": true,
    "embed": {"enabled": true, "powered_by": true},
    "social": {"likes": true, "favourites": true, "comments": true, "view_tracking": true},
    "inquire": {"enabled": true, "ai_assistant": true},
    "export": {"pdf": true, "excel": true, "zip": true},
    "health_score": {"enabled": true, "grading": "letter"},
    "history": true,
    "trash": true
  }
}
```

---

## Conformance Levels

### Level 1: Minimal (browser-only)
- Reads catdef and renders item list + item detail
- Supports field types: String, Integer, RichText, Enumerated, Photo
- In-memory or LocalStorage persistence
- No server required

### Level 2: Standard (lightweight server)
- Level 1 plus: search, sort, filter, export, history, trash
- Persistent storage (SQLite, flat files, or equivalent)
- Photo upload and storage
- API endpoints per the Thingalog API spec

### Level 3: Full (graph-native)
- Level 2 plus: social layer, embed, inquire, comments, health score
- Graph database (Neo4j or equivalent)
- Real-time collaborative filtering
- Multi-tenant support
- Template marketplace integration

### Level 4: Platform (Thingalog.app)
- Level 3 plus: AI onboarding, custom domains, billing, wildcard subdomains
- Theme marketplace
- Template marketplace
- Browser plugin integration
- Conversii support integration

---

## Versioning

The catdef version follows semver:
- **Patch** (1.0.x): documentation clarifications, no schema changes
- **Minor** (1.x.0): new optional fields, new field types, new settings. Old catdefs remain valid. Old runtimes gracefully ignore new fields.
- **Major** (x.0.0): breaking changes to required fields or semantics. Runtime MUST check major version before attempting to render.

A catdef MUST specify its version. A runtime MUST refuse to render a catdef with a higher major version than it supports.

---

## Security Considerations

- A catdef MUST NOT contain secrets (API keys, passwords, tokens). Authentication is handled by the runtime, not the catdef.
- The `contact_email` field is visible to anyone who can read the catdef. Do not include private emails unless the catalog is private.
- Theme objects MUST be sanitized by the runtime before applying as CSS variables (no `url()`, no `expression()`, no script injection).
- The `domain` field is a claim, not proof of ownership. The runtime MUST verify domain ownership before serving on a custom domain.

---

## MIME Type

`application/vnd.thingalog.catdef+json`

## File Extension

`.catdef.json` or `.catdef`

---

*Specification version 1.0. April 2026.*
*Created by Scott Chicken and Claude (Anthropic).*
