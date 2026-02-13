# Convex Workflows Reference

Comprehensive guide to building reliable multi-step agentic workflows with durability, retries, and orchestration patterns.

## What Are Workflows?

Convex Workflows decompose agentic processes into two core elements:
1. **Prompting an LLM** with message history and context
2. **Deciding what to do with the response** through business logic

Workflows are characterized by:
- **Multiple steps** involving LLM calls and business logic
- **Dynamic decision-making** based on LLM outputs
- **Long-lived processes** that survive server restarts
- **Mix of AI and traditional logic** in a single flow

## Key Characteristics

### Durable Functions

Workflows leverage durable functions with strong guarantees:
- **Resumability**: Pick up from where they left off after crashes
- **Retries**: Automatic exponential backoff for failures
- **Idempotency**: Prevent duplicate work on retries
- **Completion**: Guaranteed to finish successfully or fail permanently

### Simple Example

Chain operations with guaranteed completion:

```typescript
import { action } from "./_generated/server";
import { v } from "convex/values";
import { internal } from "./_generated/api";

export const weatherFashionAdvice = action({
  args: { city: v.string() },
  returns: v.string(),
  handler: async (ctx, args) => {
    // Step 1: Get weather data
    const weather = await ctx.runAction(internal.weather.fetch, {
      city: args.city
    });

    // Step 2: Generate fashion advice based on weather
    const advice = await openai.chat.completions.create({
      model: "gpt-4o",
      messages: [{
        role: "user",
        content: `Given this weather: ${weather}, what should I wear?`
      }],
    });

    return advice.choices[0].message.content || "No advice available";
  },
});
```

## Building Reliable Workflows

### 1. Retries

**Built-in for Mutations**:
Convex mutations include retry logic by default with exponential backoff.

**Action Retrier Component**:
For actions requiring external calls:

```typescript
import { ActionRetrier } from "@convex-dev/action-retrier";
import { components } from "./_generated/api";

const retrier = new ActionRetrier(components.actionRetrier);

export const reliableExternalCall = action({
  args: { url: v.string() },
  returns: v.string(),
  handler: async (ctx, args) => {
    const result = await retrier.run(ctx, async () => {
      const response = await fetch(args.url);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      return await response.text();
    }, {
      maxAttempts: 5,
      initialDelayMs: 1000,
      maxDelayMs: 30000,
      backoffFactor: 2,
    });

    return result;
  },
});
```

**Configuration Options**:
- `maxAttempts`: Maximum retry attempts
- `initialDelayMs`: Initial delay before first retry
- `maxDelayMs`: Maximum delay between retries
- `backoffFactor`: Exponential backoff multiplier

### 2. Load Balancing

**Workpool Component**:
Manage concurrent resource consumption in serverless environments:

```typescript
import { Workpool } from "@convex-dev/workpool";
import { components } from "./_generated/api";

const workpool = new Workpool(components.workpool, {
  maxConcurrent: 10, // Maximum concurrent workers
});

export const processDocuments = mutation({
  args: { documentIds: v.array(v.id("documents")) },
  returns: v.null(),
  handler: async (ctx, args) => {
    for (const docId of args.documentIds) {
      // Queue work with load balancing
      await workpool.schedule(ctx, internal.documents.process, {
        documentId: docId,
      });
    }
    return null;
  },
});
```

**Use Cases**:
- RAG data ingestion with spiky workloads
- Batch processing with rate limits
- Parallel LLM calls with quota management
- Resource-intensive operations

### 3. Durability & Idempotency

**Workflow Component**:
Ensures workflows resume after crashes and prevent duplicate work:

```typescript
import { WorkflowManager } from "@convex-dev/workflow";
import { components } from "./_generated/api";
import { v } from "convex/values";

const workflows = new WorkflowManager(components.workflow);

export const durableMultiStepFlow = mutation({
  args: { userId: v.id("users"), taskId: v.id("tasks") },
  returns: v.null(),
  handler: async (ctx, args) => {
    await workflows.start(ctx, "processTask", {
      userId: args.userId,
      taskId: args.taskId,
    }, async (step) => {
      // Step 1: Validate task
      const validation = await step.runQuery(internal.tasks.validate, {
        taskId: args.taskId,
      });

      if (!validation.isValid) {
        throw new Error("Task validation failed");
      }

      // Step 2: Process with AI
      const aiResult = await step.runAction(internal.ai.processTask, {
        taskId: args.taskId,
      });

      // Step 3: Save results
      await step.runMutation(internal.tasks.saveResults, {
        taskId: args.taskId,
        results: aiResult,
      });

      // Step 4: Notify user
      await step.runAction(internal.notifications.send, {
        userId: args.userId,
        message: "Task processing complete",
      });
    });

    return null;
  },
});
```

