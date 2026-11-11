# Schema Commons

**A common vocabulary for APIs, distilled from the APIs that already exist.**

Schema.org gave the web a shared vocabulary by writing one. This does the opposite. The
API market has already converged on most of its vocabulary -- 79% of CRM providers that
expose a contact call its email `email`, 72% say `first_name` -- it just never wrote it
down, and the remaining disagreements (`add_time` vs `created_at`, `/persons` vs
`/contacts`, `org_id` vs `company_id`) are the tax every integration pays.

Schema Commons measures that convergence across the providers in the
[APIs.io](https://apis.io) catalog and publishes it, one bounded context at a time, as:

| Artifact | What it is |
| --- | --- |
| `openapi.yml` | OpenAPI 3.1 of the operations the market shares. No one serves it. |
| `schema/<concept>.json` | JSON Schema 2020-12, every property carrying the share of providers that declare it |
| `profile.yml` | Every concept, operation and property with its measured adoption and tier |
| `crosswalk/<provider>.yml` | Per provider: common name -> the name that provider uses, with the spec it came from |
| `adopters.yml` | Who exposes which concept, linked back to their APIs.io page |
| `arazzo/` *(next)* | The workflows the market shares, written against the common operations |

This repository is the hub: the tooling, the naming ruleset every context is written to,
and the registry of contexts. Each context is its own repository.

## Principles

1. **Distil, never invent.** A property is in the common schema because providers declare
   it, and the schema says how many. Nothing is added because it ought to exist.
2. **Only what providers published.** The census reads harvested OpenAPI only
   (`openapi/_original/`, `method: harvested` in the provider's `provenance.yml`). Contracts
   API Evangelist generated or derived never count toward a standard.
3. **Count providers, not files.** A company publishing forty specs weighs the same as one
   publishing one.
4. **Tiers are measured.** `core` is declared by at least half of the providers with a
   readable schema for the concept; `extended` by at least a fifth (and at least three);
   everything else is the long tail, kept in `profile.yml` and kept out of the schema.
5. **The judgement is in one reviewable file.** Which spellings mean the same field
   (`firstname` = `first_name`, `org_id` = `company_id`) is a human call. It lives in each
   context's `concepts.yml` and nowhere else.
6. **Map, don't rename.** No provider is asked to break their clients. The crosswalk is the
   product: it is how an agent or integrator speaks one vocabulary to many APIs.

## The naming ruleset

[ruleset/schema-commons-naming.yaml](ruleset/schema-commons-naming.yaml) -- OpenLint /
Spectral compatible, built-in functions only. Every common artifact must lint clean
against it, and any provider can run it against their own OpenAPI. Each rule cites what the
market measurably does, and where the market is split it says so and drops to `info`:

Counts are generated into [evidence/naming.yml](evidence/naming.yml) by
`scripts/naming-evidence.py` across every built context, which also renders the ruleset
and this table from them:

<!-- commons:naming -->
Measured across Customer Relationship Management, Help Desk and Ticketing, Commerce: 620 providers.

| Rule | Measured (providers) | Severity |
| --- | --- | --- |
| path segments kebab-case | lowercase 599; multi-word kebab 330 / snake 203 / camel 142 | warn |
| timestamps end in `_at` | `_at` 149 / bare `created` 75 / `_time`, `_date`, `on` 49 | warn |
| collections are plural | plural 376 / singular 189 | info |
| properties snake_case | multi-word snake 200 / camel 180 | info |
| references `<resource>_id` | `_id` 165 / `...Id` 162 | info |
| path params snake_case | `{id}` 366; multi-word camel 282 / snake 235 | info |
| query params snake_case | snake 286 / camel 265 | info |
| paging is `limit` + `cursor` | limit 258, page 213, offset 131, cursor 80 | info |
<!-- /commons:naming -->

The ruleset is also proposed to OpenLint: [openlint/rules#2](https://github.com/openlint/rules/pull/2).

## Bounded contexts

[contexts.yml](contexts.yml) is the registry and the order of work.

| Context | Repo | Status |
| --- | --- | --- |
| Customer Relationship Management | [api-commons/crm](https://github.com/api-commons/crm) | published -- 177 providers, 112 crosswalks |
| Help Desk and Ticketing | [api-commons/ticketing](https://github.com/api-commons/ticketing) | published -- 77 providers, 48 crosswalks |
| Commerce | [api-commons/commerce](https://github.com/api-commons/commerce) | built -- 401 providers, 256 crosswalks |
| Payments, Billing, Messaging, Scheduling, People and HR, Files, Identity | -- | planned |

## Running a context

```bash
scripts/run.sh ../crm      # cohort -> census -> build -> lint (must be clean)
```

`cohort.py` picks providers by APIs.io tag with harvested OpenAPI; `census.py` finds each
concept by the path segment the provider uses and reads the resource schema behind it;
`build.py` writes every artifact above and the measured table in the context README;
`apisjson.py` writes its APIs.json index.

## The method, as it stands

Each context is the same five steps. They are written down so the method can be tightened
in one place as it matures.

1. **Cohort.** Pick APIs.io tags that mean this context and nothing else. A tag that mixes
   meanings (help desk "Ticketing" also covers concert tickets) is left out, and the README
   says so.
2. **Concepts.** Name each concept for its role in the context, list the path segments
   providers use for it, and -- where a segment is generic (`messages`, `notes`) -- require
   it to sit `under:` a parent concept's path.
3. **Run and read the long tail.** `profile.yml` lists every spelling; collapse the ones that
   mean the same field in `aliases`. That review is the work.
4. **Review every ambiguous match.** Every provider counted only through an ambiguous segment
   is looked at by hand. Wrong ones go under `exclude:` with a one-line reason; the same
   company listed twice goes under `duplicates:` and is merged, not dropped.
5. **Decide in public.** Every naming call that is a choice rather than a count is written in
   the context README's Decisions section, with the numbers that informed it. The default:
   follow the measured majority unless the majority word is ambiguous across contexts.

Then re-run `naming-evidence.py` and bring the ruleset's counts up to date.

## Versioning

**Now: draft, and allowed to change anything.** Nobody depends on these artifacts yet, so
the method, concept names, paths and properties are refined freely as each new context
teaches us something (commerce renamed line items to `items` and fulfilment to
`shipments` on the evidence; help desk renamed comments to `messages`). Every artifact
says so: `info.version` and `x-commons.version` are `0.1.0-draft.<date>`, and
`x-commons.status` is `draft`.

**Locking a context** happens when all of these hold, and is a decision recorded in its
README, not an automatic step:

1. The method has stopped changing: two consecutive rebuilds with no edit to the scripts.
2. Every ambiguous match has been reviewed, and the Decisions section is complete.
3. The naming ruleset is settled (accepted into OpenLint, or explicitly kept here).
4. APIs.io renders it, so the crosswalks have been looked at by more eyes than ours.

**After a context locks**, it follows semantic versioning, released as git tags on the
context repository, and the shape is separated from the measurements:

| Change | Version |
| --- | --- |
| Rename or remove a concept, path or property; change a type | major |
| Add a concept, operation or property; promote extended -> core | minor |
| Fix a description, an alias, an exclusion that moves no tier | patch |
| Re-measure: shares, counts, adopters, crosswalks | none -- data, dated by `generated` |

The common OpenAPI and JSON Schema are the contract and are versioned; `profile.yml`,
`adopters.yml` and `crosswalk/` are measurements and refresh on every build. Released schema
`$id`s move to a versioned path (`schema/v1/<concept>.json`) at 1.0.0 so a consumer can pin
one. A demotion -- a property falling below its tier as the market moves -- is reported
in the release notes and only applied at the next major.

## Linking both ways

- **Commons -> APIs.io.** Every `adopters.yml` entry and every crosswalk links the provider's
  APIs.io page, and every crosswalk cites the harvested spec and the operations it read.
- **APIs.io -> Commons** *(next)*. Provider, tag, capability and area pages render the
  common concepts a provider maps to, read from each context's `adopters.yml` -- the same
  way they read every other generated rollup. Nothing is written into provider repos.

## License

Artifacts CC BY-NC-SA 4.0 ([LICENSE](LICENSE)); code Apache 2.0 ([LICENSE-CODE](LICENSE-CODE)).
