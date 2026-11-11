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
Measured across Customer Relationship Management, Help Desk and Ticketing, Commerce, Payments, Card Issuing, Billing and Invoicing, Messaging (Email, SMS, Chat), Calendars and Scheduling, People and HR, Payroll, Recruiting, Files and Documents, Identity and Users, E-Signature, Accounting, Banking, Lending, Insurance, Property Management, Travel and Lodging, Shipping, Fleet and Telematics, Project Management, Content Management, Email Marketing, Advertising, Product Analytics, Observability, Incident Management, CI/CD, Source Control, Cloud Infrastructure, Vulnerability Management, Identity Verification, Healthcare, Learning Management, Food Ordering, Point of Sale, Loyalty, Events and Ticketing, Video, Maps and Geocoding, Weather, Market Data, Trading, Crypto Wallets, Search, Forms and Surveys, Reviews, Social Media, Telephony, Contact Center, Workflow Automation, Knowledge Base, Procurement, IoT Devices, EV Charging, Webhooks, Audit Logs, Feature Flags, API Management, Secrets Management, DNS and Domains, CDN and Edge, AI Agents, Document AI, Data Enrichment, Tax, Legal Practice, Contract Lifecycle, Expense Management, Time Tracking, Field Service, IT Asset Management, ITSM Change and CMDB, Customer Success, Sales Engagement, Configure, Price, Quote, Affiliates and Partners, Nonprofit Fundraising, Membership, Marketplace, Returns, Warehouse Management, Freight and TMS, Gift Cards, Subscription Commerce, Privacy and Consent, Background Checks, Open Data Catalogs, Research Repositories, News, Music, Podcasts, Books and Publishing, Translation and Localization, Speech and Transcription, Energy and Utilities, Solar and Energy Storage, Agriculture, Automotive, Mobility and Ride-Hailing, Parking, Sports Data, Gaming, Fitness and Wellness, Genomics and Clinical Trials, Blockchain Data, DeFi Protocols, NFTs and Digital Collectibles, Crypto Exchanges, Image and Video Generation, Computer Vision, Natural Language Processing, Chatbots and Conversational AI, Vector Search and RAG, MLOps and Model Registry, AI Inference and Deployments, MCP Servers and Agent Registries, Databases, Data Integration and ETL, Event Streaming and Queues, Data Catalogs and Governance, Business Intelligence, Data Warehouses and Query, Web Scraping and Crawling, SEO, Software Testing, Kubernetes and Clusters, Container Registries, Serverless Functions, Cloud Cost and FinOps, Threat Intelligence, Threat Detection and SIEM, Zero Trust and Device Posture, Fraud Prevention, Object Storage, Design Tools, Foreign Exchange, Payouts and Cross-Border Payments, Personal Finance, Wealth and Asset Management, Risk and Compliance, ESG and Carbon Accounting, Asset Tokenization, Agentic Commerce, Clinical Trials, Drug Discovery, Lab Diagnostics, Medical Imaging, Pharmacy and Prescriptions, Behavioral Health, Patient Engagement, Medical Devices, Telecommunications, IoT Connectivity and SIMs, Satellite and Earth Observation, Drones, Maritime and Vessels, Aviation and Flights, Oil and Gas, Mining, Construction, Manufacturing, Industrial Automation, Supply Chain Visibility, Inventory Management, Wholesale and B2B Ordering, Grocery, Nutrition and Recipes, Restaurants and Menus, Beauty and Salons, Fashion and Apparel, Government Services and Permits, Public Spending and Grants, Legislation, Courts and Case Records, Elections, Higher Education, Course Catalogs, Staffing, Employee Benefits, Job Boards, Real Estate Listings, Mortgages, Climate and Emissions, Sustainability Reporting, Robotics, Autonomous Vehicles, 3D Printing, Live Streaming, Movies and TV, Digital Asset Management, Content Moderation, Personalization and Recommendations, Pricing and Price Lists, Mobile Attribution, Online Communities, Notes and Productivity, Whiteboards and Collaboration, URL Shortening and Links, QR Codes, Print and Mail, Photos and Stock Media, Pets and Veterinary, Hotels and Property Systems, Churches and Congregations: 7574 providers.

