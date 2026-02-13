<workflows>
<overview>
Durable workflows for Convex agents - when to use workflows, structure, examples, crons, and best practices for multi-step operations.
</overview>

<when_to_use>
Use the Workflow component instead of plain actions when you need durability guarantees for multi-step operations that could fail midway, operations that span multiple agent calls, long-running processes that might outlive a single request, or scheduled and recurring tasks.
</when_to_use>

<basic_structure>
```ts
import { workflow } from "@convex-dev/workflow";
import { components, internal } from "./_generated/api";
import { v } from "convex/values";

export const myWorkflow = workflow(
  components.workflow,
  {
    args: v.object({
      projectId: v.id("projects"),
    }),
  },
  async (step, args) => {
    // Step 1: Each step.run is checkpointed
    const data = await step.run("fetchData", async (ctx) => {
      return await ctx.runQuery(internal.projects.get, { id: args.projectId });
    });

    // Step 2: If this fails, workflow resumes here on retry
    const analysis = await step.run("analyze", async (ctx) => {
      const { thread } = await myAgent.createThread(ctx, {});
      const result = await thread.generateText({ prompt: `Analyze: ${JSON.stringify(data)}` });
      return result.text;
    });

    // Step 3: Final step
    await step.run("saveResults", async (ctx) => {
      await ctx.runMutation(internal.analysis.save, { projectId: args.projectId, analysis });
    });

    return { success: true, analysis };
  }
);
```
</basic_structure>

<examples>
<sprint_planning_workflow>
A complete example for project management.

```ts
export const sprintPlanningWorkflow = workflow(
  components.workflow,
  {
    args: v.object({
      projectId: v.id("projects"),
      sprintStartDate: v.string(),
      sprintEndDate: v.string(),
      teamCapacityHours: v.number(),
    }),
  },
  async (step, args) => {
    // Step 1: Gather backlog
    const backlog = await step.run("getBacklog", async (ctx) => {
      return await ctx.runQuery(internal.tasks.list, {
        projectId: args.projectId,
        status: "backlog",
      });
    });

    // Step 2: Get team availability
    const teamWorkload = await step.run("getTeamWorkload", async (ctx) => {
      return await ctx.runQuery(internal.analytics.teamWorkload, {
        projectId: args.projectId,
        startDate: args.sprintStartDate,
        endDate: args.sprintEndDate,
      });
    });

    // Step 3: AI-powered sprint selection
    const sprintPlan = await step.run("generatePlan", async (ctx) => {
      const { thread } = await planningAgent.createThread(ctx, {});
      const result = await thread.generateText({
        prompt: `Given:
- Backlog tasks: ${JSON.stringify(backlog)}
- Team capacity: ${args.teamCapacityHours} hours
- Team workload: ${JSON.stringify(teamWorkload)}
- Sprint: ${args.sprintStartDate} to ${args.sprintEndDate}

Select tasks for the sprint, assign to team members, and set priorities.
Return JSON: { selectedTasks: [{ taskId, assigneeId, priority, estimatedHours }], reasoning: string }`,
      });
      return JSON.parse(result.text);
    });

    // Step 4: Apply the plan
    await step.run("applyPlan", async (ctx) => {
      for (const task of sprintPlan.selectedTasks) {
        await ctx.runMutation(internal.tasks.update, {
          taskId: task.taskId,
          status: "todo",
          assigneeId: task.assigneeId,
          priority: task.priority,
          sprintId: args.projectId, // Or create sprint record
        });
      }
    });

    // Step 5: Create sprint record
    const sprintId = await step.run("createSprint", async (ctx) => {
      return await ctx.runMutation(internal.sprints.create, {
        projectId: args.projectId,
        startDate: args.sprintStartDate,
        endDate: args.sprintEndDate,
        taskIds: sprintPlan.selectedTasks.map((t: any) => t.taskId),
      });
    });

    // Step 6: Notify team
    await step.run("notifyTeam", async (ctx) => {
      await ctx.runAction(internal.notifications.sendSprintStarted, {
        projectId: args.projectId,
        sprintId,
        taskCount: sprintPlan.selectedTasks.length,
      });
    });

    return {
      success: true,
      sprintId,
      tasksPlanned: sprintPlan.selectedTasks.length,
      reasoning: sprintPlan.reasoning,
    };
  }
);
```
</sprint_planning_workflow>

