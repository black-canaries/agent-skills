<streaming>
<overview>
Streaming patterns for Convex agents - HTTP streaming, database-reactive streaming, React hooks, and platform-specific considerations.
</overview>

<streaming_approaches>
<http_streaming>
Standard HTTP streaming works well for web clients. Text streams to the client in real-time while simultaneously saving to the database.

```ts
// Works well on web
export const streamMessage = action({
  args: { prompt: v.string(), threadId: v.string() },
  handler: async (ctx, { prompt, threadId }) => {
    const { thread } = await myAgent.continueThread(ctx, { threadId });

    // Stream returns async iterator
    const result = await thread.streamText({ prompt });

    // Consume the stream (required to complete)
    for await (const chunk of result.textStream) {
      // Chunks are sent to client via HTTP
    }

    return { text: result.text };
  },
});
```
</http_streaming>

<database_reactive_streaming>
For React Native or environments where HTTP streaming is unreliable, use database-reactive streaming. Chunks are saved to the database as they arrive, and the client's useQuery subscription receives updates.

```ts
// Backend: Save deltas to database
export const sendMessage = action({
  args: { prompt: v.string(), threadId: v.string() },
  handler: async (ctx, { prompt, threadId }) => {
    const { thread } = await myAgent.continueThread(ctx, { threadId });

    const result = await thread.streamText(
      { prompt },
      { saveStreamDeltas: true } // Key option
    );

    await result.consumeStream(); // Wait for completion
    return { success: true };
  },
});

// Query returns messages that update reactively
export const listMessages = query({
  args: { threadId: v.string() },
  handler: async (ctx, { threadId }) => {
    return await myAgent.listMessages(ctx, { threadId });
  },
});
```

```tsx
// Client: useQuery auto-updates as chunks arrive
function Chat({ threadId }) {
  const messages = useQuery(api.chat.listMessages, { threadId });

  return (
    <FlatList
      data={messages?.page ?? []}
      renderItem={({ item }) => (
        <MessageBubble
          text={item.text}
          isStreaming={item.status === "streaming"}
        />
      )}
    />
  );
}
```
</database_reactive_streaming>
</streaming_approaches>

<react_hooks>
<useUIMessages_hook>
The recommended hook for rich streaming state.

```tsx
import { useUIMessages } from "@convex-dev/agent/react";
import { api } from "../convex/_generated/api";

function Chat({ threadId }) {
  const { results, status, loadMore } = useUIMessages(
    api.chat.listMessages,
    { threadId },
    { initialNumItems: 20 }
  );

  return (
    <div>
      {results.map((message) => (
        <Message key={message.key} message={message} />
      ))}
      {status === "streaming" && <TypingIndicator />}
    </div>
  );
}
```

UIMessage provides the following properties. The key is a stable identifier for React keys. The role indicates user or assistant. The text field contains the full message text. The status shows pending, streaming, or success. The parts array contains structured content including text, tool-invocation, and tool-result items.
</useUIMessages_hook>

<message_status_handling>
```tsx
function Message({ message }) {
  const statusStyles = {
    pending: { opacity: 0.5 },
    streaming: { borderLeft: "2px solid blue" },
    success: {},
  };

  return (
    <div style={statusStyles[message.status]}>
      {message.status === "streaming" && <StreamingIndicator />}
      <MessageContent parts={message.parts} />
    </div>
  );
}
```
</message_status_handling>

<smooth_text_animation>
For character-by-character text animation during streaming.

```tsx
import { useSmoothText } from "@convex-dev/agent/react";

function StreamingText({ text, isStreaming }) {
  const smoothText = useSmoothText(text, {
    enabled: isStreaming,
    charactersPerSecond: 30,
  });

  return <Text>{smoothText}</Text>;
}
```
</smooth_text_animation>
</react_hooks>

<optimistic_updates>
Show the user's message immediately before the action completes.

```tsx
import { optimisticallySendMessage } from "@convex-dev/agent/react";

function Chat({ threadId }) {
  const sendMessage = useMutation(api.chat.sendMessage).withOptimisticUpdate(
    optimisticallySendMessage(api.chat.listMessages)
  );

  const handleSend = (prompt: string) => {
    sendMessage({ threadId, prompt });
    // Message appears immediately in UI
  };
}
```

For custom argument shapes use a manual optimistic update.

```tsx
const sendMessage = useMutation(api.chat.sendMessage).withOptimisticUpdate(
  (store, args) => {
    optimisticallySendMessage(api.chat.listMessages)(store, {
      threadId: args.threadId,
      prompt: args.content, // Map your args to prompt
    });
  }
);
```
</optimistic_updates>

<platform_considerations>
<web>
HTTP streaming works reliably. Use either approach based on preference. The streamText method provides the most responsive UX.
</web>

<react_native>
HTTP streaming may not work reliably. There are known issues where messages appear all at once instead of streaming incrementally. Database-reactive streaming with saveStreamDeltas is recommended.

```ts
// Always use saveStreamDeltas for React Native
const result = await thread.streamText(
  { prompt },
  { saveStreamDeltas: true }
);
await result.consumeStream();
```
</react_native>

<expo>
Same considerations as React Native. Test streaming behavior on actual devices since simulators may behave differently.
</expo>
</platform_considerations>

<backend_configuration>
<syncStreams_for_multiple_clients>
When multiple clients need to see the same streaming message, use syncStreams.

```ts
export const listMessages = query({
  args: {
    threadId: v.string(),
    streamArgs: v.optional(vStreamArgs),
  },
  handler: async (ctx, { threadId, streamArgs }) => {
    const paginated = await myAgent.listMessages(ctx, { threadId });

    if (streamArgs) {
      const streams = await myAgent.syncStreams(ctx, { threadId, streamArgs });
      return { ...paginated, streams };
    }

    return paginated;
  },
});
```
</syncStreams_for_multiple_clients>

<stream_options>
```ts
const result = await thread.streamText(
  { prompt },
  {
    saveStreamDeltas: true, // Save chunks to DB
    // Additional AI SDK options
    maxTokens: 1000,
    temperature: 0.7,
  }
);
```
</stream_options>
</backend_configuration>

<handling_long_responses>
For very long responses, consider chunking or summarization.

```ts
instructions: `Keep responses concise. For complex topics:
1. Provide a summary first
2. Offer to elaborate on specific points
3. Use display tools for structured data instead of long text`
```
</handling_long_responses>

<error_handling_during_streaming>
```tsx
function Chat({ threadId }) {
  const { results, status } = useUIMessages(api.chat.listMessages, { threadId });

  // Check for failed messages
  const failedMessages = results.filter(m => m.status === "failed");

  return (
    <div>
      {results.map(message => (
        <Message
          key={message.key}
          message={message}
          showRetry={message.status === "failed"}
        />
      ))}
    </div>
  );
}
```
</error_handling_during_streaming>
</streaming>
