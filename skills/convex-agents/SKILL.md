---
name: convex-agents
description: Build AI agents on Convex with persistent chat history, durable workflows, tool calling, streaming, generative UI, and RAG. Use when creating AI chatbots, agentic workflows, task automation, or any LLM-powered features in Convex applications.
---

<objective>
Build production-ready AI agents using Convex's @convex-dev/agent component. This skill covers agent architecture, tool design, durable workflows, streaming, generative UI, and RAG integration patterns optimized for real-time applications.

Convex agents provide automatic message persistence, reactive real-time updates, durable execution, and seamless integration with Convex's transactional database.
</objective>

<quick_start>
<installation>
```bash
npm install @convex-dev/agent @ai-sdk/openai
```

```ts
// convex/convex.config.ts
import { defineApp } from "convex/server";
import agent from "@convex-dev/agent/convex.config";

const app = defineApp();
app.use(agent);
export default app;
```

Run `npx convex dev` to generate component code before defining agents.
</installation>

<minimal_agent>
```ts
// convex/agent.ts
import { Agent, createTool } from "@convex-dev/agent";
import { openai } from "@ai-sdk/openai";
import { components, internal } from "./_generated/api";
import { v } from "convex/values";

export const myAgent = new Agent(components.agent, {
  name: "My Agent",
  languageModel: openai.chat("gpt-4o"),
  instructions: "You are a helpful assistant.",
  tools: { /* tools here */ },
  maxSteps: 5,
});
```
</minimal_agent>

<basic_usage>
```ts
// convex/chat.ts
import { action, query } from "./_generated/server";
import { v } from "convex/values";
import { myAgent } from "./agent";

export const sendMessage = action({
  args: { prompt: v.string(), threadId: v.optional(v.string()) },
  handler: async (ctx, { prompt, threadId }) => {
    if (threadId) {
      const { thread } = await myAgent.continueThread(ctx, { threadId });
      const result = await thread.generateText({ prompt });
      return { threadId, text: result.text };
    }
    const { threadId: newId, thread } = await myAgent.createThread(ctx, {});
    const result = await thread.generateText({ prompt });
    return { threadId: newId, text: result.text };
  },
});

export const listMessages = query({
  args: { threadId: v.string() },
  handler: async (ctx, { threadId }) => {
    return await myAgent.listMessages(ctx, { threadId });
  },
});
```
</basic_usage>
</quick_start>

<core_concepts>
<threads>
Threads persist conversation history automatically. They can be shared between multiple users and agents. Each thread maintains message order and supports pagination.

Key patterns:
- One thread per conversation session
- Pass `userId` to `createThread` for user-scoped threads
- Use `continueThread` to resume with full context
- Thread history is automatically included in LLM calls
</threads>

<tools>
Tools let agents interact with your database and external services. Use `createTool` for Convex-native tools that can call mutations and queries.

```ts
import { createTool } from "@convex-dev/agent";
import { v } from "convex/values";

const createTask = createTool({
  description: "Create a new task",
  args: v.object({
    title: v.string(),
    priority: v.union(v.literal("low"), v.literal("medium"), v.literal("high")),
  }),
  handler: async (ctx, args) => {
    const taskId = await ctx.runMutation(internal.tasks.create, args);
    return { success: true, taskId };
  },
});
```

Tool design rules:
- Descriptions must be clear and specific—the LLM uses them to decide when to call
- Return structured data the LLM can reason about
- Use `ctx.runMutation` for writes, `ctx.runQuery` for reads
- Keep handlers focused on one operation
</tools>

<maxSteps>
The `maxSteps` parameter controls how many tool calls the agent can chain. Set higher for complex reasoning tasks that require multiple operations.

Guidelines:
- Simple Q&A: 1-3 steps
- CRUD operations: 3-5 steps
- Complex planning/analysis: 5-10 steps
- Multi-phase workflows: 10+ steps (consider using Workflow component instead)
</maxSteps>
</core_concepts>

