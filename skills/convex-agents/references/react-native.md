<react_native>
<overview>
React Native patterns for Convex agents - setup, chat screens, streaming, real-time updates, UI action handling, and animations.
</overview>

<core_setup>
<convex_provider>
```tsx
// App.tsx
import { ConvexProvider, ConvexReactClient } from "convex/react";

const convex = new ConvexReactClient(process.env.EXPO_PUBLIC_CONVEX_URL!);

export default function App() {
  return (
    <ConvexProvider client={convex}>
      <Navigation />
    </ConvexProvider>
  );
}
```
</convex_provider>

<basic_chat_screen>
```tsx
import { useState, useRef } from "react";
import { View, FlatList, TextInput, TouchableOpacity, Text } from "react-native";
import { useQuery, useMutation } from "convex/react";
import { api } from "../convex/_generated/api";

export function ChatScreen({ projectId }: { projectId: string }) {
  const [input, setInput] = useState("");
  const [threadId, setThreadId] = useState<string | null>(null);
  const flatListRef = useRef<FlatList>(null);

  const messages = useQuery(
    api.chat.listMessages,
    threadId ? { threadId } : "skip"
  );

  const sendMessage = useMutation(api.chat.sendMessage);

  const handleSend = async () => {
    if (!input.trim()) return;

    const prompt = input;
    setInput("");

    const result = await sendMessage({
      prompt,
      threadId: threadId ?? undefined,
      projectId,
    });

    if (!threadId && result.threadId) {
      setThreadId(result.threadId);
    }
  };

  return (
    <View style={{ flex: 1 }}>
      <FlatList
        ref={flatListRef}
        data={messages?.page ?? []}
        keyExtractor={(item) => item._id}
        renderItem={({ item }) => <MessageBubble message={item} />}
        inverted
        onContentSizeChange={() => flatListRef.current?.scrollToEnd()}
      />

      <View style={styles.inputContainer}>
        <TextInput
          value={input}
          onChangeText={setInput}
          placeholder="Type a message..."
          style={styles.input}
          multiline
        />
        <TouchableOpacity onPress={handleSend} style={styles.sendButton}>
          <Text style={styles.sendText}>Send</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}
```
</basic_chat_screen>
</core_setup>

<streaming_considerations>
HTTP streaming may not work reliably in React Native. Messages might appear all at once instead of streaming incrementally. Use database-reactive streaming for consistent behavior.

<backend_configuration>
```ts
// convex/chat.ts
export const sendMessage = action({
  args: { prompt: v.string(), threadId: v.string() },
  handler: async (ctx, { prompt, threadId }) => {
    const { thread } = await myAgent.continueThread(ctx, { threadId });

    // Always use saveStreamDeltas for React Native
    const result = await thread.streamText(
      { prompt },
      { saveStreamDeltas: true }
    );

    await result.consumeStream();
    return { success: true };
  },
});
```
</backend_configuration>

<client_subscription>
The useQuery hook automatically receives updates as deltas are saved to the database.

```tsx
const messages = useQuery(api.chat.listMessages, { threadId });

// Messages update reactively as the agent streams
```
</client_subscription>
</streaming_considerations>

<realtime_task_updates>
Leverage Convex's reactive queries for real-time UI updates when the agent creates or modifies data.

<task_list_with_live_updates>
```tsx
function ProjectTasksScreen({ projectId }: { projectId: string }) {
  // This subscription auto-updates when agent creates tasks
  const tasks = useQuery(api.tasks.listByProject, { projectId });

  return (
    <FlatList
      data={tasks ?? []}
      keyExtractor={(item) => item._id}
      renderItem={({ item }) => <TaskRow task={item} />}
    />
  );
}
```
</task_list_with_live_updates>

<combining_chat_and_tasks>
```tsx
import { TrueSheet } from '@lodev09/react-native-true-sheet';

function ProjectScreen({ projectId }: { projectId: string }) {
  const sheetRef = useRef<TrueSheet>(null);
  const [threadId, setThreadId] = useState<string | null>(null);

  // Both subscriptions update independently
  const tasks = useQuery(api.tasks.listByProject, { projectId });
  const messages = useQuery(
    api.chat.listMessages,
    threadId ? { threadId } : "skip"
  );

  return (
    <View style={{ flex: 1 }}>
      {/* Main task list - updates when agent creates tasks */}
      <TaskList tasks={tasks ?? []} />

      {/* Chat sheet */}
      <TrueSheet ref={sheetRef} detents={[0.1, 0.5, 0.9]} scrollable>
        <ChatSheet
          projectId={projectId}
          threadId={threadId}
          messages={messages}
          onThreadCreated={setThreadId}
        />
      </TrueSheet>
    </View>
  );
}
```
</combining_chat_and_tasks>
</realtime_task_updates>

<ui_action_handling>
Process tool result signals to coordinate between chat and main UI.

