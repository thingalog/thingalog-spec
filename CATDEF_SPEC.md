# catdef — Specification v1.3

## Overview

**catdef** is an open standard for machine-enhanceable descriptors of real-world objects and catalogs. It defines two complementary concepts:

- **OpenThing** — a schema for describing any real-world object: its properties, measurements, classifications, provenance, and media. A template with field definitions.
- **OpenCatalog** — a schema for organizing collections of things: identity, branding, search, social features, and presentation settings.

A catdef document is a single JSON file that can express either or both. A minimal catdef describes one thing. A full catdef describes an entire catalog application with hundreds of things, each richly classified.

Any conforming runtime — browser JS, Docker container, Cloudflare Worker, WASM binary, AI artifact — can read a catdef and render a working application. The catdef is to structured collections what HTML is to documents: a portable, runtime-independent specification that separates content from implementation.

An AI that can see a photograph can write a catdef. A human with a spreadsheet can write a catdef. A sensor on a factory floor can write a catdef. The format is designed to be produced and consumed by both humans and machines, with each enhancing the other's work.

catdef is designed to serve the full spectrum of classification needs — from a hobbyist's watch collection to a museum's accession database, from an e-commerce product catalog to a field biologist's specimen log. The field types, validation attributes, and widget system are drawn from real-world standards including Dublin Core, MARC, PIM systems, and inventory management platforms.

## Design Principles

1. **One file, complete product.** A catdef contains everything needed to go from zero to running application: identity, branding, schema, settings, and runtime hints.
2. **Declarative, not imperative.** The catdef says *what*, never *how*. It never specifies a database engine, a programming language, or a hosting provider.
3. **Forward-compatible.** A v1.0 renderer encountering a v1.3 catdef gracefully ignores fields it doesn't understand. New capabilities degrade, never break.
4. **AI-generable.** Every part of the catdef can be produced by a conversational AI — or by AI vision analyzing photographs. No field requires technical knowledge to specify.
5. **Human-readable.** The catdef is JSON with clear key names. A non-developer can read it and understand what their catalog will contain.
6. **Domain-agnostic.** The same field types and patterns work for watches, wines, real estate, museum artifacts, library holdings, inventory, biological specimens, and anything else worth classifying.
7. **Thing-first.** The fundamental unit is the *thing* — a real-world object with structured metadata. Catalogs are collections of things, but a thing can exist independently.

## Top-Level Structure

```json
{
  "catdef": "1.3",

  "product": { ... },
  "inherits_from": "...",
  "requires": { ... },
  "hints": { ... },
  "views": { ... },
  "templates": [ ... ],
  "subcats": { ... },
  "themes": { ... },
  "embed": { ... },
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
    "domain": "scottswatches.example.com",
    "tagline": "Vintage timepieces, documented",
    "description": "<p>A curated catalog of vintage mechanical watches...</p>",
    "contact_email": "scott@example.com",
    "phone": "+1-555-0100",
    "website": "https://scottswatches.com",
    "address": "Vancouver, BC, Canada",
    "hours": "By appointment",
    "owner": "Scott Welch",
    "logo_url": "",
    "social": {
      "instagram": "@scottswatches",
      "twitter": "@scottswatches",
      "facebook": "scottswatches",
      "youtube": "@scottswatches",
      "tiktok": "@scottswatches",
      "bluesky": "scottswatches.bsky.social"
    },
    "sections": [
      {"title": "About", "content": "<p>...rich text...</p>"},
      {"title": "Provenance", "content": "<p>...</p>"},
      {"title": "Inquiries", "content": "<p>Contact me at...</p>"}
    ],
    "theme": "Midnight"
  }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | yes | Display name of the catalog |
| `slug` | string | yes | URL-safe identifier. Used for subdomain routing by platforms that support it |
| `domain` | string | no | Full custom domain if applicable |
| `tagline` | string | no | Short subtitle, displayed in header |
| `description` | string (RichText) | no | Longer description, used in meta tags, About page, and AI context |
| `contact_email` | string | no | Owner's contact email |
| `phone` | string | no | E.164 or local format phone number |
| `website` | string | no | External website URL |
| `address` | string | no | Street address or region. May render as map link |
| `hours` | string | no | Opening hours or availability description |
| `owner` | string | no | Display name of the catalog owner |
| `logo_url` | string | no | URL to a logo image |
| `social` | object | no | Social handles, keyed by platform. Renderer shows icon links |
| `sections` | array | no | Free-form content blocks for the About page. Each is `{title, content}` with RichText content |
| `theme` | string or object | no | Either a theme name (resolved by the runtime) or an inline theme object |

The extended product fields (`phone`, `website`, `address`, `hours`, `social`, `sections`) power an **About page** — for many catalog owners, their Thingalog catalog is their only online presence. Level 2+ runtimes SHOULD render an "About" link that opens these fields as a page or drawer.

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

### Theme Modes

The `mode` field controls the color scheme. A runtime MUST support `light` and `dark`.

| Mode | Description |
|------|-------------|
| `light` | Light background, dark text. Default. |
| `dark` | Dark background, light text. |

---

## Kiosk Mode

Kiosk mode is a **view modifier**, not a theme. Any catalog, any theme, any filter combination can be viewed in kiosk mode. It transforms the catalog into a full-screen display optimized for screens that show content without user interaction — digital signage, museum screens, picture frames, lobby displays, retail windows.

Kiosk mode is activated by URL parameter, not by theme configuration. This means:

1. The catalog owner sets filters in the normal UI ("only Gallery 3 items")
2. Checks a "Kiosk Mode" toggle
3. Copies the resulting URL or embed code
4. Pastes it into a TV browser, Firestick, WordPress page, Weebly site — anywhere that accepts a URL or iframe

**Not a line of code.**

### URL Parameters

```
https://mycatalog.example.com?kiosk=true&filter=Location:Gallery+3&rotate=8&layout=hero&qr=true
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `kiosk` | boolean | `false` | Enable kiosk mode: hides toolbar, navigation, and edit controls |
| `rotate` | number | `8` | Seconds between items. `0` = no auto-rotation |
| `transition` | string | `fade` | Transition effect: `fade`, `slide`, `none` |
| `layout` | string | `hero` | Display layout (see below) |
| `fields` | string | all | Comma-separated field labels to show: `fields=Title,Brand,Year` |
| `filter` | string | none | Filter: `filter=Location:Gallery+3,ObjectType:Sculpture` |
| `qr` | boolean | `false` | Show QR code linking to item's full detail view |
| `dim` | number | `0` | Dim screen after N minutes of inactivity. `0` = never |

### Layouts

| Layout | Description |
|--------|-------------|
| `hero` | Full-bleed photo with info strip at bottom. Best for visual collections. |
| `card` | Centered card with photo and fields. Best for mixed content. |
| `split` | Photo left, structured fields right. Best for data-rich items. |
| `photo` | Photo only, no metadata. Digital picture frame mode. |

### Embed Code

The embed code is just an iframe of the kiosk URL. The renderer generates it:

```html
<iframe src="https://mycatalog.example.com?kiosk=true&filter=Location:Gallery+3&rotate=8"
        width="100%" height="600" style="border:none"></iframe>
```

This is the same mechanism as embed mode (`?embed=true`). Kiosk mode is embed mode with auto-rotation and full-screen layout. They share the same URL parameter system.

