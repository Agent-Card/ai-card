# Agent Registry APIs Spec

## Summary

This spec document outlines the design for the Agent Registry's list and search API standards for the agentic AI ecosystem. It proposes two distinct endpoints: a simple **List API** (`GET /agents`) for browsing and filtering, and a powerful **Search API** (`POST /agents/search`) for complex keyword and semantic queries.

* **List API (`GET /agents`)**: Designed for fast, cacheable browsing and simple filtering (e.g., by location, language, visibility, category, creation/update dates, name contains). It supports sorting by `name`, `created_at`, or `updated_at`, and pagination. It does not support keyword search, semantic queries, or relevance-based sorting.
* **Search API (`POST /agents/search`)**: Designed for complex discovery, using a JSON body to support advanced query types. It is a superset of the List API, supporting all its filters plus full-text keyword search and semantic vector search. It also supports sorting by relevance.

Both APIs allow filtering agents based on the user's authentication status (public users see public agents; authenticated users see public and authorized private agents).

## Motivation

Define a standard Agent registry API that supports both simple, fast browsing and advanced, complex discovery use cases.

## Static AI Catalog vs. Agent Registry APIs

While both serve as directories for AI agents, they are built for fundamentally different scales and use cases:

* **Static AI Catalog:** A simpler approach best suited for a smaller number of agents. These are typically hosted and curated by one specific company or community for manual, human-driven discovery.
* **Agent Registry APIs:** Built for large-scale, federated ecosystems. This approach emphasizes robust identity and trust verification across multiple organizations, offering dynamic search and query capabilities designed for programmatic, Agent-to-Agent (A2A) orchestration.

| Feature | Static AI Catalog | Agent Registry APIs |
| --- | --- | --- |
| **Scale & Scope** | Smaller, curated lists | Large, federated ecosystems |
| **Hosting & Ownership** | Single company or community | Federated across multiple organizations |
| **Discovery Model** | Simple, static manual browsing | Dynamic programmatic search and query |
| **Identity & Trust** | Implicit or statically managed | Explicit, verified identity and trust states |

## Proposal

We propose specialized Search Interfaces to separate the List and Search endpoints to optimize for different read patterns.

**Base URL**: Format like: `https://<registry-url>/v1/org/<org-id>/group/<group-id>`
The discovery and search endpoints would be `<Base_URL>/agents` and `<Base_URL>/agents/search`.

### 1. List API (`GET /agents`)

This endpoint is designed for fast, cacheable, and simple browsing of the registry. It supports standard filtering, sorting, and pagination via URL query parameters.

* **Method:** `GET`
* **Purpose:** Browsing, simple filtering (e.g., "Show me all public agents in the US").
* **Key Features:** Highly cacheable, strictly RESTful.
* **Limitations:** Does NOT support `keyword_search`, `semantic_query`, or sorting by relevance.

### 2. Search API (`POST /agents/search`)

This endpoint is designed for complex discovery. It uses a `POST` request with a JSON body to support advanced query types that may be too complex or sensitive for URL parameters.

* **Method:** `POST`
* **Purpose:** Complex discovery (e.g., "Find agents that can help me buy stocks based on historical analysis and trends prediction").
* **Key Features:** Supports full-text keywords, semantic vector search, and complex filtering.
* **Capability:** It is a **functional superset** of the List API; it supports all the filters available in the List API plus advanced search features. **Note**: The List API is the canonical source for a guaranteed, exhaustive data set, and search API results can’t guarantee the same instantaneous completeness/consistency as List APIs. It’s optimized for relevance based on the search/queries.

### Authentication & Visibility (Applies to Both APIs)

Agents returned are **automatically filtered** based on the user's authentication status.

* **Public Users:** Only agents marked as public are returned.
* **Authenticated Users (with valid `Authorization` header):** Returns public agents *plus* all private agents the user (or their organization) has permission to access.
* An authenticated user should see the **exact same set of agents** based on their granted permissions, whether they call `GET /agents` or `POST /agents/search`. The visibility logic (public agents + authorized private agents) applies symmetrically to both.

---

## Request Models

### 1) List API Request (`GET /agents`)

Controlled entirely via query parameters.

**Example:** `GET /agents?filter=location=US-East-1&orderBy=created_at&pageSize=20`

| Parameter Group | Parameter Name | Type | Description |
| --- | --- | --- | --- |
| **Filter** | `filter` | string | Filter used to filter agents to return using EBNF formats. If no filter is specified then all agents from the search result will be returned. Filter expressions can be used to restrict results based upon name, location, language, etc., where the operators **=**, **NOT**, **AND** and **OR** can be used along with the suffix wildcard symbol `*`. |
| **Sort** | `orderBy` | string | Optional. A comma-separated list of fields specifying the sorting order of the results. The default order is ascending. Add `DESC` after the field name to indicate descending order. For example: `name, created_at, updated_at`. |
| **Page** | `pageSize` | integer | Max results (default: 20, max: 100). |
|  | `pageToken` | string | Pagination token. |

