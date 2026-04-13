# catdef — Specification v1.1

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
  "catdef": "1.1",

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
    "domain": "scottswatches.example.com",
    "tagline": "Vintage timepieces, documented",
    "description": "A curated catalog of vintage mechanical watches collected over 30 years.",
    "contact_email": "scott@example.com",
    "owner": "Scott Welch",
    "logo_url": "",
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
| `description` | string | no | Longer description, used in meta tags and AI context |
| `contact_email` | string | no | Owner's contact email |
| `owner` | string | no | Display name of the catalog owner |
| `logo_url` | string | no | URL to a logo image |
| `theme` | string or object | no | Either a theme name (resolved by the runtime) or an inline theme object |

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
  "catdef": "1.1",

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
  "catdef": "1.1",

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
  "catdef": "1.1",

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
- API endpoints per the catdef API spec

### Level 3: Full (graph-native)
- Level 2 plus: social layer, embed, inquire, comments, health score
- Graph database or equivalent
- Real-time collaborative filtering
- Multi-tenant support
- Template sharing

### Level 4: Platform
- Level 3 plus: AI onboarding, custom domains, billing, wildcard subdomains
- Theme and template marketplace
- Browser plugin integration
- Federated catalog discovery

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
