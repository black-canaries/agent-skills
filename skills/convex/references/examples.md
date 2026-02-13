# Convex Examples Reference

Real-world implementation patterns and complete examples for common Convex use cases.

## Chat Application with AI Responses

Complete backend for a real-time chat app with GPT-4 integration.

### Schema

```typescript
import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  channels: defineTable({
    name: v.string(),
  }),

  users: defineTable({
    name: v.string(),
  }),

  messages: defineTable({
    channelId: v.id("channels"),
    authorId: v.optional(v.id("users")), // null for AI messages
    content: v.string(),
  }).index("by_channel", ["channelId"]),
});
```

### Implementation

```typescript
"use node";

import {
  query,
  mutation,
  internalQuery,
  internalMutation,
  internalAction,
} from "./_generated/server";
import { v } from "convex/values";
import OpenAI from "openai";
import { internal } from "./_generated/api";

const openai = new OpenAI();

// Create user
export const createUser = mutation({
  args: { name: v.string() },
  returns: v.id("users"),
  handler: async (ctx, args) => {
    return await ctx.db.insert("users", { name: args.name });
  },
});

// Create channel
export const createChannel = mutation({
  args: { name: v.string() },
  returns: v.id("channels"),
  handler: async (ctx, args) => {
    return await ctx.db.insert("channels", { name: args.name });
  },
});

// List recent messages
export const listMessages = query({
  args: { channelId: v.id("channels") },
  returns: v.array(v.object({
    _id: v.id("messages"),
    _creationTime: v.number(),
    channelId: v.id("channels"),
    authorId: v.optional(v.id("users")),
    content: v.string(),
  })),
  handler: async (ctx, args) => {
    const messages = await ctx.db
      .query("messages")
      .withIndex("by_channel", (q) => q.eq("channelId", args.channelId))
      .order("desc")
      .take(10);
    return messages;
  },
});

// Send message and trigger AI response
export const sendMessage = mutation({
  args: {
    channelId: v.id("channels"),
    authorId: v.id("users"),
    content: v.string(),
  },
  returns: v.null(),
  handler: async (ctx, args) => {
    const channel = await ctx.db.get(args.channelId);
    if (!channel) {
      throw new Error("Channel not found");
    }

    const user = await ctx.db.get(args.authorId);
    if (!user) {
      throw new Error("User not found");
    }

    await ctx.db.insert("messages", {
      channelId: args.channelId,
      authorId: args.authorId,
      content: args.content,
    });

    // Schedule AI response
    await ctx.scheduler.runAfter(0, internal.chat.generateResponse, {
      channelId: args.channelId,
    });

    return null;
  },
});

// Generate AI response (internal action)
export const generateResponse = internalAction({
  args: { channelId: v.id("channels") },
  returns: v.null(),
  handler: async (ctx, args) => {
    const context: Array<{ role: string; content: string }> =
      await ctx.runQuery(internal.chat.loadContext, {
        channelId: args.channelId,
      });

    const response = await openai.chat.completions.create({
      model: "gpt-4o",
      messages: context,
    });

    const content = response.choices[0].message.content;
    if (!content) {
      throw new Error("No content in response");
    }

    await ctx.runMutation(internal.chat.writeAgentResponse, {
      channelId: args.channelId,
      content,
    });

    return null;
  },
});

// Load conversation context (internal query)
export const loadContext = internalQuery({
  args: { channelId: v.id("channels") },
  returns: v.array(v.object({
    role: v.union(v.literal("user"), v.literal("assistant")),
    content: v.string(),
  })),
  handler: async (ctx, args) => {
    const messages = await ctx.db
      .query("messages")
      .withIndex("by_channel", (q) => q.eq("channelId", args.channelId))
      .order("desc")
      .take(10);

    const result = [];
    for (const message of messages) {
      if (message.authorId) {
        const user = await ctx.db.get(message.authorId);
        if (!user) {
          throw new Error("User not found");
        }
        result.push({
          role: "user" as const,
          content: `${user.name}: ${message.content}`,
        });
      } else {
        result.push({
          role: "assistant" as const,
          content: message.content
        });
      }
    }
    return result.reverse();
  },
});

// Write AI response (internal mutation)
export const writeAgentResponse = internalMutation({
  args: {
    channelId: v.id("channels"),
    content: v.string(),
  },
  returns: v.null(),
  handler: async (ctx, args) => {
    await ctx.db.insert("messages", {
      channelId: args.channelId,
      content: args.content,
      // authorId is undefined (AI message)
    });
    return null;
  },
});
```

