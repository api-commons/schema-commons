# Schema Commons: what was built, and what it taught us

*2026-11-10. Covers the first 57 bounded contexts, all distilled in one working session.*

## What exists now

The goal was a common vocabulary for APIs: not a new Schema.org, but the one the market
already shares, measured from the OpenAPI providers publish about themselves. There are now
57 bounded contexts, each its own repository under `api-commons`, plus this hub.

| | |
| --- | ---: |
| Bounded contexts | 57 |
| Concepts published | 293 |
| Properties that reached core (in half or more of the providers exposing a concept) | 1,056 |
| Provider crosswalks (common name → that provider's own name, with the spec it came from) | 4,071 |
| Distinct providers measured | 5,552 |
| Wrong matches reviewed by hand and excluded, each with a reason | 255 |
| Duplicate catalog listings merged | 153 |
| Providers folded into a shared standard (Open Banking UK, CDR, FHIR) | 160 |
| Concepts measured and dropped as too thin to call common | 31 |

Each context has:
- a common OpenAPI 3.1;
- JSON Schema for every concept, where each property records its tier, its share and the spellings seen;
- a profile of every concept, operation and property;
- crosswalks and an adopters list;
- a README that records its decisions.

All 57 lint clean against the naming ruleset. The ruleset itself is measured, generated
and proposed to OpenLint ([openlint/rules#2](https://github.com/openlint/rules/pull/2)).

On apis.io, the `common-schema` branch maps 2,933 providers to the concepts their own
specs implement, and links 376 tags to the contexts built from them. It is waiting for the
weekend build.

## The method, as it settled

Each context follows five steps (written down in the hub README):

1. Pick a cohort by tag.
2. Name the concepts and the path segments that identify them.
3. Run the census.
4. Review every ambiguous match by hand.
5. Record every call that is a choice rather than a count.

The method changed during the work. Each change came from a context that the method at the
time got wrong:

| Mechanism | What it solved | Found in |
| --- | --- | --- |
| `under:` | `/messages` counts as a ticket reply only beneath a ticket | ticketing |
| `exclude:` with a reason | `/accounts` that were logins, ledgers and Instagram channels | CRM |
| `duplicates:` (merged, not dropped) | Keap and Infusionsoft; three Microsoft Dynamics listings | CRM |
| `shared_specs:` | 25 UK banks republishing one Open Banking spec are one voice | payments |
| Segment qualifiers `@` / `!` | `/customers/{id}/cards` is a saved card; a bare `/cards` is an issued one | card issuing |
| `requires:` | `/users` is a cardholder only at a provider that issues cards | card issuing |
| `requires_any:` | an event is ticketed if the provider sells tickets, registers attendees *or* lists venues | events |
| Named standards as a voice (`au-cdr-banking`, `hl7-fhir`) | a standard counts once and is named for itself | banking, healthcare |
| `duplicates.py` | finds byte-identical specs, so a person can decide duplicate or standard | payments |
| Generated READMEs, tables and ruleset | numbers in prose went stale three times before they were generated | throughout |

## What we learned

### 1. Where a standard or a dominant vendor set the shape, the market agrees almost completely

Agreement is highest where someone defined the shape once and everyone else kept it:

| Shape | Source | What is shared |
| --- | --- | --- |
| Pull request | GitHub | 12 core properties |
| Trading order and fill | FIX | side, symbol, quantity, price, type, time in force, stop price |
| Bar | none (no standards body) | full OHLCV across 43 providers |
| Calendar event | iCalendar | attendees, location, recurrence |
| Blog post | WordPress | its shape |
| Users and groups | SCIM | groups, roles and permissions |
| Analytics profile | Segment's `identify` | the profile model |
| Help article | none | id, title and body in 93–100% of providers |

### 2. Money, fulfilment and stock diverge everywhere

The same pattern showed up in commerce, billing, payments, banking and food ordering. An
order, invoice or payment agrees on `id`, `status` and its items. Then it splits:

- **Totals:** total, subtotal, tax, amount due and amount paid are each divided up differently.
- **Currency:** sits beside the amount at some providers and inside it at others.
- **Inventory:** has no core at all.

The aliases can fold the spellings. They can't fold the models.

### 3. Result-shaped APIs agree least

Most APIs are resources you create and fetch. A few kinds are operations that return a
computed result instead, and those agree least:

- **Search:** 106 providers expose a search endpoint, and none agree on the query, the hits or the total.
- **Others:** routing, analytics events, weather forecasts and logs.

Here the request and result shapes are each provider's own invention.

### 4. Standards distort naive counts, and need to count once

Counted per listing, a single standard can masquerade as the market's agreement:

- **Banking:** 50 Australian banks implement CDR, and about 30 UK providers implement Open Banking.
- **Healthcare:** 32 providers publish nothing but FHIR.
- **Weather:** four NWS listings return the Common Alerting Protocol.

Banking's "counterparty core" was CDR's field names counted fifty times.

`shared_specs` keeps every implementer as an adopter with its own crosswalk but measures
the vocabulary once. Doing this changed banking and healthcare from "the standard, repeated"
to "what the market actually shares".

### 5. Words collide across contexts, and the commons has to choose

The same path word means different things in different contexts:

| Word | Where it means what |
| --- | --- |
| `/accounts` | a bank account, a login, a ledger account, an ad account, a brokerage account |
| `/orders` | commerce, trading, food |
| `/campaigns` | email, ads |
| `/locations` | a store, a work site, a restaurant, a charging site |
| `/quotes` | insurance, market data |
| `/rates` | FX, tax, shipping, hotel |
| `/events` | a webhook feed, a calendar entry, a concert |
| `/collections` | CMS, Shopify, search indexes |
| `/products` | catalog, billing plan, bank account type |

**The rule that emerged:** follow the market's word when it means one thing across contexts.
When it collides, use the role name (`/cardholders`, `/trade-orders`, `/ledger-accounts`,
`/ad-campaigns`, `/store-locations`) and record the measured count that was overridden.

### 6. Singular path segments are often verbs

`/check`, `/register`, `/run`, `/live` and `/deploy` turned out to be actions as often as
resources. These are licensing checks, device registration, running a backup and health
probes. The plural forms are the resources.

### 7. Hand-overs between contexts go wrong in both directions, and that's the point

- **Commerce → payments:** commerce found `/checkout` to be a payment session and handed it over.
- **Payments → card issuing:** payments dropped `/cards` as issued cards.
- **Card issuing → payments:** card issuing then showed that `/customers/{id}/cards` are saved payment methods, so payments got them back (86 → 103 providers).

Each context sharpened the one before it.

### 8. The catalog is as much a finding as the market

Building contexts audited the catalog as a side effect:

- **Duplicates:** 153 duplicate listings merged (five Workday listings, six Cvent listings, three NHS listings).
- **Provenance:** gaps that hide whole platforms — Recurly, FedEx and USPS have specs with no recorded provenance.
- **Parse failures:** specs that fail to parse were silently dropping providers (Resend, OneSignal, Algolia) until the census learned to tolerate them and report what it couldn't read.
- **Thin domains:** lending (14 providers expose loans), contact center (Genesys alone publishes the full model), EV charging (4 providers) and loyalty are mostly private.

Both lists are in `evidence/`: `catalog-gaps.yml` and `unreadable-specs.yml`.

### 9. The snake_case question has no majority

Across 5,552 providers the split on multi-word names is:

- **Properties:** camelCase 51%.
- **References:** `...Id` 53%.

The commons uses snake_case as a reasoned decision (one spelling per acronym, lossless
crosswalks). It will be revisited if either side reaches 60%, and `naming-evidence.py`
warns when that happens. The split has held steady since context four.

### 10. Process lessons

- **`requires:` has a cost.** Gating an unambiguous concept on another threw away real providers, three separate times (accounting, payroll, market data). Use `requires:` only on ambiguous segments.
- **Prose that cites a number goes stale.** Every improvement to the census made earlier findings wrong. About twenty were corrected in the final pass. The fix is a findings checker that re-verifies every cited property and share against the profile on each build. It is the first tooling item below.
- **Templates must not encode direction.** The ruleset said "snake_case narrowly leads" after camelCase overtook it. The prose now gives the counts and lets them speak.
- **Claims about named providers must be checked against the crosswalks before they ship.** Uber Eats, Stripe Identity, Sumsub and Statuspage were all cut from findings for that reason.

## What's next

1. **Publish:** run `create-repos.sh` (51 repos plus the OpenLint and apis.io branches). Then the weekend build.
2. **Findings checker:** verify every property and share cited in `findings:` on each build, and fail on drift.
3. **Standards passes:** read OCPI (EV charging), RESO (real-estate listings), OTLP (logs and traces) and CAP (weather alerts) as reference shapes, as the models context does for the OpenAI interface.
4. **Catalog repair:** work `catalog-gaps.yml` and `unreadable-specs.yml` in the re-profiling session, then re-measure the contexts they touch.
5. **Arazzo:** write the cross-concept workflows (create a contact and a deal; quote, bind, claim) against the common operations.
6. **Locking:** apply the lock criteria in the README. The likeliest first candidates are the stable, well-agreed contexts: source control, trading, ticketing and identity.

## Second batch: 50 more contexts (2026-11-11)

The second 50 ran from webhooks to genomics, one at a time. 41 were built and 9 were measured
and recorded as `thin` (customer success, marketplace, gift cards, subscription commerce,
privacy, background checks, solar, parking and genomics). Their findings stay in the hub, but
they have no repository.

| | |
| --- | ---: |
| Contexts built or published | 98 |
| Contexts measured and recorded thin | 9 |
| Providers measured (naming evidence, across all 107) | 6,688 |
| Providers mapped to a concept on apis.io | 3,530 |
| Concepts published | 389 |
| Properties at core | 1,404 |
| Provider crosswalks | 5,295 |
| Concepts measured and dropped, each with a comment | 45 |
| Arazzo documents / workflows | 17 / 18 |
| Standards passes (OCPI, OTLP, CAP, RESO, DCAT-US) | 10 |

### Follow-ups done before the batch

- **Findings checker** (`check-findings.py`). It verifies every "agrees on", share, provider count and
  provider name in `findings:` against the measured profile and crosswalks, and `context.sh finish`
  refuses to commit on drift. Its first run found about twenty stale findings, including two wrong
  cores and eight provider names with no crosswalk in the context. All 107 contexts now read 0 drifted.
- **Standards passes.** OCPI, OTLP, CAP, RESO and DCAT-US were extracted as reference shapes, and each
  context's core is measured against them (the "Measured against the standard" table in each README).
- **Arazzo.** Reference workflows compose core and extended operations only. They are validated against
  the context's own common OpenAPI and linted with the Spectral Arazzo ruleset.

### What the second batch taught

1. **A config that does nothing must fail.** `duplicates:` takes `canon: [merged slugs]`. Three contexts
   (energy, agriculture, fitness) wrote `dup: canon`, which iterated as characters and merged nothing,
   with no error. In fitness this produced a ten-property sleep core that was really one aggregator
   listed under three catalog names. `build.py` now refuses the wrong form. The same rule applies to
   the earlier lessons: the silent path is the dangerous one.
2. **Standards dominate small cohorts.** Eleven Australian energy retailers publish the Consumer Data
   Right energy standard. Uncounted, its servicepoint vocabulary would have been the core of energy;
   counted as one voice, energy agrees only on a meter id and an interval with a unit. Expect this
   wherever a regulator publishes the spec.
3. **Feed formats agree; telemetry does not.** Shared mobility agrees almost completely because fleets
   follow the open bike-share feed format. Solar production, IoT readings and wearables each report
   time-series in their own shape, and agree on little beyond a timestamp or a score.
4. **Wearables agree on a judgement before a measurement.** Sleep and daily summaries share a 0-100
   score before they share any physiological field.
5. **Thin rises down the long tail.** None of the first 57 contexts was thin; 9 of the second 50 were.
   The vocabulary is common where many providers expose the same resource as REST. Where a domain moves
   data as files (genomics: VCF, BAM), browser SDKs (consent) or feeds, a market census is the wrong
   instrument, and a standards pass is the right one.
6. **Context names collide too.** `open-data` would have overwritten the existing API Commons CKAN
   standard, so it became `open-data-catalogs`. Concept names follow the same collision rule across
   contexts: `game_title`, `player_profile` and `game_match` in gaming, because sports holds game and player.
7. **The naming tie holds.** Multi-word property names are camelCase at 50% of providers across 6,688
   providers measured. snake_case stays a reasoned decision, and the 60% revisit trigger has not fired.

### Tooling backlog

- Body readers for XML and form-encoded schemas (CDN), table APIs (ServiceNow, CMDB) and OAI-PMH verbs.
- A GA4GH pass (Beacon, htsget, DRS) for genomics, a sportsbook context for odds and markets, and a
  re-measure of solar once the larger inverter and battery platforms' specs are in the catalog.
- Catalog repair (`evidence/catalog-gaps.yml`, `evidence/unreadable-specs.yml`) in the re-profiling
  session, then a re-measure of the contexts it touches.

### To publish

`create-repos.sh` creates the 41 new repositories, pushes every existing context and the hub, and
pushes the OpenLint branch (re-measured across 107 contexts) and the apis.io `common-schema` branch
(98 contexts, 3,530 providers, 601 tags). The apis.io change then waits for the weekend build.

## Appendix: every context

Generated by `scripts/report.py` from each context's files.

<!-- report:appendix -->

### Customer Relationship Management (`crm`)

177 providers measured, 112 crosswalks, [api-commons/crm](https://github.com/api-commons/crm).

- `contact` (80 providers): `email`, `id`, `last_name`, `first_name`, `phone`, `job_title`, `created_at`, `custom_fields`
- `company` (58 providers): `id`, `name`, `created_at`
- `deal` (53 providers): `id`, `name`, `created_at`, `updated_at`
- `lead` (31 providers): `id`, `status`, `created_at`, `source`
- `activity` (41 providers): `type`, `id`, `created_at`
- `task` (48 providers): `id`, `subject`, `due_at`, `created_at`
- `note` (41 providers): `id`, `created_at`, `content`, `updated_at`
- `pipeline` (25 providers): `id`, `name`

Decisions:

- **The concepts are `deal` and `company`, not `opportunity` and `account`.** The market says `opportunity` (38 providers) more than `deal` (20). `account` (39) edges `company` (31). Opportunity leans on enterprise suites (Dynamics, Siebel, PeopleSoft), and `account` also means a login, billing or ledger account, which makes it the worse common word. The crosswalk records every provider's own segment, so nothing is lost.
- **Matches that are not CRM records are excluded.** Every provider counted only through an ambiguous segment (accounts, people, opportunities) is reviewed by hand. The ones that are something else -- the API user's own account, social-channel accounts, a QuickBooks ledger, a recruiting pipeline's "opportunities" -- are listed with the reason under `exclude:` in [concepts.yml](concepts.yml). They stay in [census/](census), out of everything built from it.
- **One company counts once.** Where the catalog lists a company more than once (Keap and Infusionsoft, three Microsoft Dynamics listings), the listings are merged under `duplicates:` rather than dropped, so no evidence is lost.
- **Properties are snake_case** -- a decision made across all contexts; see [Schema Commons](https://github.com/api-commons/schema-commons#decisions-that-cross-contexts).

### Help Desk and Ticketing (`ticketing`)

77 providers measured, 48 crosswalks, [api-commons/ticketing](https://github.com/api-commons/ticketing).

- `ticket` (34 providers): `status`, `id`, `created_at`, `subject`, `assignee_id`, `priority`, `updated_at`, `requester_id`, `channel`
- `ticket_message` (18 providers): `id`, `body`, `attachments`, `author_id`, `created_at`, `ticket_id`
- `requester` (24 providers): `id`, `name`, `email`, `phone`, `created_at`
- `agent` (14 providers): `id`, `name`, `role`
- `group` (27 providers): `id`, `name`
- `organization` (14 providers): `id`, `name`, `created_at`

Decisions:

- **The "Ticketing" tag is not used.** In APIs.io it mixes support tickets with event and transit ticketing, whose `/tickets` are a seat or a fare. The help desk, customer service and ITSM tags define the cohort.
- **A support conversation is a ticket; a bot transcript is not.** Shared-inbox products (Intercom, Front, Gladly, Chatwoot, Kustomer, Hiver, Dixa) model the ticket as a conversation with a status and an assignee, and are counted as tickets. AI-assistant transcripts and conversation-analytics exports record a bot's session, not a request someone is working, and are excluded. Each exclusion and its reason is in [concepts.yml](concepts.yml).
- **Replies are `messages`.** Providers name them `messages` (8), `notes` (7), `comments` (4) and `replies` (2); the concept is `ticket_message` and the path `/tickets/{ticket_id}/messages`. Public replies and internal notes share one resource, told apart by `is_public`, as most providers do.
- **Replies only count under a ticket.** `comments`, `messages`, `notes` and `replies` are matched only beneath a ticket, case, incident, request or conversation path, so a forum's `/posts` or a CMS's `/notes` cannot pass for one.
- **`requester`, not `customer` or `contact`.** The person who raised the ticket is named for their role in this context; the crosswalk records each provider's own word (customers, contacts, end users, requesters).
- **SLA policies were measured and dropped.** Three providers expose them in their own OpenAPI. Revisit as the cohort grows.
- **One company counts once.** Lithium and Khoros are one specification under two listings, merged under `duplicates:`.

### Commerce (`commerce`)

401 providers measured, 254 crosswalks, [api-commons/commerce](https://github.com/api-commons/commerce).

- `product` (153 providers): `id`, `name`, `description`, `images`
- `product_variant` (26 providers): `id`, `name`, `price`, `product_id`, `barcode`, `inventory_quantity`
- `category` (79 providers): `id`, `name`
- `customer` (85 providers): `id`, `email`, `last_name`, `first_name`, `created_at`
- `cart` (42 providers): `id`, `line_items`
- `order` (181 providers): `id`, `status`, `line_items`
- `order_item` (29 providers): `quantity`, `id`, `product_id`
- `shipment` (24 providers): `id`, `status`, `tracking_number`
- `inventory` (46 providers): no core

Decisions:

- **"Marketplace" and "Retail" are not cohort tags.** The first also means API, talent and data marketplaces; the second takes in energy retail and retail media.
- **A checkout is a payment, not a cart.** In this cohort `/checkout` is almost always a hosted payment session (Square, Visa, Tabby, Tamara, Lemon Squeezy, Coinbase Commerce). It is left for the payments context; the cart is `carts` and `baskets`.
- **An offer is not a product.** `/offers` here is loyalty offers, FX quotes and promotions, so it is not a product segment. `/listings` (Etsy, Reverb, Back Market) is.
- **A collection is a category only on a commerce platform.** Shopify, Medusa and Shoplazza group products into collections and count; CMS, search-index and analytics collections (Webflow, Duda, Lucidworks, dotdigital, Talon.One) are excluded.
- **Line items are `/orders/{order_id}/items`, shipments `/orders/{order_id}/shipments`.** Providers nest them as `items` (24) far more than `line_items` (2), and say `shipments` (16) more than `fulfillments` (9). The order's property stays `line_items` -- that is the measured property name, which is a separate count from the path.
- **Orders that are not commerce orders are excluded.** Trading orders (Bloomberg EMSX, Gemini), buy-now-pay-later and in-store payment orders, fraud-scoring and tracking events. Each is listed with its reason under `exclude:` in [concepts.yml](concepts.yml).
- **GraphQL-only platforms are absent, not failing.** Saleor, and the GraphQL side of Shopify, publish no OpenAPI for these resources. The census reads OpenAPI only.

### Payments (`payments`)

692 providers measured, 436 crosswalks, [api-commons/payments](https://github.com/api-commons/payments).

- `payment` (289 providers): `id`, `status`, `amount`, `created_at`
- `checkout_session` (85 providers): `id`, `status`, `created_at`
- `refund` (214 providers): `id`, `amount`, `status`, `created_at`
- `payment_method` (103 providers): `id`, `type`
- `customer` (170 providers): `id`, `name`, `email`, `created_at`
- `payout` (122 providers): `id`, `status`, `amount`, `created_at`
- `dispute` (77 providers): `status`, `created_at`, `id`, `reason`

Decisions:

- **"Acquired" is not a cohort tag.** It marks acquired companies in the catalog, not card acquiring. The API, AI, LLM and MCP "gateway" tags are not payment gateways either.
- **A hosted checkout session lives here, not in commerce.** The commerce context found `/checkout` to be a payment session almost everywhere and handed it over as `checkout_session`, alongside payment links and hosted pages.
- **`/sessions` is reviewed provider by provider.** Eight are hosted payment sessions (Citi, FastSpring, Klarna, Komoju, Plug, Satispay, Versapay, Zuora); sixteen are login, 3-D Secure, KYC, school-term or event sessions and are excluded with the reason in [concepts.yml](concepts.yml).
- **A card is a payment method only when it is saved on a customer.** The first build dropped `/cards` entirely, because 104 providers matched only through it returned `cvv`, `card_number` and a status -- issued cards. Building card issuing showed that was half right: a card under a customer (`/customers/{id}/cards`: Stripe, Square, Omise, PAY.JP, Pin, Shift4) is a stored way to pay. The segment is now qualified -- `cards@customers|...` here, `cards!customers|...` in [card issuing](https://github.com/api-commons/card-issuing) -- and payment methods went from 86 providers to 103. `/tokens` is still not used.
- **`/transactions` is not a payment.** In this cohort it is as often a bank-ledger line or a card-programme feed, and the path alone cannot tell them apart.
- **A standard counts once.** Twenty-five UK banks republish the UK Open Banking specification byte-for-byte. Each is an adopter with its own crosswalk, but the vocabulary is measured once, under `shared_specs:`, because it was written once. (Their payment initiation resources, `/domestic-payments`, are a different shape from a card payment and do not match here -- a candidate for a payment-initiation concept.)
- **One company counts once.** Duplicate catalog listings found by `scripts/duplicates.py` (Finix, Billie, Mesh, Method and others) are merged under `duplicates:`.

### Card Issuing (`card-issuing`)

740 providers measured, 65 crosswalks, [api-commons/card-issuing](https://github.com/api-commons/card-issuing).

- `card` (65 providers): `status`, `id`, `last4`, `type`
- `cardholder` (28 providers): `email`, `last_name`, `id`, `first_name`, `phone`
- `authorization` (16 providers): `amount`, `id`, `merchant`
- `card_transaction` (47 providers): `amount`, `id`, `merchant`, `status`, `type`, `created_at`
- `spending_control` (8 providers): `id`
- `card_program` (13 providers): `created_at`, `id`, `name`

Decisions:

- **This context exists because payments handed it over.** Payments found `/cards` returning `cvv`, `card_number` and a status -- issued cards, not stored ways to pay.
- **The path decides whether a card is issued or saved.** A card under a customer (`/customers/{id}/cards`: Stripe, Square, Omise, PAY.JP, Pin, Shift4) is a payment method and counts in payments; a card anywhere else is an issued card and counts here. The rule is written as a segment qualifier (`cards!customers|...`) in [concepts.yml](concepts.yml), and the providers whose bare `/cards` is still a saved or one-off card are excluded by hand with the reason.
- **The Payments tag is in the cohort** -- it is where the issued cards were found. It cannot flood the context: every concept but `card` either has an issuing-only segment or `requires: [card]`.
- **A cardholder is `/cardholders`, though issuers say `users`.** Twenty-one providers name them `users` and six `employees`; three say `cardholders`. `/users` counts here only at a provider that also issues cards, and the common path keeps the role name so it cannot be mistaken for every other API's users -- the same call as `requester` in help desk.
- **Card transactions are `/transactions`.** Issuers keep them top-level (45 providers), and `requires: [card]` means a bank ledger without cards never counts.
- **A card programme is `/card-programs`, though eight providers say `products`.** `products` means something else in every other context.
- **Affirm's single-use card**, minted for one checkout, is a payment instrument, not an issuing programme, and is excluded. Bread Financial's `/virtual-card/issuance` is issuing and stays.

### Billing and Invoicing (`billing`)

837 providers measured, 270 crosswalks, [api-commons/billing](https://github.com/api-commons/billing).

- `invoice` (184 providers): `id`, `status`, `due_date`, `number`
- `invoice_line` (16 providers): `description`, `id`, `quantity`
- `subscription` (138 providers): `id`, `status`, `created_at`
- `plan` (59 providers): `id`, `name`, `description`, `created_at`, `is_active`, `amount`
- `price` (17 providers): `id`, `plan_id`, `currency`, `pricing_model`
- `credit_note` (29 providers): `id`, `total`, `status`, `description`, `currency`, `created_at`, `customer_id`, `updated_at`
- `coupon` (27 providers): `code`, `id`, `created_at`, `max_redemptions`
- `usage_record` (22 providers): `id`, `quantity`

Decisions:

- **Healthcare billing, utility metering, price data and invoice financing are out.** Medical Billing and Revenue Cycle Management are claims, Smart Metering is utility meters, Pricing is price-data feeds, Invoice Financing is lending.
- **Payments is in the cohort.** Processors bill too -- Stripe Billing, PayPal and Square invoicing -- and a processor's invoices and subscriptions are billing. Plans, prices, coupons and usage `require: [subscription]`, so a processor without subscriptions adds nothing to them.
- **A plan is `/plans`, though some providers say `/products`.** Plans lead (44 providers to 36). A billing product (Paddle, Polar, Creem, Recharge, Zuora) counts as a plan; a commerce catalog, bank account product or menu item does not, and is excluded by name.
- **`/rates` is not a price.** It was FX, tax or hourly rates at every provider reviewed.
- **A bare `/events` is not usage.** Reviewed, it was a webhook-notification feed almost everywhere (Chargebee, Paddle, GoCardless, Coinbase), and `/subscriptions/{id}/events` is a subscription's lifecycle. Events count only beneath a usage or metering path. This costs Lago, whose usage genuinely is `POST /events`; the path cannot tell it apart.
- **Invoice lines are `/invoices/{invoice_id}/lines`.** `lines` and `line-items` tie (5 each); `lines` is Stripe's and the shorter.
- **Known gaps, and why.** Three billing platforms are absent, each for a different reason the method is right to respect: Recurly's specs are in the catalog but their provenance was never recorded, so they cannot be confirmed as Recurly's own; Orb's contracts were authored by API Evangelist, which never counts; Maxio publishes none we hold. Recording Recurly's provenance would bring it in.

### Messaging (Email, SMS, Chat) (`messaging`)

365 providers measured, 198 crosswalks, [api-commons/messaging](https://github.com/api-commons/messaging).

- `message` (198 providers): `id`, `body`, `from`
- `template` (66 providers): `id`, `name`, `body`, `created_at`
- `conversation` (71 providers): `id`, `created_at`
- `phone_number` (33 providers): `number`, `id`, `capabilities`, `country`, `name`, `status`
- `sender` (19 providers): `id`, `email`, `name`
- `suppression` (22 providers): `address`, `reason`, `created_at`

Decisions:

- **Email marketing, verification, finder and security, and message brokers are out.** Campaigns and lists belong to a marketing context; verification and finder are data products; and a message on a queue is infrastructure, not communication.
- **One message concept across channels.** Email, SMS, MMS, chat-app and push messages share `body`, `id` and `from` in their core; the channel is a property (`channel`, 43%), not a separate resource. Sending by action path (`/mail/send`, `/email/batch`, `/messages/send`) counts as creating messages.
- **Phone numbers are `/phone-numbers`, though 21 providers say `/numbers`.** The `phone-numbers` family has 19, and `numbers` means something else in every other context -- the same call as `/cardholders` in card issuing.
- **A sender is `/senders`.** Twelve providers say `senders`; `identities` (four) is also an identity-and-access word.
- **Everything but the message `requires: [message]`.** A provider's `/templates` or `/threads` counts here only if it also sends messages.
- **AI-assistant chat turns are not messages.** A `/messages` that is `role` plus `content` in an LLM conversation is excluded (one provider in this cohort).

### Calendars and Scheduling (`scheduling`)

112 providers measured, 38 crosswalks, [api-commons/scheduling](https://github.com/api-commons/scheduling).

- `calendar` (13 providers): `id`, `name`
- `calendar_event` (9 providers): `description`, `attendees`, `id`, `location`, `end_at`, `start_at`, `calendar_id`, `name`, `organizer_id`, `recurrence`
- `appointment` (29 providers): `id`, `start_at`, `status`, `end_at`
- `availability` (13 providers): `end_at`, `start_at`
- `service` (15 providers): `id`, `name`, `description`, `duration`

Findings:

- Calendar events agree more than anything else here: description, attendees, location, start and end, and recurrence are all core -- the iCalendar shape every calendar API inherits.
- Availability agrees only on start and end: some providers return free/busy blocks, some bookable slots, some opening hours, and a time window is all they share.
- The cohort is thin for its size (112 tagged providers, 37 mapped). Most scheduling products publish no OpenAPI of their own.

Decisions:

- The Booking tag is not used: it is mostly travel booking, which has its own context.
- An appointment is `/appointments`, not `/bookings`. Appointments lead 16 providers to 14, and the word collides with nothing in other contexts.
- A calendar event is `/calendars/{calendar_id}/events`. A bare `/events` is a webhook feed or a ticketed event elsewhere, so here it counts only at a provider that also exposes calendars (`requires: [calendar]`).
- What can be booked is a `service` (`/services`), covering Calendly's event types and Acuity's appointment types. `services` leads (7) and is the plain word.
- Infrastructure `/services` (Nomad, Cronitor) are excluded by name.

### People and HR (`hris`)

171 providers measured, 61 crosswalks, [api-commons/hris](https://github.com/api-commons/hris).

- `employee` (61 providers): `id`, `work_email`, `last_name`, `first_name`, `status`
- `department` (21 providers): `id`, `name`
- `team` (7 providers): `id`, `name`
- `position` (14 providers): `id`, `name`
- `work_location` (27 providers): `id`, `name`, `status`
- `absence` (19 providers): `id`, `employee_id`, `end_at`, `status`, `type`, `start_at`
- `employment` (19 providers): `id`, `status`, `employment_type`, `effective_date`, `employee_id`, `job_title`

Findings:

- An employee is agreed: id, work email, first and last name and status are core across 55 providers with a readable schema -- the sharpest core of any people concept so far.
- Absences agree too: start, end, status, type and the employee are all core, so a time-off request maps cleanly between HR systems.
- Teams barely exist as a resource of their own (7 providers); most HR systems model the organisation through departments and managers instead.

Decisions:

- Employee Benefits is not a cohort tag: benefits administration is its own domain.
- `roles` is not a position and `groups` is not a team: reviewed, both were permission roles and SCIM, LMS or payment groups far more often than an org structure.
- `members` is not an employee segment (workspace members, analytics dimensions).
- Time off is `/absences`: absences lead (9) the spread of time-off spellings, and `/holidays` -- a public-holiday calendar -- is not a request and is not counted.
- Employment is `/employments`, though 14 providers say `jobs`: `jobs` is a job posting in the recruiting context. Role name over a colliding word, as with `/cardholders`.
- A work location is `/work-locations` for the same reason: `/locations` means a store or a restaurant in commerce and point of sale.
- Five Workday listings, two ADP, two HiBob and two Ethena listings are merged as duplicates.

### Payroll (`payroll`)

192 providers measured, 27 crosswalks, [api-commons/payroll](https://github.com/api-commons/payroll).

- `payroll` (16 providers): `id`
- `payslip` (18 providers): `id`, `gross_pay`, `net_pay`
- `pay_group` (4 providers): `id`, `name`

Findings:

- Payroll publishes little: 192 HR and payroll providers in the cohort, 27 mapped. Most payroll engines keep their API private or partner-gated.
- A payslip agrees on gross and net pay (both core), and carries earnings, deductions and taxes as lines -- the market does not model those as resources of their own.
- Payslips come from two kinds of provider: payroll engines, and income-verification networks (Argyle, Pinwheel) that read stubs on a worker's behalf. Both count.

Decisions:

- The HR tags are in the cohort: payroll products are tagged Human Resources far more often than Payroll.
- Earnings, deductions and taxes are not concepts: measured, 3, 5 and 2 providers expose them as resources. They are properties of the payslip.
- `benefits` is not a deduction: reviewed, it is benefit enrollment, a domain of its own.
- A bare `runs` is not a pay run (CI and workflow runs); `payroll-runs`, `payruns` and `payrolls` are.
- The names follow the market: `/payrolls` (11 providers, against 7 for any pay-run spelling), `/payslips` (13, against 4 for paystubs) and `/pay-groups` (3, against 1).
- A payslip needs no payroll: income-verification providers expose payslips without running payroll, so `requires` was dropped for it.
- Duplicates merged: Argyle (two listings), KUFU into SmartHR (the same company, renamed), Remote, Thatch, Ethena, ADP and five Workday listings.

### Recruiting (`recruiting`)

67 providers measured, 32 crosswalks, [api-commons/recruiting](https://github.com/api-commons/recruiting).

- `job` (32 providers): `id`, `name`, `status`, `created_at`, `description`, `location`, `employment_type`
- `candidate` (23 providers): `id`, `phone`, `email`, `first_name`, `last_name`, `created_at`, `resume_url`
- `application` (15 providers): `id`, `candidate_id`, `job_id`, `metadata`, `updated_at`, `created_at`, `source`, `status`
- `stage` (9 providers): `id`, `name`, `updated_at`
- `interview` (8 providers): `id`, `created_at`, `start_at`, `status`, `application_id`, `end_at`, `location`

Findings:

- Candidates agree well: name, email, phone, resume and created_at are all core, so a candidate moves between applicant-tracking systems with little loss.
- Applications agree on the join itself -- candidate, job, status, source -- which is what every ATS integration actually needs.
- Interviews agree on start, end, location and the application they belong to; Greenhouse's scheduled_interviews set the shape.

Decisions:

- A job is a posting or requisition: `/jobs` (and postings, openings, requisitions, vacancies, positions in this cohort). In the HR context the same word is an employee's job record, which is why HR uses `/employments`.
- `/positions` that are an employee's position history (Harri, HR Partner) are HR, not recruiting, and excluded by name.
- Offers were measured and dropped: three providers expose them as a resource.
- Everything but the job `requires: [job]`, so a provider's `/people` or `/profiles` counts as candidates only if it also posts jobs.

### Files and Documents (`files`)

133 providers measured, 51 crosswalks, [api-commons/files](https://github.com/api-commons/files).

- `file` (51 providers): `id`, `name`, `mime_type`, `created_at`, `size`
- `folder` (13 providers): `name`, `id`, `parent_id`, `created_at`
- `bucket` (4 providers): `name`
- `file_version` (3 providers): `id`, `name`
- `permission` (13 providers): `id`, `name`

Findings:

- Once signature documents, database documents and editor documents are set aside, a file agrees on id, name, MIME type, size and created_at -- the shape of a file everywhere. A download URL stays extended: some providers return bytes, some a link.
- Folders agree on their parent (parent_id is core), so a folder tree maps across providers even where files do not.
- Buckets and file versions are thin (4 providers each): most object stores speak the S3 protocol and publish no OpenAPI of their own for it.

Decisions:

- The bare Storage tag is not used (energy storage and databases share it); Cloud and Object Storage, Document Management, Documents, File Storage and File Sharing are.
- A document awaiting signature belongs to e-signature: BoldSign, Documenso, DocuSeal, GetAccept, PandaDoc and Nitro are excluded here by name and counted there.
- Database documents (Firestore) and editor documents (Google Docs) are not files.
- OneDrive-style `/drives/{id}/items` and `/folders/{id}/items` count as files; a bare `/items` does not.
- A shared link, a collaboration and a share are one concept, `permission`.

### Identity and Users (`identity`)

443 providers measured, 185 crosswalks, [api-commons/identity](https://github.com/api-commons/identity).

- `user` (185 providers): `id`, `email`, `name`
- `group` (84 providers): `id`, `name`, `description`
- `organization` (60 providers): `name`, `id`, `created_at`
- `role` (63 providers): `id`, `name`, `description`
- `permission` (46 providers): `id`, `name`, `description`
- `invite` (34 providers): `email`, `id`, `role`
- `api_key` (25 providers): `id`, `created_at`, `key`, `name`

Findings:

- A user agrees on id, email and name -- and only just on name: SCIM nests it as an object, others split first and last name, others carry a display name, so the most common resource in the catalog agrees on less than a CRM contact does.
- Roles and groups agree on name, id and description -- and a third of roles reference their permissions: RBAC is the same shape everywhere.
- An invite agrees on email, id and the role it grants: the minimum to bring someone in.
- API keys agree on id, name, key and created_at once only unambiguous paths count.

Decisions:

- `/accounts` is not a user: reviewed, it was brokerage, bank and ad-platform accounts.
- API keys count only as api_keys, personal_access_tokens, or keys and tokens beneath a user, account or project. Bare keys, tokens and credentials were verifiable credentials, door-access credentials and signing keys as often as API keys.
- OAuth scopes and entitlements count as permissions: each is a grantable unit of access.
- An organization covers tenants and workspaces -- the boundary users are members of -- but residential tenants (ButterflyMX) are excluded.
- Invites are `/invites`: invite and invites lead (22 providers) invitations (15).
- Duplicates merged: ConductorOne (C1), Cerner into Oracle Health, three Cvent listings, EVE Online into CCP Games, Dynamic, Kinde.

### E-Signature (`e-signature`)

72 providers measured, 35 crosswalks, [api-commons/e-signature](https://github.com/api-commons/e-signature).

- `envelope` (35 providers): `id`, `name`, `status`, `created_at`, `metadata`, `signers`
- `recipient` (16 providers): `id`, `email`, `status`, `name`, `role`
- `template` (25 providers): `id`, `name`, `created_at`, `updated_at`
- `signature_field` (14 providers): `type`, `id`, `name`, `required`, `recipient_id`

Findings:

- A recipient agrees on email, name, role and status -- the routing information every signing flow needs -- across DocuSign, PandaDoc, Documenso and the rest.
- Signature fields agree on type, name and whether they are required, so a field layout maps between products even where the documents do not.
- The envelope agrees on id, name, status, created_at and its signers; what else it carries (documents, expiry) is modelled differently by every provider.

Decisions:

- The cohort is the e-signature and contract-management tags only. With Document Management in it, `/documents` brought in database and editor documents.
- The signing transaction is an `envelope` (`/envelopes`), though most products call it a document (28 providers, against 10 for envelope): `/documents` is the files context's, and envelope means only one thing.
- A signer is a `recipient` at `/envelopes/{envelope_id}/recipients`: recipients lead (10 to 5), and the word covers carbon-copies and approvers as well as signers.
- `participants` and `parties` are recipients only beneath an envelope, document, contract or signature request; a call's participants and a chat room's are not.
- Fields are `signature_field`, DocuSign's tabs and PDF form fields included.

### Accounting (`accounting`)

139 providers measured, 67 crosswalks, [api-commons/accounting](https://github.com/api-commons/accounting).

- `ledger_account` (14 providers): `type`, `name`, `number`, `id`, `currency`, `description`, `status`, `balance`
- `journal_entry` (21 providers): `date`, `description`, `id`
- `vendor` (43 providers): `id`, `name`, `status`
- `bill` (19 providers): `due_date`, `id`, `description`, `lines`, `status`, `vendor_id`, `total`, `currency`
- `expense` (14 providers): `id`
- `tax_rate` (21 providers): `code`, `rate`, `id`, `name`

Findings:

- A bill agrees almost completely: vendor, due date, lines, total, currency and status are all core. Accounts payable is the most standardised corner of accounting.
- A ledger account agrees on its number, name, type, currency and balance -- the chart of accounts is the same shape in every system that exposes it.
- A journal entry agrees only on id, date and description: the lines that carry the debits and credits are modelled differently everywhere.
- Expenses agree on nothing but an id (14 providers): expense tools, card platforms and ledgers each describe a spend differently.
- The largest accounting platforms are thin or absent: Intuit's harvested spec covers only invoices, customers and payments, and NetSuite, Wave and MYOB publish none the catalog holds.

Decisions:

- Invoices belong to billing and payments to payments; accounting does not duplicate them. Its concepts are the ledger side.
- A ledger account is `/ledger-accounts`, though most providers say `/accounts`: that word is a bank account in banking and a login in identity. Bare `/accounts` counts only at a provider that also exposes journal entries.
- Vendors, bills, expenses and tax rates need no journal: inside an accounting cohort their names are unambiguous, and requiring journals cost most of the providers.
- `receipts` is not an expense: reviewed, it was goods received, cash receipts and receipt images as often as spend.
- Journal entries are `/journal-entries` (13 providers across spellings, against 9 for `journals`).
- Duplicates merged: Microsoft Dynamics and Navision into Dynamics 365, Codat, Ottimate.

### Banking (`banking`)

315 providers measured, 211 crosswalks, [api-commons/banking](https://github.com/api-commons/banking).

- `bank_account` (136 providers): `name`, `type`, `currency`, `status`, `id`, `account_number`, `balance`
- `balance` (74 providers): no core
- `transaction` (118 providers): `id`, `amount`, `direction`, `description`, `status`, `posted_at`, `account_id`
- `beneficiary` (43 providers): `id`, `name`
- `transfer` (73 providers): `amount`, `status`, `created_at`, `description`, `id`
- `statement` (49 providers): `id`

Findings:

- Open-banking standards dominate banking APIs, and measured naively they ARE the vocabulary: fifty Australian banks implement the Consumer Data Right and some thirty UK providers the Open Banking UK standard. Counted per bank, a beneficiary's 'core' was CDR's own field names. Counted once per standard, the market's own agreement shows.
- A bank account agrees on name, type, status, currency, id, account number and balance -- once the open-banking standards count once, a proprietary bank account and a standardised one share the shape.
- A transaction agrees on id, amount, status, direction and description -- direction (credit or debit) is core, which is not true of a payment in the payments context.
- Balances agree on nothing outright: account, available and currency all sit just under half. Open-banking standards split a balance into typed entries; proprietary APIs carry available and current side by side.

Decisions:

- A standard counts once. The 50 CDR banks are one voice (`au-cdr-banking`) and the UK Open Banking implementers another (`open-banking-uk`), identified by the standards' own paths. Every bank keeps its own crosswalk, marked with the standard it implements. Revolut, Barclays and Zopa also publish proprietary APIs and are counted on their own.
- Money moving between accounts is a `transfer` at `/transfers`, though banks say `payments` (64 providers, against 29): `/payments` is the payments context's, and an open-banking payment initiation is an account-to-account transfer.
- A counterparty is a `beneficiary` at `/beneficiaries`: beneficiaries lead (19) and the word collides with nothing.
- A bank account is `/accounts`, the market's word (123 providers), because inside banking it means only one thing. Accounting uses `/ledger-accounts` to stay clear of it.

### Lending (`lending`)

134 providers measured, 14 crosswalks, [api-commons/lending](https://github.com/api-commons/lending).

- `loan` (14 providers): `id`, `amount`
- `borrower` (4 providers): no core

Findings:

- Lending publishes less than any context so far: 134 lending, mortgage, credit and BNPL providers in the cohort, 14 exposing loans. Origination, decisioning and servicing APIs are overwhelmingly private or partner-gated.
- What is public agrees only on a loan's id and amount. Balance, rate, term and maturity are each modelled by too few providers to call shared.

Decisions:

- Applications, offers and repayments are not published as concepts: measured, 3, 1 and 1 providers expose them with a readable schema. They are recorded here so the next re-measure can add them when the market publishes.
- A borrower is `borrowers` or `applicants` only. `customers` and `members` brought in payment customers and workspace members from the wider fintech cohort.
- Credit lines, BNPL installment plans and mortgages are loans: each is a principal lent against a schedule.
- Duplicates merged: Figure, Oper, Orbii.

### Insurance (`insurance`)

143 providers measured, 47 crosswalks, [api-commons/insurance](https://github.com/api-commons/insurance).

- `policy` (30 providers): `effective_date`, `status`, `expiration_date`, `number`, `id`
- `quote` (34 providers): `id`, `premium`
- `claim` (16 providers): `status`, `policy_id`, `id`, `loss_date`, `description`, `number`
- `insurance_product` (5 providers): no core

Findings:

- A claim agrees on more than any other insurance resource: number, status, the policy, the loss date and a description are all core.
- A policy agrees on its number, status and effective and expiration dates; what it covers is modelled too differently to share.
- A quote agrees only on id and premium, with status just under (48%): embedded-insurance APIs quote by product and carriers quote by risk, and the request shapes diverge.
- Coverages live on the policy and the quote, not as resources (2 providers).

Decisions:

- Health insurance is the healthcare context's: payers, benefits plans and medical claims are a different domain from property, casualty and life.
- Policyholders are not published as a concept: counting only `insureds` and `policyholders` (`members` and `customers` were workspace members and agency CRM records), 2 providers expose them.
- `plans` is not an insurance product here: reviewed, it was health, retirement and benefits plans.
- A claim needs no policy in the same API: claims and FNOL platforms expose claims alone.
- Duplicates merged: Audatex into Solera, Oper, Orbii, Thatch.

### Property Management (`property-management`)

143 providers measured, 62 crosswalks, [api-commons/property-management](https://github.com/api-commons/property-management).

- `property` (53 providers): `address`, `id`
- `unit` (9 providers): `id`, `number`, `property_id`
- `lease` (9 providers): `id`, `start_date`, `end_date`, `property_id`, `status`, `rent`, `tenant_ids`
- `tenant` (8 providers): `id`, `phone`
- `work_order` (5 providers): `id`, `status`, `description`, `property_id`
- `listing` (19 providers): `id`

Findings:

- A lease agrees completely: start and end dates, status, rent, the property and the tenants are all core across the providers that expose one.
- A property agrees only on id and address. Type, size, year built and unit count are each modelled by too few providers to share -- residential management, commercial portfolios and MLS listings describe a building differently.
- Listings agree on nothing but an id, although the industry has a listing standard (RESO): the listing APIs published here name their fields differently enough that the aliases cannot reconcile them. Worth a RESO-specific pass, as Open Banking and CDR got.
- Units, tenants and work orders are thin (5-9 providers): most property-management systems keep their APIs to partners.
- Measured against the RESO Data Dictionary 2.0, the standard covers the listing and property core and defines about 600 more fields that no provider in the cohort publishes as OpenAPI -- the clearest measure in the commons of how much richer a standard is than what reaches an API description.

Decisions:

- Real Estate is in the cohort, so listings are a concept here alongside the management resources.
- A tenant counts only at a provider that also exposes leases (`requires: [lease]`): tenants are an organization in the identity context.
- Buildings and communities are properties; apartments and spaces beneath a building are units; tenancies and rental agreements are leases.
- Work orders cover maintenance and service requests: one resource, named for the job.
- Duplicates merged: Alto into Zoopla, Realtor.ca into CREA.

### Travel and Lodging (`travel`)

184 providers measured, 67 crosswalks, [api-commons/travel](https://github.com/api-commons/travel).

- `booking` (60 providers): `id`, `status`
- `hotel` (24 providers): `name`, `address`, `id`, `currency`
- `room` (8 providers): `id`, `name`, `hotel_id`
- `rate_plan` (9 providers): `hotel_id`, `currency`
- `guest` (6 providers): `id`
- `flight` (14 providers): `status`, `flight_number`

Findings:

- A booking agrees only on id and status. Check-in, check-out and the guests sit at 37%: hotel stays, flights, tours and car rentals are all bookings with different shapes.
- A hotel agrees on name, address and id; amenities and star rating are modelled by too few to share.
- Flights agree on a flight number and a status, and little else: NDC-style offers, schedules and flight status are three different resources published under one word.
- Guests and rooms are thin (5-7 providers): property-management systems and channel managers keep their APIs to partners.

Decisions:

- A booking is `/bookings`: bookings lead reservations 42 to 19, and the scheduling context uses `/appointments`, so the word is free. Appointment bookings (AgendaPro, Cliniko) are excluded here and counted there.
- A hotel is `/hotels`; Expedia's and Booking.com's bare `/properties` counts as a hotel at a provider that also takes bookings, because property management uses the same word for buildings.
- A room is `/rooms` (rooms lead room types 7 to 2); a rate plan stays `/rate-plans`, though `rates` leads, because a bare rate is FX or tax elsewhere.
- Passengers and travellers are guests.
- Car-rental rates and air-cargo bookings are out of scope and excluded by name.
- Duplicates merged: CrunchTime, Cvent, DOT.

### Shipping (`shipping`)

258 providers measured, 99 crosswalks, [api-commons/shipping](https://github.com/api-commons/shipping).

- `shipment` (78 providers): `id`, `status`
- `rate` (9 providers): `service`
- `label` (20 providers): no core
- `tracking` (40 providers): `status`, `tracking_number`
- `pickup` (8 providers): `id`, `pickup_date`, `status`, `address`
- `carrier` (16 providers): `name`, `id`

Findings:

- A shipment agrees only on id and status. From and to addresses sit at 44%: carriers, multi-carrier platforms and last-mile delivery networks each nest the addresses differently.
- Tracking agrees on the tracking number and a status; the event history is modelled too differently to share.
- Labels agree on nothing outright: a label is a file at some providers, a purchase record at others, and part of the shipment at the rest.
- The carriers themselves are absent: FedEx and USPS have harvested specs without recorded provenance, DHL publishes none the catalog holds, and UPS's versioned action paths do not match. The context is built from multi-carrier platforms and delivery networks.

Decisions:

- Shipping owns the shipment. Commerce's `/orders/{order_id}/shipments` is the order's view of it.
- A last-mile delivery (DoorDash Drive, Grab Express, Metrobi) is a shipment: a parcel moved from one address to another.
- A rate is `/shipping-rates`, though providers say `rates`: a bare rate is an FX or tax rate in other contexts (the same call as travel's `/rate-plans`). Bare `quotes` and `estimates` were sales quotes and ride estimates and do not count.
- A courier is a carrier only when it is a company: Nash's and Circuit's couriers are drivers.
- Tracking is `/tracking` (28 providers), covering trackers, tracks and trackings.
- Duplicates merged: Kargo.

### Fleet and Telematics (`fleet`)

85 providers measured, 29 crosswalks, [api-commons/fleet](https://github.com/api-commons/fleet).

- `vehicle` (29 providers): `vin`, `id`, `make`, `model`
- `driver` (8 providers): `id`, `name`, `phone`, `status`
- `trip` (11 providers): `id`
- `vehicle_location` (3 providers): `latitude`, `longitude`, `speed`, `timestamp`
- `geofence` (5 providers): `id`, `name`, `description`
- `inspection` (3 providers): `id`

Findings:

- A vehicle agrees on its VIN, make, model and id -- the most physical core in the commons: the identity of a vehicle is fixed by the vehicle, not by the software.
- A vehicle location agrees completely where it is published (latitude, longitude, speed, timestamp), but only three providers publish it as a resource; most stream it.
- Fleet is thin overall (29 providers expose vehicles): telematics platforms gate their APIs to customers and integration partners.

Decisions:

- Locations count only beneath a vehicle, asset or device; a bare `/locations` is a store or a work site in other contexts. GPS points, positions and breadcrumbs are vehicle locations.
- Journeys are trips; zones, places and landmarks are geofences; DVIRs are inspections.
- Drivers, trips, locations, geofences and inspections `require: [vehicle]`, so a delivery network's drivers or an irrigation system's zones do not count.

### Project Management (`project-management`)

95 providers measured, 43 crosswalks, [api-commons/project-management](https://github.com/api-commons/project-management).

- `project` (43 providers): `name`, `id`, `created_at`, `updated_at`
- `task` (28 providers): `id`, `name`, `description`, `status`, `due_date`, `project_id`, `assignee_id`, `created_at`, `parent_id`
- `comment` (6 providers): `author_id`, `body`, `created_at`, `id`, `updated_at`
- `sprint` (5 providers): `goal`, `id`, `name`, `start_date`, `created_at`, `due_date`, `state`
- `milestone` (8 providers): `created_at`, `due_date`, `id`, `name`, `start_date`, `status`, `updated_at`, `description`
- `label` (15 providers): `id`, `name`, `color`
- `time_entry` (14 providers): `id`, `started_at`, `created_at`, `duration`, `user_id`, `billable`, `description`, `task_id`, `updated_at`

Findings:

- A task agrees on more than any work item in the commons: name, description, status, due date, project, assignee and parent are all core. Asana and Basecamp map 89% of it; Jira's published spec carries most task fields inside a generic `fields` object, so it maps a third. ClickUp, Linear, Monday and Wrike publish no task resource the census can read (Linear is GraphQL).
- Sprints, labels and time entries agree almost completely where they exist; a label is a name and a color everywhere.
- Comments are thin as a resource (5 providers): most work-management APIs return comments inside the task.

Decisions:

- A task covers issues, work items, to-dos, stories, and cards beneath a board or list: one unit of work under many names. Repository issues belong to source control.
- Sprints include iterations and cycles; milestones include versions, releases and phases beneath a project.
- Time entries cover worklogs, timelogs and timesheets: logged time against work.
- Productivity and Collaboration are not cohort tags: they cover documents, chat and video as much as project work.
- Duplicates merged: Jira into Atlassian Jira.

### Content Management (`cms`)

73 providers measured, 36 crosswalks, [api-commons/cms](https://github.com/api-commons/cms).

- `content_type` (6 providers): `id`, `name`, `fields`
- `entry` (6 providers): `id`, `created_at`, `updated_at`, `locale`, `name`
- `page` (16 providers): `id`, `name`, `created_at`
- `post` (12 providers): `id`, `name`, `created_at`, `status`, `body`, `tags`, `updated_at`
- `asset` (21 providers): `id`, `name`, `created_at`, `updated_at`

Findings:

- A post agrees on id, title, status, body, tags and dates -- the blog post has one shape across every CMS that exposes one.
- An asset agrees only on id, name and dates; MIME type falls just short. A CMS asset is a file, but CMSs describe the bytes less consistently than storage APIs do.
- Headless CMS is barely represented (6 providers each for content types and entries): the leading headless platforms either publish GraphQL or no OpenAPI the catalog holds.

Decisions:

- Content and Publishing are not cohort tags: they cover media companies and news as much as content-management software.
- A page and a post are separate concepts: pages are a site's structure, posts its chronological content, and the measured cores differ.
- Stories (Storyblok) and items beneath a collection (Webflow) are entries; Box's collection items are files and excluded.
- Articles and blog posts are posts.
- Duplicates merged: Confluence, Webflow, NewsCred into Optimizely.

### Email Marketing (`email-marketing`)

102 providers measured, 51 crosswalks, [api-commons/email-marketing](https://github.com/api-commons/email-marketing).

- `list` (44 providers): `name`, `id`, `created_at`, `updated_at`
- `subscriber` (29 providers): `email`, `id`, `metadata`, `created_at`, `first_name`, `last_name`
- `segment` (15 providers): `id`, `name`, `created_at`
- `campaign` (27 providers): `id`, `created_at`, `status`, `name`
- `automation` (14 providers): `id`, `name`, `created_at`, `status`
- `campaign_report` (11 providers): no core

Findings:

- A subscriber agrees on email, first and last name, custom fields and when they joined -- the merge-field model every email platform inherited.
- A campaign agrees only on id, name, status and created_at: subject, sender and send time are each modelled too differently to share, because a campaign is a draft, a schedule and a send at once.
- Campaign reports agree on nothing. Opens, clicks, bounces and unsubscribes are counted by every platform, each with its own field names and unique-versus-total semantics.

Decisions:

- A list covers audiences, mailing lists and contact lists; a subscriber covers contacts, profiles and list members -- but only at a provider that also exposes lists.
- A campaign covers broadcasts and mailings; a publication-level newsletter (Ghost, Buttondown) is not a send and is excluded.
- An automation covers workflows, flows, journeys, sequences and autoresponders.
- Templates are the messaging context's and are not duplicated here.
- Duplicates merged: Infusionsoft into Keap.

### Advertising (`advertising`)

134 providers measured, 33 crosswalks, [api-commons/advertising](https://github.com/api-commons/advertising).

- `ad_account` (25 providers): `id`, `name`
- `ad_campaign` (16 providers): `name`, `id`, `account_id`, `status`, `campaign_id`, `budget`, `created_at`, `end_date`, `start_date`, `updated_at`
- `ad_group` (16 providers): `id`, `name`, `campaign_id`, `account_id`
- `ad` (7 providers): `id`, `name`, `creative_id`
- `creative` (10 providers): `id`, `name`, `type`
- `ad_audience` (9 providers): `name`
- `ad_report` (9 providers): no core

Findings:

- An ad campaign agrees more than anything else in advertising: name, status, account, budget, start and end dates are all core. The campaign is where ad platforms converged.
- An ad group agrees on id, name, its campaign and its account -- the hierarchy is shared even where the targeting inside it is not. Facebook's ad sets, DV360's line items and Amazon's ad groups are one concept.
- Reports agree on nothing: every platform reports impressions, clicks and spend, under its own names and its own breakdowns.
- Ads themselves are thin as a resource (7 providers); most platforms expose the ad through its creative.

Decisions:

- Ad campaigns are `/ad-campaigns` and audiences `/ad-audiences`, though ad platforms say `campaigns` and `audiences`: email marketing uses both words for something else. Reports are `/ad-reports` for the same reason.
- An ad group covers ad sets, line items, insertion orders and ad squads: the level beneath a campaign that carries budget and targeting.
- Ad-intelligence tools that list other companies' advertisers are not ad accounts.
- Duplicates merged: Habu into LiveRamp, Rubicon Project into Magnite, Mavrck into Later, Gist into ProRata.

### Product Analytics (`product-analytics`)

80 providers measured, 40 crosswalks, [api-commons/product-analytics](https://github.com/api-commons/product-analytics).

- `event` (40 providers): no core
- `profile` (15 providers): `traits`, `user_id`
- `cohort` (14 providers): `id`, `name`, `description`, `created_at`
- `dashboard` (4 providers): `id`, `name`
- `funnel` (7 providers): `name`, `id`

Findings:

- An event agrees on nothing outright: user, properties and timestamp sit at 37-43%. Tracking APIs share a shape -- event name, properties, user, time -- but publish it as a request body with names that vary (event, event_type, name; distinct_id, userId), and several document the endpoint without a schema at all.
- A cohort agrees on id, name, description and created_at; segments and cohorts are one concept across CDPs and analytics tools.
- A profile agrees on a user id and its traits -- the Segment `identify` model.

Decisions:

- The bare Analytics tag is not used: it covers business intelligence, data platforms and market analytics, not product event tracking.
- `track`, `capture`, `collect` and batch-beneath-track are events; `identify`, persons, people and profiles are profiles; segments are cohorts.
- Everything but the event `requires: [event]`, so a marketing tool's `/segments` counts only if it also tracks events.

### Observability (`observability`)

279 providers measured, 104 crosswalks, [api-commons/observability](https://github.com/api-commons/observability).

- `monitor` (44 providers): `id`, `name`, `status`, `type`
- `alert` (14 providers): `id`, `status`, `name`
- `dashboard` (14 providers): `name`, `description`, `id`, `created_at`
- `log` (47 providers): no core
- `metric` (10 providers): `metric`, `type`
- `trace` (50 providers): `trace_id`, `name`, `metadata`
- `slo` (7 providers): `created_at`, `name`, `description`, `sli`, `tags`, `updated_at`, `id`

Findings:

- A monitor agrees on name, id, status and type: uptime checks, synthetic tests and metric monitors share the identity of a watcher even where their thresholds differ.
- An SLO agrees almost completely -- name, description, its indicator, tags and dates -- the newest concept here and the most standardised.
- Traces agree on a trace id, a name and metadata; logs agree on nothing as a resource. Several are OpenTelemetry payloads whose shape lives in the OTLP standard, and others LLM-observability traces with a different shape again. OTLP deserves its own pass, as Open Banking did.
- Measured against OTLP, a trace is an OpenTelemetry span: OTLP defines every core property of a trace. Logs have no measured core, and OTLP's LogRecord is the shape the market would converge on if it published one.

Decisions:

- Incidents belong to incident management; observability ends at the alert.
- A monitor covers checks, uptime checks, synthetics and probes; singular `/check` is an action and does not count.
- Alert rules, alert policies and triggers are alerts (the rule and its firing are not yet separated -- too few providers expose both).
- Metrics count only beneath a query, series or versioned API path; a bare `/metrics` is a Prometheus scrape endpoint or a usage counter almost everywhere.
- Duplicates merged: Grafana, Honeycomb, Catchpoint.

### Incident Management (`incident-management`)

75 providers measured, 28 crosswalks, [api-commons/incident-management](https://github.com/api-commons/incident-management).

- `incident` (27 providers): `id`, `name`, `severity`, `status`, `created_at`
- `incident_update` (10 providers): `created_at`, `id`, `body`
- `service` (11 providers): `name`, `description`, `id`, `created_at`
- `on_call_schedule` (11 providers): `name`, `id`, `description`, `time_zone`, `created_at`
- `escalation_policy` (7 providers): `name`, `id`, `description`, `rules`
- `status_page` (10 providers): `name`, `id`, `subdomain`

Findings:

- An incident agrees on id, title, severity, status and created_at: PagerDuty, incident.io, FireHydrant and Opsgenie map 80-100% of it -- they share the shape of an outage.
- On-call schedules and escalation policies agree almost completely where they exist -- name, description, time zone, rules -- and PagerDuty's shape is everyone's.
- Postmortems are barely published (3 providers): the retrospective lives in a document, not an API.

Decisions:

- An ITSM incident (ServiceNow) is a ticket and stays in the help-desk context; an incident here is an operational one -- something is broken and people are paged.
- Security incidents from SOAR and XDR platforms are kept as incidents: same lifecycle, though their event timelines carry security context.
- Updates cover incident updates, timeline events, notes and log entries beneath an incident.
- Status-page components are services: the thing customers see as up or down.
- Schedules, on-calls and rotations are one concept, `on_call_schedule`.

### CI/CD (`ci-cd`)

241 providers measured, 81 crosswalks, [api-commons/ci-cd](https://github.com/api-commons/ci-cd).

- `pipeline` (38 providers): `name`, `id`, `created_at`
- `run` (27 providers): `status`, `id`, `created_at`, `started_at`
- `job` (9 providers): `name`, `created_at`, `id`, `status`
- `artifact` (14 providers): `id`, `name`, `size`
- `environment` (10 providers): `name`, `id`, `created_at`, `description`
- `deployment` (54 providers): `id`, `status`

Findings:

- The hierarchy is shared: a pipeline (name, id) runs as a run (status, id, start time), which is made of jobs (name, status). GitHub Actions' workflows and runs, GitLab's pipelines and jobs, Buildkite's builds and Azure's definitions all fit it.
- A deployment agrees only on id and status: hosting platforms, CD tools and release trackers each record a deploy differently, and its environment is referenced by under a third.
- An environment agrees on name, id, description and created_at wherever it is a resource.

Decisions:

- A pipeline covers workflows, build definitions and build types; a run covers builds, workflow runs and executions. The two levels are kept apart because every provider keeps them apart.
- Singular `/workflow` is not a pipeline (business automation); plural `workflows` is.
- `POST /deploy` on a hosting platform creates a deployment and counts as one.
- Test-session builds (BrowserStack) are not CI runs.
- Duplicates merged: Azure DevOps, Platform.sh into Upsun.

### Source Control (`source-control`)

242 providers measured, 49 crosswalks, [api-commons/source-control](https://github.com/api-commons/source-control).

- `repository` (49 providers): `name`, `id`
- `branch` (20 providers): `name`, `commit_sha`
- `commit` (20 providers): `author_id`, `sha`, `parent_shas`
- `pull_request` (18 providers): `name`, `status`, `id`, `created_at`, `description`, `author_id`, `source_branch`, `is_draft`, `labels`, `number`, `reviewers`, `target_branch`
- `repo_issue` (15 providers): `status`, `id`, `name`, `assignee_ids`, `created_at`, `description`, `author_id`, `labels`, `number`, `updated_at`
- `release` (12 providers): `created_at`, `id`, `name`, `author_id`, `description`, `published_at`, `tag_name`, `assets`, `is_prerelease`

Findings:

- A pull request agrees on more than any other change resource in the commons: title, description, status, author, source and target branch, reviewers and draft state are all core. GitHub set the shape and GitLab's merge requests and Bitbucket's pull requests kept it.
- Issues and releases agree almost as completely -- number, labels, assignees; tag name and publish date.
- A repository agrees only on name and id: hosts, mirrors, analysis tools and CI platforms all expose repositories, each with its own view of one.

Decisions:

- Merge requests (GitLab) and pull requests are one concept, published at `/pull-requests` (GitHub's own path is `/pulls`; the concept name is the readable form).
- Repository issues live here, at `/repositories/{repository_id}/issues`; project-management tasks are the other context's, and a repository issue is excluded there.
- Package and chart repositories (Cloudsmith, Helm) are not source repositories.
- DevOps and CI/CD are in the cohort, gated by `requires: [repository]` for every concept but the repository itself.
- Duplicates merged: Azure DevOps, Platform.sh into Upsun.

### Cloud Infrastructure (`cloud-infrastructure`)

384 providers measured, 88 crosswalks, [api-commons/cloud-infrastructure](https://github.com/api-commons/cloud-infrastructure).

- `instance` (88 providers): `id`, `name`, `status`, `created_at`
- `volume` (38 providers): `id`, `name`, `status`, `created_at`, `size`, `type`
- `snapshot` (31 providers): `id`, `name`, `status`, `created_at`
- `network` (36 providers): `name`, `id`
- `firewall` (21 providers): `id`, `name`, `status`, `created_at`
- `load_balancer` (14 providers): `name`, `id`, `metadata`, `region`, `status`, `created_at`
- `ssh_key` (24 providers): `name`, `public_key`, `id`, `created_at`, `fingerprint`
- `region` (29 providers): `name`, `id`

Findings:

- Cloud infrastructure agrees more than any other technical context: an SSH key (name, public key, fingerprint), a volume (size, type, status) and a load balancer (region, status) are shared almost completely across clouds, VPS hosts and GPU clouds.
- An instance agrees only on name, status, id and created_at: size, image and IP address are each named by every provider in its own way (size, plan, flavor, machine_type, shape).
- Azure maps poorly however it is measured: Azure Resource Manager nests every field of every resource under `properties`, so the common names sit one level down.

Decisions:

- An instance covers servers, droplets, virtual machines, Linodes and GPU pods; singular `/server` is a load-balancer backend or syslog target and does not count.
- A snapshot covers backups only beneath an instance, server or volume: database backups belong with the database.
- A network covers VPCs, private networks and subnets; a firewall covers security groups.
- Duplicates merged: Packet into Equinix, M0, TiDB into PingCAP, Platform.sh into Upsun, Sail.

### Vulnerability Management (`vulnerability-management`)

111 providers measured, 54 crosswalks, [api-commons/vulnerability-management](https://github.com/api-commons/vulnerability-management).

- `finding` (21 providers): `id`, `severity`, `status`
- `vulnerability` (41 providers): `severity`, `description`, `id`
- `scan` (12 providers): `id`, `status`
- `scanned_asset` (7 providers): `id`, `name`, `metadata`, `created_at`, `type`, `updated_at`

Findings:

- A vulnerability (a CVE or advisory) agrees on id, description and severity; CVSS scores, affected packages and fixed versions are each named differently, though every source descends from the same NVD and CVE records.
- A finding agrees on id, severity and status -- the triage triple every scanner shares.
- Severity is core on both findings and vulnerabilities (61-63%), under six spellings in the published specs (severity, severityLevel, severity_score, risk_level, impact...).

Decisions:

- A vulnerability is the known weakness (CVE, advisory); a finding is its instance on an asset. They are separate concepts because providers keep them separate.
- EDR and cloud threat detections are not findings: they are attacks in progress, not weaknesses -- a security-operations context, not this one.
- Pentests and security assessments count as scans; compliance questionnaires and training assessments do not.
- A scanned asset is `/security-assets`: bare `/assets` is a CMS or file asset elsewhere.

### Identity Verification (`identity-verification`)

173 providers measured, 31 crosswalks, [api-commons/identity-verification](https://github.com/api-commons/identity-verification).

- `verification` (31 providers): `id`, `status`
- `person` (6 providers): `id`, `created_at`, `status`, `email`, `first_name`, `last_name`, `person_id`, `type`
- `business` (10 providers): `id`, `metadata`, `status`, `created_at`, `type`, `updated_at`
- `document` (17 providers): `id`, `type`
- `report` (7 providers): `id`, `metadata`, `status`, `created_at`, `type`

Findings:

- A verification agrees only on id and status: Persona's inquiries, Onfido's checks and CLEAR's verification sessions model the same act very differently.
- A person being verified agrees on first and last name, email, status and type -- the identity attributes are shared even where the verification is not, though only six providers expose the person as a resource.
- Sanctions and PEP screening is not a resource of its own (1 provider): results come back inside a check or report.

Decisions:

- Fraud Prevention is not a cohort tag: risk scoring is its own domain.
- A verification covers inquiries, checks, verification sessions and KYC cases.
- A person covers applicants, individuals and end users -- but only at a provider that also runs verifications.
- A business covers companies and legal entities under KYB.
- Duplicates merged: GSMA into Open Gateway, LSEG, Moody's.

### Healthcare (`healthcare`)

259 providers measured, 69 crosswalks, [api-commons/healthcare](https://github.com/api-commons/healthcare).

- `patient` (38 providers): `date_of_birth`, `gender`, `id`, `first_name`, `last_name`, `email`
- `practitioner` (21 providers): `id`, `last_name`, `npi`, `first_name`, `specialty`, `name`
- `encounter` (11 providers): `id`, `status`, `type`
- `observation` (16 providers): `code`, `id`, `patient_id`
- `condition` (13 providers): `code`, `id`, `status`, `description`, `patient_id`
- `prescription` (13 providers): `code`, `dosage`, `id`
- `coverage` (9 providers): `id`, `code`, `patient_id`, `payer`, `relationship`, `status`
- `health_claim` (8 providers): `id`, `status`, `code`, `patient_id`, `payer`, `practitioner_id`, `service_date`

Findings:

- FHIR is to healthcare what Open Banking is to banking: 32 providers in this cohort publish nothing but FHIR resources. Counted once as HL7's voice, the market's own agreement shows.
- A patient agrees on date of birth, gender, first and last name and email -- the demographic core every EHR, telehealth platform and payer API carries.
- A practitioner agrees on name, NPI and specialty: the National Provider Identifier is the one identifier the US market shares.
- Coverage agrees on the payer, the member's relationship and status, and a claim on its patient, practitioner, payer and date of service -- the payer side of healthcare is more uniform than the clinical side.
- Clinical records (observations, conditions, prescriptions) agree only on a code and the patient: the code is the vocabulary (LOINC, SNOMED, ICD-10, RxNorm), and the structure around it is the provider's.

Decisions:

- Every provider that publishes only FHIR resources counts once, as `hl7-fhir`, with its own crosswalk. Providers with FHIR alongside a proprietary API (athenahealth, Tebra, AdvancedMD, Particle, the NHS and VA) are counted on their own.
- Appointments are the scheduling context's; health insurance -- coverage and claims -- is this context's, handed over from insurance.
- A practitioner is `/practitioners` (FHIR's word), though eight providers say `providers`: `/providers` means an API provider or a service provider in other contexts.
- A prescription covers FHIR's MedicationRequest and medication orders beneath a patient.
- A health claim is `/health-claims` and covers Explanation of Benefit; `/claims` is the insurance context's.
- Visits and consultations are encounters; vitals, lab results and measurements are observations; problems and diagnoses are conditions; eligibility checks are coverage.
- Duplicates merged: Cerner into Oracle Health, CDC, EHRbase into vitagroup, Vital into Junction, three NHS listings into NHS England, Thatch.

### Learning Management (`lms`)

57 providers measured, 22 crosswalks, [api-commons/lms](https://github.com/api-commons/lms).

- `course` (22 providers): `id`, `name`
- `lesson` (6 providers): `name`, `id`, `course_id`, `position`
- `enrollment` (16 providers): `learner_id`, `id`, `course_id`
- `learner` (6 providers): `id`, `email`, `name`
- `assignment` (9 providers): `name`, `id`
- `submission` (6 providers): `comment`, `id`, `learner_id`, `score`

Findings:

- An enrollment agrees on the join -- learner, course, id -- which is what every LMS integration (rostering, HR-to-LMS sync) needs.
- A lesson agrees on name, its course and its position: the ordering of content inside a course is shared even where the content types are not.
- LMS publishes thinly (22 providers expose courses): K-12 systems lean on the OneRoster and LTI standards rather than their own REST APIs.

Decisions:

- Higher Education and Education are not cohort tags: they cover universities and research as institutions, not learning software.
- A lesson covers modules, units, sections, chapters and topics beneath a course.
- An assignment covers quizzes, exams and assessments beneath a course, and OneRoster line items; a submission covers attempts, results and grades.
- Learners count as `users` only beneath an LMS path or a course; `students` and `learners` count anywhere in the cohort.

### Food Ordering (`food-ordering`)

77 providers measured, 35 crosswalks, [api-commons/food-ordering](https://github.com/api-commons/food-ordering).

- `restaurant` (34 providers): `name`, `id`
- `menu` (11 providers): `name`, `id`
- `menu_item` (8 providers): `name`, `description`
- `food_order` (18 providers): `restaurant_id`, `items`

Findings:

- A food order agrees only on the restaurant and its items -- aggregators (DoorDash, Just Eat), ordering platforms and kitchen systems each model the totals and the fulfilment type differently, the same divergence as orders in commerce.
- A restaurant agrees only on name and id; hours and address are carried by too few to share, because many APIs take the restaurant as given from their own onboarding.
- Modifier groups -- the min/max choice rules that make a menu orderable -- are almost never a resource of their own (2 providers); they live inside the menu item.

Decisions:

- Orders are `/food-orders`: `/orders` is commerce's (and trading's).
- A restaurant covers stores, locations, venues and outlets in this cohort.
- A menu item covers items and products beneath a menu, store or restaurant.
- Delivery is the shipping context's: a delivery job is a shipment.

### Point of Sale (`point-of-sale`)

84 providers measured, 20 crosswalks, [api-commons/point-of-sale](https://github.com/api-commons/point-of-sale).

- `store_location` (11 providers): `name`, `phone`, `address`, `id`, `status`, `country`, `currency`, `latitude`, `location_id`, `longitude`, `time_zone`
- `terminal` (4 providers): `id`, `name`
- `sale` (20 providers): `id`, `customer_id`
- `shift` (5 providers): `employee_id`, `created_at`, `id`, `location_id`, `updated_at`, `version`

Findings:

- A store location agrees on name, address, phone, status, country, currency and time zone -- the most complete location core in the commons, because a POS needs every one of them to ring a sale.
- A sale agrees only on an id and the customer -- POS systems call it a sale, a transaction, a check, a ticket or an order, and carry items, taxes and tenders under as many names.
- Terminals are thin (4 providers, agreeing only on id and name); shifts (5) agree on the employee, the location and timestamps.

Decisions:

- Store locations are `/store-locations`: `/locations` means a work site in HR and a restaurant in food ordering.
- A sale covers sales, receipts, checks and POS transactions and orders.
- A shift covers cash-drawer shifts, register closures and timecards.
- Singular `/register` is an action and does not count as a terminal.
- Products are commerce's and staff are HR's; POS does not duplicate them.

### Loyalty (`loyalty`)

77 providers measured, 17 crosswalks, [api-commons/loyalty](https://github.com/api-commons/loyalty).

- `member` (14 providers): `id`
- `reward` (11 providers): `id`, `created_at`, `status`, `type`, `description`, `name`, `updated_at`
- `referral` (7 providers): `id`

Findings:

- A reward agrees on name, type, status, description and dates: what can be redeemed is shared across loyalty platforms, card-linked offer networks and incentive tools.
- A member agrees only on an id: Square's loyalty accounts, Starbucks' star balances and Smile's customers each carry the points balance and the tier in their own shape.
- Points are a balance on the member far more often than a resource of their own, and tiers a field rather than a list (4 and 2 providers).

Decisions:

- A member covers loyalty accounts and profiles; a reward covers offers, perks, catalog items and redemptions.
- Points transactions and tiers are not published as concepts; they are recorded for the next re-measure.
- A referral covers advocates and referral codes.
- Gift cards are not a cohort tag: they are a stored-value payment instrument, not loyalty.
- Duplicates merged: Impact.

### Events and Ticketing (`events`)

123 providers measured, 26 crosswalks, [api-commons/events](https://github.com/api-commons/events).

- `event` (25 providers): `name`, `start_at`, `end_at`, `id`, `category`, `status`
- `venue` (7 providers): `name`, `id`, `address`
- `ticket_type` (5 providers): `description`, `id`, `name`, `price`
- `ticket` (11 providers): `id`, `status`
- `attendee` (15 providers): `email`, `first_name`, `id`, `last_name`, `name`

Findings:

- An event agrees on name, start, end, category and id across Eventbrite, Ticketmaster's discovery API, webinar platforms and conference tools, once webhook feeds are set aside.
- An attendee agrees on name and email; whether they checked in and which event they hold sit just below core once Cvent's six listings count once.
- A venue agrees only on id, name and address across the providers that expose one.
- Ticket types are rarely a resource of their own (5 providers); most platforms put prices and tiers on the event.

Decisions:

- The Ticketing tag lives here, not in help desk: in APIs.io it mixes support tickets with event and transit ticketing, and this is the event side.
- An event counts only at a provider that also lists venues, sells ticket types, issues tickets or registers attendees (`requires_any`); a bare `/events` is a webhook feed or a calendar entry elsewhere.
- Shows, performances and attractions are events; registrants, registrations and guests are attendees; passes and admissions are tickets.
- Duplicates merged: six Cvent listings, GoTo Webinar.

### Video (`video`)

163 providers measured, 51 crosswalks, [api-commons/video](https://github.com/api-commons/video).

- `video` (51 providers): `id`, `name`, `created_at`, `status`
- `video_upload` (13 providers): `id`
- `live_stream` (6 providers): `id`, `created_at`, `name`, `status`, `updated_at`
- `playlist` (8 providers): `id`, `name`, `description`
- `caption` (11 providers): `language`, `id`

Findings:

- A video agrees on id, title, status and created_at; duration, thumbnail and playback URL are each carried by too few to share, because a hosting platform, an encoding service and a media library describe the same file from different sides.
- A caption agrees on its language -- the one field every subtitle track needs.
- Live streams agree on id, name and created_at; stream keys and ingest URLs are named by every provider its own way.

Decisions:

- Streaming is not a cohort tag: it covers data streaming as much as video.
- A video covers assets beneath a video or media path, clips, movies and recordings.
- A bare `/live` is not a live stream (health probes); `/ingest` is not an upload.
- Captions cover subtitles and text tracks beneath a video.
- Duplicates merged: Opus into OpusClip, Overshoot.

### Maps and Geocoding (`maps`)

193 providers measured, 45 crosswalks, [api-commons/maps](https://github.com/api-commons/maps).

- `geocode` (22 providers): `address`, `name`, `country`, `confidence`, `geometry`, `id`, `latitude`, `longitude`
- `place` (25 providers): `name`, `id`, `geometry`, `address`
- `route` (15 providers): no core
- `distance_matrix` (9 providers): `destinations`, `origins`, `id`, `units`

Findings:

- A geocode agrees on an address, a name, a country, a confidence score, coordinates and a geometry -- once GeoJSON is read as GeoJSON. Pelias-style geocoders return FeatureCollections whose fields live under each Feature's `properties`.
- A place agrees on id, name, geometry and address; categories and opening hours are modelled by too few to share.
- A route agrees on nothing: routing engines publish their request options (costing, profiles, avoidances) far more than a result shape, and Valhalla, OSRM and the commercial APIs each return legs and geometry differently.
- A distance matrix agrees on its origins and destinations.

Decisions:

- Maps concepts are results, not resources: a geocode is what `/geocode`, `/reverse` and address search return.
- GeoJSON is read as a standard: the census unwraps `features` and lifts a Feature's `properties` beside its geometry (a census change that applies to every context).
- Points of interest, nearby search and place autocomplete are places; directions and route optimisation are routes; sources-to-targets is a distance matrix.
- A reverse DNS lookup and Vastu compass directions are not maps (excluded by name).
- Duplicates merged: Bee Maps into Hivemapper.

### Weather (`weather`)

54 providers measured, 27 crosswalks, [api-commons/weather](https://github.com/api-commons/weather).

- `current_conditions` (12 providers): no core
- `forecast` (14 providers): no core
- `historical_weather` (9 providers): `time`
- `weather_alert` (9 providers): `event`, `severity`
- `air_quality` (11 providers): `time`
- `station` (9 providers): `name`, `id`

Findings:

- Weather agrees on less than any other data context. Current conditions come closest -- a condition, a temperature and a time, each at 36-45% -- and forecasts agree on nothing: every provider nests readings in time-series arrays (daily, hourly, list, timelines) wrapped in its own location metadata.
- Counted per listing, alerts looked standardised: four National Weather Service listings return the Common Alerting Protocol. Counted once, alerts still agree on the event and its severity -- the two fields every warning needs -- and little else.
- The physical quantities are shared even where the shapes are not: temperature, humidity, wind and pressure collapse to one name each through the aliases, so the vocabulary is usable as a dictionary even though no resource reaches core.
- Measured against its standard, the alert is CAP: the Common Alerting Protocol 1.2 defines every core property of a weather alert, and 11 fields (urgency, certainty, response type, audience...) that providers in the cohort do not publish.

Decisions:

- Forecasting is not a cohort tag: it covers demand and financial forecasting.
- Current conditions are `/current`, history `/history` and alerts `/weather-alerts` (bare `/alerts` is observability's).
- NOAA, noaa.gov, weather.gov and the National Weather Service are one publisher and count once; OpenWeather's two listings likewise.
- Pollen counts as air quality.

### Market Data (`market-data`)

237 providers measured, 95 crosswalks, [api-commons/market-data](https://github.com/api-commons/market-data).

- `instrument` (78 providers): `name`
- `market_quote` (19 providers): `symbol`
- `bar` (43 providers): `close`, `open`, `volume`, `high`, `low`
- `market_trade` (15 providers): `price`, `time`
- `order_book` (25 providers): `bids`, `asks`, `symbol`
- `exchange` (14 providers): `name`

Findings:

- A bar agrees completely: open, high, low, close and volume are core across 43 equity, crypto and data-vendor APIs. OHLCV is the most universal shape in the commons -- the single place where the market converged without a standards body.
- An order book agrees on bids, asks and the symbol. A trade agrees on price and time. A quote agrees only on the symbol -- bid, ask and last price sit just below core, because some providers quote a last price and others a two-sided market.
- An instrument agrees only on a name: equities, crypto pairs, futures and FX each identify an instrument differently (ticker, pair, FIGI, ISIN, product id), and the symbol field is the most-aliased name in this context.

Decisions:

- Orders, positions and fills belong to trading; this context is the read side of a market.
- Quotes are `/market-quotes` and trades `/market-trades`: insurance owns `/quotes`, and trading owns the trades an account makes.
- Candles, klines, aggregates and OHLC endpoints are bars, at any provider: those names mean one thing, and requiring an instrument resource cost real exchanges (Alpaca, Bitvavo). Depth and level-2 books are order books, and do require an instrument (`books` is also publishing).
- A bare `/markets` is not an instrument (rental and prediction markets); it counts only beneath an exchange or crypto path.
- Duplicates merged: Massive into Polygon, LSEG, Dow Jones into Factiva, Bamboo, Seshat, Figure.

### Trading (`trading`)

174 providers measured, 51 crosswalks, [api-commons/trading](https://github.com/api-commons/trading).

- `trade_order` (38 providers): `id`, `type`, `quantity`, `price`, `side`, `symbol`, `time_in_force`, `created_at`, `stop_price`
- `fill` (18 providers): `order_id`, `price`, `id`, `quantity`, `symbol`, `side`, `executed_at`, `fee`
- `position` (51 providers): `quantity`, `symbol`
- `brokerage_account` (39 providers): `type`
- `portfolio` (7 providers): `name`, `account_id`, `id`
- `watchlist` (8 providers): `id`, `name`, `created_at`, `total_items`

Findings:

- A trade order agrees on more than any order in the commons: side, symbol, quantity, price, type, time in force and stop price are all core. Brokers and crypto exchanges inherited the order ticket from FIX, and it shows.
- A fill agrees just as completely -- order, price, quantity, side, symbol, execution time and fee.
- A position agrees on symbol and quantity; cost basis, market value and P&L are each named differently by brokers, exchanges and wealth platforms.
- A brokerage account agrees only on its type: buying power, cash and equity are reported by every broker under its own names.

Decisions:

- Orders are `/trade-orders` and accounts `/brokerage-accounts`: commerce owns `/orders` and banking `/accounts`. Trading orders were excluded from commerce for exactly this reason.
- Fills cover executions and an account's own trades (`myTrades`); public market trades are the market-data context's.
- Holdings are positions.
- Orders, fills, accounts, portfolios and watchlists `require: [position]`: a provider that trades holds positions, and the requirement keeps commerce's orders out.
- Duplicates merged: Arch, Bamboo.

### Crypto Wallets (`crypto-wallets`)

345 providers measured, 75 crosswalks, [api-commons/crypto-wallets](https://github.com/api-commons/crypto-wallets).

- `wallet` (75 providers): `id`
- `wallet_address` (7 providers): `address`, `chain`, `format`, `id`
- `wallet_balance` (17 providers): `asset`, `total`
- `wallet_transaction` (54 providers): `status`, `id`, `direction`, `tx_hash`
- `token` (27 providers): `symbol`, `name`

Findings:

- A wallet transaction agrees on id, status, direction and the transaction hash -- the hash is the one identifier every crypto API shares, because the chain assigns it.
- A wallet agrees only on an id: custodians, MPC wallet platforms and exchanges each model the wallet as a vault, an account or a key set.
- A token agrees on its symbol and name; contract address and decimals sit just below core.

Decisions:

- Blockchain and Web3 are not cohort tags: they cover node, RPC and chain-data infrastructure more than wallets.
- A wallet covers vaults and vault accounts in custody platforms, but not DeFi yield or staking vaults, which are investment products.
- Wallet balances and transactions are `/wallets/{wallet_id}/balances` and `/wallet-transactions`: banking owns the bare words.
- Deposits, withdrawals and transfers are wallet transactions, told apart by `direction`.
- Duplicates merged: Seshat, LootRush, M0, Massive into Polygon, Mesh, MyStars.

### Search (`search`)

187 providers measured, 112 crosswalks, [api-commons/search](https://github.com/api-commons/search).

- `search_index` (28 providers): `name`, `id`
- `search_query` (106 providers): no core

Findings:

- 106 providers expose a search endpoint, and their queries and results agree on nothing -- not the query parameter, not the hit list, not the total. Search is the most common capability in the catalog with the least common shape.
- An index agrees only on name and id; document counts, vector dimensions and similarity metrics are each named by every engine its own way.
- Documents, vectors and synonyms are almost never resources of their own: they are written and read through the index (bulk endpoints, upserts) rather than addressed one by one.

Decisions:

- Indexes cover indices, collections and namespaces beneath a search or vector path, and engines and corpora; merchandising collections are excluded.
- A search query is `/search`: a result shape, like the maps concepts, not a resource.
- Duplicates merged: Depict, Gist into ProRata, TiDB into PingCAP.

### Forms and Surveys (`forms`)

93 providers measured, 40 crosswalks, [api-commons/forms](https://github.com/api-commons/forms).

- `form` (40 providers): `name`, `id`, `created_at`
- `question` (11 providers): no core
- `response` (26 providers): `id`

Findings:

- A form agrees on name, id and created_at across form builders, survey tools and employee- engagement platforms.
- A response agrees only on an id: answers are typed by question, and every builder nests them its own way -- by field id, by question reference, as a flat map or as an array.
- Questions agree on nothing as a resource (11 providers): most tools return them inside the form definition.

Decisions:

- A form covers surveys, questionnaires and polls; a response covers submissions and entries beneath a form.
- Questions count beneath a form or survey only: a bare `/questions` is a Q&A or exam question elsewhere.
- Customer Feedback is in the cohort for its surveys; reviews are their own context.

### Reviews (`reviews`)

42 providers measured, 26 crosswalks, [api-commons/reviews](https://github.com/api-commons/reviews).

- `review` (26 providers): `rating`, `created_at`, `id`, `body`, `author_name`
- `review_reply` (7 providers): `body`
- `reviewed_location` (8 providers): `name`, `address`, `city`, `description`, `metadata`, `phone`

Findings:

- A review agrees on rating, body, author, id and created_at across reputation platforms, product-review tools and listing networks: the review is one of the most uniform user-generated resources in the commons.
- A reply agrees on its body; the author and timestamps are carried by too few to share.
- A reviewed location agrees on name, address, city, phone and description.

Decisions:

- Ratings and feedback count as reviews only beneath products, reviews or locations; bare `/ratings` is a credit or app rating elsewhere.
- Replies cover responses and comments beneath a review.
- Review locations are `/review-locations`: `/locations` is a store, a work site or a restaurant in other contexts.
- Review requests were measured and dropped (1 provider).

### Social Media (`social-media`)

118 providers measured, 53 crosswalks, [api-commons/social-media](https://github.com/api-commons/social-media).

- `social_account` (22 providers): `id`
- `post` (45 providers): `id`, `text`, `created_at`, `platform`
- `social_comment` (20 providers): `id`, `author_id`, `created_at`, `text`

Findings:

- A post agrees on id, text and created_at -- across networks (X, LinkedIn, ActivityPub servers such as Pixelfed) and the publishing tools that schedule onto them.
- A comment agrees on id, author, text and created_at -- the same core as a post, one level down.
- A social account agrees on nothing outright: networks expose a user, publishing tools a connected channel, and creator platforms an influencer profile.

Decisions:

- A social account is `/social-accounts`; profiles, connected channels, creators and influencers all count.
- Tweets, statuses and publications beneath a social path are posts; newsletters are not.
- Post analytics were measured and dropped: too few providers, no shared metric names.
- Duplicates merged: Lithium and Spredfast into Khoros, Mavrck into Later, Opus into OpusClip, Impact.

### Telephony (`telephony`)

146 providers measured, 49 crosswalks, [api-commons/telephony](https://github.com/api-commons/telephony).

- `call` (49 providers): `status`, `created_at`, `id`, `direction`, `from`
- `recording` (21 providers): `id`, `created_at`, `duration`, `status`
- `transcription` (18 providers): `id`, `created_at`, `status`
- `conference` (8 providers): `id`, `status`, `created_at`, `name`

Findings:

- A call agrees on status, direction, the caller and created_at across CPaaS platforms, business phone systems and voice-AI agents -- the call-detail record is shared.
- A recording agrees on id, duration, status and created_at; a conference on id, name, status and created_at.
- Transcriptions span call transcripts and general speech-to-text jobs, and agree only on id, status and created_at -- the transcript itself is text, utterances or segments depending on the provider.

Decisions:

- Phone numbers are the messaging context's: one number serves voice and SMS, and the concept is not duplicated.
- A call covers call logs, call records and CDRs.
- Voice is in the cohort, so voice-AI agents' calls count; every concept but the call `requires: [call]`.
- Voicemail was measured and dropped: the resources found were settings.
- Duplicates merged: OpenPhone into Quo, Wispr.

### Contact Center (`contact-center`)

93 providers measured, 10 crosswalks, [api-commons/contact-center](https://github.com/api-commons/contact-center).

- `queue` (10 providers): `id`, `name`, `created_at`

Findings:

- Contact center is the thinnest context in the commons. Queues agree on id, name and created_at across ten CPaaS and business-phone providers; every other concept is exposed by three providers or fewer, and Genesys is the only platform that publishes all of them.
- The major contact-center platforms are largely absent: of Amazon Connect, Five9, NICE and Talkdesk, none has harvested OpenAPI in this cohort.

Decisions:

- Only queues are published. Interactions, skills, agent states and dispositions were measured and dropped: with Genesys the only full publisher, their 'common' shape would be one vendor's.
- Agents are the help-desk context's and calls telephony's; neither is duplicated.
- Call queues, hunt groups, ring groups and workgroups are queues.

### Workflow Automation (`workflow-automation`)

348 providers measured, 73 crosswalks, [api-commons/workflow-automation](https://github.com/api-commons/workflow-automation).

- `workflow` (73 providers): `id`, `name`, `status`, `description`
- `workflow_run` (35 providers): `id`, `status`
- `trigger` (18 providers): `type`, `id`
- `connection` (19 providers): `id`, `name`, `app`, `created_at`, `status`

Findings:

- A workflow agrees on id, name, status and description across iPaaS platforms, no-code builders, RPA tools and AI-agent orchestrators -- Zapier's zaps, Make's scenarios and n8n's workflows are one concept.
- A connection agrees on id, name, the app it connects, status and created_at: the credential-to-an-app is the most uniform resource in integration platforms.
- A run agrees only on id and status: what a run records (steps, logs, errors) is the platform's own.

Decisions:

- The bare Automation tag is not used: it covers industrial automation and RPA hardware.
- A workflow covers flows, scenarios, zaps, automations, recipes and playbooks; CI pipelines are the CI/CD context's.
- Runs are `/workflow-runs` (CI/CD owns `/runs`); singular `/run` and `/execution` are actions and do not count.
- Credentials, authorizations and connected accounts are connections.
- Duplicates merged: Albato, Ethena, Webflow.

### Knowledge Base (`knowledge-base`)

146 providers measured, 21 crosswalks, [api-commons/knowledge-base](https://github.com/api-commons/knowledge-base).

- `knowledge_base` (8 providers): `name`, `id`, `created_at`, `description`, `updated_at`
- `article` (16 providers): `id`, `name`, `body`, `created_at`, `updated_at`, `metadata`, `status`

Findings:

- An article agrees almost completely -- id and title at 100%, body at 93%, timestamps and status -- across help centers (Freshdesk, Intercom, Front, Dixa), wikis (Confluence, GitBook) and documentation platforms (Document360). Of all content in the commons, a help article is the most uniform.
- A knowledge base agrees on name, id, description and timestamps, but only 8 providers expose one as a resource: most help centers are a single, implicit knowledge base.

Decisions:

- Help Desk, Customer Service and Customer Support are in the cohort: the largest help centers are tagged as help desks, and `articles` inside that cohort means help articles.
- Knowledge bases are `/knowledge-bases`, covering help centers, wikis and spaces beneath a wiki or knowledge path.
- Wiki pages and knowledge solutions are articles; blog posts are content management's.
- Categories were measured and dropped: 3 providers, not all of them knowledge categories.
- Duplicates merged: Confluence.

### Procurement (`procurement`)

126 providers measured, 35 crosswalks, [api-commons/procurement](https://github.com/api-commons/procurement).

- `purchase_order` (26 providers): `status`, `id`, `currency`, `vendor_id`, `number`, `issued_at`
- `requisition` (11 providers): `id`, `description`, `status`, `created_at`, `total`
- `sourcing_event` (6 providers): `description`, `id`, `status`, `created_at`, `currency`, `updated_at`

Findings:

- A purchase order agrees on status, number, vendor, currency and order date across procurement suites and ERPs; its lines sit just under core (44%), carried inside the order or as a separate resource.
- A requisition agrees on description, status, total and created_at -- the request to buy is shared before any supplier is chosen.
- Sourcing events (RFQs, RFPs, tenders) are thin (6 providers) but agree on status, currency and description.

Decisions:

- Suppliers are the accounting context's vendors and are not duplicated.
- ERP is in the cohort: purchase orders live in ERPs as often as in procurement suites, and `purchase_orders` means one thing.
- Purchase requests and intake requests are requisitions; RFQs, RFPs, tenders and sourcing auctions are sourcing events (`/sourcing-events`).
- Goods receipts were measured and dropped (1 provider).
- Duplicates merged: Qubiqle into Ottimate.

### IoT Devices (`iot`)

195 providers measured, 69 crosswalks, [api-commons/iot](https://github.com/api-commons/iot).

- `device` (69 providers): `name`, `type`, `id`
- `telemetry` (18 providers): `timestamp`
- `device_command` (12 providers): `command`, `status`
- `firmware_update` (11 providers): `description`

Findings:

- A device agrees on name, id and type across IoT clouds, smart-home platforms and industrial systems; firmware version and last-seen time are carried by too few to share.
- Telemetry agrees only on a timestamp -- a reading is a value, a map of values, a fragment or a sample with every sensor in it, depending on the platform.
- A device command agrees on the command and its status -- the remote-procedure-call shape that IoT platforms share.

Decisions:

- Things, gateways and endpoints beneath a device path are devices; vehicles are fleet's.
- Readings, measurements, samples and device events are telemetry.
- Device jobs (AWS IoT) and RPC calls are device commands; OTA jobs and firmware deployments are firmware updates (`/firmware-updates`).
- Sensors were measured and dropped (1 provider).
- Duplicates merged: three AWS IoT listings into AWS IoT Core.

### EV Charging (`ev-charging`)

41 providers measured, 4 crosswalks, [api-commons/ev-charging](https://github.com/api-commons/ev-charging).

- `charger` (4 providers): `id`, `name`
- `charging_session` (3 providers): `id`

Findings:

- EV charging publishes the least of any context in the commons: 41 tagged providers, 4 with a charger or session the census can read. Chargers agree on id and name; sessions on an id.
- OCPI -- the roaming standard that defines locations, EVSEs, sessions, tariffs and charge detail records -- does not appear in this cohort as harvested OpenAPI: no provider here publishes an OCPI contract the census can read. The standard exists; its OpenAPI is not in the catalog.
- Measured against OCPI 2.2.1, the standard defines all of a charging session's core and every core property of a charger except a display name -- and it defines locations, tariffs and charge detail records that no provider in the cohort publishes as OpenAPI. OCPI is the spine this context lacked; its crosswalk is in standards/.

Decisions:

- Only chargers and charging sessions are published; locations, tariffs and charge detail records were measured and dropped, and are recorded for the next re-measure.
- Chargers cover EVSEs, charge points and charge boxes; sessions are `/charging-sessions`.
- An OCPI pass -- reading the standard's own module definitions as the reference, as the models context does for the OpenAI interface -- would give this context its spine. Noted as the next step rather than done by hand.
- Duplicates merged: Leap into Leapfrog Power.

### Webhooks (`webhooks`)

487 providers measured, 202 crosswalks, [api-commons/webhooks](https://github.com/api-commons/webhooks).

- `webhook_endpoint` (202 providers): `id`, `url`, `status`, `events`, `created_at`
- `event_type` (17 providers): `id`, `name`
- `event` (65 providers): `type`, `id`
- `delivery` (27 providers): `id`, `status`, `created_at`, `attempt`, `event_id`

Findings:

- A webhook endpoint agrees on its url, the events it subscribes to, its status and created_at across 207 providers -- the most widely implemented management resource in the commons, and one of the most uniform.
- An event agrees on its type and id; its payload is the resource that changed, so it takes the shape of whichever context sent it.
- Event types and deliveries are thin as resources (17 and 30 providers): most providers document their event types rather than serving them, and few expose delivery history.

Decisions:

- The Webhook tag marks APIs that offer webhooks, which is the cohort wanted: the management API for webhooks, wherever it lives.
- In this context a bare `/events` is the event feed -- the meaning it had in every other context where it was excluded.
- Webhook subscriptions, hooks, callbacks and notification channels are webhook endpoints, published at `/webhooks` (the market's word).
- Attempts count as deliveries only beneath a webhook, delivery or event path; a bare `/attempts` was an exam or an import elsewhere.
- Duplicates merged: eight listings, including Keap, Quo and Later.

### Audit Logs (`audit-logs`)

844 providers measured, 61 crosswalks, [api-commons/audit-logs](https://github.com/api-commons/audit-logs).

- `audit_event` (61 providers): `action`, `id`, `created_at`, `actor_id`

Findings:

- An audit event agrees on the action, the actor, an id and when it happened -- who did what, and when -- across 62 providers. The target, the IP address and the outcome sit below core: every audit log records the actor and the act, fewer record what was acted on.
- Log streams to a SIEM are almost never a resource of their own (2 providers); exporting audit logs is configured, not modelled.

Decisions:

- The cohort is the security, identity, compliance and governance tags: audit logs are part of the enterprise surface of almost any API, and these tags find the ones that publish them.
- Only audit-specific paths count -- audit logs, audit events, audit trails, activity logs, and events or logs beneath an audit path; a bare `/events` or `/logs` is another context's.
- Audit events are `/audit-events`.
- Duplicates merged: eight listings, including ConductorOne, Oracle Health, Cvent and LSEG.

### Feature Flags (`feature-flags`)

36 providers measured, 19 crosswalks, [api-commons/feature-flags](https://github.com/api-commons/feature-flags).

- `flag` (19 providers): `name`, `description`, `enabled`, `id`, `key`, `metadata`, `created_at`, `type`
- `flag_environment` (11 providers): `name`, `id`
- `flag_segment` (9 providers): `description`, `id`, `name`, `created_at`, `rules`
- `experiment` (7 providers): `id`, `name`, `description`, `status`, `created_at`, `ended_at`, `started_at`

Findings:

- A flag agrees on key, name, description, whether it is enabled, its type and created_at -- feature-flag platforms, experimentation tools and identity providers with flags (Statsig's gates, PostHog, Kinde) share the toggle's shape almost completely.
- Segments agree on name, description and rules; experiments on status, start and end -- the targeting and the test share a shape as well as the flag.
- The cohort is small (36 providers, 19 mapped): most flag platforms deliver flags through SDKs and keep the management API secondary.

Decisions:

- Gates, toggles and switches are flags; features count as flags only beneath a project or environment (a bare `/features` is a product's feature list elsewhere).
- Environments are `/flag-environments` and segments `/flag-segments`: CI/CD owns `/environments` and analytics owns cohorts. Audiences and cohorts count as flag segments only at a provider that also serves flags.

### API Management (`api-management`)

135 providers measured, 23 crosswalks, [api-commons/api-management](https://github.com/api-commons/api-management).

- `managed_api` (23 providers): `name`, `id`, `created_at`, `description`, `metadata`, `updated_at`
- `api_product` (6 providers): `description`, `name`, `created_at`
- `consumer_app` (12 providers): `name`, `created_at`, `description`, `id`, `status`, `credentials`, `metadata`

Findings:

- A managed API agrees on name, description, id and timestamps across gateways and API management platforms; base path and upstream target are each named too differently to share.
- An API product agrees on Apigee's quota model -- quota, interval and time unit -- because Apigee defined the API product and the rest of the market copied it.
- A consumer app agrees on name, status, credentials and description: the developer app that holds keys is the same resource across Apigee, Azure API Management, Kong and APISIX.

Decisions:

- API keys are the identity context's and plans billing's; neither is duplicated here.
- Managed APIs are `/apis`; proxies and gateway services count. Products are `/api-products` (billing owns plans, commerce owns products); consumers, developer apps and clients beneath a portal are `/consumer-apps`.
- Routes were measured and dropped (4 providers).
- Duplicates merged: Google Apigee into Apigee, Gloo into Solo.io.

### Secrets Management (`secrets`)

46 providers measured, 11 crosswalks, [api-commons/secrets](https://github.com/api-commons/secrets).

- `secret` (9 providers): `metadata`, `created_at`, `id`, `name`, `type`, `updated_at`
- `secret_store` (4 providers): `id`, `name`
- `encryption_key` (3 providers): `name`

Findings:

- A secret agrees on name, type, id and timestamps -- and never on its value: providers return secret metadata on the resource and the value through a separate read, so the value does not reach core anywhere.
- Secrets management publishes thinly: 46 providers in the cohort, 12 mapped.

Decisions:

- Password-manager items in a vault, credentials and passwords beneath a vault, KV paths and parameter-store parameters are secrets.
- Vaults, safes and secret environments are `/secret-stores`: crypto custody owns the bare word vault in the crypto-wallets context.
- Encryption keys are `/encryption-keys` and count only beneath a KMS, key ring, vault or transit path: identity owns API keys.
- Secret versions were measured and dropped (2 providers).
- Duplicates merged: HVault into HashiCorp Vault.

### DNS and Domains (`dns`)

69 providers measured, 28 crosswalks, [api-commons/dns](https://github.com/api-commons/dns).

- `domain` (23 providers): `id`, `name`, `created_at`
- `zone` (7 providers): `id`, `name`, `created_at`, `status`
- `dns_record` (18 providers): `name`, `type`, `ttl`, `id`, `priority`

Findings:

- A DNS record agrees on name, type, TTL, priority and id across registrars, DNS hosts and clouds (Cloudflare, Route 53, Google Cloud DNS, Hetzner) -- the record is fixed by the DNS protocol, and the APIs follow it. Its content is the one field named differently everywhere (content, value, rdata, rrdatas, target).
- A domain agrees on name, id and created_at; expiry, auto-renew and nameservers are each carried by too few registrars to share.

Decisions:

- Records, resource-record sets and DNS records are one concept, published beneath their zone at `/zones/{zone_id}/records`.
- Zones count only at a provider that also exposes records; hosted zones and managed zones are zones.

### CDN and Edge (`cdn`)

77 providers measured, 17 crosswalks, [api-commons/cdn](https://github.com/api-commons/cdn).

- `purge` (17 providers): no core
- `tls_certificate` (4 providers): `id`, `status`, `type`, `updated_at`

Findings:

- CDN is the context where the census sees least of a large market. The major CDNs publish APIs, but CloudFront's is XML, Fastly's takes form-encoded bodies -- so distributions, the central concept, could not be measured from 4 providers.
- Purges are the most published CDN operation (17 providers) and agree on nothing outright: a purge is a list of URLs at some providers, of cache tags at others, and a whole-zone flush at the rest.

Decisions:

- Purges cover invalidations and cache flushes, at `/purges`.
- TLS certificates count at a provider that also exposes purges, at `/tls-certificates`.
- Distributions and edge functions were measured and dropped. Reading XML and form-encoded APIs is the census change that would recover them; it is recorded for the tooling backlog.
- Pull zones (Bunny), services (Fastly) and distributions (CloudFront) are the same concept under three names.

### AI Agents (`ai-agents`)

680 providers measured, 156 crosswalks, [api-commons/ai-agents](https://github.com/api-commons/ai-agents).

- `ai_agent` (156 providers): `name`, `id`, `created_at`
- `agent_thread` (52 providers): `id`, `created_at`
- `agent_run` (41 providers): `status`, `id`, `created_at`
- `agent_tool` (37 providers): `name`, `id`, `description`, `created_at`, `parameters`

Findings:

- An agent agrees on its name, id and created_at -- and not on what makes it an agent: its instructions sit at 29%, and the model and the tools it may call are each carried by a minority under different names. 156 platforms expose an agent; they describe its brain 156 ways.
- A tool agrees on name, description and a parameters schema -- the function-calling shape the model providers defined, which agent platforms adopted wholesale.
- A run agrees on status, id and created_at; a thread only on id and created_at.

Decisions:

- Agents are `/ai-agents`, threads `/agent-threads`, runs `/agent-runs` and tools `/agent-tools`: help desk owns agents, messaging owns conversations, and CI/CD and workflow automation own runs.
- Assistants, bots and copilots are agents.
- Singular `/chat` is a chat-completion call and belongs to the models standard, not here.
- Executions count as runs only beneath an agent, task or workflow path.
- Duplicates merged: Duvo, Parallel, Sail, Ottic into Rime, and the eventwren family.

### Document AI (`document-ai`)

132 providers measured, 35 crosswalks, [api-commons/document-ai](https://github.com/api-commons/document-ai).

- `extraction` (35 providers): `id`, `status`
- `extractor` (2 providers): no core

Findings:

- An extraction agrees only on id and status. What comes back -- key-value fields, tables, markdown, entities, a JSON object shaped by a schema -- is each product's own model; document AI shares the job, not the result.
- Extractors (parsers, processors, document types) are a resource at only a few providers; most take the schema inline with each extraction request.

Decisions:

- An extraction covers OCR, parse, extract and analyze operations, and jobs or predictions beneath a document or parser path.
- Extractors cover parsers, processors, document types and extraction templates, at `/extractors`.
- Web-page extraction (Diffbot) is not document AI and is excluded; a web-scraping context would own it.
- Duplicates merged: Nitro, Sensible.

### Data Enrichment (`data-enrichment`)

137 providers measured, 47 crosswalks, [api-commons/data-enrichment](https://github.com/api-commons/data-enrichment).

- `person_profile` (26 providers): `name`
- `company_profile` (35 providers): `name`, `domain`, `description`, `id`
- `email_lookup` (7 providers): `email`, `result`, `catch_all`, `domain`, `first_name`, `last_name`, `linkedin_url`, `score`

Findings:

- A company profile agrees on name, domain, description and id -- the domain is the join key of B2B data, and every enrichment provider returns it.
- A person profile agrees only on a name: email, title, company and LinkedIn URL are each returned by a minority, because people data is sold field by field and each vendor's coverage differs.
- An email lookup agrees on the email, a result and a confidence score, and whether the domain is catch-all -- verification is the most uniform enrichment product.

Decisions:

- Enrichment returns results about people and companies; CRM owns the contacts and companies you keep. Profiles are `/person-profiles` and `/company-profiles`, lookups `/email-lookups`.
- Prospects, and people or contacts beneath an enrich or search path, are person profiles; organizations and firmographics are company profiles.
- Duplicates merged: Apollo, Golden, Parallel, Windfall.

### Tax (`tax`)

51 providers measured, 13 crosswalks, [api-commons/tax](https://github.com/api-commons/tax).

- `tax_calculation` (6 providers): `tax_amount`
- `tax_transaction` (12 providers): `id`, `amount`, `date`, `type`

Findings:

- A tax transaction agrees on id, amount, date and type -- the committed record a tax engine reports from.
- A tax calculation agrees on nothing: sales-tax engines, VAT services and global tax APIs each take addresses, lines and exemptions in their own shape, and return a breakdown in another.
- Tax is thin as published OpenAPI (51 providers, 15 mapped), and splits by country -- US sales tax, EU VAT and the UK's Making Tax Digital are three different vocabularies.

Decisions:

- Payroll and contractor tax belong to payroll; property-transfer tax quotes are excluded.
- Calculations are `/tax-calculations` and committed transactions `/tax-transactions`: payments and banking own the bare words.
- Rates, exemption certificates and filings were measured and dropped.

### Legal Practice (`legal`)

79 providers measured, 10 crosswalks, [api-commons/legal](https://github.com/api-commons/legal).

- `matter` (10 providers): `id`, `name`, `client_id`, `status`, `created_at`, `description`, `number`, `practice_area`, `closed_at`, `matter_type`

Findings:

- A matter agrees on more than most work records in the commons: number, client, practice area, status, description and when it closed are all core across practice-management systems (Clio, MyCase and others) -- legal practice converged on one shape of a case file.
- Court data is not published as OpenAPI by courts. The few legal-data services that expose dockets, filings and opinions do so in their own shapes, too few to call common.

Decisions:

- Contracts belong to contract lifecycle, time entries to project management, documents to files, and invoices to billing; legal practice keeps the matter.
- Cases beneath a firm, client or matter path are matters; cases beneath a court are dockets.
- Dockets, filings and opinions were measured and dropped.
- Duplicates merged: CourtListener into Free Law Project.

### Contract Lifecycle (`contracts`)

45 providers measured, 10 crosswalks, [api-commons/contracts](https://github.com/api-commons/contracts).

- `contract` (10 providers): `id`, `status`, `name`, `created_at`
- `contract_template` (5 providers): `id`, `name`

Findings:

- A contract agrees only on id, name, status and created_at. Counterparty, value, effective and expiration dates -- the facts a contract system exists to track -- are each carried by a minority under different names.
- Contract lifecycle publishes little (45 providers, 11 mapped), and the analysis that sets CLM apart -- clauses, obligations -- is almost never a resource of its own.

Decisions:

- Signing is e-signature's: envelopes and recipients are not duplicated. Agreements count as contracts here unless they are clickwrap acceptance records.
- Templates are `/contract-templates`: e-signature owns `/templates`.
- Clauses and obligations were measured and dropped.

### Expense Management (`expenses`)

58 providers measured, 11 crosswalks, [api-commons/expenses](https://github.com/api-commons/expenses).

- `expense_claim` (11 providers): `description`, `id`, `amount`, `category`, `date`, `currency`, `employee_id`, `merchant`, `status`

Findings:

- An expense claim agrees almost completely -- amount, currency, date, category, merchant, employee, description and status are all core. The line on an expense report is one of the most uniform records in the commons.
- Everything around the claim -- receipts, reports, policies -- is rarely a resource in the published APIs (2 providers or fewer readable): expense platforms expose the spend, and keep the approval workflow inside the product.

Decisions:

- Claims are `/expense-claims`: accounting owns `/expenses` as a ledger posting, and the two are different records of the same spend.
- Expense transactions and report entries are claims.
- Receipts, reports and policies were measured and dropped.
- Duplicates merged: Concur into SAP Concur Expense.

### Time Tracking (`time-tracking`)

80 providers measured, 20 crosswalks, [api-commons/time-tracking](https://github.com/api-commons/time-tracking).

- `timesheet` (13 providers): `employee_id`
- `scheduled_shift` (12 providers): `end_at`, `employee_id`, `id`, `start_at`, `break_minutes`

Findings:

- A scheduled shift agrees on its start, its end, the employee and the unpaid break -- workforce scheduling shares the shape of a shift completely enough to move one between systems.
- A timesheet agrees only on the employee: the period, the hours and the approval are each modelled differently, because a timesheet is a weekly roll-up in some products and a single day's card in others.

Decisions:

- Time logged against tasks is project management's (time entries); time off is HR's (absences); pay is payroll's.
- Timecards are timesheets; rosters are shifts.
- Shifts are `/scheduled-shifts`: point of sale owns `/shifts` for cash-drawer shifts.
- Clock punches were measured and dropped.

### Field Service (`field-service`)

50 providers measured, 21 crosswalks, [api-commons/field-service](https://github.com/api-commons/field-service).

- `field_job` (21 providers): `id`, `description`, `status`, `location_id`
- `technician` (4 providers): `email`, `id`, `phone`

Findings:

- A field job agrees on description, status and the service location -- the where and what of a dispatch -- across home-service platforms, maintenance systems and FSM suites. Schedule, priority and totals are each named too differently to share.
- Technicians agree on email and phone where they are a resource (4 providers); most platforms treat them as users.

Decisions:

- Jobs, work orders, service orders and service calls are one concept, `/field-jobs`: recruiting owns `/jobs` and property management `/work-orders`. Property maintenance requests stay with property management.
- Customers are CRM's, invoices billing's and appointments scheduling's.
- Estimates and visits were measured and dropped.

### IT Asset Management (`it-assets`)

54 providers measured, 31 crosswalks, [api-commons/it-assets](https://github.com/api-commons/it-assets).

- `it_asset` (31 providers): `id`, `name`
- `software_license` (4 providers): `status`

Findings:

- A managed device agrees only on id and name across MDM, endpoint-management and asset platforms. Serial number, model, OS and assignee are each carried by a minority under different names: every tool describes the same laptop from its own angle (inventory, security posture, assignment).
- Software licenses are thin as a resource; most platforms report installed software per device rather than licenses owned.

Decisions:

- Devices are `/it-assets`. In this cohort a bare `/devices` is a managed computer or phone; IoT devices are the IoT context's.
- Installed-software inventory (`/devices/{id}/software`) is not a license.

### ITSM Change and CMDB (`cmdb`)

32 providers measured, 4 crosswalks, [api-commons/cmdb](https://github.com/api-commons/cmdb).

- `change_request` (4 providers): `description`, `name`

Findings:

- ITSM beyond the ticket is nearly invisible as OpenAPI (32 providers, 4 mapped). The market's largest platform exposes every ITSM record through a generic table API (`/table/{tableName}`), so configuration items, changes and problems have no resource paths to measure.
- A change request agrees on its title and description where it is a resource (3 providers): too few to say more.

Decisions:

- Incidents and service requests stay in help desk; this context keeps changes, problems and the CMDB.
- Configuration items and problems were measured and dropped. A table-API reader -- one that reads a provider's table schemas as resources -- would recover them; it is recorded for the tooling backlog.

### Customer Success (`customer-success`)

65 providers measured, 14 crosswalks, measured and recorded as `thin`, not published.

- `health_score` (12 providers): no core
- `nps_response` (2 providers): no core
- `success_plan` (2 providers): no core
- `playbook` (2 providers): no core

Findings:

- Customer success is not published as OpenAPI. Every health-score match in a 65-provider cohort was a `/health` service check; the success objects themselves -- CTAs, success plans -- come from one platform (Gainsight). No concept clears the three-provider floor.

Decisions:

- Measured and not published: the context is recorded as `thin`, with its findings, and gets no repository until the market publishes enough to distil.
- A bare `/health` is a service health check, not a customer health score.

### Sales Engagement (`sales-engagement`)

61 providers measured, 12 crosswalks, [api-commons/sales-engagement](https://github.com/api-commons/sales-engagement).

- `sequence` (12 providers): `id`, `name`, `owner_id`, `created_at`, `updated_at`, `status`
- `sequence_step` (5 providers): `id`, `type`, `name`, `position`
- `enrollment` (4 providers): `id`, `created_at`, `prospect_id`, `sequence_id`, `state`, `updated_at`

Findings:

- A sequence agrees on name, owner, status and timestamps; its steps on type, name and position; an enrollment on the sequence, the prospect and a state. Outreach's model -- sequences, steps and sequence states -- is the shape the rest of the category kept.
- Sales engagement publishes modestly (61 providers, 12 mapped), but what is published agrees well: the three concepts together describe a cadence end to end.

Decisions:

- Cadences are sequences; campaigns count as sequences beneath an outreach or sequence path.
- Sequence states, memberships and prospects or leads beneath a sequence or campaign are enrollments.
- Prospects are CRM's contacts and leads; marketing automations are email marketing's.
- Duplicates merged: Infusionsoft into Keap.

### Configure, Price, Quote (`cpq`)

46 providers measured, 16 crosswalks, [api-commons/cpq](https://github.com/api-commons/cpq).

- `sales_quote` (16 providers): `id`, `status`

Findings:

- A sales quote agrees only on id and status: total, discount, expiry and the deal it belongs to are each carried by a minority. Quotes are built inside CRM and CPQ suites and exposed as documents more than as structured records.
- Quote lines and price books are almost never resources in published APIs (2 and 1 providers).

Decisions:

- Quotes are `/sales-quotes`: insurance and market data own `/quotes`. Proposals count.
- Products are commerce's, deals CRM's, and invoices billing's.
- Quote lines and price books were measured and dropped.

### Affiliates and Partners (`affiliates`)

28 providers measured, 6 crosswalks, [api-commons/affiliates](https://github.com/api-commons/affiliates).

- `partner` (6 providers): `created_at`, `email`, `id`, `metadata`, `name`

Findings:

- A partner agrees on name, email, id and created_at where it is published -- but affiliate networks publish thinly (28 providers, 8 mapped), and programs, conversions and commissions are not resources often enough to share a shape.

Decisions:

- Affiliates, partners, publishers beneath an affiliate path, media partners and ambassadors are partners.
- Customer referral programs are loyalty's; ad campaigns are advertising's.
- Programs, conversions and commissions were measured and dropped.
- Duplicates merged: Impact Radius into Impact.

### Nonprofit Fundraising (`fundraising`)

50 providers measured, 14 crosswalks, [api-commons/fundraising](https://github.com/api-commons/fundraising).

- `donor` (6 providers): `email`, `first_name`, `id`, `last_name`, `created_at`, `phone`, `address`, `gender`, `name`, `organization_id`, `updated_at`
- `donation` (11 providers): `id`, `amount`, `metadata`, `created_at`, `donor_id`, `type`
- `fundraising_campaign` (6 providers): `created_at`, `id`, `name`, `goal`, `end_date`, `status`, `updated_at`, `currency`, `start_date`
- `fund` (5 providers): `id`, `name`, `created_at`, `updated_at`, `campaign_id`, `description`, `is_default`

Findings:

- Fundraising publishes little (50 providers, 14 mapped), but what is published agrees almost completely: a donation on amount, type, donor and date; a campaign on name, goal, currency, start and end; a donor on name, email, phone and address; a fund on name, description and the campaign it belongs to.
- Nonprofit software converged on one model of giving -- the donor, the gift, the appeal and the fund -- and the published APIs carry it with little drift.

Decisions:

- Constituents and supporters are donors; gifts and contributions are donations; designations are funds.
- Campaigns are `/fundraising-campaigns`: email marketing and advertising own `/campaigns`.
- Donations need no donor resource in the same API: gift-processing platforms expose gifts alone.
- Pledges were measured and dropped.

### Membership (`membership`)

26 providers measured, 9 crosswalks, [api-commons/membership](https://github.com/api-commons/membership).

- `member` (9 providers): `id`, `email`, `status`

Findings:

- A member agrees on id, email and status across association, club and gym platforms -- and that is all membership publishes in common (26 providers, 9 mapped). Memberships, levels and chapters are kept inside the products.

Decisions:

- Members are `/members`, the market's word: inside this cohort it means only one thing (HR excluded it as workspace members, identity counts it as users).
- Dues are billing's invoices; events are the events context's.
- Memberships, membership types and chapters were measured and dropped.

### Marketplace (`marketplace`)

468 providers measured, 14 crosswalks, measured and recorded as `thin`, not published.

- `seller` (14 providers): `id`
- `marketplace_listing` (5 providers): `name`, `sku`

Findings:

- Marketplace is not published in a common shape. Across a 468-provider cohort, sellers agree on nothing but an id (14 providers), and listings and offers are one marketplace's model each -- the large marketplaces publish proprietary seller APIs, and `offers` elsewhere are loyalty, game-store and order-book offers.

Decisions:

- Measured and not published: recorded as `thin`, with its findings, and given no repository until a shared seller or listing shape appears.
- Orders are commerce's and seller payouts are payments'.

### Returns (`returns`)

370 providers measured, 32 crosswalks, [api-commons/returns](https://github.com/api-commons/returns).

- `return_request` (32 providers): `id`, `status`, `created_at`

Findings:

- A return agrees on id, status and created_at across returns platforms and commerce systems. Returns-management tools carry items and reasons; commerce platforms record a return as a status on an order -- so line items and reasons fall just short of core once both count.

Decisions:

- Returns are `/returns`; RMAs and return requests count. Exchanges do not -- in this cohort they were currency exchanges as often as product exchanges.
- The e-commerce, order-management and fulfillment tags are in the cohort: commerce platforms expose returns that returns-only tools do not. Refunds are payments'; return labels are shipping's.
- Return reasons were measured and dropped.
- Duplicates merged: four listings.

### Warehouse Management (`warehouse`)

75 providers measured, 13 crosswalks, [api-commons/warehouse](https://github.com/api-commons/warehouse).

- `warehouse` (11 providers): `name`, `id`, `address`
- `inbound_receipt` (4 providers): `status`

Findings:

- A warehouse agrees on name, id and address across WMS, 3PL and inventory platforms. Everything that happens inside it -- bins, receiving, picking -- is barely published: inbound receipts at 4 providers (agreeing on a status), bins and pick lists at 2 or fewer.
- 3PLs expose the receiving workflow (ShipBob, ShipMonk) without exposing the warehouse; a warehouse is the customer's view, receiving is the operator's.

Decisions:

- Facilities, fulfillment centers and distribution centers are warehouses.
- ASNs, inbound shipments and receivings are inbound receipts (`/inbound-receipts`) -- the concept procurement measured and dropped as goods receipts.
- Stock levels are commerce's inventory; outbound shipments are shipping's.
- Bins and pick lists were measured and dropped.
- Duplicates merged: 3PL Central into Extensiv.

### Freight and TMS (`freight`)

205 providers measured, 12 crosswalks, [api-commons/freight](https://github.com/api-commons/freight).

- `load` (12 providers): `commodity`, `id`, `status`, `weight`
- `freight_carrier` (5 providers): `email`, `id`, `name`, `phone`

Findings:

- A load agrees on its weight, commodity, status and id: what is moving and how heavy, not where -- origin, destination and dates are each nested differently (stops, pickup/delivery objects, addresses).
- Freight publishes thinly as OpenAPI: 205 providers in the cohort, 13 mapped.

Decisions:

- Loads cover freight shipments, TMS orders and freight bookings; parcel shipments are shipping's.
- Carriers are `/freight-carriers` (trucking companies identified by SCAC, DOT and MC numbers); shipping's carriers are parcel networks.
- Freight quotes and tenders were measured and dropped.
- Duplicates merged: Kargo.

### Gift Cards (`gift-cards`)

54 providers measured, 5 crosswalks, measured and recorded as `thin`, not published.

- `gift_card` (5 providers): `id`, `created_at`, `status`
- `gift_card_activity` (3 providers): no core
- `gift_card_brand` (1 providers): no core

Findings:

- Gift cards are not published in a common shape: 54 providers in the cohort, 4 with a readable gift-card resource, agreeing only on id, status and created_at. Gift-card platforms expose a brand catalog and an order flow; loyalty platforms expose redemptions -- the card itself is rarely a resource.

Decisions:

- Measured and not published: recorded as `thin`, with its findings.
- Redemptions are loyalty's where they spend points, and payments' where they spend money.

### Subscription Commerce (`subscription-commerce`)

413 providers measured, 6 crosswalks, measured and recorded as `thin`, not published.

- `scheduled_order` (6 providers): `id`, `created_at`, `status`, `total`

Findings:

- The scheduled order a product subscription produces is barely a resource of its own: 6 providers in a 413-provider commerce cohort, agreeing on id, status, total and created_at. A first measurement found 21 -- most of them payment processors' `/charges`, which are payments, not scheduled orders.

Decisions:

- Measured and not published: recorded as `thin`, with its findings.
- A bare `/charges` is a payment charge (payments); charges count here only beneath a subscription path.
- The subscription is billing's; its products are commerce's.

### Privacy and Consent (`privacy`)

113 providers measured, 8 crosswalks, measured and recorded as `thin`, not published.

- `consent` (7 providers): no core
- `data_subject_request` (1 providers): no core

Findings:

- Privacy is not published in a common shape: in a 113-provider cohort, consent records appear at 7 providers with no shared property, and data-subject requests at one. Consent-management platforms deliver consent through a browser SDK and a consent string, not a REST resource.

Decisions:

- Measured and not published: recorded as `thin`, with its findings.
- Email unsubscribes and suppressions are messaging's; privacy here is regulatory consent and data-subject rights.

### Background Checks (`background-checks`)

16 providers measured, 3 crosswalks, measured and recorded as `thin`, not published.

- `screening` (3 providers): `created_at`, `id`, `status`
- `screening_report` (2 providers): no core
- `screening_package` (1 providers): no core

Findings:

- Background screening is barely published as OpenAPI: 16 providers in the cohort, 3 exposing a screening, agreeing on id, status and created_at.

Decisions:

- Measured and not published: recorded as `thin`, with its findings.
- Identity verification is its own context; candidates are recruiting's.

### Open Data Catalogs (`open-data-catalogs`)

276 providers measured, 33 crosswalks, [api-commons/open-data-catalogs](https://github.com/api-commons/open-data-catalogs).

- `dataset` (33 providers): `id`

Findings:

- A dataset agrees only on an id across 33 portals; its name (48%) and description (41%) fall just short. CKAN portals wrap every response in an untyped result, and portals built on other platforms serve datasets as views, so the dataset that every open-data standard describes is rarely published as a typed resource.
- Measured against DCAT-US 1.1, the standard defines the dataset core and eleven more fields -- keywords, publisher, contact point, access level, temporal and spatial coverage -- that no portal in the cohort publishes as a property of the dataset resource.

Decisions:

- CKAN's Action API is profiled as its own standard in api-commons/open-data; this context measures the dataset across every kind of portal, CKAN action paths included.
- Packages, package_show and views beneath a data API are datasets.
- Distributions and publishers were measured and dropped; DCAT-US's distribution is recorded as the shape the standard defines.
- Duplicates merged: BLS, CDC, NESO, Powershop.

### Research Repositories (`research-repositories`)

123 providers measured, 21 crosswalks, [api-commons/research-repositories](https://github.com/api-commons/research-repositories).

- `work` (11 providers): `id`, `type`
- `collection` (6 providers): `id`, `description`, `name`, `type`

Findings:

- Eleven universities in the cohort publish DSpace's REST API and nothing else for their repository -- the same distortion as CDR in banking and FHIR in healthcare. Counted once as DSpace's voice, a scholarly work agrees only on id and type.
- Even the DOI, the identifier scholarly publishing is built around, is carried by only 30% of work resources: bibliographic indexes key on it, repository software keys on a handle.
- A collection (journal, community, set) agrees on name, description and type.

Decisions:

- DSpace implementers count once (`dspace`), each with its own crosswalk, as the open-banking and FHIR implementers do.
- Works cover publications, outputs, preprints, theses, research datasets and repository items and records; collections cover communities, journals and OAI sets.
- OAI-PMH is query-parameter based and is not measured by path; a verb-aware reader is recorded for the tooling backlog.
- Researchers were measured and dropped (2 providers).

### News (`news`)

73 providers measured, 31 crosswalks, [api-commons/news](https://github.com/api-commons/news).

- `news_article` (31 providers): `name`, `description`, `published_at`, `id`, `source_id`
- `news_source` (10 providers): `name`, `category`, `language`, `country`

Findings:

- A news article agrees on title, description, publish date, id and its source across aggregators, publishers and media-monitoring tools -- the headline record NewsAPI popularised, which most of the category copied.
- A news source agrees on name, category, language and country.

Decisions:

- Articles are `/news-articles` and sources `/news-sources`: the knowledge base owns `/articles`, and a bare `/sources` means something else in most contexts.
- Stories, headlines and news search results are news articles.
- Duplicates merged: Dow Jones into Factiva.

### Music (`music`)

45 providers measured, 22 crosswalks, [api-commons/music](https://github.com/api-commons/music).

- `track` (20 providers): `id`, `name`, `artist_ids`, `duration_ms`, `isrc`
- `artist` (15 providers): `id`, `name`, `type`
- `album` (10 providers): `id`, `name`, `artist_ids`, `type`
- `music_playlist` (11 providers): `id`, `description`, `name`, `type`

Findings:

- A track agrees on id, name, artists, duration and ISRC across streaming services, music-data providers and licensing libraries: the ISRC is the music industry's shared key, and the published APIs carry it.
- Albums and artists agree on id, name and type; Spotify's object model -- the `type` field on every object -- is visible in the core.

Decisions:

- Songs and recordings are tracks; releases and release groups are albums.
- Playlists are `/music-playlists`: video owns `/playlists`.
- Podcasts are their own context.

### Podcasts (`podcasts`)

88 providers measured, 13 crosswalks, [api-commons/podcasts](https://github.com/api-commons/podcasts).

- `show` (13 providers): `id`, `name`, `description`, `author`
- `episode` (11 providers): `id`, `description`, `name`, `duration`, `audio_url`, `show_id`

Findings:

- An episode agrees on title, description, duration, the audio URL and the show it belongs to -- the RSS enclosure model every podcast API inherits, because every podcast is an RSS feed first.
- A show agrees on title, description and author.

Decisions:

- Podcasts, shows and podcast feeds are one concept, published as `/shows`.
- Audio streaming of music is music's.

### Books and Publishing (`books`)

132 providers measured, 12 crosswalks, [api-commons/books](https://github.com/api-commons/books).

- `book` (12 providers): `id`, `name`

Findings:

- A book agrees only on an id and a title. ISBN, authors, publisher and publication date are each carried by a minority: Google Books nests them under `volumeInfo`, library systems model titles as holdings, and retailers as products.

Decisions:

- Titles, volumes, editions, ebooks, audiobooks and works beneath a library path are books.
- Authors were measured and dropped.
- Duplicates merged: the eventwren family.

### Translation and Localization (`localization`)

49 providers measured, 27 crosswalks, [api-commons/localization](https://github.com/api-commons/localization).

- `localization_project` (6 providers): `name`, `target_locales`, `description`, `id`, `project_id`, `slug`, `source_locale`
- `string_key` (6 providers): `key`, `id`, `platforms`
- `translation` (26 providers): no core
- `locale_resource` (4 providers): `code`

Findings:

- A localization project agrees on name, description, its source locale and its target locales across translation-management platforms; a string key on the key and the platforms it ships to.
- A translation agrees on nothing: machine-translation engines (DeepL among them) return translated text with a detected source language, while translation- management platforms store a reviewed translation of a key. One word, two records.

Decisions:

- Projects are `/localization-projects` (project management owns `/projects`) and count only at a provider that also exposes string keys; keys are `/string-keys`.
- Machine translations and stored translations stay one concept for now; the measurement says they should split, and the next re-measure will split them if it holds.
- Locales count only at a provider that also exposes string keys.

### Speech and Transcription (`speech`)

131 providers measured, 67 crosswalks, [api-commons/speech](https://github.com/api-commons/speech).

- `speech_transcript` (42 providers): no core
- `voice` (35 providers): `name`, `id`, `gender`
- `speech_synthesis` (21 providers): `text`, `voice_id`, `format`, `model`

Findings:

- Text-to-speech agrees and speech-to-text does not. A synthesis request agrees on the text, the voice, the output format and the model -- and a voice on name, id and gender. A transcript agrees on nothing across 37 engines: words, utterances, segments, channels and speaker labels are each modelled differently.

Decisions:

- Transcripts are `/speech-transcripts`: telephony owns `/transcriptions` for call transcripts.
- Listen, recognize and speech-to-text calls are transcripts; speak, synthesize and text-to-speech calls are syntheses (`/speech-syntheses`).
- Duplicates merged: Wispr.

### Energy and Utilities (`energy`)

95 providers measured, 25 crosswalks, [api-commons/energy](https://github.com/api-commons/energy).

- `meter` (15 providers): `id`
- `meter_reading` (8 providers): `end_at`, `start_at`, `unit`
- `utility_account` (5 providers): `id`, `created_at`

Findings:

- Eleven Australian retailers and regulators publish the same Consumer Data Right energy standard; counted once, the open market is thin. Meters agree only on id -- status, meter_type and number each reach a third of providers.
- Meter readings agree on start and end and unit: an interval with a unit is the shared shape, the value field is spelled differently by every provider.

Decisions:

- The CDR energy standard counts as one voice (au-cdr-energy), as the banking standard did; without that, its servicepoint vocabulary would be the core of the context.
- Bills were dropped: two readable schemas share nothing. Utility accounts stay at extended, with the meter they belong to as the required parent.

### Solar and Energy Storage (`solar`)

53 providers measured, 13 crosswalks, measured and recorded as `thin`, not published.

- `site` (9 providers): `id`, `address`, `status`
- `device` (2 providers): no core
- `energy_production` (8 providers): `id`

Findings:

- Distributed energy is not yet published in a common shape: in a 53-provider cohort, sites agree on id, address and status at 8 readable providers, production telemetry shares nothing but an id, and devices appear at two. Each monitoring platform reports energy in its own time-series form.

Decisions:

- Measured and not published: recorded as `thin`, with its findings.
- Revisit when the catalog carries the larger inverter and battery platforms' specs.

### Agriculture (`agriculture`)

47 providers measured, 9 crosswalks, [api-commons/agriculture](https://github.com/api-commons/agriculture).

- `farm` (5 providers): `id`, `name`
- `field` (7 providers): `boundary`, `id`, `name`, `area`

Findings:

- The field is the farm-data resource the market shares: fields agree on id, name, boundary and area, the boundary as GeoJSON geometry and the area in acres or hectares.
- Farms agree only on id and name; they are the container, and the data lives on the field.

Decisions:

- Area keeps the provider's unit beside it rather than choosing acres or hectares; the market splits by region.
- Crops, seasons and field operations were measured and dropped; they are the next agriculture revision once the catalog carries more farm-management specs.

### Automotive (`automotive`)

99 providers measured, 36 crosswalks, [api-commons/automotive](https://github.com/api-commons/automotive).

- `vehicle` (36 providers): `id`, `make`, `model`
- `vehicle_location` (8 providers): `latitude`, `longitude`, `id`, `recorded_at`

Findings:

- Vehicles agree on id, make and model; year reaches 46%. The VIN is how the market addresses a vehicle -- it sits in the path (/vin/{vin}) -- far more often than it appears as a property.
- Vehicle locations agree on latitude, longitude and recorded_at: a timestamped point, with latitude and longitude at 88%.

Decisions:

- vin is kept as the canonical name for the identification number, though below the core line, because it is the vehicle's key across the market.
- Odometer readings and dealer listings were measured and dropped; each provider shapes them its own way.

### Mobility and Ride-Hailing (`mobility`)

54 providers measured, 13 crosswalks, [api-commons/mobility](https://github.com/api-commons/mobility).

- `station` (13 providers): `id`, `latitude`, `name`
- `mobility_vehicle` (3 providers): `battery_level`, `id`, `is_disabled`, `is_reserved`, `latitude`, `longitude`, `max_range_meters`, `propulsion_type`, `vehicle_type`

Findings:

- Stations agree on id, latitude and name, with longitude at 46% -- the open bike-share feed format (station_information with lat, lon and capacity) carries most of that agreement.
- Shared vehicles are published by fleets that follow that same feed format and agree almost completely: id, latitude, longitude, vehicle_type, propulsion_type, battery_level, is_reserved and is_disabled.

Decisions:

- The feed format's station_id and bike_id map to id; lat and lon map to latitude and longitude.
- Trips were measured and dropped: ride-hailing and transit trips share no property at half the providers.

### Parking (`parking`)

32 providers measured, 5 crosswalks, measured and recorded as `thin`, not published.

- `parking_facility` (2 providers): no core
- `parking_session` (0 providers): no core
- `parking_reservation` (4 providers): `status`

Findings:

- Parking is not published in a common shape: in a 32-provider cohort, one facility schema is readable, no parking sessions are exposed, and reservations at 4 providers share only a status.

Decisions:

- Measured and not published: recorded as `thin`, with its findings.

### Sports Data (`sports`)

64 providers measured, 38 crosswalks, [api-commons/sports](https://github.com/api-commons/sports).

- `league` (21 providers): `name`, `id`
- `team` (26 providers): `name`, `id`
- `player` (21 providers): `id`, `name`
- `game` (26 providers): `id`

Findings:

- Leagues, teams and players agree on id and name and on little else: team abbreviation reaches 33%, and player first_name, last_name and position each reach 47%.
- Games agree only on id; status is at 48% and start_at 35%. Home and away teams appear under a different name, nesting and score shape at nearly every provider -- the game is where sports data providers differ most.

Decisions:

- The market's word is kept per concept: league for competitions and tournaments, game for matches, fixtures and events.
- Odds and betting markets were left out of this pass; they are a sportsbook context of their own.

### Gaming (`gaming`)

73 providers measured, 26 crosswalks, [api-commons/gaming](https://github.com/api-commons/gaming).

- `game_title` (15 providers): `name`, `id`
- `player_profile` (7 providers): `id`, `player_id`, `name`, `username`
- `leaderboard` (15 providers): no core
- `achievement` (5 providers): `name`, `description`, `id`

Findings:

- Game platforms agree on the game title's id and name, and on player profiles' id, name and username; player_id appears beside id at the same providers, the platform's key next to the game's own.
- Leaderboards are widely exposed but share no core: rank reaches 42% and score 33%. Achievements agree on name, description and id.

Decisions:

- game_title, player_profile and game_match carry role names because game, player and match collide with the sports context.
- Matches and lobbies were measured and dropped; each game-server platform shapes a session its own way.

### Fitness and Wellness (`fitness`)

52 providers measured, 18 crosswalks, [api-commons/fitness](https://github.com/api-commons/fitness).

- `workout` (16 providers): `id`, `created_at`, `distance`, `workout_type`
- `sleep` (10 providers): `score`, `id`
- `daily_summary` (6 providers): `date`, `score`

Findings:

- Workouts agree on id, created_at, distance and workout_type; calories and duration reach 43%. The type of exercise is spelled type, sport_type or activity_type and is kept as workout_type.
- Sleep and daily summaries agree on a score -- the wearable's own 0-100 judgement -- before they agree on any measurement: sleep agrees on score and id, daily summaries on date and score.
- Before merging, one aggregator listed under three catalog names made a ten-property sleep core look like market agreement; folded into one company, it disappears.

Decisions:

- duplicates must be written canon: [merged slugs]; build.py now refuses any other form, because a bare string merged nothing and reported nothing.
- Body measurements and fitness classes were measured and dropped.

### Genomics and Clinical Trials (`genomics`)

101 providers measured, 27 crosswalks, measured and recorded as `thin`, not published.

- `gene` (5 providers): no core
- `variant` (5 providers): no core
- `sample` (10 providers): `created_at`, `updated_at`
- `sequencing_run` (1 providers): no core
- `dataset` (13 providers): `name`

Findings:

- Genomics is not published in a common shape: in a 101-provider cohort, genes and variants appear at 5 providers each with no shared property, samples agree only on timestamps, and datasets only on a name. Research genomics is exchanged through GA4GH protocols and file formats (VCF, BAM) more than through resource schemas.

Decisions:

- Measured and not published: recorded as `thin`, with its findings.
- A GA4GH standards pass (Beacon, htsget, DRS) is the better route than a market census here.