### Use cases
- **Museum gallery**: filter by room, hero layout, 12-second rotation, QR codes
- **Real estate office window**: filter by open house date, show price + specs, QR to listing
- **Living room picture frame**: your collection, no filter, fade transition, 8 seconds
- **Restaurant menu board**: filter by available today, show price + allergens, split layout
- **Retail signage**: filter by in stock, show price + photos, card layout
- **Conference/event**: filter by session track, show speaker + time + room
- **WordPress/Weebly page**: embed code dropped into any "What's On" page

### Theme Conformance

The theme is **cosmetic guidance, not behavioral instruction**. A runtime MUST accept and apply theme colors and fonts where possible, but MAY override or adapt based on context:

- **Mobile**: layout adapts (single column, larger tap targets), colors preserved
- **Embed (iframe)**: host page constraints take precedence (width, scroll)
- **Print/PDF**: ignore dark mode, use high-contrast print-safe values
- **Accessibility**: user's OS preferences override (high contrast, reduced motion, forced colors, large text)
- **Kiosk**: renderer optimizes for distance readability (larger fonts, higher contrast)

The principle: **respect the intent, adapt the execution.**

---

## `inherits_from` (string, optional)

Declares that this catalog is a child of a parent **model catalog**. The parent provides the base field_defs, subcats, themes, and views; the child can customize freely.

```json
{
  "inherits_from": "watchomatic_model"
}
```

The parent reference is either:
- A slug within the same platform (`"watchomatic_model"`)
- A fully qualified URL to a published catdef (`"https://watchomatic.com/models/collector.catdef"`)

**Inheritance semantics:**
- At catalog creation, the parent's `templates`, `subcats`, and `themes` are cloned into the child.
- The child may add, rename, or remove fields without affecting the parent.
- Optional live link: child can subscribe to parent updates and receive "new fields available" notifications.
- Parent-scoped themes, views, and CSS are available only to catalogs that inherit from that parent (see `themes.scope`).

**Use cases:**
- **Partner white-label:** Partner provides the perfect `watchomatic_model`; every customer's catalog inherits it. Zero AI wait at creation time, consistent quality, interoperable data across the partner's customer base.
- **Marketplace templates:** A curator publishes "Vintage Watch Collector" as a shareable model; any user can create a catalog that inherits from it.
- **Organizational standards:** A museum consortium publishes a canonical accession template; member institutions inherit it.

**URL invocation:**
Partners typically send customers to the Thingalog builder with:
`https://builder.thingalog.com/?inherits_from=watchomatic_model`

The builder skips the "Describe It" step and creates a catalog pre-populated with the inherited schema.

---

## `requires` (object, optional)

Declares the capabilities the catdef needs from the runtime. Used for compatibility checking and graceful degradation.

