<generative_ui>
<overview>
Generative UI patterns for Convex agents - connecting tool results to React components for interactive, structured responses instead of plain text.
</overview>

<concept>
Generative UI connects tool results to React components. Instead of the agent responding with text like "Here are your 5 tasks...", it returns structured data that renders as an interactive task list, chart, or form.

The pattern works as follows. First, you provide the agent with display tools that return typed UI data. The agent calls these tools with structured arguments. The client inspects tool results in message parts and renders matching components.
</concept>

<display_tool_pattern>
<basic_display_tool>
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
    // Return data with uiType marker
    return { uiType: "taskList", ...args };
  },
});
```
</basic_display_tool>

<guiding_agent_usage>
Add explicit instructions so the agent uses display tools instead of text:

```ts
instructions: `When showing tasks to users:
- ALWAYS use showTaskList tool instead of describing tasks in text
- Group by status for sprint views, by priority for planning views

When showing analytics:
- Use showChart for numerical data
- Use showProjectDashboard for project overviews

Never describe data in prose when a display tool is appropriate.`
```
</guiding_agent_usage>
</display_tool_pattern>

<ui_action_signals>
Return signals that trigger client-side behaviors.

```ts
const createTask = createTool({
  description: "Create a task and signal UI to highlight it",
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
      // UI action payload
      uiAction: {
        type: "minimizeChat",
        focusOn: { type: "project", id: args.projectId },
        highlight: { type: "task", id: taskId },
      },
    };
  },
});

const createMultipleTasks = createTool({
  description: "Create multiple tasks with staggered UI highlights",
  args: v.object({
    projectId: v.id("projects"),
    tasks: v.array(v.object({
      title: v.string(),
      priority: v.string(),
    })),
  }),
  handler: async (ctx, args) => {
    const taskIds = [];

    for (const task of args.tasks) {
      const taskId = await ctx.runMutation(internal.tasks.create, {
        ...task,
        projectId: args.projectId,
        createdBy: "ai",
      });
      taskIds.push(taskId);
    }

    return {
      success: true,
      taskIds,
      uiAction: {
        type: "minimizeChat",
        focusOn: { type: "project", id: args.projectId },
        highlightMultiple: taskIds.map(id => ({ type: "task", id })),
        staggerDelay: 300, // ms between each highlight
      },
    };
  },
});
```
</ui_action_signals>

<client_implementation>
<detecting_ui_actions>
```tsx
// hooks/useChatWithUIActions.ts
import { useEffect, useRef } from "react";
import { useQuery } from "convex/react";
import { api } from "../convex/_generated/api";

type UIAction = {
  type: "minimizeChat" | "navigateTo" | "highlight";
  focusOn?: { type: string; id: string };
  highlight?: { type: string; id: string };
  highlightMultiple?: Array<{ type: string; id: string }>;
  staggerDelay?: number;
};

export function useChatWithUIActions({
  threadId,
  onUIAction,
}: {
  threadId: string | null;
  onUIAction: (action: UIAction) => void;
}) {
  const messages = useQuery(
    api.chat.listMessages,
    threadId ? { threadId } : "skip"
  );
  const processedToolCalls = useRef(new Set<string>());

  useEffect(() => {
    if (!messages?.page) return;

    for (const message of messages.page) {
      if (message.role !== "assistant") continue;

      for (const part of message.parts ?? []) {
        if (part.type === "tool-result" && part.result?.uiAction) {
          const toolCallId = part.toolCallId;

          // Process each tool call only once
          if (!processedToolCalls.current.has(toolCallId)) {
            processedToolCalls.current.add(toolCallId);
            onUIAction(part.result.uiAction);
          }
        }
      }
    }
  }, [messages, onUIAction]);

  return { messages };
}
```
</detecting_ui_actions>

<rendering_generative_ui>
```tsx
// components/ChatMessage.tsx
function ChatMessage({ message }: { message: UIMessage }) {
  return (
    <View>
      {message.parts?.map((part, i) => {
        // Text content
        if (part.type === "text") {
          return <Text key={i}>{part.text}</Text>;
        }

        // Tool in progress
        if (part.type === "tool-invocation" && part.state === "running") {
          return <ToolProgress key={i} toolName={part.toolName} />;
        }

        // Completed tool with UI result
        if (part.type === "tool-result" && part.result?.uiType) {
          return <GenerativeUIRenderer key={i} data={part.result} />;
        }

        return null;
      })}
    </View>
  );
}

function GenerativeUIRenderer({ data }: { data: any }) {
  switch (data.uiType) {
    case "taskList":
      return <TaskListCard title={data.title} tasks={data.tasks} groupBy={data.groupBy} />;

    case "projectDashboard":
      return <ProjectDashboard stats={data.stats} deadlines={data.upcomingDeadlines} />;

    case "chart":
      return <ChartCard type={data.chartType} title={data.title} data={data.data} />;

    case "planningReport":
      return <PlanningReport summary={data.summary} recommendations={data.recommendations} />;

    default:
      return null;
  }
}
```
</rendering_generative_ui>

<coordinating_sheet_and_main_view>
```tsx
// screens/ProjectScreen.tsx
import { TrueSheet } from '@lodev09/react-native-true-sheet';

