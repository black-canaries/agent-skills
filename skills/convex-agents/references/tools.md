<tools>
<overview>
Tool design patterns for Convex agents - anatomy, categories, descriptions, validation, error handling, and composition.
</overview>

<tool_anatomy>
```ts
import { createTool } from "@convex-dev/agent";
import { v } from "convex/values";
import { internal } from "../_generated/api";

const myTool = createTool({
  // REQUIRED: Clear description for LLM to decide when to use
  description: "What this tool does and when to use it",

  // REQUIRED: Convex validator for arguments
  args: v.object({
    requiredField: v.string(),
    optionalField: v.optional(v.number()),
  }),

  // REQUIRED: Handler receives ctx and validated args
  handler: async (ctx, args) => {
    // Use ctx.runMutation for writes
    // Use ctx.runQuery for reads
    // Return data the LLM can reason about
    return { success: true, data: "..." };
  },
});
```
</tool_anatomy>

<tool_categories>
<data_retrieval_tools>
Fetch data for LLM reasoning. Return structured data.

```ts
const listTasks = createTool({
  description: "List tasks with optional filters. Returns task details including status, priority, and assignee.",
  args: v.object({
    projectId: v.optional(v.id("projects")),
    status: v.optional(v.union(
      v.literal("backlog"),
      v.literal("todo"),
      v.literal("in_progress"),
      v.literal("done")
    )),
    assigneeId: v.optional(v.id("users")),
    limit: v.optional(v.number()),
  }),
  handler: async (ctx, args) => {
    const tasks = await ctx.runQuery(internal.tasks.list, args);
    return tasks; // Return array for LLM to process
  },
});

const searchTasks = createTool({
  description: "Search tasks by text query across titles and descriptions",
  args: v.object({
    query: v.string(),
    projectId: v.optional(v.id("projects")),
  }),
  handler: async (ctx, args) => {
    const results = await ctx.runQuery(internal.tasks.search, args);
    return results;
  },
});
```
</data_retrieval_tools>

<data_mutation_tools>
Create, update, or delete data. Return confirmation with IDs.

```ts
const createTask = createTool({
  description: "Create a new task in a project",
  args: v.object({
    projectId: v.id("projects"),
    title: v.string(),
    description: v.optional(v.string()),
    priority: v.union(v.literal("low"), v.literal("medium"), v.literal("high")),
    dueDate: v.optional(v.string()), // ISO date string
    assigneeId: v.optional(v.id("users")),
  }),
  handler: async (ctx, args) => {
    const taskId = await ctx.runMutation(internal.tasks.create, args);
    return {
      success: true,
      taskId,
      message: `Created task "${args.title}"`,
    };
  },
});

const updateTask = createTool({
  description: "Update an existing task's properties. Only include fields to change.",
  args: v.object({
    taskId: v.id("tasks"),
    title: v.optional(v.string()),
    status: v.optional(v.string()),
    priority: v.optional(v.string()),
    dueDate: v.optional(v.string()),
    assigneeId: v.optional(v.id("users")),
  }),
  handler: async (ctx, args) => {
    await ctx.runMutation(internal.tasks.update, args);
    return { success: true, message: "Task updated" };
  },
});

const deleteTask = createTool({
  description: "Permanently delete a task. This cannot be undone.",
  args: v.object({
    taskId: v.id("tasks"),
    confirmDelete: v.literal(true), // Force explicit confirmation
  }),
  handler: async (ctx, args) => {
    await ctx.runMutation(internal.tasks.delete, { taskId: args.taskId });
    return { success: true, message: "Task deleted" };
  },
});
```
</data_mutation_tools>

<display_tools>
Return structured data for UI rendering (Generative UI pattern).

```ts
const showTaskList = createTool({
  description: "Display a list of tasks as an interactive UI component. Use when presenting multiple tasks to the user.",
  args: v.object({
    title: v.string(),
    tasks: v.array(v.object({
      id: v.string(),
      title: v.string(),
      status: v.string(),
      priority: v.string(),
      dueDate: v.optional(v.string()),
      assignee: v.optional(v.string()),
    })),
    groupBy: v.optional(v.union(
      v.literal("status"),
      v.literal("priority"),
      v.literal("assignee")
    )),
  }),
  handler: async (ctx, args) => {
    return { uiType: "taskList", ...args };
  },
});

const showChart = createTool({
  description: "Display data as a chart",
  args: v.object({
    chartType: v.union(v.literal("bar"), v.literal("pie"), v.literal("line")),
    title: v.string(),
    data: v.array(v.object({
      label: v.string(),
      value: v.number(),
    })),
  }),
  handler: async (ctx, args) => {
    return { uiType: "chart", ...args };
  },
});
```
</display_tools>

<action_signal_tools>
Trigger client-side behaviors via tool results.