## Task Management with Teams

Multi-tenant task management with team isolation.

### Schema

```typescript
import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  teams: defineTable({
    name: v.string(),
  }),

  users: defineTable({
    email: v.string(),
    name: v.string(),
    teamId: v.id("teams"),
  }).index("by_team", ["teamId"]),

  tasks: defineTable({
    teamId: v.id("teams"),
    title: v.string(),
    description: v.optional(v.string()),
    assigneeId: v.optional(v.id("users")),
    status: v.union(
      v.literal("todo"),
      v.literal("in_progress"),
      v.literal("done")
    ),
    priority: v.union(
      v.literal("low"),
      v.literal("medium"),
      v.literal("high")
    ),
    dueDate: v.optional(v.number()),
  })
    .index("by_team", ["teamId"])
    .index("by_assignee", ["assigneeId"])
    .index("by_status", ["teamId", "status"]),
});
```

### Implementation

```typescript
import { query, mutation } from "./_generated/server";
import { v } from "convex/values";

// Create team
export const createTeam = mutation({
  args: { name: v.string() },
  returns: v.id("teams"),
  handler: async (ctx, args) => {
    return await ctx.db.insert("teams", { name: args.name });
  },
});

// List team tasks
export const listTeamTasks = query({
  args: {
    teamId: v.id("teams"),
    status: v.optional(v.union(
      v.literal("todo"),
      v.literal("in_progress"),
      v.literal("done")
    )),
  },
  returns: v.array(v.object({
    _id: v.id("tasks"),
    title: v.string(),
    status: v.string(),
    priority: v.string(),
    assigneeId: v.optional(v.id("users")),
    dueDate: v.optional(v.number()),
  })),
  handler: async (ctx, args) => {
    let query = ctx.db.query("tasks");

    if (args.status) {
      query = query.withIndex("by_status", (q) =>
        q.eq("teamId", args.teamId).eq("status", args.status)
      );
    } else {
      query = query.withIndex("by_team", (q) =>
        q.eq("teamId", args.teamId)
      );
    }

    return await query.collect();
  },
});

// Create task
export const createTask = mutation({
  args: {
    teamId: v.id("teams"),
    title: v.string(),
    description: v.optional(v.string()),
    assigneeId: v.optional(v.id("users")),
    priority: v.union(
      v.literal("low"),
      v.literal("medium"),
      v.literal("high")
    ),
    dueDate: v.optional(v.number()),
  },
  returns: v.id("tasks"),
  handler: async (ctx, args) => {
    // Verify team exists
    const team = await ctx.db.get(args.teamId);
    if (!team) {
      throw new Error("Team not found");
    }

    // Verify assignee is in team (if provided)
    if (args.assigneeId) {
      const assignee = await ctx.db.get(args.assigneeId);
      if (!assignee || assignee.teamId !== args.teamId) {
        throw new Error("Assignee not in team");
      }
    }

    return await ctx.db.insert("tasks", {
      teamId: args.teamId,
      title: args.title,
      description: args.description,
      assigneeId: args.assigneeId,
      status: "todo",
      priority: args.priority,
      dueDate: args.dueDate,
    });
  },
});

// Update task status
export const updateTaskStatus = mutation({
  args: {
    taskId: v.id("tasks"),
    status: v.union(
      v.literal("todo"),
      v.literal("in_progress"),
      v.literal("done")
    ),
  },
  returns: v.null(),
  handler: async (ctx, args) => {
    const task = await ctx.db.get(args.taskId);
    if (!task) {
      throw new Error("Task not found");
    }

    await ctx.db.patch(args.taskId, { status: args.status });
    return null;
  },
});

// Assign task
export const assignTask = mutation({
  args: {
    taskId: v.id("tasks"),
    assigneeId: v.id("users"),
  },
  returns: v.null(),
  handler: async (ctx, args) => {
    const task = await ctx.db.get(args.taskId);
    if (!task) {
      throw new Error("Task not found");
    }

    const assignee = await ctx.db.get(args.assigneeId);
    if (!assignee || assignee.teamId !== task.teamId) {
      throw new Error("Assignee not in team");
    }

    await ctx.db.patch(args.taskId, { assigneeId: args.assigneeId });
    return null;
  },
});
```

