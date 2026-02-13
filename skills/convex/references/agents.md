# Convex Agents Reference

Comprehensive guide to building AI-powered applications with Convex Agents, including LLM integration, conversation persistence, tool calling, and multi-agent workflows.

## What Are Convex Agents?

Convex Agents are AI-powered components that manage LLM interactions with persistent message history, enabling "long-running agentic workflows" that remain separate from UI layers while maintaining real-time reactivity.

**Key Capabilities**:
- Persistent conversation history across sessions
- Tool calling with custom functions
- Streaming text responses
- Structured object generation
- Human-in-the-loop workflows
- Hybrid vector/text search across message history
- Multi-agent orchestration

## Core Architecture

### Components

**Agents**:
- Encapsulate LLM models, prompts, and tools in reusable units
- Define behavior, instructions, and capabilities
- Support multiple LLM providers (OpenAI, Anthropic, etc.)

**Threads**:
- Persist conversation history shareable across users and agents
- Enable multi-session conversations
- Support hybrid vector/text search
- Allow human-AI collaboration

**Messages**:
- Automatically included as conversation context in each LLM call
- Stored persistently for conversation continuity
- Searchable with semantic and text queries

## Setup and Basic Implementation

### Agent Definition

Define agents outside action handlers for reusability:

```typescript
import { Agent } from "@convex-dev/agent";
import { components } from "./_generated/api";
import openai from "openai";

const supportAgent = new Agent(components.agent, {
  name: "Support Agent",
  chat: openai.chat("gpt-4o-mini"),
  instructions: "You are a helpful customer support assistant.",
  tools: {
    accountLookup,
    fileTicket,
    sendEmail
  },
});
```

### Creating and Using Threads

**Create Thread**:
```typescript
import { mutation } from "./_generated/server";
import { v } from "convex/values";

export const createThread = mutation({
  args: { userId: v.id("users") },
  returns: v.id("threads"),
  handler: async (ctx, args) => {
    const threadId = await supportAgent.createThread(ctx);
    // Store threadId with user for later retrieval
    await ctx.db.insert("userThreads", {
      userId: args.userId,
      threadId,
    });
    return threadId;
  },
});
```

**Send Message and Get Response**:
```typescript
import { action } from "./_generated/server";
import { v } from "convex/values";

export const chat = action({
  args: {
    threadId: v.id("threads"),
    message: v.string(),
  },
  returns: v.string(),
  handler: async (ctx, args) => {
    const response = await supportAgent.asTextAction(ctx, {
      threadId: args.threadId,
      userMessage: args.message,
    });
    return response;
  },
});
```

## Text Responses

### Streaming Text

For real-time streaming responses:

```typescript
import { action } from "./_generated/server";
import { v } from "convex/values";

export const streamChat = action({
  args: {
    threadId: v.id("threads"),
    message: v.string(),
  },
  returns: v.null(),
  handler: async (ctx, args) => {
    for await (const chunk of supportAgent.stream(ctx, {
      threadId: args.threadId,
      userMessage: args.message,
    })) {
      // Stream chunk to client
      console.log(chunk);
    }
    return null;
  },
});
```

### Complete Text Response

For non-streaming complete responses:

```typescript
export const chatComplete = action({
  args: {
    threadId: v.id("threads"),
    message: v.string(),
  },
  returns: v.string(),
  handler: async (ctx, args) => {
    const response = await supportAgent.asTextAction(ctx, {
      threadId: args.threadId,
      userMessage: args.message,
    });
    return response;
  },
});
```

## Structured Object Generation

Agents can generate type-safe structured objects instead of text:

```typescript
import { z } from "zod";

const FlightSchema = z.object({
  airline: z.string(),
  flightNumber: z.string(),
  departure: z.string(),
  arrival: z.string(),
  price: z.number(),
});

const travelAgent = new Agent(components.agent, {
  name: "Travel Agent",
  chat: openai.chat("gpt-4o"),
  instructions: "Find and recommend flights based on user preferences.",
  tools: { searchFlights },
});

export const findFlight = action({
  args: {
    threadId: v.id("threads"),
    query: v.string(),
  },
  returns: v.object({
    airline: v.string(),
    flightNumber: v.string(),
    departure: v.string(),
    arrival: v.string(),
    price: v.number(),
  }),
  handler: async (ctx, args) => {
    const flight = await travelAgent.asObjectAction(ctx, {
      threadId: args.threadId,
      userMessage: args.query,
      schema: FlightSchema,
    });
    return flight;
  },
});
```

## Tool Integration

### Defining Tools

Tools extend agent capabilities beyond text generation:

```typescript
import { createTool } from "@convex-dev/agent";
import { z } from "zod";

const accountLookup = createTool({
  description: "Look up customer account information by email",
  args: z.object({
    email: z.string().email(),
  }),
  handler: async (ctx, { email }) => {
    const account = await ctx.runQuery(internal.users.getByEmail, { email });
    if (!account) {
      return "Account not found";
    }
    return `Account ID: ${account._id}, Status: ${account.status}`;
  },
});

const fileTicket = createTool({
  description: "File a support ticket for the customer",
  args: z.object({
    subject: z.string(),
    description: z.string(),
    priority: z.enum(["low", "medium", "high"]),
  }),
  handler: async (ctx, args) => {
    const ticketId = await ctx.runMutation(internal.tickets.create, args);
    return `Ticket ${ticketId} created successfully`;
  },
});
```

### Using Tools in Agents

Pass tools to agent configuration:

```typescript
const supportAgent = new Agent(components.agent, {
  name: "Support Agent",
  chat: openai.chat("gpt-4o-mini"),
  instructions: "Use available tools to help customers with their issues.",
  tools: {
    accountLookup,
    fileTicket,
    sendEmail,
  },
});
```

The LLM will automatically decide when to call tools based on conversation context.

## Thread Management

### Thread Continuation

Preserve conversation context across sessions:

```typescript
export const continueConversation = action({
  args: {
    threadId: v.id("threads"),
    message: v.string(),
  },
  returns: v.string(),
  handler: async (ctx, args) => {
    // Thread history is automatically loaded
    const response = await supportAgent.asTextAction(ctx, {
      threadId: args.threadId,
      userMessage: args.message,
    });
    return response;
  },
});
```

### Searching Thread History

Perform hybrid vector/text search across messages:

```typescript
export const searchThreadHistory = action({
  args: {
    threadId: v.id("threads"),
    query: v.string(),
  },
  returns: v.array(v.string()),
  handler: async (ctx, args) => {
    const results = await supportAgent.searchThread(ctx, {
      threadId: args.threadId,
      query: args.query,
      limit: 5,
    });
    return results.map(r => r.content);
  },
});
```

## Human-in-the-Loop Workflows

Support mixed human-AI collaboration within threads:

```typescript
export const humanResponse = mutation({
  args: {
    threadId: v.id("threads"),
    message: v.string(),
    agentId: v.optional(v.string()),
  },
  returns: v.null(),
  handler: async (ctx, args) => {
    await supportAgent.addMessage(ctx, {
      threadId: args.threadId,
      role: "assistant", // Human agent acting as assistant
      content: args.message,
      metadata: {
        source: "human",
        agentId: args.agentId,
      },
    });
    return null;
  },
});
```

## File Support

Agents automatically handle file attachments in conversations:

```typescript
export const chatWithFile = action({
  args: {
    threadId: v.id("threads"),
    message: v.string(),
    fileId: v.optional(v.id("_storage")),
  },
  returns: v.string(),
  handler: async (ctx, args) => {
    const response = await supportAgent.asTextAction(ctx, {
      threadId: args.threadId,
      userMessage: args.message,
      attachments: args.fileId ? [args.fileId] : undefined,
    });
    return response;
  },
});
```

Files are automatically saved to file storage and included in chat history.

## Multi-Agent Workflows

### Agent Handoff

Transfer conversation between specialized agents:

```typescript
const salesAgent = new Agent(components.agent, {
  name: "Sales Agent",
  chat: openai.chat("gpt-4o"),
  instructions: "Help customers with purchases.",
  tools: { processOrder, checkInventory },
});

const supportAgent = new Agent(components.agent, {
  name: "Support Agent",
  chat: openai.chat("gpt-4o"),
  instructions: "Help customers with technical issues.",
  tools: { fileTicket, checkStatus },
});

export const routeToAgent = action({
  args: {
    threadId: v.id("threads"),
    message: v.string(),
    intent: v.union(v.literal("sales"), v.literal("support")),
  },
  returns: v.string(),
  handler: async (ctx, args) => {
    const agent = args.intent === "sales" ? salesAgent : supportAgent;
    const response = await agent.asTextAction(ctx, {
      threadId: args.threadId,
      userMessage: args.message,
    });
    return response;
  },
});
```

### Parallel Agent Execution

Run multiple agents concurrently and aggregate results:

```typescript
export const consultExperts = action({
  args: {
    threadId: v.id("threads"),
    question: v.string(),
  },
  returns: v.string(),
  handler: async (ctx, args) => {
    const [techResponse, bizResponse, legalResponse] = await Promise.all([
      techAgent.asTextAction(ctx, {
        threadId: args.threadId,
        userMessage: args.question
      }),
      bizAgent.asTextAction(ctx, {
        threadId: args.threadId,
        userMessage: args.question
      }),
      legalAgent.asTextAction(ctx, {
        threadId: args.threadId,
        userMessage: args.question
      }),
    ]);

    // Aggregate responses with a coordinator agent
    const finalResponse = await coordinatorAgent.asTextAction(ctx, {
      threadId: args.threadId,
      userMessage: `Synthesize these expert opinions:\n\nTech: ${techResponse}\n\nBusiness: ${bizResponse}\n\nLegal: ${legalResponse}`,
    });

    return finalResponse;
  },
});
```