| Rule | Measured (providers) | Severity |
| --- | --- | --- |
| path segments kebab-case | lowercase 7106; multi-word kebab 3761 / snake 1966 / camel 1431 | warn |
| timestamps end in `_at` | `_at` 1566 / bare `created` 750 / `_time`, `_date`, `on` 426 | warn |
| collections are plural | plural 4362 / singular 2467 | info |
| properties snake_case | multi-word snake 2266 / camel 2292 | info |
| references `<resource>_id` | `_id` 1644 / `...Id` 1748 | info |
| path params snake_case | `{id}` 4149; multi-word camel 3161 / snake 2368 | info |
| query params snake_case | snake 3031 / camel 3054 | info |
| paging is `limit` + `cursor` | limit 2805, page 1973, offset 1555, cursor 769 | info |
<!-- /commons:naming -->

The ruleset is also proposed to OpenLint: [openlint/rules#2](https://github.com/openlint/rules/pull/2).

## Bounded contexts

[contexts.yml](contexts.yml) is the registry and the order of work.

<!-- commons:contexts -->
| Context | Repo | Status | Providers measured | Crosswalks |
| --- | --- | --- | ---: | ---: |
| Customer Relationship Management | [api-commons/crm](https://github.com/api-commons/crm) | published | 177 | 112 |
| Help Desk and Ticketing | [api-commons/ticketing](https://github.com/api-commons/ticketing) | published | 77 | 48 |
| Commerce | [api-commons/commerce](https://github.com/api-commons/commerce) | published | 401 | 254 |
| Payments | [api-commons/payments](https://github.com/api-commons/payments) | published | 692 | 436 |
| Card Issuing | [api-commons/card-issuing](https://github.com/api-commons/card-issuing) | published | 740 | 65 |
| Billing and Invoicing | [api-commons/billing](https://github.com/api-commons/billing) | published | 837 | 270 |
| Messaging (Email, SMS, Chat) | [api-commons/messaging](https://github.com/api-commons/messaging) | built | 365 | 198 |
| Calendars and Scheduling | [api-commons/scheduling](https://github.com/api-commons/scheduling) | built | 112 | 38 |
| People and HR | [api-commons/hris](https://github.com/api-commons/hris) | built | 171 | 61 |
| Payroll | [api-commons/payroll](https://github.com/api-commons/payroll) | built | 192 | 27 |
| Recruiting | [api-commons/recruiting](https://github.com/api-commons/recruiting) | built | 67 | 32 |
| Files and Documents | [api-commons/files](https://github.com/api-commons/files) | built | 133 | 51 |
| Identity and Users | [api-commons/identity](https://github.com/api-commons/identity) | built | 443 | 185 |
| E-Signature | [api-commons/e-signature](https://github.com/api-commons/e-signature) | built | 72 | 35 |
| Accounting | [api-commons/accounting](https://github.com/api-commons/accounting) | built | 139 | 67 |
| Banking | [api-commons/banking](https://github.com/api-commons/banking) | built | 315 | 211 |
| Lending | [api-commons/lending](https://github.com/api-commons/lending) | built | 134 | 14 |
| Insurance | [api-commons/insurance](https://github.com/api-commons/insurance) | built | 143 | 47 |
| Property Management | [api-commons/property-management](https://github.com/api-commons/property-management) | built | 143 | 62 |
| Travel and Lodging | [api-commons/travel](https://github.com/api-commons/travel) | built | 184 | 67 |
| Shipping | [api-commons/shipping](https://github.com/api-commons/shipping) | built | 258 | 99 |
| Fleet and Telematics | [api-commons/fleet](https://github.com/api-commons/fleet) | built | 85 | 29 |
| Project Management | [api-commons/project-management](https://github.com/api-commons/project-management) | built | 95 | 43 |
| Content Management | [api-commons/cms](https://github.com/api-commons/cms) | built | 73 | 36 |
| Email Marketing | [api-commons/email-marketing](https://github.com/api-commons/email-marketing) | built | 102 | 51 |
| Advertising | [api-commons/advertising](https://github.com/api-commons/advertising) | built | 134 | 33 |
| Product Analytics | [api-commons/product-analytics](https://github.com/api-commons/product-analytics) | built | 80 | 40 |
| Observability | [api-commons/observability](https://github.com/api-commons/observability) | built | 279 | 104 |
| Incident Management | [api-commons/incident-management](https://github.com/api-commons/incident-management) | built | 75 | 28 |
| CI/CD | [api-commons/ci-cd](https://github.com/api-commons/ci-cd) | built | 241 | 81 |
| Source Control | [api-commons/source-control](https://github.com/api-commons/source-control) | built | 242 | 49 |
| Cloud Infrastructure | [api-commons/cloud-infrastructure](https://github.com/api-commons/cloud-infrastructure) | built | 384 | 88 |
| Vulnerability Management | [api-commons/vulnerability-management](https://github.com/api-commons/vulnerability-management) | built | 111 | 54 |
| Identity Verification | [api-commons/identity-verification](https://github.com/api-commons/identity-verification) | built | 173 | 31 |
| Healthcare | [api-commons/healthcare](https://github.com/api-commons/healthcare) | built | 259 | 69 |
| Learning Management | [api-commons/lms](https://github.com/api-commons/lms) | built | 57 | 22 |
| Food Ordering | [api-commons/food-ordering](https://github.com/api-commons/food-ordering) | built | 77 | 35 |
| Point of Sale | [api-commons/point-of-sale](https://github.com/api-commons/point-of-sale) | built | 84 | 20 |
| Loyalty | [api-commons/loyalty](https://github.com/api-commons/loyalty) | built | 77 | 17 |
| Events and Ticketing | [api-commons/events](https://github.com/api-commons/events) | built | 123 | 26 |
| Video | [api-commons/video](https://github.com/api-commons/video) | built | 163 | 51 |
| Maps and Geocoding | [api-commons/maps](https://github.com/api-commons/maps) | built | 193 | 45 |
| Weather | [api-commons/weather](https://github.com/api-commons/weather) | built | 54 | 27 |
| Market Data | [api-commons/market-data](https://github.com/api-commons/market-data) | built | 237 | 95 |
| Trading | [api-commons/trading](https://github.com/api-commons/trading) | built | 174 | 51 |
| Crypto Wallets | [api-commons/crypto-wallets](https://github.com/api-commons/crypto-wallets) | built | 345 | 75 |
| Search | [api-commons/search](https://github.com/api-commons/search) | built | 187 | 112 |
| Forms and Surveys | [api-commons/forms](https://github.com/api-commons/forms) | built | 93 | 40 |
| Reviews | [api-commons/reviews](https://github.com/api-commons/reviews) | built | 42 | 26 |
| Social Media | [api-commons/social-media](https://github.com/api-commons/social-media) | built | 118 | 53 |
| Telephony | [api-commons/telephony](https://github.com/api-commons/telephony) | built | 146 | 49 |
| Contact Center | [api-commons/contact-center](https://github.com/api-commons/contact-center) | built | 93 | 10 |
| Workflow Automation | [api-commons/workflow-automation](https://github.com/api-commons/workflow-automation) | built | 348 | 73 |
| Knowledge Base | [api-commons/knowledge-base](https://github.com/api-commons/knowledge-base) | built | 146 | 21 |
| Procurement | [api-commons/procurement](https://github.com/api-commons/procurement) | built | 126 | 35 |
| IoT Devices | [api-commons/iot](https://github.com/api-commons/iot) | built | 195 | 69 |
| EV Charging | [api-commons/ev-charging](https://github.com/api-commons/ev-charging) | built | 41 | 4 |
| Webhooks | [api-commons/webhooks](https://github.com/api-commons/webhooks) | built | 487 | 202 |
| Audit Logs | [api-commons/audit-logs](https://github.com/api-commons/audit-logs) | built | 844 | 61 |
| Feature Flags | [api-commons/feature-flags](https://github.com/api-commons/feature-flags) | built | 36 | 19 |
| API Management | [api-commons/api-management](https://github.com/api-commons/api-management) | built | 135 | 23 |
| Secrets Management | [api-commons/secrets](https://github.com/api-commons/secrets) | built | 46 | 11 |
| DNS and Domains | [api-commons/dns](https://github.com/api-commons/dns) | built | 69 | 28 |
| CDN and Edge | [api-commons/cdn](https://github.com/api-commons/cdn) | built | 77 | 17 |
| AI Agents | [api-commons/ai-agents](https://github.com/api-commons/ai-agents) | built | 680 | 156 |
| Document AI | [api-commons/document-ai](https://github.com/api-commons/document-ai) | built | 132 | 35 |
| Data Enrichment | [api-commons/data-enrichment](https://github.com/api-commons/data-enrichment) | built | 137 | 47 |
| Tax | [api-commons/tax](https://github.com/api-commons/tax) | built | 51 | 13 |
| Legal Practice | [api-commons/legal](https://github.com/api-commons/legal) | built | 79 | 10 |
| Contract Lifecycle | [api-commons/contracts](https://github.com/api-commons/contracts) | built | 45 | 10 |
| Expense Management | [api-commons/expenses](https://github.com/api-commons/expenses) | built | 58 | 11 |
| Time Tracking | [api-commons/time-tracking](https://github.com/api-commons/time-tracking) | built | 80 | 20 |
| Field Service | [api-commons/field-service](https://github.com/api-commons/field-service) | built | 50 | 21 |
| IT Asset Management | [api-commons/it-assets](https://github.com/api-commons/it-assets) | built | 54 | 31 |
| ITSM Change and CMDB | [api-commons/cmdb](https://github.com/api-commons/cmdb) | built | 32 | 4 |
| Customer Success | -- | thin | 65 | 14 |
| Sales Engagement | [api-commons/sales-engagement](https://github.com/api-commons/sales-engagement) | built | 61 | 12 |
| Configure, Price, Quote | [api-commons/cpq](https://github.com/api-commons/cpq) | built | 46 | 16 |
| Affiliates and Partners | [api-commons/affiliates](https://github.com/api-commons/affiliates) | built | 28 | 6 |
| Nonprofit Fundraising | [api-commons/fundraising](https://github.com/api-commons/fundraising) | built | 50 | 14 |
| Membership | [api-commons/membership](https://github.com/api-commons/membership) | built | 26 | 9 |
| Marketplace | -- | thin | 468 | 14 |
| Returns | [api-commons/returns](https://github.com/api-commons/returns) | built | 370 | 32 |
| Warehouse Management | [api-commons/warehouse](https://github.com/api-commons/warehouse) | built | 75 | 13 |
| Freight and TMS | [api-commons/freight](https://github.com/api-commons/freight) | built | 205 | 12 |
| Gift Cards | -- | thin | 54 | 5 |
| Subscription Commerce | -- | thin | 413 | 6 |
| Privacy and Consent | -- | thin | 113 | 8 |
| Background Checks | -- | thin | 16 | 3 |
| Open Data Catalogs | [api-commons/open-data-catalogs](https://github.com/api-commons/open-data-catalogs) | built | 276 | 33 |
| Research Repositories | [api-commons/research-repositories](https://github.com/api-commons/research-repositories) | built | 123 | 21 |
| News | [api-commons/news](https://github.com/api-commons/news) | built | 73 | 31 |
| Music | [api-commons/music](https://github.com/api-commons/music) | built | 45 | 22 |
| Podcasts | [api-commons/podcasts](https://github.com/api-commons/podcasts) | built | 88 | 13 |
| Books and Publishing | [api-commons/books](https://github.com/api-commons/books) | built | 132 | 12 |
| Translation and Localization | [api-commons/localization](https://github.com/api-commons/localization) | built | 49 | 27 |
| Speech and Transcription | [api-commons/speech](https://github.com/api-commons/speech) | built | 131 | 67 |
| Energy and Utilities | [api-commons/energy](https://github.com/api-commons/energy) | built | 95 | 25 |
| Solar and Energy Storage | -- | thin | 53 | 13 |
| Agriculture | [api-commons/agriculture](https://github.com/api-commons/agriculture) | built | 47 | 9 |
| Automotive | [api-commons/automotive](https://github.com/api-commons/automotive) | built | 99 | 36 |
| Mobility and Ride-Hailing | [api-commons/mobility](https://github.com/api-commons/mobility) | built | 54 | 13 |
| Parking | -- | thin | 32 | 5 |
| Sports Data | [api-commons/sports](https://github.com/api-commons/sports) | built | 64 | 38 |
| Gaming | [api-commons/gaming](https://github.com/api-commons/gaming) | built | 73 | 26 |
| Fitness and Wellness | [api-commons/fitness](https://github.com/api-commons/fitness) | built | 52 | 18 |
| Genomics and Clinical Trials | -- | thin | 101 | 27 |
| Blockchain Data | [api-commons/blockchain-data](https://github.com/api-commons/blockchain-data) | built | 374 | 109 |
| DeFi Protocols | -- | thin | 154 | 74 |
| NFTs and Digital Collectibles | [api-commons/nfts](https://github.com/api-commons/nfts) | built | 47 | 25 |
| Crypto Exchanges | [api-commons/crypto-exchanges](https://github.com/api-commons/crypto-exchanges) | built | 288 | 55 |
| Image and Video Generation | [api-commons/image-generation](https://github.com/api-commons/image-generation) | built | 148 | 70 |
| Computer Vision | -- | thin | 73 | 24 |
| Natural Language Processing | -- | thin | 91 | 34 |
| Chatbots and Conversational AI | [api-commons/chatbots](https://github.com/api-commons/chatbots) | built | 147 | 69 |
| Vector Search and RAG | [api-commons/vector-search](https://github.com/api-commons/vector-search) | built | 125 | 26 |
| MLOps and Model Registry | [api-commons/mlops](https://github.com/api-commons/mlops) | built | 342 | 126 |
| AI Inference and Deployments | [api-commons/ai-inference](https://github.com/api-commons/ai-inference) | built | 172 | 41 |
| MCP Servers and Agent Registries | -- | thin | 926 | 38 |
| Databases | [api-commons/databases](https://github.com/api-commons/databases) | built | 184 | 73 |
| Data Integration and ETL | [api-commons/etl](https://github.com/api-commons/etl) | built | 101 | 47 |
| Event Streaming and Queues | -- | thin | 421 | 44 |
| Data Catalogs and Governance | [api-commons/data-governance](https://github.com/api-commons/data-governance) | built | 94 | 27 |
| Business Intelligence | [api-commons/business-intelligence](https://github.com/api-commons/business-intelligence) | built | 159 | 42 |
| Data Warehouses and Query | -- | thin | 112 | 39 |
| Web Scraping and Crawling | [api-commons/web-scraping](https://github.com/api-commons/web-scraping) | built | 109 | 50 |
| SEO | -- | thin | 51 | 13 |
| Software Testing | [api-commons/testing](https://github.com/api-commons/testing) | built | 95 | 32 |
| Kubernetes and Clusters | -- | thin | 296 | 71 |
| Container Registries | -- | thin | 104 | 22 |
| Serverless Functions | [api-commons/serverless](https://github.com/api-commons/serverless) | built | 136 | 22 |
| Cloud Cost and FinOps | [api-commons/finops](https://github.com/api-commons/finops) | built | 81 | 21 |
| Threat Intelligence | -- | thin | 135 | 35 |
| Threat Detection and SIEM | [api-commons/threat-detection](https://github.com/api-commons/threat-detection) | built | 60 | 25 |
| Zero Trust and Device Posture | -- | thin | 103 | 51 |
| Fraud Prevention | -- | thin | 173 | 48 |
| Object Storage | [api-commons/object-storage](https://github.com/api-commons/object-storage) | built | 121 | 21 |
| Design Tools | -- | thin | 27 | 8 |
| Foreign Exchange | [api-commons/foreign-exchange](https://github.com/api-commons/foreign-exchange) | built | 65 | 30 |
| Payouts and Cross-Border Payments | [api-commons/payouts](https://github.com/api-commons/payouts) | built | 100 | 62 |
| Personal Finance | [api-commons/personal-finance](https://github.com/api-commons/personal-finance) | built | 133 | 34 |
| Wealth and Asset Management | -- | thin | 85 | 18 |
| Risk and Compliance | -- | thin | 336 | 57 |
| ESG and Carbon Accounting | -- | thin | 79 | 11 |
| Asset Tokenization | -- | thin | 113 | 52 |
| Agentic Commerce | -- | thin | 160 | 34 |
| Clinical Trials | -- | thin | 40 | 4 |
| Drug Discovery | -- | thin | 59 | 7 |
| Lab Diagnostics | -- | thin | 23 | 9 |
| Medical Imaging | -- | thin | 11 | 2 |
| Pharmacy and Prescriptions | -- | thin | 45 | 9 |
| Behavioral Health | -- | thin | 17 | 7 |
| Patient Engagement | -- | thin | 57 | 12 |
| Medical Devices | -- | thin | 18 | 4 |
| Telecommunications | -- | thin | 95 | 20 |
| IoT Connectivity and SIMs | [api-commons/iot-connectivity](https://github.com/api-commons/iot-connectivity) | built | 35 | 10 |
| Satellite and Earth Observation | -- | thin | 170 | 61 |
| Drones | -- | thin | 30 | 4 |
| Maritime and Vessels | -- | thin | 228 | 25 |
| Aviation and Flights | [api-commons/aviation](https://github.com/api-commons/aviation) | built | 56 | 17 |
| Oil and Gas | -- | thin | 19 | 3 |
| Mining | -- | thin | 10 | 1 |
| Construction | -- | thin | 54 | 28 |
| Manufacturing | -- | thin | 82 | 24 |
| Industrial Automation | [api-commons/industrial-automation](https://github.com/api-commons/industrial-automation) | built | 30 | 11 |
| Supply Chain Visibility | -- | thin | 280 | 55 |
| Inventory Management | -- | thin | 122 | 54 |
| Wholesale and B2B Ordering | -- | thin | 151 | 31 |
| Grocery | -- | thin | 11 | 3 |
| Nutrition and Recipes | [api-commons/nutrition](https://github.com/api-commons/nutrition) | built | 62 | 24 |
| Restaurants and Menus | -- | thin | 106 | 31 |
| Beauty and Salons | -- | thin | 21 | 3 |
| Fashion and Apparel | -- | thin | 157 | 78 |
| Government Services and Permits | -- | thin | 208 | 8 |
| Public Spending and Grants | -- | thin | 117 | 9 |
| Legislation | -- | thin | 129 | 15 |
| Courts and Case Records | -- | thin | 22 | 3 |
| Elections | -- | thin | 39 | 5 |
| Higher Education | -- | thin | 164 | 27 |
| Course Catalogs | -- | thin | 91 | 30 |
| Staffing | [api-commons/staffing](https://github.com/api-commons/staffing) | built | 51 | 12 |
| Employee Benefits | [api-commons/employee-benefits](https://github.com/api-commons/employee-benefits) | built | 37 | 18 |
| Job Boards | [api-commons/job-boards](https://github.com/api-commons/job-boards) | built | 33 | 23 |
| Real Estate Listings | -- | thin | 131 | 54 |
| Mortgages | -- | thin | 44 | 14 |
| Climate and Emissions | -- | thin | 79 | 16 |
| Sustainability Reporting | -- | thin | 68 | 19 |
| Robotics | -- | thin | 25 | 1 |
| Autonomous Vehicles | -- | thin | 6 | 0 |
| 3D Printing | -- | thin | 19 | 10 |
| Live Streaming | -- | thin | 170 | 43 |
| Movies and TV | [api-commons/movies](https://github.com/api-commons/movies) | built | 203 | 35 |
| Digital Asset Management | [api-commons/digital-asset-management](https://github.com/api-commons/digital-asset-management) | built | 82 | 42 |
| Content Moderation | -- | thin | 32 | 8 |
| Personalization and Recommendations | -- | thin | 107 | 35 |
| Pricing and Price Lists | -- | thin | 66 | 11 |
| Mobile Attribution | -- | thin | 39 | 5 |
| Online Communities | -- | thin | 68 | 21 |
| Notes and Productivity | [api-commons/productivity](https://github.com/api-commons/productivity) | built | 171 | 49 |
| Whiteboards and Collaboration | -- | thin | 122 | 5 |
| URL Shortening and Links | -- | thin | 6 | 3 |
| QR Codes | -- | thin | 11 | 5 |
| Print and Mail | -- | thin | 31 | 15 |
| Photos and Stock Media | -- | thin | 56 | 26 |
| Pets and Veterinary | -- | thin | 7 | 5 |
| Hotels and Property Systems | -- | thin | 86 | 18 |
| Churches and Congregations | -- | thin | 4 | 4 |

Planned, in order: .
<!-- /commons:contexts -->

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
   is looked at by hand. Wrong ones go under `exclude:` with a one-line reason. When the
   same segment means different things by where it sits, qualify it instead of dropping it:
   `cards@customers|users` counts only beneath those parents, `cards!customers` never beneath
   them. When a generic segment (`users`, `transactions`) is this concept only at providers
   that also expose another one, say `requires: [card]`. Run
   `scripts/duplicates.py`: the same company listed twice goes under `duplicates:` (merged,
   not dropped); different companies on one standard go under `shared_specs:`.
5. **Decide in public.** Every naming call that is a choice rather than a count is written in
   the context README's Decisions section, with the numbers that informed it. The default:
   follow the measured majority unless the majority word is ambiguous across contexts.

Then re-run `naming-evidence.py`: it re-measures naming, renders the ruleset and the tables
in this README, and writes [evidence/unreadable-specs.yml](evidence/unreadable-specs.yml) --
every harvested spec the census could not parse even after tolerating control characters,
JSON trailing commas and YAML's `=` tag. That file is a work list for re-profiling those
providers, not a finding about the market.

`scripts/check-findings.py` re-checks every context's prose findings against its profile --
the properties a finding says are core, the shares and provider counts it cites, and that any
provider it names has a crosswalk -- and `context.sh finish` refuses to commit when one has
drifted. Findings are the one hand-written part of a context that cites measurements, and in
the first batch about twenty went stale as the census improved.

The census also reads an action verb after a collection (`/mail/send`, `/email/batch`) as a
write to that collection.

## Decisions that cross contexts

- **snake_case.** Measured across every context the market is split down the middle on
  multi-word names (see the naming table). The count cannot decide it, so the reasons do:
  snake_case has one spelling for an acronym (`customer_id`, never `customerID` or
  `customerId`), it is the form the census already normalises every name to, and a camelCase
  provider loses nothing because the crosswalk keeps its own spelling. **Revisit when either
  side reaches 60% of the multi-word providers** on properties or on references --
  `naming-evidence.py` prints a warning when it does. After 57 contexts and 5,552 providers the
  split has held: properties 51% camelCase, references 53% `...Id` -- below the trigger, and
  steady since fintech joined at context four.
- **A concept moves to the context that owns it.** Commerce found `/checkout` to be a
  payment session and handed `checkout_session` to payments; payments found `/cards` to be
  issued cards and registered card issuing as a context. Concepts are not duplicated across
  contexts to make one look complete. A hand-over can be wrong in both directions: payments
  dropped `/cards` as issued cards, and card issuing then showed that `/customers/{id}/cards`
  are saved payment methods -- so the segment is now split by its parent between the two.
- **Duplicates merge; shared specifications count once.** One company listed twice is merged
  (`duplicates:`). Different companies republishing one specification -- the UK Open Banking
  standard -- each stay an adopter with a crosswalk but are one voice in the vocabulary
  (`shared_specs:`). `scripts/duplicates.py` finds both by byte-identical specs; a person
  decides which is which.

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

**The tools.** `scripts/lock-check.py [<ctx> ...]` reports the four criteria per context
(criterion 3 is hub-wide: `LOCK_RULESET_ACCEPTED=1` now that openlint/rules#2 is merged).
`scripts/release.py <ctx> <version>` freezes the contract at `schema/v<major>/`, records
`release:` in concepts.yml, writes CHANGELOG.md, commits and tags; it refuses a context that is
not ready unless `RELEASE_OVERRIDE='<reason>'` records the exception. After a release every
build stamps the released version (status `stable`) and keeps re-measuring the live `schema/`;
`release.py <ctx> --diff` lists promotions (next minor) and demotions (next major). Builds never
touch `schema/v<major>/`.

**Lock queue.** Source control, trading, ticketing and identity are reviewed and findings-clean.
They wait on criterion 1 (the method changed on 2026-11-11 with the standards layer, and the
catalog repair will trigger a re-measure) and criterion 4 (the apis.io build of 2026-11-13).
Run `lock-check.py` after both; the first context to show READY is the first 1.0.0.

## Linking both ways

- **Commons -> APIs.io.** Every `adopters.yml` entry and every crosswalk links the provider's
  APIs.io page, and every crosswalk cites the harvested spec and the operations it read.
- **APIs.io -> Commons** *(next)*. Provider, tag, capability and area pages render the
  common concepts a provider maps to, read from each context's `adopters.yml` -- the same
  way they read every other generated rollup. Nothing is written into provider repos.

## License

Artifacts CC BY-NC-SA 4.0 ([LICENSE](LICENSE)); code Apache 2.0 ([LICENSE-CODE](LICENSE-CODE)).