```json
{
  "requires": {
    "renderer": ">=1.0",
    "features": ["photos", "social", "embed", "export"],
    "field_types": ["String", "Integer", "Number", "RichText", "Enumerated", "Photo", "Date", "Money"],
    "widgets": ["autocomplete", "dropdown", "checkbox_table", "rating"]
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
| ≤5000 items, heavy media | Full server (Postgres/Neo4j + object storage) |
| >5000 items or realtime | Scaled infrastructure |

---

## `views` (object, optional)

Declares how this catalog prefers to be displayed. A catdef isn't just a schema — it's also a hint about presentation. A concert calendar wants a date-forward view; a real estate catalog wants a map; a watch collection wants a grid. Same engine, different lens.

```json
{
  "views": {
    "primary_axis": "date",
    "modes": ["grid", "calendar", "table", "kiosk"],
    "default": "calendar",
    "default_icon": "🎸",
    "kiosk_layout": "tonight",
    "mode_config": {
      "calendar": {
        "group_by": "week",
        "primary_field": "Show Date"
      }
    }
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `primary_axis` | string | `"thing"` (default), `"date"`, `"place"`. Determines the dominant organizing principle |
| `modes` | array | Which view modes this catalog supports. Renderer hides unavailable modes |
| `default` | string | Mode to load on first open (and for disconnected kiosks) |
| `default_icon` | string | Emoji or icon hint used when no logo is set. Critical for kiosk/Thingstick displays |
| `kiosk_layout` | string | Layout name for kiosk mode. Interpreted by theme |
| `mode_config` | object | Per-mode configuration. Keys are mode names |

**Primary axis:**
- `"thing"` — classic thing-forward catalog (watches, artifacts, products). Default if omitted.
- `"date"` — calendar / timeline / event-stream. Items have a primary Date field.
- `"place"` — map / atlas / location-first. Items have a primary GeoLocation field.

**Mode list:**
- `grid`, `table`, `calendar`, `map`, `kiosk`, `poster`, `timeline`, `gallery` — runtime-dependent

**Default icon note (kiosks):**
Thingstick and other disconnected displays may boot before network is reliable. `default_icon` is shown during pairing and while loading. Pick something distinctive.

**Partner-scoped views** can be declared here if scoped to an `inherits_from` tree. See `themes.scope`.

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
  "label": "Case Diameter",
  "type": "Number",
  "sort_order": 70,
  "unit": "mm",
  "precision": 1,
  "min": 10,
  "max": 60,
  "required": false,
  "importance": "preferred",
  "filterable": true,
  "placeholder": "e.g. 42"
}
```

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `label` | string | yes | — | Display name and internal identifier for this field |
| `type` | string | yes | — | Field type. See Field Types below |
| `sort_order` | integer | yes | — | Display order (ascending). Gaps allowed (10, 20, 30...) |
| `target` | string | conditional | `""` | For Enumerated/Table types: the label namespace for Value nodes |
| `multi` | boolean | no | `false` | Whether multiple values can be attached (Enumerated, Photo) |
| `required` | boolean | no | `false` | Whether the field must have a value before save |
| `importance` | string | no | `"optional"` | For health score: `"required"`, `"preferred"`, or `"optional"` |
| `filterable` | boolean | no | `false` | Whether the list view shows a filter dropdown for this field |
| `widget` | string | no | auto | Override the default widget. See Widget Types below |
| `placeholder` | string | no | `""` | Placeholder text in the empty input |
| `help_text` | string | no | `""` | Tooltip or helper text for the field |
| `columns` | array | conditional | — | For Table type: sub-field definitions for each column |
| `unique` | boolean | no | `false` | Whether values must be unique across items (for identifiers: SKU, accession number, ISBN) |
| `default` | any | no | — | Default value for new items. Type must match the field type |
| `format` | string | no | `""` | For String type: named validation format or regex. See String Formats below |
| `unit` | string | no | `""` | For Number type: display unit (e.g. `"mm"`, `"kg"`, `"sqft"`, `"ml"`) |
| `precision` | integer | no | — | For Number type: decimal places to display |
| `min` | number | no | — | For Number/Integer/Date: minimum allowed value |
| `max` | number | no | — | For Number/Integer/Date: maximum allowed value |
| `step` | number | no | — | For Number/Integer: input step increment |
| `circa` | boolean | no | `false` | For Date type: whether approximate dates are allowed ("c. 1850") |
| `currency` | string | no | `""` | For Money type: default ISO 4217 currency code (e.g. `"USD"`, `"EUR"`) |
| `photo_labels` | string[] | no | — | For Photo type (multi): suggested labels for photos (e.g. `["Front", "Back", "Detail"]`) |
| `max_items` | integer | no | — | For Photo/CloudFile types: maximum number of linked items. `1` = single photo/file (no strip, no add). `null` = unlimited |
| `range` | boolean | no | `false` | For Number/Money/Date types: accept a low/high pair instead of a single value. See Range Modifier |
| `scorable` | string | no | — | Hint for context-aware sorting. Values: `"distance"` (GeoLocation), `"recency"` (Date), `"imminence"` (Date), `"popularity"` (any). See Context-Aware Rendering |
| `primary` | boolean | no | `false` | Marks the field as the primary axis for this template. Used with `views.primary_axis` to auto-pick date/geo fields |

---

## Field Types

| Type | Value Storage | Description |
|------|---------------|-------------|
| `String` | Inline | Single-line text. Optionally validated by `format` |
| `Integer` | Inline | Whole number. Optionally bounded by `min`/`max` |
| `Number` | Inline | Decimal number with optional `unit`, `precision`, `min`, `max`, `step`. Use for measurements, dimensions, percentages, scores, quantities — anything that isn't a whole number or money |
| `RichText` | Inline | Multi-line formatted text (HTML subset) |
| `Enumerated` | Edge to Value node | Pick from (or create) shared values. Dedupe by name (case-insensitive). Requires `target` |
| `Photo` | Edge to Photo node | An image with storage path, dimensions, metadata. Supports `multi: true` for galleries |
| `Table` | Edges to Value nodes with sub-fields | Structured multi-row data. Each row is a Value node with its own Fields defined by `columns` |
| `CloudFile` | Inline (URL + provider metadata) | Pointer to a file in cloud storage (Dropbox, GDrive, OneDrive, Box). Not downloaded, just referenced |
| `URL` | Inline | A web URL with optional auto-extracted title, description, og:image |
| `Date` | Inline | ISO 8601 date string. Supports `circa: true` for approximate dates. Optionally bounded by `min`/`max` |
| `Money` | Inline (amount + currency) | Monetary value with ISO 4217 currency code |
| `Boolean` | Inline | True/false toggle |
| `GeoLocation` | Inline (lat + lng + address + label) | Geographic coordinates with optional structured address. Enables map rendering and distance filtering |

**Support requirements:**
- Runtimes MUST support: `String`, `Integer`, `RichText`, `Enumerated`, `Photo`.
- Runtimes SHOULD support: `Number`, `Table`, `URL`, `Date`, `Money`, `Boolean`, `GeoLocation`.
- Runtimes MAY support: `CloudFile`.

### Subcats (Enriched Enumerated Values)

An Enumerated field's values are simple name strings by default. A **subcat** (sub-catalog) promotes any Enumerated field's value namespace into a mini-catalog with its own field definitions. Each value becomes a record with structured columns.

This is how "Stanley" stops being a bare string and becomes a rich lookup entry: founded 1843, headquartered in New Britain CT, known for hand tools.

**Subcat definition** lives at the top level alongside templates, keyed by the Enumerated field's `target` label:

```json
{
  "subcats": {
    "Brand": {
      "field_defs": [
        {"label": "Founded", "type": "Integer", "sort_order": 10},
        {"label": "Country", "type": "String", "sort_order": 20},
        {"label": "Specialty", "type": "String", "sort_order": 30},
        {"label": "Notes", "type": "RichText", "sort_order": 40}
      ]
    },
    "Condition": {
      "field_defs": [
        {"label": "Description", "type": "String", "sort_order": 10},
        {"label": "Grade", "type": "String", "sort_order": 20}
      ]
    }
  }
}
```

**Value data** follows the same pattern as item fields. Each Value node gets child Field nodes matching the subcat's field_defs:

```json
{
  "name": "Stanley",
  "label": "Brand",
  "fields": [
    {"label": "Founded", "value": 1843},
    {"label": "Country", "value": "USA"},
    {"label": "Specialty", "value": "Hand tools"},
    {"label": "Notes", "value": "Stanley Works, founded in New Britain, Connecticut."}
  ]
}
```

**Key properties:**

| Property | Description |
|----------|-------------|
| `subcats` | Top-level object. Keys are Enumerated `target` labels |
| `field_defs` | Array of field definitions (same schema as template field_defs) |
| `values` | (optional) Seed values for the subcat, keyed by value name. See Seed Values below |

**Architecture:**
- Subcat field_defs use the same schema as template field_defs — same types, same sort_order, same validation attributes
- Value child Field nodes use the same `:HAS` relationship and same node structure as Item child Fields
- A subcat's field_defs can include all scalar types (String, Integer, Number, Date, Money, RichText, Boolean, URL), plus `Photo` and `Enumerated` (both with conformance caveats — see below)
- Adding a subcat field_def propagates empty Field nodes to all existing Values of that label

**Photo fields in subcats:**
Subcats MAY declare Photo fields. A Brand subcat can have a logo. An Artist subcat can have a portrait. A Venue subcat can have an exterior photo.

```json
"subcats": {
  "Brand": {
    "field_defs": [
      {"label": "Logo", "type": "Photo", "sort_order": 10},
      {"label": "Founded", "type": "Integer", "sort_order": 20}
    ]
  }
}
```

The Sub-Catalogs tab can render values as cards with their images — a visual directory of brands, artists, places.

**Enumerated fields in subcats (recursive graphs):**
Subcats MAY declare Enumerated fields, which create edges between values. This allows arbitrary graph hierarchies: Twin Otter → de Havilland → Airplane Manufacturers → Vehicle Manufacturers.

```json
"subcats": {
  "Aircraft Model": {
    "field_defs": [
      {"label": "Manufacturer", "type": "Enumerated", "target": "Manufacturer", "sort_order": 10}
    ]
  },
  "Manufacturer": {
    "field_defs": [
      {"label": "Category", "type": "Enumerated", "target": "Category", "sort_order": 10}
    ]
  }
}
```

**⚠️ Implementation note:** Recursive subcats are a spec feature — the data model supports arbitrary depth. However, runtimes are NOT required to support them. A runtime that supports recursive subcats effectively becomes a graph database editor, which is a different product category than a catalog tool. The spec permits it so that specialized graph-tagging applications (PXMemo-style photo collections, knowledge bases, taxonomies) can use catdef as transport. A general-purpose catalog tool should think carefully before enabling them.

Cycle handling: if a runtime supports recursive subcats, it MUST detect cycles and cap render depth (typically 3-4 levels) to prevent infinite loops in value detail views.

**Seed Values:**
Subcats may declare a `values` object that pre-populates the catalog with seeded value data. Keys are value names; values are `{field_label: value}` pairs:

```json
"subcats": {
  "Brand": {
    "field_defs": [
      {"label": "Founded", "type": "Integer"},
      {"label": "Country", "type": "String"}
    ],
    "values": {
      "Stanley": {"Founded": 1843, "Country": "USA"},
      "DeWalt": {"Founded": 1923, "Country": "USA"},
      "Milwaukee": {"Founded": 1924, "Country": "USA"}
    }
  }
}
```

On import:
1. Subcat field_defs are created first
2. Named values are created (via `find_or_create_value`)
3. Each value's fields are populated from the seed data
4. Photo fields referenced by filename pull from the CATIO `photos/` bundle

Seed values carry in CATIO bundles, enabling partners to ship curated subcat libraries (common brands, common conditions, common materials) that customers get automatically when they inherit from a model catalog.

**Renderer behavior:**
- A "Sub-Catalogs" tab (alongside Items, Photos) lists all Enumerated value namespaces
- Clicking a namespace shows all values in a table with subcat columns
- Value detail view shows subcat fields, editable in write mode
- Enumerated field labels are clickable links to the Sub-Catalogs tab
- If the subcat has a Photo field, the tab may offer a grid view with images

**AI generation:**
- When generating sample data or templates, AI should produce subcat definitions and seed values for every Enumerated field
- 2-4 columns per subcat is typical — enough to be useful, not overwhelming
- Including `photo_query` hints per seeded value allows runtimes to auto-fetch stock photos

**Relationship to Table type:**
- **Table** = per-item structured rows (Complications on *this specific watch*)
- **Subcat** = shared value enrichment (what "Omega" means across *all* watches)
- Both use child Field nodes with the same schema; the difference is scope

**Conformance:**
- Level 1 runtimes MAY ignore subcats (values still work as plain strings)
- Level 2+ runtimes SHOULD render subcat fields in value detail views
- Level 3+ runtimes MUST support subcat CRUD

### Table Type with Spatial Linking (bbox)

`Table` fields hold structured multi-row data — complications on a watch, components on a circuit board, rooms in a floor plan. Each row can optionally carry a **bounding box** (`bbox`) linking it to a region on one of the item's photos.

```json
{
  "label": "Complications",
  "type": "Table",
  "sort_order": 80,
  "target": "Complication",
  "multi": true,
  "columns": [
    {"label": "Complication", "type": "String"},
    {"label": "Position", "type": "String"},
    {"label": "Notes", "type": "String"}
  ]
}
```

**Row values with bounding boxes:**
```json
[
  {
    "Complication": "Chronograph 30-min counter",
    "Position": "3 o'clock",
    "Notes": "Valjoux 72 cam-operated",
    "bbox": {"x": 0.65, "y": 0.35, "w": 0.15, "h": 0.15, "photo_slot": 1}
  },
  {
    "Complication": "Moon phase",
    "Position": "6 o'clock",
    "Notes": "122-year cycle",
    "bbox": {"x": 0.48, "y": 0.72, "w": 0.12, "h": 0.10, "photo_slot": 1}
  }
]
```

**bbox properties** (all coordinates normalized 0..1 relative to the photo):

| Property | Type | Description |
|----------|------|-------------|
| `x` | float | Left edge of the bounding box |
| `y` | float | Top edge of the bounding box |
| `w` | float | Width of the bounding box |
| `h` | float | Height of the bounding box |
| `photo_slot` | integer | Which photo this bbox refers to (1-based slot number) |

**Interactive rendering (screen):**
- The renderer draws SVG/CSS overlays on the photo for each bbox
- Hover a photo region → highlight the corresponding Table row
- Hover a Table row → highlight the bounding box on the photo
- Zero domain-specific code — the renderer doesn't know what a "complication" is, it just draws rectangles and wires hover events

**Print rendering (PDF/catalog):**
- Each bbox becomes a numbered callout: a line from the bbox center to a margin label
- Labels are lettered or numbered: "(a) Chronograph 30-min counter (b) Moon phase"
- Standard museum catalog / product manual style — feature keys generated automatically from the data

**Kiosk rendering (digital signage):**
- Auto-zoom: the display cycles through bbox regions, zooming into each one with the label overlaid
- A guided visual tour of the object — "Ivory paddle", "Bone ulu", "Carved handle" — with smooth pan/zoom transitions
- Each bbox gets screen time proportional to its size, or equal time if configured

**AI generation:**
- Claude vision can identify regions of interest in a photo and generate Table rows with bboxes automatically
- The photo-drop builder creates spatially-linked annotations without any manual drawing

The `bbox` property is optional on any Table row. Rows without bbox are rendered normally (no spatial link). This means the same Table can have some rows linked to photo regions and others that are purely textual.

### Number Type

`Number` is the workhorse for physical measurements, scores, percentages, and quantities — anything where sorting, comparison, and unit display matter.

```json
{"label": "Case Diameter",  "type": "Number", "unit": "mm", "precision": 1, "min": 10, "max": 60}
{"label": "Weight",         "type": "Number", "unit": "g",  "precision": 0}
{"label": "ABV",            "type": "Number", "unit": "%",  "precision": 1, "min": 0, "max": 100}
{"label": "Mileage",        "type": "Number", "unit": "km", "precision": 0}
{"label": "Square Footage", "type": "Number", "unit": "sqft", "precision": 0}
{"label": "Rating",         "type": "Number", "min": 0, "max": 100, "step": 0.5, "widget": "rating"}
```

When `unit` is present, the runtime SHOULD display it as a suffix (e.g. "42 mm", "13.5%"). The value stored is always the raw number; the unit is metadata.

### GeoLocation Type

`GeoLocation` stores geographic coordinates with an optional human-readable address. Enables map views, distance-based sorting, and geo-filtering.

```json
{"label": "Location", "type": "GeoLocation"}
```

**Value shape:**
```json
{
  "lat": 48.8566,
  "lng": 2.3522,
  "address": "Musée du Louvre, Rue de Rivoli, 75001 Paris, France",
  "label": "Louvre Museum"
}
```

At minimum, `lat` and `lng` must be present. `address` and `label` are optional display strings.

### Date Type Extensions

`Date` stores an ISO 8601 date string. When `circa` is `true` on the field definition, the runtime SHOULD accept and display approximate dates:

```json
{"label": "Year Made", "type": "Date", "circa": true}
```

**Value shapes:**
- Exact: `"2024-06-15"` → displayed as "June 15, 2024"
- Year only: `"1850"` → displayed as "1850"
- Approximate: `{"date": "1850", "circa": true}` → displayed as "c. 1850"
- Range: `{"start": "1845", "end": "1855"}` → displayed as "1845–1855"

### Money Type

`Money` stores a monetary value with an ISO 4217 currency code. The field def may specify a `currency` default.

```json
{"label": "Purchase Price", "type": "Money", "currency": "USD"}
```

**Value shape:**
```json
{"amount": 4500.00, "currency": "USD"}
```

If the value omits `currency`, the field def's `currency` default is used. The runtime SHOULD format according to the currency's conventions (e.g. "$4,500.00" for USD, "€4.500,00" for EUR).

### Range Modifier

A field definition MAY set `range: true` on `Number`, `Money`, or `Date` types to accept a pair of values — a low/high, min/max, or start/end — instead of a single scalar.

```json
{"label": "Case Diameter", "type": "Number", "range": true, "unit": "mm"}
{"label": "Price Range", "type": "Money", "range": true, "currency": "USD"}
{"label": "Exhibition Dates", "type": "Date", "range": true}
```

**Value shapes:**

- `Number` with `range: true` → `{"min": 42, "max": 45}`
- `Money` with `range: true` → `{"low": {"amount": 500, "currency": "USD"}, "high": {"amount": 1500, "currency": "USD"}}`
- `Date` with `range: true` → `{"start": "2024-06-01", "end": "2024-06-05"}`

**Rendering:**
- Two adjacent input widgets (e.g. "From" / "To")
- Display as "42–45 mm", "$500–$1,500", "Jun 1–5, 2024"
- Filter/search match if the search value falls within the range

**Sort semantics:**
- Sort by the low end by default
- Runtimes MAY offer "sort by high" or "sort by midpoint" as options

Ranges do not modify other type attributes. A `Number` with `range: true, unit: "mm", precision: 1` gives you a diameter range in millimeters with one decimal.

### Context-Aware Rendering

Fields may declare a `scorable` attribute that tells the runtime how to weight them when the viewing context is known. The same CATIO bundle can render very differently depending on where, when, and to whom it's displayed.

```json
{"label": "Venue", "type": "Enumerated", "target": "Venue", "scorable": "distance"}
{"label": "Show Date", "type": "Date", "scorable": "imminence"}
{"label": "Popularity", "type": "Integer", "scorable": "popularity"}
```

**Scorable values:**

| Value | Applicable to | Meaning |
|-------|---------------|---------|
| `"distance"` | GeoLocation (or Enumerated linking to a Venue subcat with geo fields) | Weight items closer to viewer's location higher |
| `"recency"` | Date | Weight newer items higher |
| `"imminence"` | Date | Weight upcoming items higher ("tonight" > "next week" > "last month") |
| `"popularity"` | Integer, Number | Higher values weight higher |
| `"relevance"` | any | User-scored relevance signal (likes, views) |

**Runtime behavior:**
- A renderer that knows the viewer's geolocation, local time, or profile MAY use scorable fields to re-sort items
- A concert calendar in Brooklyn shows L'Amour shows first; in LA it shows Whisky a Go Go shows first
- A Thingstick in a hotel lobby sorts a restaurant guide by walking distance; a mobile app does the same for the user's current location
- The same data, different orderings — context as a rendering dimension

**Signals available to the runtime:**
- Device geolocation (if granted)
- Current time in the device's timezone
- Viewer identity (if authenticated)
- Kiosk location (set at pairing time)

Scorable fields are hints, not guarantees. A renderer without geolocation simply falls back to the catalog's default sort.

### Photo Type with Galleries and Labels

When `multi: true` is set on a Photo field, the field represents an ordered gallery rather than a single image.

```json
{"label": "Photos", "type": "Photo", "multi": true, "importance": "required"}
```

The runtime stores an ordered list of photos with per-photo captions and a designated hero/primary image.

### Photo Labels

The `photo_labels` attribute declares suggested labels for photos in a gallery. Each photo can be tagged with a label. Labels are not enforced — you can have 3 "Kitchen" photos and 0 "Backyard" photos.

```json
{"label": "Photos", "type": "Photo", "multi": true,
 "photo_labels": ["Street View", "Kitchen", "Living Room", "Master Bedroom", "Backyard"]}
```

**Use cases:**
- **Real estate**: Street View ×1, Kitchen ×3, Master Bedroom ×2, Backyard ×1
- **Vintage scans**: Original Scan, Edited Master, Social Version (versions of the same image)
- **Museum objects**: Front, Back, Detail, Installation View
- **Products**: Hero Shot, Lifestyle, Close-up, Packaging

The label is stored on the photo-item edge (the `caption` property). The renderer displays labels as tags or tabs. The health score can track whether expected labels are present.

Labels are suggestions, not slots. An item can have photos with labels not in the template's list, and can have multiple photos with the same label.

### Limiting Photo and File Counts

The `max_items` attribute on a Photo or CloudFile field controls the maximum number of linked items:

```json
{"label": "Photos", "type": "Photo", "multi": true, "max_items": 10}
{"label": "Hero Image", "type": "Photo", "multi": false, "max_items": 1}
{"label": "Attachments", "type": "CloudFile", "multi": true, "max_items": 5}
```

When `max_items` is set, the runtime SHOULD:
- Hide the "add" button when the limit is reached
- Display the limit in the UI (e.g. "3 of 10 photos")
- Reject additional uploads with a clear message

When `max_items` is `null` or omitted, no limit is enforced. When `multi: false`, `max_items` defaults to `1`.

### Photo Transforms (Per-Item Edge Properties)

Each photo-item link carries optional transform properties that describe how the photo should be displayed for that item. These are **per-edge**, not per-photo — the same photo linked to two items can have different crops, rotations, and deskew settings.

```json
{
  "filename": "watch_front.jpg",
  "slot": 1,
  "is_primary": true,
  "caption": "Front view",
  "rotation": 90,
  "crop_mode": "freeform",
  "crop_x1": 0.15,
  "crop_y1": 0.20,
  "crop_x2": 0.85,
  "crop_y2": 0.75,
  "deskew": null
}
```

#### Transform Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `slot` | integer | auto | Position in the item's photo gallery (1-based) |
| `is_primary` | boolean | `false` | Whether this is the hero/card photo. Slot 1 is typically primary |
| `caption` | string | `""` | Per-slot caption or label tag |
| `rotation` | integer | `0` | Clockwise rotation in degrees: `0`, `90`, `180`, `270` |
| `crop_mode` | string | `"none"` | `"none"`, `"freeform"`, or `"deskew"` |
| `crop_x1` | float | `0` | Freeform crop: left edge (0..1, in original image space) |
| `crop_y1` | float | `0` | Freeform crop: top edge (0..1) |
| `crop_x2` | float | `1` | Freeform crop: right edge (0..1) |
| `crop_y2` | float | `1` | Freeform crop: bottom edge (0..1) |
| `deskew` | object | `null` | Perspective correction: 4 corner points |

#### Coordinate Space

All crop coordinates are in **original image space** (before rotation). This means:

1. The runtime displays the original (unrotated) image
2. Applies `crop_x1/y1/x2/y2` to select the region (via CSS `background-size`/`background-position` or equivalent)
3. Applies `rotation` as a final visual transform (via CSS `transform: rotate()` or equivalent)

This order matters: crop first, rotate second. The coordinates never need to be recalculated when rotation changes.

#### Deskew (Perspective Correction)

When `crop_mode` is `"deskew"`, the `deskew` object contains four corner points defining a quadrilateral on the image. The runtime applies a perspective transform to rectify the region into a rectangle.

```json
{
  "crop_mode": "deskew",
  "rotation": 0,
  "deskew": {
    "tl": {"x": 0.15, "y": 0.10},
    "tr": {"x": 0.85, "y": 0.12},
    "br": {"x": 0.83, "y": 0.88},
    "bl": {"x": 0.17, "y": 0.90}
  }
}
```

| Property | Type | Description |
|----------|------|-------------|
| `tl` | `{x, y}` | Top-left corner (0..1 normalized, in **rotated** image space) |
| `tr` | `{x, y}` | Top-right corner |
| `br` | `{x, y}` | Bottom-right corner |
| `bl` | `{x, y}` | Bottom-left corner |

**Important:** Deskew coordinates are in **rotated** image space (rotation is applied first, then deskew). This differs from crop coordinates which are in original space. The reason: deskew requires server-side pixel manipulation (CSS cannot do perspective transforms), so the server applies rotation then deskew to generate a corrected thumbnail.

#### Rendering Requirements

| Transform | CSS-capable | Server-side required |
|-----------|------------|---------------------|
| Rotation | Yes (`transform: rotate()`) | No |
| Freeform crop | Yes (`background-size` + `background-position`) | No |
| Deskew | No | Yes (perspective warp, generates a thumbnail) |

Runtimes MUST support rotation and freeform crop via client-side rendering (instant, no server round-trip). Runtimes SHOULD support deskew via server-side thumbnail generation. Runtimes that don't support deskew SHOULD display the uncorrected image with a visual indicator.

#### Export/Import

Photo transforms MUST be preserved during export and import. Each photo reference in a catio document includes its transform properties:

```json
{
  "photos": [
    {
      "filename": "scan_001.jpg",
      "slot": 1,
      "rotation": 90,
      "crop_mode": "freeform",
      "crop_x1": 0.1, "crop_y1": 0.2,
      "crop_x2": 0.9, "crop_y2": 0.8
    }
  ]
}
```

### String Formats

The `format` attribute on a String field enables validation and specialized rendering without creating new field types. Named formats provide well-known validation rules; custom formats use regex.

| Format | Description | Example |
|--------|-------------|---------|
| `email` | Email address. Renders as `mailto:` link | `scott@example.com` |
| `phone` | Phone number. Renders as `tel:` link | `+1-555-123-4567` |
| `isbn` | ISBN-10 or ISBN-13 with check digit validation | `978-0-13-468599-1` |
| `issn` | ISSN with check digit validation | `0378-5955` |
| `doi` | Digital Object Identifier | `10.1000/xyz123` |
| `vin` | Vehicle Identification Number (17 chars, checksum) | `1HGBH41JXMN109186` |
| `upc` | UPC-A barcode (12 digits) | `012345678905` |
| `ean` | EAN-13 barcode (13 digits) | `4006381333931` |
| `sku` | Stock Keeping Unit (freeform, but unique) | `WCH-OMG-SPD-001` |
| `accession` | Museum accession number (freeform, unique) | `2024.001.003` |
| `hex_color` | Hex color code. Renders as color swatch | `#1a365d` |

Custom regex: `"format": "^[A-Z]{2}-\\d{4}$"` (any string starting with `^` is treated as a regex pattern).

When a named format implies uniqueness (e.g. `isbn`, `vin`, `sku`, `accession`), the runtime SHOULD enforce uniqueness even if `unique` is not explicitly set.

---

## Widget Types

Widgets control how a field is presented in the UI. The runtime selects a default widget based on the field type, but the catdef can override it.

| Widget | Best For | Description |
|--------|----------|-------------|
| `text` | String, Integer | Single-line input |
| `textarea` | RichText | Multi-line editor |
| `number` | Integer, Number, Money | Numeric input with validation |
| `autocomplete` | Enumerated (open-ended) | Type-ahead with find-or-create |
| `dropdown` | Enumerated (closed set) | Single or multi select dropdown |
| `checkbox_table` | Enumerated (multi, all visible) | All options displayed with checkboxes |
| `table` | Table | Rows with sub-columns |
| `photo` | Photo | Upload/capture with preview. Gallery mode when multi:true |
| `url` | URL | Input with auto-preview (favicon, og:image) |
| `file_picker` | CloudFile | OAuth-connected cloud file browser |
| `date` | Date | Date picker. Supports circa mode and ranges |
| `toggle` | Boolean | On/off switch |
| `rating` | Number (bounded) | Star rating, slider, or gauge. Requires `min`/`max` |
| `map` | GeoLocation | Map pin picker with address autocomplete |
| `color_swatch` | String (format: hex_color) | Color picker with swatch preview |
| `barcode` | String (format: upc/ean) | Barcode renderer with scan input |

### Default Widget Selection

| Field Type | Default Widget |
|------------|----------------|
| String | `text` |
| Integer | `number` |
| Number | `number` |
| RichText | `textarea` |
| Enumerated (multi:false) | `autocomplete` |
| Enumerated (multi:true) | `autocomplete` |
| Photo (multi:false) | `photo` |
| Photo (multi:true) | `photo` (gallery mode) |
| Table | `table` |
| CloudFile | `file_picker` |
| URL | `url` |
| Date | `date` |
| Money | `number` |
| Boolean | `toggle` |
| GeoLocation | `map` |

---

## `themes` (object, optional)

Named theme packs that can be applied to the catalog. Themes are a presentation layer only — they never modify data.

```json
{
  "themes": {
    "midnight": {
      "accent": "#1a365d",
      "bg": "#0d1117",
      "ink": "#e6edf3",
      "mode": "dark"
    },
    "watchomatic_vintage": {
      "accent": "#c9a04e",
      "bg": "#1a1208",
      "ink": "#e8d9b5",
      "mode": "dark",
      "font_heading": "'Playfair Display', serif",
      "scope": "inherits_from:watchomatic_model"
    }
  }
}
```

**Theme properties (non-exhaustive — runtimes pass unknown keys to CSS custom properties):**

| Field | Description |
|-------|-------------|
| `accent` | Primary color for interactive elements |
| `bg` | Background color |
| `ink` | Primary text color |
| `mode` | `"light"` or `"dark"` — hint for surrounding UI |
| `font_heading`, `font_body` | CSS font-family strings |
| `css` | Optional full CSS override block |
| `scope` | Inheritance scope (see below) |

**Partner-scoped themes:**

A theme's `scope` attribute restricts its visibility to catalogs matching the scope expression:

- `"scope": "inherits_from:watchomatic_model"` — only catalogs that inherit from `watchomatic_model` can apply this theme
- `"scope": "tier:pro"` — only catalogs on the Pro tier
- `"scope": "public"` (default) — available to any catalog

Partner-scoped themes, views, and CSS are the partner's value-add — their customers get a curated visual experience that non-partner customers cannot access. This creates healthy ecosystem dynamics: partners compete on experience quality; customer data remains portable via CATIO.

---

## `embed` (object, optional)

Declares how this catalog behaves when embedded in another site via iframe or widget.

```json
{
  "embed": {
    "enabled": true,
    "allowed_domains": ["*"],
    "default_view": "grid",
    "default_size": {"width": "100%", "height": "600"},
    "attribution": "required",
    "hide_header": true,
    "hide_sign_in": true
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `enabled` | boolean | Whether embedding is permitted |
| `allowed_domains` | string[] | Parent domains permitted to embed. `["*"]` = any site |
| `default_view` | string | View mode to load when embedded |
| `default_size` | object | Suggested iframe size |
| `attribution` | string | `"required"` (show "Powered by") or `"none"` (paid tiers only) |
| `hide_header` | boolean | Hide the catalog header in embed mode |
| `hide_sign_in` | boolean | Hide the sign-in button |

**Embed URL pattern:**
Runtimes invoke embed mode via `?embed=true` and MAY accept additional parameters:
- `?embed=true&view=calendar` — override view mode
- `?embed=true&filter=Brand:Stanley` — pre-apply filter
- `?embed=true&theme=watchomatic_vintage` — apply named theme

**Copy-paste snippet** produced by a conforming runtime's "Get embed code" feature:
```html
<iframe src="https://scotts-tools.thingalog.app/?embed=true&view=grid"
        width="100%" height="600" frameborder="0"
        style="border:0;border-radius:12px;"
        loading="lazy"
        allow="fullscreen"></iframe>
```

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
      "recipient_email": "owner@example.com",
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

## Extension Namespace

catdef is extensible. Any implementer can add custom fields, settings, or metadata without modifying the spec — and without risk of collision with future spec versions or other implementers.

### Naming Convention

Extension identifiers use the prefix `x.` followed by a reverse-DNS namespace and an identifier:

```
x.<domain>.<identifier>
```

Examples:
```json
{"label": "x.calendly.com.next_available",    "type": "DateTime"}
{"label": "x.pxcatalog.com.provenance_score",  "type": "Number"}
{"label": "x.gameengine.io.lod_level",         "type": "Integer"}
```

The domain is the extension author's domain. DNS *is* the registry — no central coordination needed. The identifier is freeform within the author's namespace.

### Extension Scope

The `x.` prefix applies anywhere an identifier appears in a catdef:

- **Field labels**: `"label": "x.myapp.com.custom_metric"`
- **Settings keys**: `"x.myapp.com.sync_interval": 300`
- **Feature names**: `"features": ["photos", "x.myapp.com.3d_viewer"]`
- **Widget names**: `"widget": "x.myapp.com.panorama"`

### Import Behavior

Runtimes MUST handle unknown identifiers according to these tiers:

| Identifier | Behavior |
|------------|----------|
| Known spec identifier | Validate normally |
| `x.*` extension | Accept silently. Store as-is. Round-trip without loss. |
| Unknown, not `x.*` | Accept with a **hard warning** (see below) |

**Hard warning text for non-namespaced unknowns:**

> Unrecognized identifier '{name}' is not defined in catdef v{version} and is not in an extension namespace. Use `x.yourdomain.com.{name}` instead. Non-namespaced extensions **may be rejected** in future spec versions.

The warning MUST be surfaced to the user (not silently swallowed). The data SHOULD still be accepted in the current version to avoid data loss, but implementers are explicitly warned that future spec versions MAY reject non-namespaced unknowns.

### Guidelines for Extension Authors

1. **Use your own domain.** Don't squat on someone else's namespace.
2. **Document your extensions.** Publish a schema or README at your domain so others can interoperate.
3. **Expect graceful ignorance.** Runtimes that don't understand your extension will store it but won't render or validate it.
4. **Don't depend on extensions for core functionality.** A catdef with all `x.*` fields stripped should still be a valid, useful catalog.

### Promotion Path

If an extension proves widely useful, it may be promoted to a first-class spec feature in a future version. At that point:
- The `x.*` version remains valid (backwards compatibility)
- The new spec identifier becomes the canonical form
- Runtimes SHOULD accept both during a transition period

---

## Complete Example: Vintage Watch Catalog

```json
{
  "catdef": "1.3",

  "product": {
    "name": "Scott's Watch Collection",
    "slug": "scottswatches",
    "tagline": "Vintage timepieces, documented",
    "contact_email": "scott@example.com",
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
    "field_types": ["String", "Integer", "Number", "RichText", "Enumerated", "Photo", "Date", "Money"]
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
        {"label": "Reference",        "type": "String",     "sort_order": 30, "importance": "preferred", "format": "sku", "unique": true, "placeholder": "e.g. 145.022-69"},
        {"label": "Year",             "type": "Integer",    "sort_order": 40, "importance": "preferred", "min": 1800, "max": 2030},
        {"label": "Movement",         "type": "Enumerated", "sort_order": 50, "target": "Movement", "filterable": true, "widget": "dropdown"},
        {"label": "Case Material",    "type": "Enumerated", "sort_order": 60, "target": "Material", "filterable": true},
        {"label": "Case Diameter",    "type": "Number",     "sort_order": 70, "unit": "mm", "precision": 1, "min": 20, "max": 55, "placeholder": "e.g. 42"},
        {"label": "Complications",    "type": "Table",      "sort_order": 80, "target": "Complication", "multi": true, "widget": "table", "columns": [
          {"label": "Complication", "type": "String"},
          {"label": "Subdial", "type": "String"},
          {"label": "Notes", "type": "String"}
        ]},
        {"label": "Condition",        "type": "Enumerated", "sort_order": 90,  "target": "Grade", "widget": "dropdown"},
        {"label": "Box & Papers",     "type": "Enumerated", "sort_order": 100, "target": "Completeness", "widget": "dropdown"},
        {"label": "Photos",           "type": "Photo",      "sort_order": 110, "multi": true, "importance": "required"},
        {"label": "Purchase Price",   "type": "Money",      "sort_order": 120, "currency": "USD"},
        {"label": "Purchased From",   "type": "Enumerated", "sort_order": 130, "target": "Dealer"},
        {"label": "Purchase Date",    "type": "Date",       "sort_order": 140},
        {"label": "Service History",  "type": "RichText",   "sort_order": 150, "importance": "preferred"},
        {"label": "Notes",            "type": "RichText",   "sort_order": 160}
      ]
    }
  ],

  "subcats": {
    "Brand": {
      "field_defs": [
        {"label": "Founded", "type": "Integer", "sort_order": 10},
        {"label": "Country", "type": "String", "sort_order": 20},
        {"label": "Specialty", "type": "String", "sort_order": 30},
        {"label": "Active", "type": "Boolean", "sort_order": 40}
      ]
    },
    "Movement": {
      "field_defs": [
        {"label": "Type", "type": "String", "sort_order": 10},
        {"label": "Jewels", "type": "Integer", "sort_order": 20},
        {"label": "Frequency", "type": "String", "sort_order": 30}
      ]
    },
    "Dealer": {
      "field_defs": [
        {"label": "Location", "type": "String", "sort_order": 10},
        {"label": "Website", "type": "URL", "sort_order": 20},
        {"label": "Notes", "type": "String", "sort_order": 30}
      ]
    }
  },

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