### 2) Search API Request (`POST /agents/search`)

Controlled via a structured JSON body.

```json
{
  "searchString": "string", // Search string, it could be either keywords or semantic based search across all fields 
  "searchType": "enum(keywords|semantic)", // default: keywords
  "filter": "string", // Format is the same as in List. Defines hard constraints applied at the index level to filter candidates prior to relevance scoring.
  "orderBy": "string", // default: relevance. order by string same as in List
  "pageSize": 20, // max: 100
  "pageToken": "string"
}

```

---

## Response Models (Shared by Both APIs)

### 1) Paginated Response Model

Top-level object for both `GET /agents` and `POST /agents/search` responses.

```json
{
  "agents": [
    // ... list of Agent objects (see below) ...
  ],
  "nextPageToken": "string"
}

```

### 2) The Agent Object

This is the data model for each agent in the data array.

```json
{
  "agentIdentifier": "urn:agent:acme.com:sales-department:supply-chain-agent",
  "displayName": "Supply chain Agent",
  "description": "Places an order with various vendors",
  "version": "1.0.0",
  "protocols": [
    {
      "type": "A2A_AGENT",
      "protocolVersion": "0.3",
      "interfaces": [
        {
          "protocolBinding": "JSONRPC",
          "url": "https://api.example.com/my-agent/"
        }
      ]
    }
  ],
  "location": "us-central1",
  "trust": {
    "agentId": {
      "state": "ACTIVE",
      "lastVerificationTime": "2025-12-01T15:23:43.169Z"
    }
  },
  "createTime": "2025-12-01T15:23:43.169Z",
  "updateTime": "2025-12-01T15:23:43.169Z",
  "skills": [
    {
      "description": "Places an order with various vendors.",
      "examples": [
        "Place an order for more coffee with the cheapest vendor.",
        "We are running low on chocolates"
      ],
      "id": "create_order",
      "name": "Supply Chain Agent",
      "tags": [
        "Order",
        "Inventory"
      ]
    }
  ],
  "card": {},
  "metadata": {
    "custom/key1": "value1",
    "acme.com/framework": "ADK",
    "acme.com/service_uri": "https://api.acme.com/services/123",
    "acme.com/runtime_identity": "sa://my-agent-server-sa@acme.com"
  }
}

```

### 3) Error Response

The API returns a standardized error response when the request cannot be fulfilled due to a client error (e.g., invalid parameter, missing authentication) or a server error.

**HTTP Status Code:**

* **2XX** Normal (Return the responses as above)
* **400** Bad Request (e.g. missing a required parameter or invalid date format)
* **401** Unauthorized (e.g., invalid auth bearer token, expired token, etc)
* **404** Not Found (e.g., requesting a non-existent agent by ID in a future endpoint)
* **429** Rate Limit Exceeded (e.g., Too many requests, quota exceeded, etc)
* **500** Internal Server Error (Internal errors)

**Response Body for Errors**: The body will contain the standardized error object as below. The client only has to parse this one consistent structure for all errors, regardless of which endpoint failed.

```json
{
  "code": "INVALID_ARGUMENT",
  "message": "The provided filter_location is not valid.",
  "details": [ /* optional field-specific info */ ]
}

```

---

## Design Considerations

### Why Separated APIs (Specialized Search Interfaces)

Instead of a single unified endpoint, we chose to separate the List and Search endpoints to optimize for different read patterns.

1. **Optimized Read Models:** Listing relies on simple, fast filtering (often directly from a primary DB), whereas semantic search requires a specialized, heavier engine (e.g., Vector DB). Separating the interfaces allows us to route these distinct traffic patterns to the appropriate backend infrastructure efficiently.
2. **Handling Different Sort Logic:** `sort_by=relevance` is only valid in the context of a search query. Separating them allows the `GET` API to have a simpler, stricter validation contract (it explicitly rejects relevance sorting), while the `POST` API handles it as a default.
3. **Optimized Backends (Router Pattern):** Listing often relies on a primary database, while semantic/keyword search relies on a specialized engine (e.g., embedding DB + retrieval + ranking). Separating endpoints at the API level makes routing traffic to the correct backend service trivial for load balancers.
4. **GET vs. POST Trade-offs:**
* We keep `GET` for listing to maximize **cacheability** and adhere to **RESTful standards** for simple read operations.
* We use `POST` for search to support potentially **long semantic queries** that would exceed URL limits and to ensure **security** by keeping sensitive query terms out of server logs and browser history.