<hook_for_ui_actions>
```tsx
import { useEffect, useRef, useCallback } from "react";

type UIAction = {
  type: "minimizeChat" | "navigateTo" | "highlight";
  focusOn?: { type: string; id: string };
  highlight?: { type: string; id: string };
  highlightMultiple?: Array<{ type: string; id: string }>;
  staggerDelay?: number;
};

export function useUIActionsFromMessages(
  messages: any[] | undefined,
  onUIAction: (action: UIAction) => void
) {
  const processedIds = useRef(new Set<string>());

  useEffect(() => {
    if (!messages) return;

    for (const message of messages) {
      if (message.role !== "assistant") continue;

      for (const part of message.parts ?? []) {
        if (part.type === "tool-result" && part.result?.uiAction) {
          const id = part.toolCallId;

          if (!processedIds.current.has(id)) {
            processedIds.current.add(id);
            onUIAction(part.result.uiAction);
          }
        }
      }
    }
  }, [messages, onUIAction]);
}
```
</hook_for_ui_actions>

<coordinated_screen>
```tsx
import { TrueSheet } from '@lodev09/react-native-true-sheet';

function ProjectScreen({ projectId }: { projectId: string }) {
  const sheetRef = useRef<TrueSheet>(null);
  const [highlightedIds, setHighlightedIds] = useState<Set<string>>(new Set());
  const [threadId, setThreadId] = useState<string | null>(null);

  const tasks = useQuery(api.tasks.listByProject, { projectId });
  const messages = useQuery(
    api.chat.listMessages,
    threadId ? { threadId } : "skip"
  );

  const handleUIAction = useCallback((action: UIAction) => {
    if (action.type === "minimizeChat") {
      sheetRef.current?.resize(0); // Resize to first detent

      if (action.highlight) {
        setHighlightedIds(new Set([action.highlight.id]));
        setTimeout(() => setHighlightedIds(new Set()), 3000);
      }

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

  useUIActionsFromMessages(messages?.page, handleUIAction);

  return (
    <View style={{ flex: 1 }}>
      <TaskList tasks={tasks ?? []} highlightedIds={highlightedIds} />

      <TrueSheet ref={sheetRef} detents={[0.1, 0.5, 0.9]} scrollable>
        <ChatInterface
          threadId={threadId}
          messages={messages}
          onThreadCreated={setThreadId}
        />
      </TrueSheet>
    </View>
  );
}
```
</coordinated_screen>
</ui_action_handling>

<highlight_animations>
<animated_task_row>
```tsx
import { useEffect, useRef } from "react";
import { Animated, View, Text, StyleSheet } from "react-native";

function TaskRow({
  task,
  isHighlighted,
  isAICreated
}: {
  task: Task;
  isHighlighted: boolean;
  isAICreated: boolean;
}) {
  const highlightAnim = useRef(new Animated.Value(0)).current;
  const slideAnim = useRef(new Animated.Value(isAICreated ? -50 : 0)).current;
  const opacityAnim = useRef(new Animated.Value(isAICreated ? 0 : 1)).current;

  // Entrance animation for AI-created items
  useEffect(() => {
    if (isAICreated) {
      Animated.parallel([
        Animated.spring(slideAnim, {
          toValue: 0,
          tension: 50,
          friction: 8,
          useNativeDriver: true,
        }),
        Animated.timing(opacityAnim, {
          toValue: 1,
          duration: 300,
          useNativeDriver: true,
        }),
      ]).start();
    }
  }, []);

  // Highlight pulse animation
  useEffect(() => {
    if (isHighlighted) {
      Animated.sequence([
        Animated.timing(highlightAnim, {
          toValue: 1,
          duration: 200,
          useNativeDriver: false,
        }),
        Animated.timing(highlightAnim, {
          toValue: 0.3,
          duration: 1500,
          useNativeDriver: false,
        }),
        Animated.timing(highlightAnim, {
          toValue: 0,
          duration: 500,
          useNativeDriver: false,
        }),
      ]).start();
    }
  }, [isHighlighted]);

  const backgroundColor = highlightAnim.interpolate({
    inputRange: [0, 1],
    outputRange: ["#ffffff", "#e0f2fe"],
  });

  return (
    <Animated.View
      style={[
        styles.taskRow,
        {
          backgroundColor,
          transform: [{ translateX: slideAnim }],
          opacity: opacityAnim,
        },
      ]}
    >
      <View style={styles.taskContent}>
        <Text style={styles.taskTitle}>{task.title}</Text>
        {isAICreated && <AIBadge />}
      </View>
    </Animated.View>
  );
}

function AIBadge() {
  return (
    <View style={styles.aiBadge}>
      <Text style={styles.aiBadgeText}>AI</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  taskRow: {
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: "#e5e7eb",
  },
  taskContent: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  taskTitle: {
    fontSize: 16,
    fontWeight: "500",
    flex: 1,
  },
  aiBadge: {
    backgroundColor: "#f0e6ff",
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 12,
  },
  aiBadgeText: {
    fontSize: 12,
    color: "#7c3aed",
  },
});
```
</animated_task_row>
</highlight_animations>