## Complete Example: E-Commerce Product Catalog

```json
{
  "catdef": "1.3",

  "product": {
    "name": "Artisan Ceramics Shop",
    "slug": "artisan-ceramics",
    "tagline": "Handmade pottery, direct from the studio"
  },

  "requires": {
    "renderer": ">=1.0",
    "field_types": ["String", "Number", "Enumerated", "Photo", "Money", "Boolean"]
  },

  "templates": [
    {
      "name": "Product",
      "icon": "🏺",
      "field_defs": [
        {"label": "Name",           "type": "String",     "sort_order": 10, "required": true},
        {"label": "SKU",            "type": "String",     "sort_order": 15, "format": "sku", "unique": true},
        {"label": "Category",       "type": "Enumerated", "sort_order": 20, "target": "Category", "filterable": true},
        {"label": "Price",          "type": "Money",      "sort_order": 30, "currency": "USD", "required": true},
        {"label": "Cost",           "type": "Money",      "sort_order": 35, "currency": "USD"},
        {"label": "Weight",         "type": "Number",     "sort_order": 40, "unit": "g", "precision": 0},
        {"label": "Height",         "type": "Number",     "sort_order": 50, "unit": "cm", "precision": 1},
        {"label": "Width",          "type": "Number",     "sort_order": 60, "unit": "cm", "precision": 1},
        {"label": "Glaze",          "type": "Enumerated", "sort_order": 70, "target": "Glaze", "filterable": true},
        {"label": "In Stock",       "type": "Boolean",    "sort_order": 80, "default": true},
        {"label": "Qty Available",  "type": "Integer",    "sort_order": 85, "min": 0, "default": 1},
        {"label": "Photos",         "type": "Photo",      "sort_order": 90, "multi": true, "importance": "required"},
        {"label": "Description",    "type": "RichText",   "sort_order": 100}
      ]
    }
  ],

  "settings": {
    "public": true,
    "embed": {"enabled": true, "powered_by": true},
    "inquire": {"enabled": true, "ai_assistant": true}
  }
}
```