**Workflow Benefits**:
- Automatic checkpoint after each step
- Resume from last completed step on failure
- Idempotent step execution (won't re-run completed steps)
- Transactional guarantees per step

## Implementation Patterns

### Exposing Agent Capabilities

Make agents usable within workflows:

```typescript
import { Agent } from "@convex-dev/agent";
import { components } from "./_generated/api";

const supportAgent = new Agent(components.agent, {
  name: "Support Agent",
  chat: openai.chat("gpt-4o-mini"),
  instructions: "Help users with support requests",
  tools: { fileTicket, lookupAccount },
});

// Create thread (mutation)
export const createSupportThread = supportAgent.createThreadMutation();

// Generate text response (action)
export const getSupportResponse = supportAgent.asTextAction();

// Generate structured output (action)
export const getSupportDecision = supportAgent.asObjectAction();

// Save messages explicitly (mutation)
export const saveSupportMessages = supportAgent.asSaveMessagesMutation();
```

### Workflow with Step Manager

Integrate agent actions using `step.runMutation()` and `step.runAction()`:

```typescript
export const supportWorkflow = mutation({
  args: {
    userId: v.id("users"),
    issue: v.string(),
  },
  returns: v.null(),
  handler: async (ctx, args) => {
    await workflows.start(ctx, "handleSupport", args, async (step) => {
      // Step 1: Create thread for conversation
      const threadId: Id<"threads"> = await step.runMutation(
        internal.support.createSupportThread,
        {}
      );

      // Step 2: Get initial AI response
      const response: string = await step.runAction(
        internal.support.getSupportResponse,
        {
          threadId,
          userMessage: args.issue,
        }
      );

      // Step 3: If issue requires escalation, create ticket
      const decision: { escalate: boolean, priority: string } =
        await step.runAction(
          internal.support.getSupportDecision,
          {
            threadId,
            userMessage: "Should this be escalated?",
            schema: z.object({
              escalate: z.boolean(),
              priority: z.enum(["low", "medium", "high"]),
            }),
          }
        );

      if (decision.escalate) {
        // Step 4: Create support ticket
        await step.runMutation(
          internal.tickets.create,
          {
            userId: args.userId,
            priority: decision.priority,
            description: args.issue,
          }
        );
      }

      // Step 5: Save final messages to thread
      await step.runMutation(
        internal.support.saveSupportMessages,
        {
          threadId,
          messages: [{
            role: "assistant",
            content: response,
          }],
        }
      );
    });

    return null;
  },
});
```

**Type Annotations**:
When calling same-file functions within workflow steps, add type annotations to work around TypeScript circularity:

```typescript
const threadId: Id<"threads"> = await step.runMutation(
  internal.support.createThread,
  {}
);
```

## Advanced Patterns

### Dynamic Agent Routing

Route to different agents based on intent:

```typescript
export const routedWorkflow = mutation({
  args: {
    userId: v.id("users"),
    message: v.string(),
  },
  returns: v.null(),
  handler: async (ctx, args) => {
    await workflows.start(ctx, "routeIntent", args, async (step) => {
      // Step 1: Classify intent
      const intent: { type: string, confidence: number } = await step.runAction(
        internal.ai.classifyIntent,
        { message: args.message }
      );

      // Step 2: Route to appropriate agent
      let agentResponse: string;
      if (intent.type === "sales") {
        agentResponse = await step.runAction(
          internal.agents.sales.respond,
          { message: args.message }
        );
      } else if (intent.type === "support") {
        agentResponse = await step.runAction(
          internal.agents.support.respond,
          { message: args.message }
        );
      } else {
        agentResponse = await step.runAction(
          internal.agents.general.respond,
          { message: args.message }
        );
      }

      // Step 3: Save interaction
      await step.runMutation(
        internal.interactions.save,
        {
          userId: args.userId,
          intent: intent.type,
          response: agentResponse,
        }
      );
    });

    return null;
  },
});
```

### Parallel LLM Calls

Execute multiple LLM calls concurrently and aggregate:

```typescript
export const parallelAnalysis = mutation({
  args: { documentId: v.id("documents") },
  returns: v.null(),
  handler: async (ctx, args) => {
    await workflows.start(ctx, "analyzeDocument", args, async (step) => {
      // Step 1: Fetch document
      const doc = await step.runQuery(
        internal.documents.get,
        { documentId: args.documentId }
      );

      // Step 2: Run parallel analyses
      const [sentiment, topics, summary] = await Promise.all([
        step.runAction(internal.ai.analyzeSentiment, { text: doc.content }),
        step.runAction(internal.ai.extractTopics, { text: doc.content }),
        step.runAction(internal.ai.summarize, { text: doc.content }),
      ]);

      // Step 3: Aggregate results
      await step.runMutation(
        internal.documents.saveAnalysis,
        {
          documentId: args.documentId,
          sentiment,
          topics,
          summary,
        }
      );
    });

    return null;
  },
});
```

### Multi-Agent Orchestration

Coordinate multiple agents for complex tasks:

```typescript
export const multiAgentResearch = mutation({
  args: { query: v.string() },
  returns: v.null(),
  handler: async (ctx, args) => {
    await workflows.start(ctx, "research", args, async (step) => {
      // Step 1: Research agent gathers information
      const research: string = await step.runAction(
        internal.agents.researcher.investigate,
        { query: args.query }
      );

      // Step 2: Analyst agent evaluates findings
      const analysis: { findings: string[], confidence: number } =
        await step.runAction(
          internal.agents.analyst.evaluate,
          { research }
        );

      // Step 3: If confidence low, critic agent provides feedback
      let finalReport: string;
      if (analysis.confidence < 0.8) {
        const critique: string = await step.runAction(
          internal.agents.critic.review,
          { analysis: analysis.findings.join("\n") }
        );

        // Step 4: Researcher incorporates feedback
        const revisedResearch: string = await step.runAction(
          internal.agents.researcher.refine,
          {
            original: research,
            critique,
          }
        );

        finalReport = revisedResearch;
      } else {
        finalReport = analysis.findings.join("\n");
      }

      // Step 5: Save final report
      await step.runMutation(
        internal.reports.save,
        {
          query: args.query,
          report: finalReport,
        }
      );
    });

    return null;
  },
});
```

### ReAct Cycles

Implement Reasoning + Acting loops:

```typescript
export const reactWorkflow = mutation({
  args: {
    threadId: v.id("threads"),
    task: v.string(),
  },
  returns: v.null(),
  handler: async (ctx, args) => {
    await workflows.start(ctx, "react", args, async (step) => {
      let maxIterations = 5;
      let completed = false;

      for (let i = 0; i < maxIterations && !completed; i++) {
        // Think: Agent reasons about next action
        const thought: { action: string, complete: boolean } =
          await step.runAction(
            internal.agents.reactor.think,
            {
              threadId: args.threadId,
              task: args.task,
            }
          );

        if (thought.complete) {
          completed = true;
          break;
        }

        // Act: Execute the decided action
        const result: string = await step.runAction(
          internal.agents.reactor.act,
          {
            threadId: args.threadId,
            action: thought.action,
          }
        );

        // Observe: Record action result for next iteration
        await step.runMutation(
          internal.agents.reactor.observe,
          {
            threadId: args.threadId,
            observation: result,
          }
        );
      }

      if (!completed) {
        // Handle max iterations reached
        await step.runMutation(
          internal.errors.log,
          {
            workflowId: "react",
            error: "Max iterations reached without completion",
          }
        );
      }
    });

    return null;
  },
});
```

### Pauseable Workflows

Pause for human input or external events:

```typescript
export const pauseableWorkflow = mutation({
  args: { taskId: v.id("tasks") },
  returns: v.null(),
  handler: async (ctx, args) => {
    await workflows.start(ctx, "reviewTask", args, async (step) => {
      // Step 1: AI processes task
      const aiResult = await step.runAction(
        internal.ai.processTask,
        { taskId: args.taskId }
      );

      // Step 2: Request human review
      await step.runMutation(
        internal.reviews.requestHuman,
        {
          taskId: args.taskId,
          aiResult,
          status: "pending_review",
        }
      );

      // Step 3: Wait for human approval (workflow pauses here)
      const approval = await step.waitFor(
        internal.reviews.checkApproval,
        { taskId: args.taskId }
      );

      // Step 4: Apply feedback if needed
      if (!approval.approved) {
        const revised = await step.runAction(
          internal.ai.reviseTask,
          {
            taskId: args.taskId,
            feedback: approval.feedback,
          }
        );

        // Save revised result
        await step.runMutation(
          internal.tasks.saveRevised,
          {
            taskId: args.taskId,
            result: revised,
          }
        );
      } else {
        // Save original result
        await step.runMutation(
          internal.tasks.saveApproved,
          {
            taskId: args.taskId,
            result: aiResult,
          }
        );
      }
    });

    return null;
  },
});
```

## Error Handling

### Try-Catch in Steps

Handle errors gracefully within workflow steps:

```typescript
export const resilientWorkflow = mutation({
  args: { taskId: v.id("tasks") },
  returns: v.null(),
  handler: async (ctx, args) => {
    await workflows.start(ctx, "resilient", args, async (step) => {
      try {
        // Attempt primary processing
        const result = await step.runAction(
          internal.ai.processPrimary,
          { taskId: args.taskId }
        );

        await step.runMutation(
          internal.tasks.saveResult,
          { taskId: args.taskId, result }
        );
      } catch (error) {
        // Log error
        await step.runMutation(
          internal.errors.log,
          {
            taskId: args.taskId,
            error: String(error),
          }
        );

        // Fallback processing
        const fallbackResult = await step.runAction(
          internal.ai.processFallback,
          { taskId: args.taskId }
        );

        await step.runMutation(
          internal.tasks.saveResult,
          {
            taskId: args.taskId,
            result: fallbackResult,
            isFallback: true,
          }
        );
      }
    });

    return null;
  },
});
```

### Compensating Transactions

Rollback on failure:

```typescript
export const transactionalWorkflow = mutation({
  args: { orderId: v.id("orders") },
  returns: v.null(),
  handler: async (ctx, args) => {
    await workflows.start(ctx, "processOrder", args, async (step) => {
      // Step 1: Reserve inventory
      const reservationId = await step.runMutation(
        internal.inventory.reserve,
        { orderId: args.orderId }
      );

      try {
        // Step 2: Charge payment
        const paymentId = await step.runAction(
          internal.payments.charge,
          { orderId: args.orderId }
        );

        // Step 3: Fulfill order
        await step.runMutation(
          internal.orders.fulfill,
          {
            orderId: args.orderId,
            paymentId,
          }
        );
      } catch (error) {
        // Compensate: Release reservation
        await step.runMutation(
          internal.inventory.release,
          { reservationId }
        );

        throw error; // Re-throw to mark workflow as failed
      }
    });

    return null;
  },
});
```

## Best Practices

1. **Use Step Manager**: Always wrap workflow logic in `workflows.start()` for durability
2. **Add Type Annotations**: Specify return types for same-file function calls in workflows
3. **Handle Errors Gracefully**: Use try-catch blocks and compensating transactions
4. **Minimize Action-to-Query Calls**: Batch data fetching to reduce round trips
5. **Leverage Workpool**: Use for rate-limited or resource-intensive operations
6. **Implement Retries**: Use ActionRetrier for external API calls
7. **Design Idempotent Steps**: Ensure steps can safely re-run without side effects
8. **Monitor Workflow Status**: Log progress and errors for debugging
9. **Set Reasonable Timeouts**: Prevent workflows from running indefinitely
10. **Test Failure Scenarios**: Verify workflow resumption after simulated crashes

## Common Patterns Summary

| Pattern | Use Case | Key Component |
|---------|----------|---------------|
| **Retries** | External API calls | ActionRetrier |
| **Load Balancing** | Spiky workloads | Workpool |
| **Durability** | Multi-step processes | WorkflowManager |
| **Dynamic Routing** | Intent-based agents | Conditional logic + agents |
| **Parallel Execution** | Multiple LLM calls | Promise.all + steps |
| **Multi-Agent** | Complex coordination | Sequential agent calls |
| **ReAct** | Iterative reasoning | Loop with think-act-observe |
| **Pauseable** | Human-in-the-loop | step.waitFor |
| **Error Handling** | Graceful degradation | Try-catch + fallbacks |
| **Compensation** | Transactional rollback | Cleanup in catch blocks |

## Debugging Workflows

### Logging

Add comprehensive logging for visibility:

```typescript
await workflows.start(ctx, "debugWorkflow", args, async (step) => {
  console.log("Workflow started", { args });

  const result1 = await step.runAction(internal.step1, args);
  console.log("Step 1 complete", { result1 });

  const result2 = await step.runMutation(internal.step2, { result1 });
  console.log("Step 2 complete", { result2 });

  console.log("Workflow complete");
});
```

### Status Tracking

Store workflow state for monitoring:

```typescript
export const trackedWorkflow = mutation({
  args: { taskId: v.id("tasks") },
  returns: v.null(),
  handler: async (ctx, args) => {
    const workflowId = await ctx.db.insert("workflowStatus", {
      taskId: args.taskId,
      status: "running",
      currentStep: "init",
    });

    try {
      await workflows.start(ctx, "tracked", args, async (step) => {
        await ctx.db.patch(workflowId, { currentStep: "step1" });
        await step.runAction(internal.step1, args);

        await ctx.db.patch(workflowId, { currentStep: "step2" });
        await step.runAction(internal.step2, args);

        await ctx.db.patch(workflowId, { currentStep: "complete" });
      });

      await ctx.db.patch(workflowId, { status: "completed" });
    } catch (error) {
      await ctx.db.patch(workflowId, {
        status: "failed",
        error: String(error),
      });
      throw error;
    }

    return null;
  },
});
```
