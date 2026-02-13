---
name: manage-convex
description: Build full-stack applications with Convex - serverless backend with TypeScript, real-time queries, mutations, actions, agents, RAG, workflows, and authentication. Use when working with Convex projects, building serverless backends, implementing AI agents, setting up authentication, or integrating LLM-powered features with persistent state.
---

<objective>
Master Convex development for building production-ready full-stack applications with serverless TypeScript backend, real-time data synchronization, AI agents, RAG systems, durable workflows, and authentication.
</objective>

<quick_start>
<essential_patterns>
**Query with validators** (read-only, reactive):
```typescript
import { query } from "./_generated/server";
import { v } from "convex/values";

export const listTasks = query({
  args: { userId: v.id("users") },
  returns: v.array(v.object({
    _id: v.id("tasks"),
    title: v.string(),
    completed: v.boolean(),
  })),
  handler: async (ctx, args) => {
    return await ctx.db
      .query("tasks")
      .withIndex("by_user", (q) => q.eq("userId", args.userId))
      .collect();
  },
});
```

**Mutation with validators** (write operations):
```typescript
import { mutation } from "./_generated/server";
import { v } from "convex/values";

export const createTask = mutation({
  args: { title: v.string(), userId: v.id("users") },
  returns: v.id("tasks"),
  handler: async (ctx, args) => {
    return await ctx.db.insert("tasks", {
      title: args.title,
      userId: args.userId,
      completed: false,
    });
  },
});
```

**Schema definition** (convex/schema.ts):
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
</essential_patterns>

<critical_rules>
- ALWAYS use new function syntax with args and returns validators
- ALWAYS include `returns` validator (use `v.null()` for void functions)
- NEVER use filter in queries - define indexes and use `withIndex` instead
- NEVER use deprecated validators like `v.bigint()` (use `v.int64()`)
- NEVER register functions through `api` or `internal` objects
- ALWAYS use file-based routing (api.filename.functionName)
</critical_rules>
</quick_start>

<context>
<architecture>
Convex is a serverless backend-as-a-service with:
- **Queries**: Reactive, read-only, transactional database access
- **Mutations**: Write operations with automatic retries and transactions
- **Actions**: Long-running operations with external API calls (Node.js runtime)
- **Schemas**: TypeScript-first validation with automatic type generation
- **Real-time**: Automatic subscription updates to React/React Native clients
- **Agents**: AI-powered workflows with LLM integration and persistent threads
- **File Storage**: Built-in file storage with signed URLs
- **Scheduling**: Cron jobs and one-time scheduled functions
</architecture>

<function_types>
**Public Functions** (exposed to client):
- `query` - Read-only database access
- `mutation` - Write operations
- `action` - External API calls, LLM interactions

**Internal Functions** (server-only):
- `internalQuery` - Private read operations
- `internalMutation` - Private write operations
- `internalAction` - Private external calls

Use internal functions for sensitive operations not part of public API.
</function_types>
</context>

<workflow>
<step_1_setup>
**Initialize Convex project**:
```bash
pnpm add convex
pnpm convex dev
```

Create `convex/schema.ts` with table definitions.
</step_1_setup>

<step_2_functions>
**Write queries and mutations** in `convex/` directory using file-based routing:
- Define args with validators
- Define returns with validators
- Implement handler logic
- Export with descriptive names

File: `convex/tasks.ts` creates functions accessible as `api.tasks.functionName`.
</step_2_functions>

<step_3_indexes>
**Define indexes for efficient queries**:
- Index name format: `by_field1_and_field2`
- Query fields in same order as index definition
- Create separate indexes for different query orders
- Use `withIndex` instead of `filter` for performance
</step_3_indexes>

<step_4_calling>
**Call functions from other functions**:
- `ctx.runQuery(api.file.query, args)` from query/mutation/action
- `ctx.runMutation(internal.file.mutation, args)` from mutation/action
- `ctx.runAction(internal.file.action, args)` from action only
- Use FunctionReference, not direct function calls
- Add type annotation when calling same-file functions
</step_4_calling>

<step_5_validation>
**Validate implementation**:
- Check all functions have args and returns validators
- Verify indexes match query patterns
- Ensure internal functions use `internal.*` references
- Test with TypeScript strict mode enabled
- Run `pnpm convex dev` to verify schema and functions
</step_5_validation>
</workflow>

<advanced_features>
<agents>
**AI Agents with LLM integration**:
Build agentic applications with persistent conversation history, tool calling, and real-time reactivity. Agents encapsulate LLM models, prompts, and custom tools.

See [references/agents.md](references/agents.md) for:
- Agent setup and configuration
- Thread management for conversation persistence
- Tool integration patterns
- Streaming responses and structured outputs
- Human-in-the-loop workflows
- Rate limiting and usage tracking
</agents>

<rag>
**Retrieval-Augmented Generation (RAG)**:
Implement semantic search over custom knowledge bases with vector embeddings, enabling LLMs to provide accurate, domain-specific answers with source citations.

See [references/rag.md](references/rag.md) for:
- Prompt-based vs tool-based RAG patterns
- Vector search with namespaces
- Document ingestion strategies (PDFs, images, text)
- Chunk management and context retrieval
- Importance weighting and filtering
</rag>

<workflows>
**Durable Workflows**:
Build reliable multi-step processes with automatic retries, idempotency, and resumability after server restarts.