---

## Complete Example: Museum Accession Database

```json
{
  "catdef": "1.3",

  "product": {
    "name": "Pacific Northwest Heritage Collection",
    "slug": "pnw-heritage",
    "tagline": "Preserving the material culture of the Pacific Northwest"
  },

  "requires": {
    "renderer": ">=1.0",
    "field_types": ["String", "Integer", "Number", "RichText", "Enumerated", "Photo", "Date", "GeoLocation"]
  },

  "templates": [
    {
      "name": "Artifact",
      "icon": "🏛️",
      "field_defs": [
        {"label": "Title",            "type": "String",      "sort_order": 10, "required": true},
        {"label": "Accession Number", "type": "String",      "sort_order": 15, "format": "accession", "unique": true, "placeholder": "e.g. 2024.001.003"},
        {"label": "Creator",          "type": "Enumerated",  "sort_order": 20, "target": "Person", "multi": true, "filterable": true},
        {"label": "Date Created",     "type": "Date",        "sort_order": 30, "circa": true},
        {"label": "Object Type",      "type": "Enumerated",  "sort_order": 40, "target": "ObjectType", "filterable": true},
        {"label": "Material",         "type": "Enumerated",  "sort_order": 50, "target": "Material", "multi": true, "filterable": true},
        {"label": "Height",           "type": "Number",      "sort_order": 60, "unit": "cm", "precision": 1},
        {"label": "Width",            "type": "Number",      "sort_order": 65, "unit": "cm", "precision": 1},
        {"label": "Depth",            "type": "Number",      "sort_order": 67, "unit": "cm", "precision": 1},
        {"label": "Weight",           "type": "Number",      "sort_order": 68, "unit": "g", "precision": 0},
        {"label": "Origin",           "type": "GeoLocation", "sort_order": 70},
        {"label": "Location",         "type": "Enumerated",  "sort_order": 75, "target": "Location", "filterable": true},
        {"label": "Condition",        "type": "Enumerated",  "sort_order": 80, "target": "Condition", "widget": "dropdown"},
        {"label": "Provenance",       "type": "RichText",    "sort_order": 90},
        {"label": "Photos",           "type": "Photo",       "sort_order": 100, "multi": true},
        {"label": "Estimated Value",  "type": "Money",       "sort_order": 110, "currency": "USD"},
        {"label": "Notes",            "type": "RichText",    "sort_order": 120}
      ]
    }
  ],

  "settings": {
    "public": true,
    "health_score": {"enabled": true, "grading": "letter"},
    "history": true,
    "trash": true
  }
}
```

