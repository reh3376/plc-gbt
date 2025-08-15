# Frontend Schema & API Contract Playbook (Zod + OpenAPI)

**Audience:** AI coding agent building Whiskey House’s Next.js/TypeScript frontend  
**Goal:** Use **OpenAPI** as the *backend contract* and **Zod** as the *frontend runtime/type-safe validation layer*, with zero drift between the two.

---

## 0) TL;DR Rules

1. **OpenAPI is the single source of truth** for the HTTP contract (paths, params, bodies, responses, errors).  
2. **Generate TypeScript types + Zod validators from OpenAPI**; never hand-write types for server payloads.  
3. **Use Zod at the edges of the UI** (forms, client guards, feature flags) and for any extra client-only constraints or transformations.  
4. **Every request/response is validated** by a Zod schema derived from OpenAPI before it touches app state.  
5. **CI blocks the build** if the OpenAPI spec or the generated client is out of date.

---

## 1) Project Setup

### Packages
```bash
# OpenAPI → TS types (+ clients) and Zod schemas
pnpm add -D openapi-typescript openapi-zod-client @anatine/zod-openapi
pnpm add axios zod @hookform/resolvers react-hook-form

# Optional tools
pnpm add -D orval redocly speccy
```

### Repo Layout
```
/src
  /api
    openapi.json                 # pulled from backend CI artifact or URL
    client.ts                    # generated axios client (do not edit)
    zod-schemas.ts               # generated Zod validators (do not edit)
    index.ts                     # thin wrappers + interceptors
  /features
    /orders
      form.schema.ts             # Zod: UI-only validation & transforms
      api.ts                     # calls into /src/api
      components/...
  /lib
    zod-helpers.ts               # common zod helpers (date, money, enums)
scripts/
  generate-api.mjs               # codegen pipeline
```

---

## 2) Codegen Pipeline (OpenAPI → Types + Zod)

**Source of truth:** `src/api/openapi.json` (or a URL).

**Generate types + Zod + client:**
```jsonc
// package.json
{
  "scripts": {
    "api:pull": "curl -sSL $OPENAPI_URL -o src/api/openapi.json",
    "api:gen:types": "openapi-typescript src/api/openapi.json -o src/api/types.gen.ts",
    "api:gen:zod": "openapi-zod-client --input src/api/openapi.json --output src/api/zod-schemas.ts",
    "api:gen": "pnpm api:gen:types && pnpm api:gen:zod && node scripts/generate-api.mjs",
    "check:openapi": "redocly lint src/api/openapi.json",
    "postinstall": "pnpm api:gen"
  }
}
```

**`scripts/generate-api.mjs` (example skeleton):**
```js
import { promises as fs } from 'node:fs';

// Optionally stitch a typed axios instance with interceptors:
const header = `
import axios from "axios";
export const http = axios.create({ baseURL: process.env.NEXT_PUBLIC_API_BASE });
http.interceptors.response.use(r => r, (err) => Promise.reject(err));
`;
await fs.writeFile("src/api/index.ts", header);
```

> **Contract-first**: if the backend spec changes, `pnpm api:gen` must run. CI will fail if generated files are stale.

---

## 3) Using Generated Zod in the UI

### 3.1 Form Validation (React Hook Form + Zod)
```ts
// features/orders/form.schema.ts (UI-only rules layered on top of API types)
import { z } from "zod";
// Suppose POST /orders uses OrderCreate schema from OpenAPI:
import { components } from "@/api/types.gen";
type OrderCreate = components["schemas"]["OrderCreate"];

export const OrderFormSchema = z.object({
  sku: z.string().min(1),
  qty: z.coerce.number().int().positive(),
  shipDate: z.coerce.date(),
});

// In the component:
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";

const { register, handleSubmit, formState } = useForm<z.infer<typeof OrderFormSchema>>({
  resolver: zodResolver(OrderFormSchema),
});
```

### 3.2 Calling the API with Validation
```ts
// features/orders/api.ts
import { http } from "@/api";
import { z } from "zod";
import { OrderCreateSchema, OrderSchema } from "@/api/zod-schemas"; 
// these are generated from OpenAPI by openapi-zod-client

export async function createOrder(input: unknown) {
  // Validate outbound payload against the generated OpenAPI-derived Zod
  const payload = OrderCreateSchema.parse(input);
  const { data } = await http.post("/orders", payload);

  // Validate inbound response before using it
  const order = OrderSchema.parse(data);
  return order;
}
```

> Rule: **No unvalidated JSON** is allowed into app state. Outbound/inbound shapes must pass the generated Zod schemas.

---

## 4) When to Author Zod by Hand (and how)

- **UI-only constraints** not present in the server contract (e.g., client-side coercion, helpful messages, intermediate wizard steps).  
- **Derived inputs** (e.g., comma-separated tags → `string[]`).  
- **Feature flags / local storage** schemas.

