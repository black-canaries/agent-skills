# Convex Core Patterns Reference

Comprehensive guide to Convex function patterns, validators, schemas, and API design.

## Function Syntax

### New Function Syntax (Required)

ALWAYS use the new function syntax with explicit args and returns validators:

```typescript
import { query } from "./_generated/server";
import { v } from "convex/values";

export const f = query({
    args: {},
    returns: v.null(),
    handler: async (ctx, args) => {
        // Function body
    },
});
```

### Function Registration

**Public Functions** (exposed to client):
- `query` - Read-only operations with reactive subscriptions
- `mutation` - Write operations with transactions
- `action` - External API calls with Node.js runtime

**Internal Functions** (private, server-only):
- `internalQuery` - Private read operations
- `internalMutation` - Private write operations
- `internalAction` - Private external operations

**Critical Rules**:
- ALWAYS include args and returns validators for ALL functions
- If function doesn't return anything, use `returns: v.null()`
- JavaScript functions without return implicitly return `null`
- NEVER register functions through `api` or `internal` objects
- Use internal functions for sensitive operations

### HTTP Endpoint Syntax

HTTP endpoints are defined in `convex/http.ts`:

```typescript
import { httpRouter } from "convex/server";
import { httpAction } from "./_generated/server";

const http = httpRouter();
http.route({
    path: "/echo",
    method: "POST",
    handler: httpAction(async (ctx, req) => {
        const body = await req.bytes();
        return new Response(body, { status: 200 });
    }),
});
export default http;
```

Endpoints are registered at the exact path specified (e.g., `/api/someRoute`).

## Validators

### Complete Validator Reference

| Convex Type | TS/JS type  | Example Usage         | Validator                     | Notes                                                                                                                                                                                                 |
| ----------- | ------------| -----------------------| ------------------------------| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Id          | string      | `doc._id`              | `v.id(tableName)`             |                                                                                                                                                                                                       |
| Null        | null        | `null`                 | `v.null()`                    | JavaScript's `undefined` is not a valid Convex value. Functions that return `undefined` or do not return will return `null` when called from a client. Use `null` instead.                           |
| Int64       | bigint      | `3n`                   | `v.int64()`                   | Int64s only support BigInts between -2^63 and 2^63-1. Convex supports `bigint`s in most modern browsers.                                                                                             |
| Float64     | number      | `3.1`                  | `v.number()`                  | Convex supports all IEEE-754 double-precision floating point numbers (such as NaNs). Inf and NaN are JSON serialized as strings.                                                                     |
| Boolean     | boolean     | `true`                 | `v.boolean()`                 |                                                                                                                                                                                                       |
| String      | string      | `"abc"`                | `v.string()`                  | Strings are stored as UTF-8 and must be valid Unicode sequences. Strings must be smaller than the 1MB total size limit when encoded as UTF-8.                                                        |
| Bytes       | ArrayBuffer | `new ArrayBuffer(8)`   | `v.bytes()`                   | Convex supports first class bytestrings, passed in as `ArrayBuffer`s. Bytestrings must be smaller than the 1MB total size limit for Convex types.                                                    |
| Array       | Array       | `[1, 3.2, "abc"]`      | `v.array(values)`             | Arrays can have at most 8192 values.                                                                                                                                                                  |
| Object      | Object      | `{a: "abc"}`           | `v.object({property: value})` | Convex only supports "plain old JavaScript objects" (objects that do not have a custom prototype). Objects can have at most 1024 entries. Field names must be nonempty and not start with "$" or "_".|
| Record      | Record      | `{"a": "1", "b": "2"}` | `v.record(keys, values)`      | Records are objects at runtime, but can have dynamic keys. Keys must be only ASCII characters, nonempty, and not start with "$" or "_".                                                              |

### Array Validator Example

```typescript
import { mutation } from "./_generated/server";
import { v } from "convex/values";

export default mutation({
    args: {
        simpleArray: v.array(v.union(v.string(), v.number())),
    },
    handler: async (ctx, args) => {
        // ...
    },
});
```

### Discriminated Union Validator

```typescript
import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
    results: defineTable(
        v.union(
            v.object({
                kind: v.literal("error"),
                errorMessage: v.string(),
            }),
            v.object({
                kind: v.literal("success"),
                value: v.number(),
            }),
        ),
    )
});
```

### Null Return Validator

Always use `v.null()` when returning null:

```typescript
import { query } from "./_generated/server";
import { v } from "convex/values";

export const exampleQuery = query({
    args: {},
    returns: v.null(),
    handler: async (ctx, args) => {
        console.log("This query returns a null value");
        return null;
    },
});
```

### Deprecated Validators

- `v.bigint()` is DEPRECATED - use `v.int64()` instead
- `v.map()` and `v.set()` are NOT supported - use `v.record()` for key-value pairs

## Function Calling

### Calling Patterns

**From Queries, Mutations, or Actions**:
```typescript
ctx.runQuery(api.file.query, args)
```

**From Mutations or Actions**:
```typescript
ctx.runMutation(internal.file.mutation, args)
```

**From Actions Only**:
```typescript
ctx.runAction(internal.file.action, args)
```

### Critical Rules

- All calls take FunctionReference - NEVER pass the function directly
- ONLY call action from action if crossing runtimes (V8 to Node) - otherwise use shared helper functions
- Minimize action-to-query/mutation calls to avoid race conditions (queries/mutations are transactions)
- When calling same-file functions, add type annotation to work around TypeScript circularity:

```typescript
export const f = query({
    args: { name: v.string() },
    returns: v.string(),
    handler: async (ctx, args) => {
        return "Hello " + args.name;
    },
});

export const g = query({
    args: {},
    returns: v.null(),
    handler: async (ctx, args) => {
        const result: string = await ctx.runQuery(api.example.f, { name: "Bob" });
        return null;
    },
});
```

## Function References

Function references are pointers to registered Convex functions.

**Public functions** use `api` object from `convex/_generated/api.ts`:
- File: `convex/example.ts` with function `f` → Reference: `api.example.f`
- Nested: `convex/messages/access.ts` with function `h` → Reference: `api.messages.access.h`

**Internal functions** use `internal` object:
- File: `convex/example.ts` with internal function `g` → Reference: `internal.example.g`

Convex uses file-based routing for all function references.

## Schema Design

### Schema Definition

Always define schema in `convex/schema.ts`:

```typescript
import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
    tasks: defineTable({
        title: v.string(),
        userId: v.id("users"),
        completed: v.boolean(),
    }).index("by_user", ["userId"]),
});
```

### System Fields

Automatically added to all documents (prefixed with underscore):
- `_id` - Document ID with validator `v.id(tableName)`
- `_creationTime` - Creation timestamp with validator `v.number()`

### Index Naming Convention

ALWAYS include all index fields in the index name:
- Index `["field1", "field2"]` → Name: `"by_field1_and_field2"`

### Index Query Order

Index fields MUST be queried in the same order as defined:
- To query by "field1" then "field2" AND "field2" then "field1", create separate indexes
- Different query orders require different indexes

## Query Patterns

### Indexed Queries (Required)

DO NOT use `filter` - define indexes and use `withIndex`:

```typescript
const tasks = await ctx.db
    .query("tasks")
    .withIndex("by_user", (q) => q.eq("userId", userId))
    .collect();
```

### Query Operations

**Collecting Results**:
```typescript
.collect()  // Get all results as array
.take(n)    // Get first n results
.unique()   // Get single result (throws if multiple)
```