---

## Complete Example: Concert Calendar (Date-forward)

This example showcases v1.3 features: date-forward primary axis, partner inheritance, subcat images (band logos, venue exteriors), About page, scorable fields for geo-weighted kiosks.

```json
{
  "catdef": "1.3",

  "inherits_from": "venuepartner_model",

  "product": {
    "name": "L'Amour Brooklyn",
    "slug": "lamour",
    "tagline": "Rock Capitol of Brooklyn",
    "description": "<p>Since 1981. Live rock every night.</p>",
    "website": "https://lamourbrooklyn.com",
    "address": "1545 62nd St, Brooklyn, NY",
    "hours": "Doors 8pm, every night",
    "phone": "+1-718-232-1616",
    "social": {"instagram": "@lamourbrooklyn"},
    "sections": [
      {"title": "About", "content": "<p>The Rock Capitol of Brooklyn since 1981...</p>"},
      {"title": "Tickets", "content": "<p>Box office opens at 6pm...</p>"}
    ]
  },

  "views": {
    "primary_axis": "date",
    "modes": ["calendar", "grid", "poster", "kiosk"],
    "default": "calendar",
    "default_icon": "🎸",
    "kiosk_layout": "tonight"
  },

  "templates": [
    {
      "name": "Show",
      "icon": "🎸",
      "field_defs": [
        {"label": "Show Date", "type": "Date", "sort_order": 10, "required": true, "primary": true, "scorable": "imminence"},
        {"label": "Headliner", "type": "Enumerated", "target": "Band", "sort_order": 20, "required": true},
        {"label": "Opening Acts", "type": "Enumerated", "target": "Band", "sort_order": 30, "multi": true},
        {"label": "Ticket Price", "type": "Money", "range": true, "currency": "USD", "sort_order": 40},
        {"label": "Poster", "type": "Photo", "sort_order": 50},
        {"label": "Notes", "type": "RichText", "sort_order": 60}
      ]
    }
  ],

  "subcats": {
    "Band": {
      "field_defs": [
        {"label": "Logo", "type": "Photo", "sort_order": 10},
        {"label": "Genre", "type": "String", "sort_order": 20},
        {"label": "Origin", "type": "String", "sort_order": 30},
        {"label": "Formed", "type": "Integer", "sort_order": 40}
      ]
    }
  },

  "themes": {
    "lamour_flyer": {
      "accent": "#e00000",
      "bg": "#f5f2e8",
      "ink": "#111111",
      "mode": "light",
      "font_heading": "'Chunk Five', 'Impact', sans-serif",
      "scope": "inherits_from:venuepartner_model"
    }
  },

  "embed": {
    "enabled": true,
    "default_view": "calendar",
    "default_size": {"width": "100%", "height": "720"},
    "attribution": "required",
    "hide_header": false,
    "hide_sign_in": true
  },

  "settings": {
    "public": true,
    "social": {"likes": true, "comments": false}
  }
}
```