<daily_summary_workflow>
Generate and distribute daily standup summaries.

```ts
export const dailySummaryWorkflow = workflow(
  components.workflow,
  {
    args: v.object({
      projectId: v.id("projects"),
      recipientIds: v.array(v.id("users")),
    }),
  },
  async (step, args) => {
    const yesterday = new Date(Date.now() - 86400000).toISOString().split("T")[0];

    // Gather activity
    const activity = await step.run("getActivity", async (ctx) => {
      return await ctx.runQuery(internal.tasks.getRecentActivity, {
        projectId: args.projectId,
        since: yesterday,
      });
    });

    // Get blockers
    const blockers = await step.run("getBlockers", async (ctx) => {
      return await ctx.runQuery(internal.analytics.blockers, {
        projectId: args.projectId,
      });
    });

    // Generate AI summary
    const summary = await step.run("generateSummary", async (ctx) => {
      const { thread } = await projectAssistant.createThread(ctx, {});
      const result = await thread.generateText({
        prompt: `Generate a concise daily standup summary:

Completed yesterday:
${JSON.stringify(activity.completed)}

In progress:
${JSON.stringify(activity.inProgress)}

Blockers:
${JSON.stringify(blockers)}

Format as:
- What was accomplished
- What's in progress
- Blockers and risks
- Key priorities for today`,
      });
      return result.text;
    });

    // Store summary
    await step.run("saveSummary", async (ctx) => {
      await ctx.runMutation(internal.summaries.create, {
        projectId: args.projectId,
        date: yesterday,
        content: summary,
        activity,
        blockers,
      });
    });

    // Notify recipients
    await step.run("notify", async (ctx) => {
      for (const userId of args.recipientIds) {
        await ctx.runMutation(internal.notifications.create, {
          userId,
          type: "daily_summary",
          content: summary,
          projectId: args.projectId,
        });
      }
    });

    return { success: true, summary };
  }
);
```
</daily_summary_workflow>

<bulk_operations_workflow>
Handle large batch operations with progress tracking.

```ts
export const bulkUpdateWorkflow = workflow(
  components.workflow,
  {
    args: v.object({
      taskIds: v.array(v.id("tasks")),
      updates: v.object({
        status: v.optional(v.string()),
        assigneeId: v.optional(v.id("users")),
        priority: v.optional(v.string()),
      }),
      operationId: v.string(), // For progress tracking
    }),
  },
  async (step, args) => {
    const results: { taskId: string; success: boolean; error?: string }[] = [];
    const total = args.taskIds.length;

    for (let i = 0; i < args.taskIds.length; i++) {
      const taskId = args.taskIds[i];

      const result = await step.run(`update-${i}`, async (ctx) => {
        try {
          await ctx.runMutation(internal.tasks.update, {
            taskId,
            ...args.updates,
          });

          // Update progress
          await ctx.runMutation(internal.operations.updateProgress, {
            operationId: args.operationId,
            completed: i + 1,
            total,
          });

          return { taskId, success: true };
        } catch (error) {
          return { taskId, success: false, error: String(error) };
        }
      });

      results.push(result);
    }

    // Mark operation complete
    await step.run("complete", async (ctx) => {
      await ctx.runMutation(internal.operations.complete, {
        operationId: args.operationId,
        results,
      });
    });

    return {
      success: true,
      updated: results.filter(r => r.success).length,
      failed: results.filter(r => !r.success).length,
    };
  }
);
```
</bulk_operations_workflow>
</examples>