```ts
const createTaskWithUI = createTool({
  description: "Create a task and signal the UI to highlight it",
  args: v.object({
    projectId: v.id("projects"),
    title: v.string(),
    priority: v.string(),
  }),
  handler: async (ctx, args) => {
    const taskId = await ctx.runMutation(internal.tasks.create, {
      ...args,
      createdBy: "ai",
    });

    return {
      success: true,
      taskId,
      // Client interprets this to update UI
      uiAction: {
        type: "minimizeChat",
        focusOn: { type: "project", id: args.projectId },
        highlight: { type: "task", id: taskId },
      },
    };
  },
});
```
</action_signal_tools>

<delegation_tools>
Hand off to another agent or workflow.

```ts
const requestDetailedAnalysis = createTool({
  description: "Delegate complex analysis to the specialized Planning Agent",
  args: v.object({
    analysisType: v.string(),
    projectId: v.id("projects"),
    context: v.optional(v.string()),
  }),
  handler: async (ctx, args) => {
    const { thread } = await planningAgent.createThread(ctx, {});
    const result = await thread.generateText({
      prompt: `Perform ${args.analysisType} analysis for project ${args.projectId}. ${args.context ?? ""}`,
    });
    return { analysis: result.text };
  },
});

const startWorkflow = createTool({
  description: "Start a long-running workflow for sprint planning",
  args: v.object({
    projectId: v.id("projects"),
    sprintDuration: v.number(),
  }),
  handler: async (ctx, args) => {
    const workflowId = await ctx.runMutation(internal.workflows.startSprintPlanning, args);
    return {
      started: true,
      workflowId,
      message: "Sprint planning workflow started. You'll be notified when complete.",
    };
  },
});
```
</delegation_tools>
</tool_categories>

<description_best_practices>
<good_descriptions>
```ts
// Specific about what and when
description: "Create a new task in a project. Use when user asks to add, create, or make a new task."

// Explains return value
description: "List tasks with optional filters. Returns array of tasks with status, priority, assignee, and due date."

// Clarifies edge cases
description: "Search tasks by text query. Searches titles and descriptions. Returns empty array if no matches."

// Guides usage
description: "Display tasks as interactive list. Use this instead of text when showing multiple tasks to user."
```
</good_descriptions>

<bad_descriptions>
```ts
// Too vague
description: "Handle tasks"

// No guidance on when to use
description: "A tool for tasks"

// Missing important details
description: "Update task" // Which fields? What's required?
```
</bad_descriptions>
</description_best_practices>

<argument_validation>
<use_specific_types>
```ts
// Good: Specific union types
args: v.object({
  priority: v.union(v.literal("low"), v.literal("medium"), v.literal("high")),
  status: v.union(v.literal("todo"), v.literal("in_progress"), v.literal("done")),
})

// Avoid: Generic strings for enum-like values
args: v.object({
  priority: v.string(), // LLM might pass invalid values
})
```
</use_specific_types>

<document_optional_fields>
```ts
args: v.object({
  // Required
  title: v.string(),
  projectId: v.id("projects"),

  // Optional - document what happens if omitted
  dueDate: v.optional(v.string()), // ISO date, defaults to no due date
  assigneeId: v.optional(v.id("users")), // If omitted, task is unassigned
})
```
</document_optional_fields>

<use_id_types>
```ts
// Good: Type-safe document references
args: v.object({
  taskId: v.id("tasks"),
  projectId: v.id("projects"),
  assigneeId: v.id("users"),
})

// Avoid: Raw strings for IDs
args: v.object({
  taskId: v.string(), // No type safety
})
```
</use_id_types>
</argument_validation>

<error_handling>
<return_errors_in_data>
```ts
const updateTask = createTool({
  description: "Update a task",
  args: v.object({ taskId: v.id("tasks"), status: v.string() }),
  handler: async (ctx, args) => {
    const task = await ctx.runQuery(internal.tasks.get, { taskId: args.taskId });

    if (!task) {
      return { success: false, error: "Task not found" };
    }

    if (task.status === "done" && args.status !== "done") {
      return { success: false, error: "Cannot reopen completed tasks" };
    }

    await ctx.runMutation(internal.tasks.update, args);
    return { success: true };
  },
});
```
</return_errors_in_data>

<actionable_error_messages>
```ts
handler: async (ctx, args) => {
  const project = await ctx.runQuery(internal.projects.get, { id: args.projectId });

  if (!project) {
    return {
      success: false,
      error: `Project ${args.projectId} not found. Use listProjects to see available projects.`,
    };
  }
  // ...
}
```
</actionable_error_messages>
</error_handling>

<tool_composition>
<fetch_then_display>
Combine data retrieval with display in instructions:

```ts
instructions: `When user asks to see tasks:
1. First use listTasks to fetch the data
2. Then use showTaskList to display them

When user asks about project status:
1. Use getProjectStats to gather metrics
2. Use showProjectDashboard to display the overview`
```
</fetch_then_display>

<analysis_pipeline>
Chain tools for complex operations:

```ts
instructions: `For sprint planning:
1. Use getTasksWithDependencies to see all tasks
2. Use getTeamWorkload to understand capacity
3. Use identifyBottlenecks to find risks
4. Synthesize findings and present with showPlanningReport`
```
</analysis_pipeline>
</tool_composition>
</tools>