On a venue's lobby kiosk, this renders as a date-forward calendar with tonight's show as the hero card. On the venue's website, the same catalog embeds as a calendar widget. On a mobile phone, the same catalog shows the next upcoming show first (imminence scoring). On a Thingstick in another city, distance scoring could surface shows at nearby sister venues.

---

## Conformance Levels

### Level 1: Minimal (browser-only)
- Reads catdef and renders item list + item detail
- Supports field types: String, Integer, RichText, Enumerated, Photo
- In-memory or LocalStorage persistence
- No server required
- MAY ignore: subcats, views declaration, inherits_from, embed config, themes

### Level 2: Standard (lightweight server)
- Level 1 plus: search, sort, filter, export, history, trash
- Persistent storage (SQLite, flat files, or equivalent)
- Photo upload and storage
- API endpoints per the catdef API spec
- SHOULD render About page from expanded `product` object
- SHOULD render subcat fields in value detail
- MAY ignore: inherits_from, partner-scoped themes

### Level 3: Full (graph-native)
- Level 2 plus: social layer, embed, inquire, comments, health score
- Graph database or equivalent
- Real-time collaborative filtering
- Multi-tenant support
- Template sharing
- MUST support subcat CRUD (seed values, Photo fields in subcats)
- SHOULD support views declaration (calendar, map if primary_axis is date/place)
- MAY support recursive subcats (Enumerated in subcats). Runtimes that do MUST handle cycle detection and depth caps.
- **Recursive subcats implementation note:** Supporting recursive subcats turns the product into a graph-database editor, which is a different product category than a catalog tool. Most Level 3 runtimes should deliberately NOT support recursive subcats. The spec permits them so that specialized graph-tagging applications (PXMemo-style photo collections, knowledge bases, taxonomies) can use catdef as a transport format.