<loading_states>
<skeleton_loading>
```tsx
function TaskListSkeleton() {
  return (
    <View>
      {[1, 2, 3, 4, 5].map(i => (
        <View key={i} style={styles.skeletonRow}>
          <View style={styles.skeletonTitle} />
          <View style={styles.skeletonBadge} />
        </View>
      ))}
    </View>
  );
}

function TaskList({ projectId }: { projectId: string }) {
  const tasks = useQuery(api.tasks.listByProject, { projectId });

  if (tasks === undefined) {
    return <TaskListSkeleton />;
  }

  return (
    <FlatList
      data={tasks}
      renderItem={({ item }) => <TaskRow task={item} />}
    />
  );
}
```
</skeleton_loading>

<ai_working_indicator>
```tsx
function ChatSheet({ messages }) {
  const isAIWorking = messages?.page?.some(m =>
    m.role === "assistant" &&
    m.parts?.some(p => p.type === "tool-invocation" && p.state === "running")
  );

  return (
    <View>
      {isAIWorking && (
        <View style={styles.workingBanner}>
          <ActivityIndicator size="small" color="#6366f1" />
          <Text style={styles.workingText}>AI is working...</Text>
        </View>
      )}
      <MessageList messages={messages} />
    </View>
  );
}
```
</ai_working_indicator>
</loading_states>

<generative_ui_components>
<message_with_parts_rendering>
```tsx
function MessageBubble({ message }: { message: UIMessage }) {
  const isUser = message.role === "user";

  return (
    <View style={[styles.bubble, isUser ? styles.userBubble : styles.assistantBubble]}>
      {message.parts?.map((part, index) => (
        <MessagePart key={index} part={part} />
      ))}
    </View>
  );
}

function MessagePart({ part }: { part: any }) {
  switch (part.type) {
    case "text":
      return <Text style={styles.messageText}>{part.text}</Text>;

    case "tool-invocation":
      if (part.state === "running") {
        return <ToolRunningIndicator toolName={part.toolName} />;
      }
      return null;

    case "tool-result":
      if (part.result?.uiType) {
        return <GenerativeUI data={part.result} />;
      }
      return null;

    default:
      return null;
  }
}

function GenerativeUI({ data }: { data: any }) {
  switch (data.uiType) {
    case "taskList":
      return <TaskListCard {...data} />;
    case "projectDashboard":
      return <ProjectDashboardCard {...data} />;
    case "chart":
      return <ChartCard {...data} />;
    default:
      return null;
  }
}
```
</message_with_parts_rendering>

<inline_task_list_card>
```tsx
function TaskListCard({ title, tasks, groupBy }: TaskListData) {
  return (
    <View style={styles.card}>
      <Text style={styles.cardTitle}>{title}</Text>
      {tasks.map(task => (
        <View key={task.id} style={styles.inlineTaskRow}>
          <StatusBadge status={task.status} />
          <Text style={styles.inlineTaskTitle}>{task.title}</Text>
          <PriorityIndicator priority={task.priority} />
        </View>
      ))}
    </View>
  );
}
```
</inline_task_list_card>
</generative_ui_components>

<bottom_sheet_integration>
Using TrueSheet for native bottom sheet chat interfaces.

```tsx
import { TrueSheet } from '@lodev09/react-native-true-sheet';

function ChatBottomSheet({
  threadId,
  onMinimize
}: {
  threadId: string;
  onMinimize: () => void;
}) {
  const sheetRef = useRef<TrueSheet>(null);
  const messages = useQuery(api.chat.listMessages, { threadId });

  // Present/dismiss via ref
  const present = () => sheetRef.current?.present();
  const minimize = () => sheetRef.current?.resize(0);

  return (
    <TrueSheet
      ref={sheetRef}
      detents={[0.1, 0.5, 0.9]}
      scrollable
      footer={<ChatInput threadId={threadId} />}
    >
      <FlatList
        data={messages?.page ?? []}
        keyExtractor={(item) => item._id}
        renderItem={({ item }) => <MessageBubble message={item} />}
        inverted
      />
    </TrueSheet>
  );
}
```

**TrueSheet advantages:**
- Native Fabric implementation for better performance
- `scrollable` prop handles ScrollView/FlatList automatically
- `footer` prop keeps input above keyboard
- `detents` use fractional values (0.1, 0.5, 0.9) instead of percentages
- `resize(index)` method to programmatically change detent
</bottom_sheet_integration>

<performance_tips>
Use FlatList with proper keyExtractor for message lists. Memoize message components to prevent unnecessary re-renders. Use inverted FlatList for chat to keep new messages at the bottom. Implement pagination with loadMore for long conversations. Keep generative UI components lightweight since they render inline in messages.
</performance_tips>
</react_native>