<agent_architecture>
<single_agent>
Use a single agent for straightforward applications where one set of instructions and tools covers all use cases.
</single_agent>

<multi_agent>
Split into specialist agents when:
- Different tasks require different models or temperature settings
- Tool sets become large and unfocused (15+ tools)
- Instructions become complex with many conditionals

Common pattern: Primary agent (fast, cheap) for general interaction + Specialist agents (capable) for complex analysis.

See [references/agent-architecture.md](references/agent-architecture.md) for multi-agent patterns, routing strategies, and delegation tools.
</multi_agent>
</agent_architecture>

<tool_patterns>
<data_tools>
Fetch or mutate data. Return raw data for LLM reasoning.

```ts
const listTasks = createTool({
  description: "List tasks with optional filters",
  args: v.object({
    status: v.optional(v.string()),
    assigneeId: v.optional(v.id("users")),
  }),
  handler: async (ctx, args) => {
    return await ctx.runQuery(internal.tasks.list, args);
  },
});
```
</data_tools>

<display_tools>
Return structured data for UI rendering (Generative UI pattern).

```ts
const showTaskList = createTool({
  description: "Display tasks as an interactive list component",
  args: v.object({
    title: v.string(),
    tasks: v.array(v.object({
      id: v.string(),
      title: v.string(),
      status: v.string(),
    })),
  }),
  handler: async (ctx, args) => {
    return { uiType: "taskList", ...args };
  },
});
```

Instruct agents: "When showing tasks, use showTaskList tool" so they produce UI components.
</display_tools>

<action_signal_tools>
Return UI actions for client-side behavior (minimize sheet, navigate, highlight).

```ts
const createTask = createTool({
  description: "Create a task and signal UI to show it",
  args: v.object({ title: v.string(), projectId: v.id("projects") }),
  handler: async (ctx, args) => {
    const taskId = await ctx.runMutation(internal.tasks.create, args);
    return {
      success: true,
      taskId,
      uiAction: {
        type: "minimizeChat",
        highlight: { type: "task", id: taskId },
      },
    };
  },
});
```

See [references/generative-ui.md](references/generative-ui.md) for complete patterns.
</action_signal_tools>
</tool_patterns>

<streaming>
Two streaming approaches:
- **HTTP streaming**: Works well on web, real-time text chunks
- **Database-reactive**: Use `saveStreamDeltas: true` for React Native or when HTTP streaming is unreliable

```ts
const result = await thread.streamText(
  { prompt },
  { saveStreamDeltas: true } // Chunks saved to DB, useQuery auto-updates
);
await result.consumeStream();
```

Use `useUIMessages` hook for rich streaming state (pending, streaming, success).

See [references/streaming.md](references/streaming.md) for platform-specific guidance and React hooks.
</streaming>

<workflows>
Use the Workflow component for multi-step operations requiring durability:

```ts
import { workflow } from "@convex-dev/workflow";

export const planSprintWorkflow = workflow(
  components.workflow,
  {
    args: v.object({ projectId: v.id("projects") }),
  },
  async (step, args) => {
    const tasks = await step.run("getTasks", async (ctx) => {
      return await ctx.runQuery(internal.tasks.list, { projectId: args.projectId });
    });

    const plan = await step.run("generatePlan", async (ctx) => {
      const { thread } = await planningAgent.createThread(ctx, {});
      const result = await thread.generateText({
        prompt: `Plan sprint for: ${JSON.stringify(tasks)}`,
      });
      return JSON.parse(result.text);
    });

    await step.run("applyPlan", async (ctx) => {
      for (const task of plan.tasks) {
        await ctx.runMutation(internal.tasks.update, task);
      }
    });

    return { success: true, plan };
  }
);
```

See [references/workflows.md](references/workflows.md) for patterns.
</workflows>

<rag>
Integrate RAG for context augmentation:

```ts
import { RAG } from "@convex-dev/rag";

const rag = new RAG(components.rag, {
  textEmbeddingModel: openai.embedding("text-embedding-3-small"),
  embeddingDimension: 1536,
});

// As a tool
const searchContext = createTool({
  description: "Search knowledge base for relevant context",
  args: v.object({ query: v.string() }),
  handler: async (ctx, { query }) => {
    const results = await rag.search(ctx, { namespace: "docs", query, limit: 5 });
    return results.text;
  },
});
```

See [references/rag.md](references/rag.md) for patterns.
</rag>

<instructions_guidelines>
<effective_instructions>
Write instructions that:
- Define the agent's role and personality
- Specify when to use which tools
- Establish reasoning frameworks (e.g., "Consider dependencies before prioritizing")
- Set boundaries ("Always confirm before deleting")

```ts
instructions: `You are a project management assistant.

When managing tasks:
1. Use listTasks to understand current state
2. Consider dependencies and priorities
3. Use showTaskList to display results visually

For destructive operations:
- Always confirm with user before deleting
- Explain consequences of bulk updates

For planning:
- Apply Eisenhower matrix: Urgent+Important first
- Identify blockers before scheduling`,
```
</effective_instructions>

<anti_patterns>
Avoid:
- Vague instructions: "Be helpful" (too generic)
- Tool instruction mismatch: Describing tools agent doesn't have
- Missing display guidance: Agent will respond with text instead of UI components
- Over-specification: Let LLM reason; don't script every decision
</anti_patterns>
</instructions_guidelines>

<react_integration>
Use `useQuery` for reactive message subscriptions and `useMutation` for sending. Render message parts by type: text, tool-invocation (in progress), and tool-result (render as GenerativeUI based on `uiType`).

```tsx
const messages = useQuery(api.chat.listMessages, { threadId });
// Render message.parts, switch on part.type and part.result?.uiType
```

See [references/react-native.md](references/react-native.md) for mobile-specific patterns, bottom sheet integration, and animations.
</react_integration>

<common_mistakes>
<mistake name="Not running convex dev first">
The component code must be generated before defining agents. Run `npx convex dev` after adding to convex.config.ts.
</mistake>

<mistake name="Using mutations in query context">
Tools run in action context. Use `ctx.runMutation` and `ctx.runQuery`—not direct database access.
</mistake>

<mistake name="Missing tool descriptions">
The LLM decides when to call tools based on descriptions. Vague descriptions lead to wrong tool selection.
</mistake>

<mistake name="Ignoring maxSteps">
Default maxSteps may be too low for complex tasks. Increase for multi-tool reasoning chains.
</mistake>

<mistake name="Text responses instead of UI">
Without explicit instruction, agents return text. Add to instructions: "When showing X, use the showX tool."
</mistake>

<mistake name="HTTP streaming in React Native">
HTTP streaming may not work reliably in RN. Use database-reactive streaming with `saveStreamDeltas: true`.
</mistake>
</common_mistakes>

<success_criteria>
A well-implemented Convex agent system has:

- Clean separation between data tools and display tools
- Specific, actionable instructions that guide tool usage
- Appropriate maxSteps for task complexity
- Database-reactive streaming for real-time UI updates
- Durable workflows for multi-step operations
- Generative UI components that render tool results
- Proper error handling in tool handlers
- Thread-per-conversation pattern for context management
</success_criteria>

<reference_guides>
For detailed patterns and examples:

- **Agent architecture**: [references/agent-architecture.md](references/agent-architecture.md) - Multi-agent patterns, routing, delegation
- **Tool design**: [references/tools.md](references/tools.md) - Tool patterns, validation, error handling
- **Workflows**: [references/workflows.md](references/workflows.md) - Durable workflows, scheduled jobs, crons
- **Streaming**: [references/streaming.md](references/streaming.md) - Streaming patterns by platform
- **Generative UI**: [references/generative-ui.md](references/generative-ui.md) - UI action signals, component rendering
- **RAG integration**: [references/rag.md](references/rag.md) - Context augmentation patterns
- **React Native**: [references/react-native.md](references/react-native.md) - Mobile-specific patterns
</reference_guides>