### Level 4: Platform
- Level 3 plus: AI onboarding, custom domains, billing, wildcard subdomains
- Theme and template marketplace
- Browser plugin integration
- Federated catalog discovery
- Partner inheritance (inherits_from with live update link)
- Partner-scoped themes and views
- Context-aware rendering (scorable fields + environment hints)
- Kiosk pairing and management (Thingstick-class devices)

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
- String `format` regex patterns MUST be validated in a sandbox (no ReDoS). Runtimes SHOULD impose a maximum pattern length and execution timeout.

---

## MIME Types

| MIME Type | Description |
|-----------|-------------|
| `application/vnd.openthing+json` | A single classified object |
| `application/vnd.opencatalog+json` | A collection with schema, data, and settings |
| `application/vnd.catdef+json` | A schema definition (templates only, no data) |

## File Extensions

| Extension | Description |
|-----------|-------------|
| `.openthing` | A single classified object — the minimal unit. One real-world object with structured metadata. Opening an `.openthing` file implies a schema; a schema implies a catalog. |
| `.opencatalog` | A complete catalog — schema, data, values, settings, theme. The full interchange format for collections. |
| `.catdef` | Schema only — template definitions, no data. Used for starter kits, template marketplace, and "create a catalog like this." |

These extensions belong to the catdef standard, not to any runtime. Any conformant application reads and writes all three.

---

*Specification version 1.1. April 2026.*
*An open standard. Licensed under MIT.*