<scheduled_jobs>
```ts
// convex/crons.ts
import { cronJobs } from "convex/server";
import { internal } from "./_generated/api";

const crons = cronJobs();

// Daily standup summary at 9am UTC
crons.daily(
  "daily-summary",
  { hourUTC: 9, minuteUTC: 0 },
  internal.workflows.triggerDailySummaries
);

// Weekly sprint review on Fridays at 5pm UTC
crons.weekly(
  "sprint-review",
  { dayOfWeek: "friday", hourUTC: 17, minuteUTC: 0 },
  internal.workflows.triggerSprintReview
);

// Check for overdue tasks every 4 hours
crons.interval(
  "overdue-check",
  { hours: 4 },
  internal.notifications.checkOverdueTasks
);

// Monthly analytics report on the 1st
crons.monthly(
  "monthly-report",
  { day: 1, hourUTC: 8, minuteUTC: 0 },
  internal.workflows.triggerMonthlyReport
);

export default crons;
```
</scheduled_jobs>

<triggering_workflows>
<from_agent_tools>
```ts
const startSprintPlanning = createTool({
  description: "Start the sprint planning workflow",
  args: v.object({
    projectId: v.id("projects"),
    sprintStart: v.string(),
    sprintEnd: v.string(),
  }),
  handler: async (ctx, args) => {
    // Start workflow
    await ctx.scheduler.runAfter(0, internal.workflows.sprintPlanningWorkflow, {
      projectId: args.projectId,
      sprintStartDate: args.sprintStart,
      sprintEndDate: args.sprintEnd,
      teamCapacityHours: 160, // or fetch from config
    });

    return {
      started: true,
      message: "Sprint planning workflow started. You'll see tasks update as planning completes.",
    };
  },
});
```
</from_agent_tools>

<from_mutations>
```ts
export const requestBulkUpdate = mutation({
  args: {
    taskIds: v.array(v.id("tasks")),
    updates: v.object({ status: v.optional(v.string()) }),
  },
  handler: async (ctx, args) => {
    const operationId = crypto.randomUUID();

    // Create operation record for progress tracking
    await ctx.db.insert("operations", {
      operationId,
      type: "bulk_update",
      status: "running",
      completed: 0,
      total: args.taskIds.length,
    });

    // Start workflow
    await ctx.scheduler.runAfter(0, internal.workflows.bulkUpdateWorkflow, {
      ...args,
      operationId,
    });

    return { operationId };
  },
});
```
</from_mutations>

<from_cron_triggers>
```ts
// convex/workflows/triggers.ts
export const triggerDailySummaries = internalAction({
  args: {},
  handler: async (ctx) => {
    // Get all active projects
    const projects = await ctx.runQuery(internal.projects.listActive, {});

    for (const project of projects) {
      // Get project members
      const members = await ctx.runQuery(internal.projects.getMembers, {
        projectId: project._id
      });

      // Start workflow for each project
      await ctx.scheduler.runAfter(0, internal.workflows.dailySummaryWorkflow, {
        projectId: project._id,
        recipientIds: members.map(m => m.userId),
      });
    }
  },
});
```
</from_cron_triggers>
</triggering_workflows>

<best_practices>
Each step should be idempotent since steps may retry on failure. Store incremental results to avoid recomputation. Use meaningful step names for debugging. Keep steps focused and atomic. Handle errors gracefully within steps.

```ts
// Good: Idempotent step with meaningful name
await step.run("upsertAnalysisRecord", async (ctx) => {
  const existing = await ctx.runQuery(internal.analysis.get, { projectId });
  if (existing) {
    await ctx.runMutation(internal.analysis.update, { ...existing, data });
  } else {
    await ctx.runMutation(internal.analysis.create, { projectId, data });
  }
});

// Avoid: Non-idempotent operations without guards
await step.run("step1", async (ctx) => {
  await ctx.runMutation(internal.counter.increment, {}); // Will double-count on retry
});
```
</best_practices>
</workflows>
