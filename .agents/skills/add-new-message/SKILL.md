---
name: add-new-message
description: Use when adding a new Flockwave protocol message type (e.g., TIMESYNC-STATUS, X-FOO-BAR). Conducts a systematic Q&A to gather message name, examples, and field details, then creates all schema JSON files, AsciiDoc documentation, and registers the message in the body union schemas. Handles X- prefix stripping automatically.
---

# Adding a new Flockwave message type

## Workflow

The agent should conduct a systematic Q&A with the user, one step at a time, until all necessary information is collected. After each answer, the agent may infer follow-up questions automatically.

---

### Step 1 — Message type name

Ask: *"What is the message type name?"*

Examples: `TIMESYNC-STATUS`, `X-FOO-BAR`, `OBJ-CMD`, `RTK-SURVEY`

**Rules:**
- If the name has an `X-` prefix (e.g., the user says `X-FOO-BAR`), **strip the `X-`** and treat the effective name as `FOO-BAR` for all purposes. The `X-` is the user's personal marker for "this was experimental before being formally added". It is **never** preserved in any file in this repo.
- The **message family** is the first tag (before the first hyphen). E.g., `TIMESYNC-STATUS` → family `TIMESYNC`; `FOO-BAR` → family `FOO`.

---

### Step 2 — Message family description

If the family already exists (e.g., `show.adoc` for family `SHOW`), read the existing file at `doc/modules/ROOT/pages/messages/<family>.adoc` and check whether the family-level description at the top is still broad enough to cover the new message type.

Ask the user: *"The `{FAMILY}` family already exists with the description: `{quote}`. Is this still accurate and broad enough to cover the new message type, or would you like to extend it?"*

If the family does NOT exist yet, ask: *"What is the description of the `{FAMILY}` message family?"*

---

### Step 3 — Example request (concrete JSON)

Ask: *"Please provide a concrete example request JSON for `{MSG}`."*

Example:
```json
{
  "type": "TIMESYNC-STATUS"
}
```

---

### Step 4 — Example response (concrete JSON)

Ask: *"Please provide a concrete example response JSON for `{MSG}`."*

Example:
```json
{
  "type": "TIMESYNC-STATUS",
  "status": {
    "state": "sync",
    "offset": 0.012,
    "source": "ntp:time.google.com",
    "jitter": 0.004
  }
}
```

---

### Step 5 — Example notification (optional)

Ask: *"Does this message also have a notification variant? If yes, provide an example notification JSON."*

If the user says no (request+response only), skip notification files entirely.

---

### Step 6 — Infer fields and ask about non-trivial details

From the examples, the agent should now infer:

- **Request fields** (they appear under `"type"` in the request JSON)
- **Response/notification fields** (they appear under `"type"` in the response JSON)
- **Custom types** (nested objects or complex arrays used in the request or response)

For each field, determine:
- Name
- Type (string, number, boolean, object, array, null, etc.)
- Required or optional
- Description

**Ask exactly one question per message** — never batch multiple questions, never confirm-and-ask in the same message. Wait for the user's answer before sending the next message. This includes not mixing a confirmation with a follow-up question.

**After each answer, confirm the question is fully resolved** before proceeding. If the user provides context or clarification (e.g., pasting Python code) instead of a direct answer, summarize your understanding and ask for confirmation: *"So `showDuration` is the same as `show_duration` in your code — a float in seconds? Correct?"* Do not assume and move on.

Pacing:
- *"Is field `{field}` required?"* (only if not obvious from examples/context)
- *"What is the type, description and unit of `{field}`?"*
- For nested objects not matching an existing type in `definitions.json`: *"This looks like a new custom type. What fields does it have?"*

**Before defining new custom types**, check existing types in `definitions.json` for reusable matches.

---

### Step 7 — Describe what will be created (MANDATORY)

Summarize the files that will be created/modified and **ask for confirmation before writing any changes**. Do not skip this step under any circumstances. Wait for the user's explicit "yes" or "proceed" before creating or editing any files.