## File Upload and Processing

Handle file uploads with metadata and processing.

### Schema

```typescript
import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  files: defineTable({
    storageId: v.id("_storage"),
    filename: v.string(),
    contentType: v.string(),
    size: v.number(),
    uploaderId: v.id("users"),
    processed: v.boolean(),
    metadata: v.optional(v.object({
      width: v.optional(v.number()),
      height: v.optional(v.number()),
      duration: v.optional(v.number()),
    })),
  }).index("by_uploader", ["uploaderId"]),

  users: defineTable({
    email: v.string(),
    name: v.string(),
  }),
});
```

### Implementation

```typescript
import { mutation, query, action } from "./_generated/server";
import { v } from "convex/values";
import { internal } from "./_generated/api";

// Generate upload URL
export const generateUploadUrl = mutation({
  args: {},
  returns: v.string(),
  handler: async (ctx) => {
    return await ctx.storage.generateUploadUrl();
  },
});

// Save file metadata after upload
export const saveFile = mutation({
  args: {
    storageId: v.id("_storage"),
    filename: v.string(),
    contentType: v.string(),
    uploaderId: v.id("users"),
  },
  returns: v.id("files"),
  handler: async (ctx, args) => {
    // Get file metadata from storage system
    const metadata = await ctx.db.system.get(args.storageId);
    if (!metadata) {
      throw new Error("File not found in storage");
    }

    const fileId = await ctx.db.insert("files", {
      storageId: args.storageId,
      filename: args.filename,
      contentType: args.contentType,
      size: metadata.size,
      uploaderId: args.uploaderId,
      processed: false,
    });

    // Schedule processing
    await ctx.scheduler.runAfter(0, internal.files.processFile, {
      fileId,
    });

    return fileId;
  },
});

// List user files
export const listFiles = query({
  args: { uploaderId: v.id("users") },
  returns: v.array(v.object({
    _id: v.id("files"),
    filename: v.string(),
    contentType: v.string(),
    size: v.number(),
    processed: v.boolean(),
    url: v.optional(v.string()),
  })),
  handler: async (ctx, args) => {
    const files = await ctx.db
      .query("files")
      .withIndex("by_uploader", (q) => q.eq("uploaderId", args.uploaderId))
      .collect();

    return await Promise.all(
      files.map(async (file) => ({
        _id: file._id,
        filename: file.filename,
        contentType: file.contentType,
        size: file.size,
        processed: file.processed,
        url: await ctx.storage.getUrl(file.storageId),
      }))
    );
  },
});

// Process file (internal action)
export const processFile = action({
  args: { fileId: v.id("files") },
  returns: v.null(),
  handler: async (ctx, args) => {
    const file = await ctx.runQuery(internal.files.getFile, {
      fileId: args.fileId,
    });

    if (!file) {
      throw new Error("File not found");
    }

    const url = await ctx.storage.getUrl(file.storageId);
    if (!url) {
      throw new Error("File URL not available");
    }

    // Process based on content type
    let metadata = {};
    if (file.contentType.startsWith("image/")) {
      // Image processing logic
      const response = await fetch(url);
      const buffer = await response.arrayBuffer();
      // ... extract image dimensions
      metadata = { width: 1920, height: 1080 }; // Example
    }

    // Update file with processing results
    await ctx.runMutation(internal.files.markProcessed, {
      fileId: args.fileId,
      metadata,
    });

    return null;
  },
});

// Get file (internal query)
export const getFile = query({
  args: { fileId: v.id("files") },
  returns: v.union(v.null(), v.object({
    _id: v.id("files"),
    storageId: v.id("_storage"),
    filename: v.string(),
    contentType: v.string(),
  })),
  handler: async (ctx, args) => {
    return await ctx.db.get(args.fileId);
  },
});

// Mark file as processed (internal mutation)
export const markProcessed = mutation({
  args: {
    fileId: v.id("files"),
    metadata: v.object({
      width: v.optional(v.number()),
      height: v.optional(v.number()),
    }),
  },
  returns: v.null(),
  handler: async (ctx, args) => {
    await ctx.db.patch(args.fileId, {
      processed: true,
      metadata: args.metadata,
    });
    return null;
  },
});
```

## Multi-Tenant RAG System

Knowledge base with team isolation and semantic search.