Pattern:
```ts
// zod-helpers.ts
import { z } from "zod";
export const Money = z.coerce.number().nonnegative().finite();
export const ISODate = z.string().datetime({ offset: true }).transform((s) => new Date(s));
```

Compose UI schemas with generated ones:
```ts
import { OrderCreateSchema as ApiOrderCreate } from "@/api/zod-schemas";
export const OrderFormSchema = ApiOrderCreate.merge(z.object({
  // extra client-only coercions
  shipDate: z.coerce.date()
}));
```

---

## 5) Error Handling & UX

- **Normalize API errors** via a single utility that attempts to parse server error bodies with generated Zod; fall back to a generic shape:
```ts
const ApiError = z.object({ code: z.string(), message: z.string(), details: z.any().optional() });

export function asApiError(e: unknown) {
  if (axios.isAxiosError(e)) {
    const parsed = ApiError.safeParse(e.response?.data);
    if (parsed.success) return parsed.data;
  }
  return { code: "UNKNOWN", message: "Unexpected error" } as const;
}
```
- **Form surfaces** map `details` to field errors when present.  
- **Always display validation failures** from `safeParse` with developer-friendly logs in dev.

---

## 6) Date/Time, Enums, Files, and Pagination

- **Dates:** Prefer string format in OpenAPI (`format: date-time`) → use `z.string().datetime()` then transform to `Date` in UI.  
- **Enums:** Define them in OpenAPI; consume via generated TS union types. For UI selects, derive options from the enum union.  
- **File uploads:** Use `multipart/form-data` in OpenAPI; in UI create `FormData` and skip Zod for the binary part (validate metadata only).  
- **Pagination:** Standardize `?page&limit` request and `{items, page, total}` response in OpenAPI and validate with generated Zod.

---

## 7) Testing & CI

### Unit tests (Vitest/Jest)
- **Schema tests:** For every critical form, add `good` and `bad` examples and assert `safeParse`.  
- **Contract tests:** Given a recorded server fixture, validate response with generated Zod.

```ts
import { describe, it, expect } from "vitest";
import { OrderSchema } from "@/api/zod-schemas";
it("validates order payload", () => {
  const ok = OrderSchema.safeParse({ id: "1", sku: "ABC", qty: 3 });
  expect(ok.success).toBe(true);
});
```

### CI gates
1. `pnpm check:openapi` (lint spec)  
2. `pnpm api:gen && git diff --exit-code` (fail if generated files changed)  
3. Run unit tests & type-check (`tsc --noEmit`)

---

## 8) Drift Prevention & Versioning

- **Spec version** in `openapi.info.version`; bump on any breaking change.  
- Frontend reads spec from a **pinned artifact** (`OPENAPI_URL`) per environment.  
- For breaking changes, **generate to a new folder** (`/src/api/v2`) and migrate features incrementally.

---

## 9) Alternative: Zod‑first (if no OpenAPI yet)

If the backend has no spec, define Zod schemas first and **export OpenAPI automatically**:
```ts
import { z } from "zod";
import { extendZodWithOpenApi, generateOpenApiDocument } from "@anatine/zod-openapi";

extendZodWithOpenApi(z);

export const Order = z.object({
  id: z.string().uuid(),
  sku: z.string().min(1),
  qty: z.number().int().positive(),
}).openapi("Order");

// Later:
const doc = generateOpenApiDocument({ title: "WHK API", version: "1.0.0" }, { components: { schemas: { Order } } });
```
Backends can consume this doc; frontend still uses the same codegen pipeline (now in reverse).

---

## 10) Do/Don’t Checklist

**Do**
- ✅ Validate every network boundary with generated Zod.  
- ✅ Keep all API types generated; wrap, don’t edit.  
- ✅ Use coercion (`z.coerce`) at the UI edge (inputs are strings).  
- ✅ Centralize axios instance & interceptors.  
- ✅ Add form resolver (Zod) for every complex form.

**Don’t**
- ❌ Hand-write request/response interfaces for API data.  
- ❌ Mutate generated files.  
- ❌ Accept unvalidated JSON into state.  
- ❌ Encode business logic into OpenAPI; keep it descriptive.

---

## 11) Example End-to-End Flow (Create Order)

1. User fills form → `OrderFormSchema` (UI) validates & coerces values.  
2. Call `createOrder(formData)` → payload validated by **generated** `OrderCreateSchema`.  
3. Axios sends request.  
4. Response parsed and validated by **generated** `OrderSchema`.  
5. State updated; errors normalized via `asApiError`.

---

## 12) Handoff Notes for the Agent

- Assume **Next.js (App Router)** with server actions permitted only for non-sensitive ops; otherwise use the axios client.  
- All feature modules follow the pattern `form.schema.ts` (UI rules) + `api.ts` (generated Zod in/out) + `components/*`.  
- Before opening a PR, run: `pnpm api:pull && pnpm api:gen && pnpm test && pnpm typecheck`.