### Keyword Search vs Semantic Search

Provides different Search Intent:

1. **Keyword search**: The user knows what they are looking for (e.g., "trader," "finance"). This is a filtering action.
2. **Semantic search**: The user knows why they are searching (e.g., "find an agent to buy stock"). This is an answering action.

*Note: We recommend these be mutually exclusive in a single request to avoid the complexity of merging widely different relevance scoring algorithms (TF-IDF vs. Vector Cosine Similarity).*

Uses different Backend Systems:

1. **keyword_search** is best implemented by a full-text search index (like BM25). It's fast at matching keywords.
2. **semantic_query** is implemented by a vector embedding database. It finds results based on semantic meaning.

Different sorting algorithms:

1. Both types of search imply `orderBy=relevance`. However, "relevance" means something different for each. A keyword search's relevance is based on term frequency (TF-IDF), while a semantic search's relevance is based on embedding distance (like cosine similarity). If the user specifies the field name explicitly, then the results will be ordered by that field.
2. Combining results from these two different systems is more complex. It requires an additional layer to merge two separate relevance scores (like "hybrid search or RRF"), which is up to the implementation details but for simplicity, we suggest that only one of them is required.

### Search Filtering Execution Strategy

To ensure low latency and maintain accurate pagination, the application layer is recommended to push the filter parameter down to the underlying search index (e.g., Vector DB or Full-Text Search Engine) rather than applying it in-memory after retrieval.

* **Index-Based Filtering (Pre-filtering):** Implementations should utilize the native metadata filtering capabilities of the backend search engine. This ensures the search space is restricted *before* or *during* the Top-K retrieval phase. This prevents the "empty page" problem and avoids the severe latency penalties associated with over-fetching data to satisfy a post-filter constraint.
* **Engine-Level Query Planning:** While application-layer post-filtering is discouraged, the underlying search database (e.g., modern Vector databases) may dynamically choose its own execution plan. For instance, the database's query planner might utilize internal post-filtering for low-selectivity filters (e.g., `visibility=public`) if it determines that pre-filtering would be computationally heavier than filtering after an Approximate Nearest Neighbor (ANN) search. The API contract assumes the backend handles this optimization natively.

### Static Filters vs Filter String

We chose a single, flexible query string (e.g., `filter="location=... AND visibility=..."`) over static, prefixed parameters.

* **Pro (Flexibility)**: Easy to support all the AND, OR, NOT, =, logic and also *, ~ matches. (e.g., "find agents in 'US-East-1' OR with 'Acme' in the name"). It supports all the complex filtering as well.
* **Pro (Standard)**: Consistent with API standards.
* **Con (Security)**: A flexible query string (`filter="..."`) requires writing a complex parser, which is a more security vulnerability. It opens up to injection attacks. Static parameters are 100% safe, as we just validate a known key.
* **Con (Discoverability):** The API is self-documenting. A developer can easily see the list of available filters. A flexible string is an opaque "black box" that requires extensive documentation.
* **Con (Complexity)**: Need to build a parsing library.

---

## Filter Fields

| Filter | Type | Description |
| --- | --- | --- |
| `displayName` | string | Filter based on agent display Name (case-insensitive). |
| `location` | string | Filters by specific location/region (e.g., US-East-1). |
| `language` | string | Filters by supported language. |
| `visibility` | string | public, private, or all. |
| `category` | string | Comma-separated list of categories (OR logic). |
| `publisherId` | string | Comma-separated list of IDs (OR logic). |
| `publisherName` | string | Comma-separated list of Names (OR logic). |
| `createdAfter` | string | ISO 8601 timestamp (e.g., 2025-10-01T00:00:00Z). |
| `createdBefore` | string | ISO 8601 timestamp (e.g., 2025-10-01T00:00:00Z). |
| `updatedAfter` | string | ISO 8601 timestamp (e.g., 2025-10-01T00:00:00Z). |
| `updatedBefore` | string | ISO 8601 timestamp (e.g., 2025-10-01T00:00:00Z). |

Filter used to filter agents to return. If no filter is specified then all agents from the search result will be returned.

Filter expressions can be used to restrict results based upon `displayName`, `location`, `language`, etc. where the operators **=**, **NOT**, **AND** and **OR** can be used along with the suffix wildcard symbol `*`.

**Example queries:**

* `Filter displayName=Test*`: Filter Agent name whose name starts with "Test".
* `Filter publisherId=Sale*`: Returns Agents publisher Id starts with Sale.
* `Filter category=ABC,123`: Returns Agent category are ABC and 123.
* `Filter publisherName=Acme* AND NOT created_before=2025-10-01T00:00:00Z`: Returns Agent with publisher name starts with Acme and agents created before 2025-10-01T00:00:00Z.

