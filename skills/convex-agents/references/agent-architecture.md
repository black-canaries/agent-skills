<agent_architecture>
<overview>
Agent Architecture Patterns for Convex agents - single vs multi-agent design, routing strategies, and context sharing.
</overview>

<single_vs_multi_agent>
<when_single_agent>
Use a single agent when:
- The domain is focused (e.g., customer support for one product)
- Tool count is manageable (under 10-15 tools)
- Instructions fit in under 500 words without conditionals
- All tasks benefit from the same model/temperature
</when_single_agent>

<when_multi_agent>
Split when:
- Different tasks need different models (fast vs capable)
- Tool sets exceed 15+ and become unfocused
- Instructions become complex with many "if X then Y" patterns
- Some tasks need higher maxSteps than others
- You want to isolate billing/usage tracking per capability
</when_multi_agent>
</single_vs_multi_agent>

<multi_agent_patterns>
<primary_specialist_pattern>
The primary agent handles most interactions and delegates complex work.

```ts
// Primary: Fast, cheap, handles 80% of requests
export const assistant = new Agent(components.agent, {
  name: "Assistant",
  languageModel: openai.chat("gpt-4o-mini"),
  instructions: `You are a helpful project assistant.

Handle these directly:
- Task CRUD operations
- Status questions
- Simple searches

Delegate to Planning Agent for:
- Sprint planning
- Workload optimization
- Dependency analysis
- Risk assessment

When delegating, use the requestAnalysis tool.`,
  tools: {
    createTask,
    updateTask,
    listTasks,
    searchTasks,
    requestAnalysis, // Delegation tool
  },
  maxSteps: 5,
});

// Specialist: More capable, handles complex reasoning
export const planningAgent = new Agent(components.agent, {
  name: "Planning Agent",
  languageModel: openai.chat("gpt-4o"),
  instructions: `You are a project planning specialist.

When analyzing:
1. Gather all relevant data first
2. Consider dependencies, priorities, deadlines
3. Identify risks and bottlenecks
4. Provide concrete recommendations with reasoning

Always explain your methodology.`,
  tools: {
    getTasksWithDependencies,
    getTeamWorkload,
    identifyBottlenecks,
    calculateCriticalPath,
    showPlanningReport,
  },
  maxSteps: 10,
});
```
</primary_specialist_pattern>

<delegation_tool_pattern>
```ts
const requestAnalysis = createTool({
  description: "Delegate complex analysis to the Planning Agent. Use for sprint planning, optimization, risk assessment.",
  args: v.object({
    analysisType: v.union(
      v.literal("sprint_planning"),
      v.literal("workload_optimization"),
      v.literal("risk_assessment")
    ),
    projectId: v.id("projects"),
    additionalContext: v.optional(v.string()),
  }),
  handler: async (ctx, args) => {
    // Option 1: Run synchronously in same action
    const { thread } = await planningAgent.createThread(ctx, {});
    const result = await thread.generateText({
      prompt: `Perform ${args.analysisType} for project ${args.projectId}. ${args.additionalContext ?? ""}`,
    });
    return result.text;

    // Option 2: Schedule async and return immediately
    // await ctx.scheduler.runAfter(0, internal.analysis.run, args);
    // return "Analysis started. Results will appear shortly.";
  },
});
```
</delegation_tool_pattern>
</multi_agent_patterns>

<routing_strategies>
<keyword_routing>
Simple but effective for clear intent separation.

```ts
export const sendMessage = action({
  args: { prompt: v.string(), threadId: v.optional(v.string()) },
  handler: async (ctx, { prompt, threadId }) => {
    // Route based on keywords
    const isPlanningRequest = /optimize|plan|schedule|sprint|prioritize|workload|analyze/i.test(prompt);
    const agent = isPlanningRequest ? planningAgent : assistant;

    if (threadId) {
      const { thread } = await agent.continueThread(ctx, { threadId });
      const result = await thread.generateText({ prompt });
      return { threadId, text: result.text };
    }

    const { threadId: newId, thread } = await agent.createThread(ctx, {});
    const result = await thread.generateText({ prompt });
    return { threadId: newId, text: result.text };
  },
});
```
</keyword_routing>