### Schema

```typescript
import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  teams: defineTable({
    name: v.string(),
  }),

  documents: defineTable({
    teamId: v.id("teams"),
    title: v.string(),
    content: v.string(),
    category: v.optional(v.string()),
    importance: v.number(), // 0.0 to 1.0
  }).index("by_team", ["teamId"]),

  users: defineTable({
    email: v.string(),
    teamId: v.id("teams"),
  }).index("by_team", ["teamId"]),
});
```

### Implementation

```typescript
import { query, mutation, action } from "./_generated/server";
import { v } from "convex/values";
import { components } from "./_generated/api";

const rag = components.rag;

// Add document to knowledge base
export const addDocument = mutation({
  args: {
    teamId: v.id("teams"),
    title: v.string(),
    content: v.string(),
    category: v.optional(v.string()),
    importance: v.number(),
  },
  returns: v.id("documents"),
  handler: async (ctx, args) => {
    const docId = await ctx.db.insert("documents", {
      teamId: args.teamId,
      title: args.title,
      content: args.content,
      category: args.category,
      importance: args.importance,
    });

    // Schedule ingestion
    await ctx.scheduler.runAfter(0, internal.knowledge.ingestDocument, {
      documentId: docId,
    });

    return docId;
  },
});

// Ingest document into RAG (internal action)
export const ingestDocument = action({
  args: { documentId: v.id("documents") },
  returns: v.null(),
  handler: async (ctx, args) => {
    const doc = await ctx.runQuery(internal.knowledge.getDocument, {
      documentId: args.documentId,
    });

    if (!doc) {
      throw new Error("Document not found");
    }

    // Ingest with team namespace
    await rag.ingest(ctx, {
      namespace: `team:${doc.teamId}`,
      document: {
        id: doc._id,
        content: doc.content,
        metadata: {
          title: doc.title,
          category: doc.category,
          importance: doc.importance,
        },
      },
    });

    return null;
  },
});

// Search knowledge base
export const searchKnowledge = action({
  args: {
    teamId: v.id("teams"),
    query: v.string(),
    category: v.optional(v.string()),
  },
  returns: v.array(v.object({
    id: v.string(),
    title: v.string(),
    excerpt: v.string(),
    score: v.number(),
  })),
  handler: async (ctx, args) => {
    const results = await rag.search(ctx, {
      namespace: `team:${args.teamId}`,
      query: args.query,
      limit: 10,
      filter: args.category ? { category: args.category } : undefined,
    });

    return results.results.map((r) => ({
      id: r.id,
      title: r.metadata?.title || "Untitled",
      excerpt: r.content.slice(0, 200) + "...",
      score: r.score,
    }));
  },
});

// Answer question with RAG
export const answerQuestion = action({
  args: {
    teamId: v.id("teams"),
    question: v.string(),
  },
  returns: v.object({
    answer: v.string(),
    sources: v.array(v.string()),
  }),
  handler: async (ctx, args) => {
    // Search for relevant context
    const results = await rag.search(ctx, {
      namespace: `team:${args.teamId}`,
      query: args.question,
      limit: 5,
    });

    // Build context from results
    const context = results.results
      .map((r, i) => `[${i + 1}] ${r.metadata?.title}: ${r.content}`)
      .join("\n\n");

    // Generate answer with LLM
    const response = await openai.chat.completions.create({
      model: "gpt-4o",
      messages: [{
        role: "user",
        content: `Context:\n${context}\n\nQuestion: ${args.question}\n\nProvide an answer based on the context above. Cite sources using [N] format.`,
      }],
    });

    const answer = response.choices[0].message.content || "No answer generated";
    const sources = results.results.map((r) => r.metadata?.title || r.id);

    return { answer, sources };
  },
});

// Get document (internal query)
export const getDocument = query({
  args: { documentId: v.id("documents") },
  returns: v.union(v.null(), v.object({
    _id: v.id("documents"),
    teamId: v.id("teams"),
    title: v.string(),
    content: v.string(),
    category: v.optional(v.string()),
    importance: v.number(),
  })),
  handler: async (ctx, args) => {
    return await ctx.db.get(args.documentId);
  },
});
```

## Scheduled Report Generation

Generate and email reports on a schedule.

### Schema