## Rate Limiting

Prevent provider quota violations:

```typescript
import { RateLimiter } from "@convex-dev/rate-limiter";

const rateLimiter = new RateLimiter(components.rateLimiter, {
  maxRequests: 10,
  windowMs: 60000, // 10 requests per minute
});

export const rateLimitedChat = action({
  args: {
    userId: v.id("users"),
    threadId: v.id("threads"),
    message: v.string(),
  },
  returns: v.string(),
  handler: async (ctx, args) => {
    // Check rate limit
    const allowed = await rateLimiter.check(ctx, args.userId);
    if (!allowed) {
      throw new Error("Rate limit exceeded. Please try again later.");
    }

    const response = await supportAgent.asTextAction(ctx, {
      threadId: args.threadId,
      userMessage: args.message,
    });

    return response;
  },
});
```

## Usage Tracking

Track LLM costs per user or team:

```typescript
export const trackUsage = mutation({
  args: {
    userId: v.id("users"),
    threadId: v.id("threads"),
    tokensUsed: v.number(),
    cost: v.number(),
  },
  returns: v.null(),
  handler: async (ctx, args) => {
    await ctx.db.insert("usage", {
      userId: args.userId,
      threadId: args.threadId,
      tokensUsed: args.tokensUsed,
      cost: args.cost,
      timestamp: Date.now(),
    });
    return null;
  },
});
```

## Debugging and Monitoring

### Agent Playground

Use the Convex dashboard's agent playground to:
- Test prompts interactively
- Inspect message metadata
- Debug tool calling behavior
- Monitor token usage
- View conversation history

### Logging

Add comprehensive logging for production debugging:

```typescript
export const debugChat = action({
  args: {
    threadId: v.id("threads"),
    message: v.string(),
  },
  returns: v.string(),
  handler: async (ctx, args) => {
    console.log("Chat request:", {
      threadId: args.threadId,
      message: args.message
    });

    const startTime = Date.now();
    const response = await supportAgent.asTextAction(ctx, {
      threadId: args.threadId,
      userMessage: args.message,
    });
    const duration = Date.now() - startTime;

    console.log("Chat response:", {
      duration,
      responseLength: response.length
    });

    return response;
  },
});
```

## Best Practices

1. **Organize Agent Definitions**: Define agents outside action handlers for reusability across functions
2. **Leverage Thread Continuation**: Preserve conversation context across sessions for coherent multi-turn dialogues
3. **Use Tools Strategically**: Extend agent capabilities with well-defined tools that have clear descriptions
4. **Implement Rate Limiting**: Protect against quota violations and abuse before production deployment
5. **Track Usage**: Monitor costs per user/team for billing and optimization
6. **Structure Instructions Clearly**: Write precise, actionable instructions for consistent agent behavior
7. **Handle Errors Gracefully**: Wrap agent calls in try-catch blocks and provide meaningful error messages
8. **Test in Playground**: Iterate on prompts and tools using the agent playground before deployment
9. **Use Structured Outputs**: When possible, use `asObjectAction` for type-safe, predictable responses
10. **Separate Concerns**: Use multiple specialized agents rather than one general-purpose agent

## Common Patterns

### ReAct (Reasoning + Acting) Loop

Agent reasons about actions before executing them:

```typescript
const reactAgent = new Agent(components.agent, {
  name: "ReAct Agent",
  chat: openai.chat("gpt-4o"),
  instructions: `Think step-by-step before acting:
    1. Analyze the user's request
    2. Determine which tools are needed
    3. Execute tools in the right order
    4. Synthesize results into a coherent response`,
  tools: { search, calculate, fetchData },
});
```

### Fallback Chain

Try multiple agents with fallback logic:

```typescript
export const robustChat = action({
  args: { threadId: v.id("threads"), message: v.string() },
  returns: v.string(),
  handler: async (ctx, args) => {
    try {
      return await primaryAgent.asTextAction(ctx, {
        threadId: args.threadId,
        userMessage: args.message,
      });
    } catch (error) {
      console.warn("Primary agent failed, trying fallback:", error);
      return await fallbackAgent.asTextAction(ctx, {
        threadId: args.threadId,
        userMessage: args.message,
      });
    }
  },
});
```

### Context Injection

Dynamically inject context before agent processing:

```typescript
export const contextualChat = action({
  args: {
    threadId: v.id("threads"),
    userId: v.id("users"),
    message: v.string(),
  },
  returns: v.string(),
  handler: async (ctx, args) => {
    // Load user context
    const user = await ctx.runQuery(internal.users.get, { userId: args.userId });
    const recentActivity = await ctx.runQuery(internal.activity.getRecent, {
      userId: args.userId
    });

    // Inject context into message
    const contextualMessage = `User: ${user.name} (${user.email})
Recent activity: ${recentActivity}

User message: ${args.message}`;

    return await supportAgent.asTextAction(ctx, {
      threadId: args.threadId,
      userMessage: contextualMessage,
    });
  },
});
```