function ProjectScreen({ projectId }: { projectId: string }) {
  const sheetRef = useRef<TrueSheet>(null);
  const [highlightedIds, setHighlightedIds] = useState<Set<string>>(new Set());
  const [threadId, setThreadId] = useState<string | null>(null);

  // Reactive subscription - updates when AI creates tasks
  const tasks = useQuery(api.tasks.listByProject, { projectId });

  const handleUIAction = useCallback((action: UIAction) => {
    if (action.type === "minimizeChat") {
      // Collapse the sheet to first detent
      sheetRef.current?.resize(0);

      // Handle highlight
      if (action.highlight) {
        setHighlightedIds(new Set([action.highlight.id]));
        setTimeout(() => setHighlightedIds(new Set()), 3000);
      }

      // Handle staggered highlights
      if (action.highlightMultiple) {
        const delay = action.staggerDelay ?? 300;
        action.highlightMultiple.forEach((item, index) => {
          setTimeout(() => {
            setHighlightedIds(prev => new Set([...prev, item.id]));
          }, index * delay);
        });

        const totalDuration = action.highlightMultiple.length * delay + 2000;
        setTimeout(() => setHighlightedIds(new Set()), totalDuration);
      }
    }
  }, []);

  return (
    <View style={{ flex: 1 }}>
      <TaskList tasks={tasks ?? []} highlightedIds={highlightedIds} />

      <TrueSheet ref={sheetRef} detents={[0.1, 0.5, 0.9]} scrollable>
        <ChatSheet
          projectId={projectId}
          threadId={threadId}
          onThreadCreated={setThreadId}
          onUIAction={handleUIAction}
        />
      </TrueSheet>
    </View>
  );
}
```
</coordinating_sheet_and_main_view>
</client_implementation>

<highlight_animations>
```tsx
// components/TaskRow.tsx
function TaskRow({ task, isHighlighted, isAICreated }) {
  const highlightAnim = useRef(new Animated.Value(0)).current;
  const slideAnim = useRef(new Animated.Value(isAICreated ? -50 : 0)).current;

  // Entrance animation for AI-created tasks
  useEffect(() => {
    if (isAICreated) {
      Animated.spring(slideAnim, {
        toValue: 0,
        tension: 50,
        friction: 8,
        useNativeDriver: true,
      }).start();
    }
  }, []);

  // Highlight pulse
  useEffect(() => {
    if (isHighlighted) {
      Animated.sequence([
        Animated.timing(highlightAnim, { toValue: 1, duration: 200, useNativeDriver: false }),
        Animated.timing(highlightAnim, { toValue: 0.3, duration: 1500, useNativeDriver: false }),
        Animated.timing(highlightAnim, { toValue: 0, duration: 500, useNativeDriver: false }),
      ]).start();
    }
  }, [isHighlighted]);

  const backgroundColor = highlightAnim.interpolate({
    inputRange: [0, 1],
    outputRange: ["#ffffff", "#e0f2fe"],
  });

  return (
    <Animated.View style={[styles.row, { backgroundColor, transform: [{ translateX: slideAnim }] }]}>
      <Text>{task.title}</Text>
      {isAICreated && <AIBadge />}
    </Animated.View>
  );
}
```
</highlight_animations>

<common_display_components>
<task_list_card>
```tsx
function TaskListCard({ title, tasks, groupBy, onTaskPress }) {
  const grouped = groupBy ? groupTasksBy(tasks, groupBy) : { all: tasks };

  return (
    <View style={styles.card}>
      <Text style={styles.title}>{title}</Text>
      {Object.entries(grouped).map(([group, groupTasks]) => (
        <View key={group}>
          {groupBy && <Text style={styles.groupHeader}>{group}</Text>}
          {groupTasks.map(task => (
            <TouchableOpacity key={task.id} onPress={() => onTaskPress?.(task.id)}>
              <View style={styles.taskRow}>
                <StatusBadge status={task.status} />
                <Text style={styles.taskTitle}>{task.title}</Text>
                <PriorityIndicator priority={task.priority} />
              </View>
            </TouchableOpacity>
          ))}
        </View>
      ))}
    </View>
  );
}
```
</task_list_card>

<chart_card>
```tsx
function ChartCard({ type, title, data }) {
  return (
    <View style={styles.card}>
      <Text style={styles.title}>{title}</Text>
      {type === "bar" && <BarChart data={data} />}
      {type === "pie" && <PieChart data={data} />}
      {type === "line" && <LineChart data={data} />}
    </View>
  );
}
```
</chart_card>

<planning_report>
```tsx
function PlanningReport({ summary, recommendations }) {
  return (
    <View style={styles.card}>
      <Text style={styles.summary}>{summary}</Text>

      <Text style={styles.sectionTitle}>Recommendations</Text>
      {recommendations.map((rec, i) => (
        <View key={i} style={styles.recommendation}>
          <RecommendationIcon type={rec.type} />
          <View style={styles.recContent}>
            <Text>{rec.description}</Text>
            {rec.action && (
              <TouchableOpacity style={styles.actionButton}>
                <Text>{rec.action}</Text>
              </TouchableOpacity>
            )}
          </View>
        </View>
      ))}
    </View>
  );
}
```
</planning_report>
</common_display_components>

<realtime_magic>
Because your main view subscribes to task data via `useQuery`, when the agent's tool calls `ctx.runMutation(internal.tasks.create, ...)`, the following happens automatically. The mutation writes to the database, Convex detects affected queries, updated data pushes to all subscribed clients, and React re-renders with the new task.

No polling, no refetching, no state synchronization code. The task simply appears because the subscription is already active.
</realtime_magic>
</generative_ui>