<intent_classification_routing>
Use a lightweight LLM call to classify intent.

```ts
const classifyIntent = async (prompt: string): Promise<"general" | "planning" | "reporting"> => {
  const result = await generateText({
    model: openai.chat("gpt-4o-mini"),
    prompt: `Classify this user request into one category:
- general: Task CRUD, questions, searches
- planning: Optimization, scheduling, sprint planning
- reporting: Analytics, metrics, summaries

Request: "${prompt}"

Respond with only the category name.`,
  });
  return result.text.trim().toLowerCase() as any;
};

export const sendMessage = action({
  args: { prompt: v.string(), threadId: v.optional(v.string()) },
  handler: async (ctx, { prompt, threadId }) => {
    const intent = await classifyIntent(prompt);

    const agents = {
      general: assistant,
      planning: planningAgent,
      reporting: reportingAgent,
    };

    const agent = agents[intent];
    // ... continue with agent
  },
});
```
</intent_classification_routing>

<thread_sticky_routing>
Keep the same agent for a conversation unless explicitly switched.

```ts
export const sendMessage = action({
  args: {
    prompt: v.string(),
    threadId: v.optional(v.string()),
    forceAgent: v.optional(v.string()), // Allow explicit switch
  },
  handler: async (ctx, { prompt, threadId, forceAgent }) => {
    let agent = assistant; // default

    if (threadId) {
      // Get stored agent preference for this thread
      const threadMeta = await ctx.runQuery(internal.threads.getMeta, { threadId });
      if (threadMeta?.agentName) {
        agent = agents[threadMeta.agentName];
      }
    }

    // Allow override
    if (forceAgent && agents[forceAgent]) {
      agent = agents[forceAgent];
    }

    // ... continue and store agent choice in thread metadata
  },
});
```
</thread_sticky_routing>
</routing_strategies>

<shared_thread_patterns>
<multiple_agents_same_thread>
Agents can share a thread for handoffs.

```ts
// User starts with assistant
const { threadId, thread } = await assistant.createThread(ctx, { userId });
await thread.generateText({ prompt: "Help me plan my sprint" });

// Assistant delegates to planner using SAME thread
const { thread: plannerThread } = await planningAgent.continueThread(ctx, { threadId });
await plannerThread.generateText({ prompt: "Generate sprint plan based on conversation" });

// All messages in one thread, visible to user
```
</multiple_agents_same_thread>

<isolated_threads_per_agent>
Keep agent work separate, summarize results.

```ts
const requestAnalysis = createTool({
  description: "Request deep analysis",
  args: v.object({ projectId: v.id("projects") }),
  handler: async (ctx, args) => {
    // Create separate thread for analyst
    const { thread } = await planningAgent.createThread(ctx, {});
    const result = await thread.generateText({
      prompt: `Analyze project ${args.projectId}`,
    });

    // Return summary to main conversation
    return {
      summary: result.text,
      // Don't expose internal thread ID
    };
  },
});
```
</isolated_threads_per_agent>
</shared_thread_patterns>

<context_sharing>
<injecting_project_context>
```ts
export const sendMessage = action({
  args: {
    prompt: v.string(),
    threadId: v.optional(v.string()),
    projectId: v.optional(v.id("projects")),
  },
  handler: async (ctx, { prompt, threadId, projectId }) => {
    let contextualPrompt = prompt;

    if (projectId) {
      const project = await ctx.runQuery(internal.projects.get, { projectId });
      contextualPrompt = `[Context: Working in project "${project.name}" (${projectId})]

${prompt}`;
    }

    const { thread } = await agent.continueThread(ctx, { threadId });
    const result = await thread.generateText({ prompt: contextualPrompt });
    return result.text;
  },
});
```
</injecting_project_context>

<system_context_via_instructions>
```ts
const createProjectAgent = (projectId: Id<"projects">) => {
  return new Agent(components.agent, {
    name: "Project Assistant",
    languageModel: openai.chat("gpt-4o"),
    instructions: `You are assisting with project ${projectId}.

All task operations should default to this project unless specified otherwise.`,
    tools: { /* ... */ },
  });
};
```
</system_context_via_instructions>
</context_sharing>
</agent_architecture>