**Async Iteration** (don't use `.collect()` or `.take()`):
```typescript
for await (const row of query) {
    // Process row
}
```

**Deletion** (queries don't support `.delete()`):
```typescript
const results = await ctx.db.query("tasks").collect();
for (const task of results) {
    await ctx.db.delete(task._id);
}
```

### Ordering

- Default: Ascending `_creationTime` order
- `.order('asc')` or `.order('desc')` to control order
- Indexed queries ordered by index columns (avoids table scans)

## Mutation Patterns

### Update Operations

**Full Replacement**:
```typescript
await ctx.db.replace(docId, newDoc);  // Throws if document doesn't exist
```

**Partial Update**:
```typescript
await ctx.db.patch(docId, { field: newValue });  // Shallow merge, throws if doesn't exist
```

### Insert Operations

```typescript
const newId = await ctx.db.insert("tasks", {
    title: "New task",
    userId: userId,
    completed: false,
});
```

## Action Patterns

### Node.js Runtime

Add `"use node";` to the top of files using Node.js built-in modules:

```typescript
"use node";

import { action } from "./_generated/server";
```

### Database Access

NEVER use `ctx.db` inside actions - actions don't have database access.
Use `ctx.runQuery` and `ctx.runMutation` instead.

### Action Example

```typescript
import { action } from "./_generated/server";
import { v } from "convex/values";

export const exampleAction = action({
    args: {},
    returns: v.null(),
    handler: async (ctx, args) => {
        console.log("This action does not return anything");
        return null;
    },
});
```

## Pagination

### Paginated Query Pattern

```typescript
import { v } from "convex/values";
import { query } from "./_generated/server";
import { paginationOptsValidator } from "convex/server";

export const listWithExtraArg = query({
    args: { paginationOpts: paginationOptsValidator, author: v.string() },
    handler: async (ctx, args) => {
        return await ctx.db
            .query("messages")
            .filter((q) => q.eq(q.field("author"), args.author))
            .order("desc")
            .paginate(args.paginationOpts);
    },
});
```

### Pagination Types

**paginationOpts object**:
- `numItems: v.number()` - Maximum documents to return
- `cursor: v.union(v.string(), v.null())` - Cursor for next page

**Returns**:
- `page` - Array of fetched documents
- `isDone` - Boolean indicating if this is the last page
- `continueCursor` - String cursor for next page

## Full-Text Search

Search index pattern:

```typescript
const messages = await ctx.db
    .query("messages")
    .withSearchIndex("search_body", (q) =>
        q.search("body", "hello hi").eq("channel", "#general"),
    )
    .take(10);
```

## TypeScript Patterns

### Id Types

Use `Id` helper from generated dataModel:

```typescript
import { Id } from "./_generated/dataModel";

function processUser(userId: Id<"users">) {
    // userId is strictly typed to users table
}
```

### Record Types with Ids

```typescript
import { query } from "./_generated/server";
import { Doc, Id } from "./_generated/dataModel";
import { v } from "convex/values";

export const exampleQuery = query({
    args: { userIds: v.array(v.id("users")) },
    returns: v.record(v.id("users"), v.string()),
    handler: async (ctx, args) => {
        const idToUsername: Record<Id<"users">, string> = {};
        for (const userId of args.userIds) {
            const user = await ctx.db.get(userId);
            if (user) {
                idToUsername[user._id] = user.username;
            }
        }
        return idToUsername;
    },
});
```

### Type Strictness

- Be strict with types, particularly around IDs
- Use `Id<"tableName">` not `string`
- Use `as const` for string literals in discriminated unions
- Define arrays as `const array: Array<T> = [...];`
- Define records as `const record: Record<KeyType, ValueType> = {...};`
- Add `@types/node` to package.json when using Node.js built-ins

## Scheduling

### Cron Jobs

ONLY use `crons.interval` or `crons.cron` (NOT deprecated helpers):

```typescript
import { cronJobs } from "convex/server";
import { internal } from "./_generated/api";
import { internalAction } from "./_generated/server";
import { v } from "convex/values";

const empty = internalAction({
    args: {},
    returns: v.null(),
    handler: async (ctx, args) => {
        console.log("empty");
    },
});

const crons = cronJobs();

// Run every two hours
crons.interval("delete inactive users", { hours: 2 }, internal.crons.empty, {});

export default crons;
```

**Critical Rules**:
- Take FunctionReference, not direct function
- Define as top-level object and export as default
- Can register functions in `crons.ts` like any other file
- Always import `internal` from `_generated/api` for internal functions

## File Storage

### Storage Operations

**Upload**:
```typescript
const storageId = await ctx.storage.store(blob);
```

**Get URL** (returns null if not found):
```typescript
const url = await ctx.storage.getUrl(storageId);
```

### File Metadata

DO NOT use deprecated `ctx.storage.getMetadata()`. Query `_storage` system table instead:

```typescript
import { query } from "./_generated/server";
import { Id } from "./_generated/dataModel";
import { v } from "convex/values";

type FileMetadata = {
    _id: Id<"_storage">;
    _creationTime: number;
    contentType?: string;
    sha256: string;
    size: number;
}

export const exampleQuery = query({
    args: { fileId: v.id("_storage") },
    returns: v.null(),
    handler: async (ctx, args) => {
        const metadata: FileMetadata | null = await ctx.db.system.get(args.fileId);
        console.log(metadata);
        return null;
    },
});
```

**Storage Format**: Convex stores items as `Blob` objects - must convert to/from Blob.

## API Design Best Practices

- Use file-based routing to organize public functions thoughtfully
- Define public APIs with `query`, `mutation`, `action`
- Define internal/private functions with `internalQuery`, `internalMutation`, `internalAction`
- Organize files within `convex/` directory by domain
- Never expose sensitive internal operations as public functions