---

## File manifest

### Schema files (`src/flockwave/spec/`)

| File | Action |
|------|--------|
| `definitions.json` | Add new custom type definitions (camelCase key with `title` and `description`) |
| `request_<MSG>.json` | Create JSON Schema with `type: "const": "<MSG>"` and fields |
| `response_<MSG>.json` | Create JSON Schema for response (if applicable) |
| `notification_<MSG>.json` | Create JSON Schema for notification (if applicable, and if different from response) |
| `request_body.json` | Add `$ref` — alphabetically |
| `response_body.json` | Add `$ref` — alphabetically |
| `notification_body.json` | Add `$ref` (if notification exists) — alphabetically |

### Doc files (`doc/modules/ROOT/`)

| File | Action |
|------|--------|
| `pages/messages/<family>.adoc` | Create new doc page |
| `pages/types.adoc` | Add custom type documentation (alphabetically, after the preamble) |
| `nav.adoc` | Add nav entry (alphabetically in the appropriate section) |
| `examples/request_<MSG>.json` | Example from step 3 |
| `examples/response_<MSG>.json` | Example from step 4 (if applicable) |
| `examples/notification_<MSG>.json` | Example from step 5 (if applicable) |

### TypeScript

| File | Action |
|------|--------|
| `types/index.d.ts` | **Auto-generated** — run `npm run build` after schema changes. Do not edit manually. |

## JSON Schema conventions

- Request: `{ "type": "object", "properties": { "type": { "const": "<MSG>" }, ... }, "required": ["type", ...], "additionalProperties": false }`
- Simple request with no fields → just `"type": { "const": "<MSG>" }` in properties, `"required": ["type"]`
- Response/notification: same pattern as request, with response fields
- Custom types in `definitions.json` use camelCase keys, have `title` and `description`
- All schemas are JSON Schema draft-07

## Doc conventions

- In field tables, if a field is optional (not required), do **not** append "or null" to the type — just write the expected type, e.g., `float` instead of `float or null`. Nullability is implied by the field being optional.
- Use `float` or `integer`, not `number`, to be more specific when applicable.

```adoc
= `<FAMILY>` — <Family description>

<General description>

== `<MSG>` — <Message description>

<Description of request/response semantics>

*Request fields*
[width="100%",cols="15%,10%,25%,50%",options="header",]
|===
|Name |Required? |Type |Description
|=== (or "This request has no fields.")

*Response and notification fields*
(same table, or omit)

*Example request*
[source,json]
----
include::example$request_<MSG>.json[]
----

*Example response*
[source,json]
----
include::example$response_<MSG>.json[]
----

*Example notification*
[source,json]
----
include::example$notification_<MSG>.json[]
----
```

For custom types in `types.adoc`:
```adoc
[#anchor-id]
== `TypeName`

<Description>

*Fields*
[width="100%",cols="15%,10%,25%,50%",options="header",]
|===
|Name |Required? |Type |Description
|===

*Example*
[source,json]
----
{ ... }
----
```

## TypeScript type naming

- Hyphens removed: `TIMESYNC-STATUS` → `TIMESYNCSTATUS`
- Prefix: `Notification_`, `Request_`, `Response_`
- Custom types: PascalCase (`TimeSyncSnapshot`)
- Union lists are alphabetical

## Ordering rules

- `request_body.json`, `response_body.json`, `notification_body.json`: alphabetical by filename (e.g., `..._SYS-VER.json#`, `..._TIMESYNC-STATUS.json#`, `..._UAV-CALIB.json#`)
- `nav.adoc`: alphabetical within each section
- `types.adoc`: alphabetical by type name (after preamble)

## Testing

```bash
uv run pytest --cov=src --cov-report=html -vv -s -x
```

Always run `npm run build` **last**, after all fixes and schema changes are finalized and tests pass. Do not run it before the final iteration — if you have to fix a bug and re-run tests, re-run `npm run build` again after the fix.

## Reference

Commit `465787f` — the TIMESYNC-STATUS addition.