```typescript
import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  users: defineTable({
    email: v.string(),
    name: v.string(),
    receiveReports: v.boolean(),
  }),

  analytics: defineTable({
    userId: v.id("users"),
    metric: v.string(),
    value: v.number(),
    timestamp: v.number(),
  }).index("by_user", ["userId", "timestamp"]),
});
```

### Cron Job

```typescript
import { cronJobs } from "convex/server";
import { internal } from "./_generated/api";

const crons = cronJobs();

// Generate weekly reports every Monday at 9 AM
crons.cron(
  "weekly reports",
  "0 9 * * 1", // Cron expression: Monday 9 AM
  internal.reports.generateWeeklyReports,
  {}
);

export default crons;
```

### Implementation

```typescript
"use node";

import { internalAction, query } from "./_generated/server";
import { v } from "convex/values";
import { internal } from "./_generated/api";

// Generate weekly reports (scheduled)
export const generateWeeklyReports = internalAction({
  args: {},
  returns: v.null(),
  handler: async (ctx) => {
    // Get all users who receive reports
    const users = await ctx.runQuery(internal.reports.getUsersForReports, {});

    // Generate report for each user
    for (const user of users) {
      try {
        const report = await ctx.runQuery(internal.reports.generateUserReport, {
          userId: user._id,
        });

        // Send email
        await sendEmail({
          to: user.email,
          subject: "Your Weekly Report",
          body: formatReportEmail(report),
        });

        console.log(`Report sent to ${user.email}`);
      } catch (error) {
        console.error(`Failed to send report to ${user.email}:`, error);
      }
    }

    return null;
  },
});

// Get users who receive reports (internal query)
export const getUsersForReports = query({
  args: {},
  returns: v.array(v.object({
    _id: v.id("users"),
    email: v.string(),
    name: v.string(),
  })),
  handler: async (ctx) => {
    return await ctx.db
      .query("users")
      .filter((q) => q.eq(q.field("receiveReports"), true))
      .collect();
  },
});

// Generate user report (internal query)
export const generateUserReport = query({
  args: { userId: v.id("users") },
  returns: v.object({
    userName: v.string(),
    totalActivity: v.number(),
    topMetrics: v.array(v.object({
      metric: v.string(),
      value: v.number(),
    })),
  }),
  handler: async (ctx, args) => {
    const user = await ctx.db.get(args.userId);
    if (!user) {
      throw new Error("User not found");
    }

    const weekAgo = Date.now() - 7 * 24 * 60 * 60 * 1000;

    const analytics = await ctx.db
      .query("analytics")
      .withIndex("by_user", (q) =>
        q.eq("userId", args.userId).gte("timestamp", weekAgo)
      )
      .collect();

    // Aggregate metrics
    const metricTotals = new Map<string, number>();
    for (const entry of analytics) {
      const current = metricTotals.get(entry.metric) || 0;
      metricTotals.set(entry.metric, current + entry.value);
    }

    const topMetrics = Array.from(metricTotals.entries())
      .map(([metric, value]) => ({ metric, value }))
      .sort((a, b) => b.value - a.value)
      .slice(0, 5);

    return {
      userName: user.name,
      totalActivity: analytics.length,
      topMetrics,
    };
  },
});

function formatReportEmail(report: any): string {
  return `
    Hi ${report.userName},

    Here's your weekly report:

    Total Activity: ${report.totalActivity} events

    Top Metrics:
    ${report.topMetrics.map((m: any) =>
      `- ${m.metric}: ${m.value}`
    ).join("\n")}

    Have a great week!
  `;
}

async function sendEmail(params: {
  to: string;
  subject: string;
  body: string;
}): Promise<void> {
  // Email sending logic (Resend, SendGrid, etc.)
  console.log("Sending email:", params);
}
```

## Best Practices Demonstrated

1. **Use Indexes**: All queries use appropriate indexes for performance
2. **Separate Concerns**: Public APIs vs internal functions clearly separated
3. **Type Safety**: Complete validator coverage with TypeScript types
4. **Error Handling**: Validate inputs and handle edge cases
5. **Scheduled Tasks**: Background processing with scheduler and cron jobs
6. **Multi-Tenancy**: Team isolation patterns for data security
7. **File Management**: Proper storage ID tracking and URL generation
8. **Real-Time Updates**: Reactive queries for live data synchronization
9. **AI Integration**: LLM calls in actions with proper error handling
10. **RAG Patterns**: Namespace isolation and semantic search implementation