See [references/workflows.md](references/workflows.md) for:
- Workflow manager setup
- Step composition patterns
- Error handling and retries
- Load balancing with Workpool
- Multi-agent orchestration
- Pauseable workflows
</workflows>

<auth>
**Authentication with Convex Auth**:
Implement secure authentication directly in your Convex backend without separate auth services.

See [references/auth.md](references/auth.md) for:
- Setup and configuration
- OAuth providers (GitHub, Google, Apple)
- Email authentication (magic links, OTPs)
- Password authentication with reset flows
- Session management
- Securing functions with middleware
</auth>

<file_storage>
**File Storage**:
Store and retrieve large files (images, videos, PDFs) with signed URLs.

Key operations:
- `await ctx.storage.store(blob)` - Upload file, returns storage ID
- `await ctx.storage.getUrl(storageId)` - Get signed URL (returns null if not found)
- Query `_storage` system table for metadata (use `ctx.db.system.get(storageId)`)

NEVER use deprecated `ctx.storage.getMetadata()`.
</file_storage>

<pagination>
**Paginated Queries**:
Return large result sets incrementally with cursor-based pagination.

```typescript
import { paginationOptsValidator } from "convex/server";

export const list = query({
  args: { paginationOpts: paginationOptsValidator },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("messages")
      .order("desc")
      .paginate(args.paginationOpts);
  },
});
```

Returns: `{ page: Doc[], isDone: boolean, continueCursor: string }`
</pagination>

<scheduling>
**Cron Jobs**:
Schedule recurring tasks with `crons.interval` or `crons.cron`.

```typescript
import { cronJobs } from "convex/server";
import { internal } from "./_generated/api";

const crons = cronJobs();
crons.interval("cleanup", { hours: 2 }, internal.tasks.cleanup, {});
export default crons;
```

NEVER use deprecated `crons.hourly/daily/weekly` helpers.
</scheduling>

<http_endpoints>
**HTTP Endpoints**:
Expose REST endpoints for webhooks and external integrations.

```typescript
import { httpRouter } from "convex/server";
import { httpAction } from "./_generated/server";

const http = httpRouter();
http.route({
  path: "/webhook",
  method: "POST",
  handler: httpAction(async (ctx, req) => {
    const body = await req.json();
    // Process webhook
    return new Response("OK", { status: 200 });
  }),
});
export default http;
```

Define in `convex/http.ts`. Paths are exact (e.g., `/api/webhook`).
</http_endpoints>
</advanced_features>

<validation>
<type_safety>
- Use strict TypeScript types for all functions
- Use `Id<"tableName">` for document IDs, not `string`
- Use `Doc<"tableName">` for document types
- Define `Record<KeyType, ValueType>` with explicit types
- Use `as const` for string literals in discriminated unions
- Add `@types/node` when using Node.js built-ins
</type_safety>

<common_mistakes>
- Using `filter` instead of indexed queries (creates table scans)
- Missing `returns` validator (required for all functions)
- Calling functions directly instead of using FunctionReference
- Using `v.bigint()` instead of `v.int64()`
- Registering functions through `api` or `internal` objects
- Using deprecated `ctx.storage.getMetadata()`
- Querying without indexes (performance issue)
</common_mistakes>

<diagnostics>
Run checks before deployment:
1. `pnpm convex dev` - Verify schema and function signatures
2. `pnpm tsc --noEmit` - Check TypeScript types
3. Review index coverage for all queries
4. Test pagination limits for large datasets
5. Verify internal functions use correct references
</diagnostics>
</validation>

<success_criteria>
A well-structured Convex backend has:

- Schema with proper indexes for all query patterns
- All functions with complete args and returns validators
- Internal functions for sensitive operations
- Efficient queries using `withIndex` instead of `filter`
- TypeScript strict mode enabled with proper types
- File-based routing organized by domain
- Error handling for external API calls in actions
- Rate limiting for LLM calls and expensive operations
- Proper function references (api.* for public, internal.* for private)
</success_criteria>

<reference_guides>
For comprehensive details on specific topics:

**Core Patterns**: [references/core-patterns.md](references/core-patterns.md)
- Complete function syntax and registration
- Validator patterns and type mapping
- Schema design and indexing strategies
- Query and mutation best practices
- Action guidelines for external APIs
- Function calling patterns
- Pagination implementation
- Full-text search

**Agents**: [references/agents.md](references/agents.md)
- Agent architecture and setup
- Thread management and conversation persistence
- Tool integration and custom capabilities
- Streaming and structured outputs
- Multi-agent workflows
- Debugging and monitoring

**RAG**: [references/rag.md](references/rag.md)
- Prompt-based vs tool-based approaches
- Vector search and embedding strategies
- Document ingestion (PDFs, images, text)
- Namespace isolation
- Chunk management and context retrieval

**Workflows**: [references/workflows.md](references/workflows.md)
- Durable workflow patterns
- Step composition and orchestration
- Error handling and retries
- Workpool for load balancing
- Multi-agent coordination
- Pauseable and resumable workflows

**Auth**: [references/auth.md](references/auth.md)
- Setup and configuration
- OAuth integration (GitHub, Google, Apple)
- Email authentication (magic links, OTPs)
- Password authentication
- Session management and middleware
- Securing functions

**Examples**: [references/examples.md](references/examples.md)
- Real-world implementation patterns
- Chat application with AI responses
- Task management with pagination
- File upload and retrieval
- Multi-tenant RAG system
</reference_guides>
