<rag>
<overview>
RAG (Retrieval-Augmented Generation) integration patterns for Convex agents - setup, content management, search, and agent integration strategies.
</overview>

<setup>
Install and configure the RAG component alongside the agent.

```bash
npm install @convex-dev/rag
```

```ts
// convex/convex.config.ts
import { defineApp } from "convex/server";
import agent from "@convex-dev/agent/convex.config";
import rag from "@convex-dev/rag/convex.config";

const app = defineApp();
app.use(agent);
app.use(rag);
export default app;
```

```ts
// convex/rag.ts
import { RAG } from "@convex-dev/rag";
import { components } from "./_generated/api";
import { openai } from "@ai-sdk/openai";

export const rag = new RAG(components.rag, {
  textEmbeddingModel: openai.embedding("text-embedding-3-small"),
  embeddingDimension: 1536,
});
```
</setup>

<adding_content>
<basic_text_ingestion>
```ts
export const addDocument = action({
  args: {
    content: v.string(),
    namespace: v.string(),
    metadata: v.optional(v.object({
      title: v.string(),
      source: v.string(),
    })),
  },
  handler: async (ctx, args) => {
    await rag.add(ctx, {
      namespace: args.namespace,
      text: args.content,
      metadata: args.metadata,
    });
    return { success: true };
  },
});
```
</basic_text_ingestion>

<chunked_content>
For large documents, chunk the content before adding.

```ts
export const addLargeDocument = action({
  args: { content: v.string(), namespace: v.string() },
  handler: async (ctx, { content, namespace }) => {
    // Simple chunking by paragraphs
    const chunks = content.split("\n\n").filter(c => c.trim().length > 0);

    await rag.add(ctx, {
      namespace,
      chunks: chunks.map((text, i) => ({
        text,
        metadata: { chunkIndex: i },
      })),
    });

    return { success: true, chunkCount: chunks.length };
  },
});
```
</chunked_content>

<custom_chunking>
```ts
import { RecursiveCharacterTextSplitter } from "langchain/text_splitter";

export const addWithSmartChunking = action({
  args: { content: v.string(), namespace: v.string() },
  handler: async (ctx, { content, namespace }) => {
    const splitter = new RecursiveCharacterTextSplitter({
      chunkSize: 1000,
      chunkOverlap: 200,
    });

    const chunks = await splitter.splitText(content);

    await rag.add(ctx, {
      namespace,
      chunks: chunks.map(text => ({ text })),
    });

    return { success: true };
  },
});
```
</custom_chunking>
</adding_content>

<search_patterns>
<direct_search>
```ts
export const searchDocs = action({
  args: { query: v.string(), namespace: v.string() },
  handler: async (ctx, { query, namespace }) => {
    const results = await rag.search(ctx, {
      namespace,
      query,
      limit: 10,
    });

    return results;
  },
});
```
</direct_search>

<search_with_filters>
```ts
const results = await rag.search(ctx, {
  namespace: "docs",
  query: "authentication setup",
  limit: 5,
  filter: {
    // Filter by metadata fields
    category: "security",
  },
});
```
</search_with_filters>
</search_patterns>

<rag_agent_patterns>
<context_injection>
Search for context and inject it into the prompt before calling the LLM. The message history includes only the original prompt and response, not the context.

```ts
export const askWithContext = action({
  args: { prompt: v.string(), threadId: v.string(), namespace: v.string() },
  handler: async (ctx, { prompt, threadId, namespace }) => {
    // Search for relevant context
    const context = await rag.search(ctx, {
      namespace,
      query: prompt,
      limit: 5,
    });

    // Inject context into prompt
    const augmentedPrompt = `# Relevant Context:
${context.text}

---

# User Question:
${prompt}

Answer based on the context provided. If the context doesn't contain relevant information, say so.`;

    const { thread } = await myAgent.continueThread(ctx, { threadId });
    const result = await thread.generateText({ prompt: augmentedPrompt });

    return { text: result.text, sourcesUsed: context.results.length };
  },
});
```
</context_injection>

<rag_as_tool>
Let the agent decide when to search for context. The message history includes the tool call.

```ts
const searchKnowledgeBase = createTool({
  description: "Search the knowledge base for relevant information. Use when you need specific facts, documentation, or context to answer the user's question.",
  args: v.object({
    query: v.string(),
    namespace: v.optional(v.string()),
  }),
  handler: async (ctx, { query, namespace }) => {
    const results = await rag.search(ctx, {
      namespace: namespace ?? "docs",
      query,
      limit: 5,
    });

    return results.text;
  },
});

const myAgent = new Agent(components.agent, {
  name: "Knowledge Assistant",
  languageModel: openai.chat("gpt-4o"),
  instructions: `You are a helpful assistant with access to a knowledge base.

When users ask factual questions:
1. Use searchKnowledgeBase to find relevant information
2. Synthesize the results into a clear answer
3. Cite sources when appropriate

If the knowledge base doesn't have relevant information, be honest about it.`,
  tools: { searchKnowledgeBase },
});
```
</rag_as_tool>

<automatic_rag>
Use the RAG component's generateText helper for automatic context injection.

```ts
export const askQuestion = action({
  args: { prompt: v.string(), namespace: v.string() },
  handler: async (ctx, { prompt, namespace }) => {
    const { text, context } = await rag.generateText(ctx, {
      search: {
        namespace,
        limit: 10,
      },
      prompt,
      model: openai.chat("gpt-4o"),
    });

    return {
      answer: text,
      sourcesUsed: context.results.length,
    };
  },
});
```
</automatic_rag>
</rag_agent_patterns>

<namespace_strategies>
<per_user_namespaces>
Isolate each user's documents.

```ts
export const addUserDocument = action({
  args: { content: v.string(), userId: v.id("users") },
  handler: async (ctx, { content, userId }) => {
    await rag.add(ctx, {
      namespace: `user:${userId}`,
      text: content,
    });
  },
});

export const searchUserDocs = action({
  args: { query: v.string(), userId: v.id("users") },
  handler: async (ctx, { query, userId }) => {
    return await rag.search(ctx, {
      namespace: `user:${userId}`,
      query,
    });
  },
});
```
</per_user_namespaces>

<per_project_namespaces>
Organize by project for team access.

```ts
const namespace = `project:${projectId}`;
```
</per_project_namespaces>

<global_plus_personal>
Search both global knowledge base and user-specific content.

```ts
export const comprehensiveSearch = action({
  args: { query: v.string(), userId: v.id("users") },
  handler: async (ctx, { query, userId }) => {
    const [globalResults, userResults] = await Promise.all([
      rag.search(ctx, { namespace: "global", query, limit: 5 }),
      rag.search(ctx, { namespace: `user:${userId}`, query, limit: 5 }),
    ]);

    return {
      global: globalResults.results,
      personal: userResults.results,
    };
  },
});
```
</global_plus_personal>
</namespace_strategies>

<content_management>
<updating_content>
Replace content in a namespace.

```ts
export const updateDocument = action({
  args: {
    documentId: v.string(),
    newContent: v.string(),
    namespace: v.string(),
  },
  handler: async (ctx, args) => {
    // Delete old content
    await rag.delete(ctx, {
      namespace: args.namespace,
      filter: { documentId: args.documentId },
    });

    // Add new content
    await rag.add(ctx, {
      namespace: args.namespace,
      text: args.newContent,
      metadata: { documentId: args.documentId },
    });
  },
});
```
</updating_content>

<deleting_content>
```ts
export const deleteFromNamespace = action({
  args: { namespace: v.string(), documentId: v.optional(v.string()) },
  handler: async (ctx, { namespace, documentId }) => {
    if (documentId) {
      await rag.delete(ctx, {
        namespace,
        filter: { documentId },
      });
    } else {
      // Delete entire namespace
      await rag.delete(ctx, { namespace });
    }
  },
});
```
</deleting_content>
</content_management>

<file_handling>
<pdf_processing>
```ts
import pdfParse from "pdf-parse";

export const indexPDF = action({
  args: { storageId: v.id("_storage"), namespace: v.string() },
  handler: async (ctx, { storageId, namespace }) => {
    const blob = await ctx.storage.get(storageId);
    if (!blob) throw new Error("File not found");

    const buffer = await blob.arrayBuffer();
    const pdf = await pdfParse(Buffer.from(buffer));

    await rag.add(ctx, {
      namespace,
      text: pdf.text,
      metadata: {
        type: "pdf",
        pages: pdf.numpages,
        storageId,
      },
    });

    return { success: true, pages: pdf.numpages };
  },
});
```
</pdf_processing>

<image_descriptions>
Use an LLM to describe images, then index the description.

```ts
export const indexImage = action({
  args: { storageId: v.id("_storage"), namespace: v.string() },
  handler: async (ctx, { storageId, namespace }) => {
    const url = await ctx.storage.getUrl(storageId);

    // Get image description from LLM
    const result = await generateText({
      model: openai.chat("gpt-4o"),
      messages: [{
        role: "user",
        content: [
          { type: "image", image: url },
          { type: "text", text: "Describe this image in detail for search indexing." },
        ],
      }],
    });

    await rag.add(ctx, {
      namespace,
      text: result.text,
      metadata: { type: "image", storageId },
    });
  },
});
```
</image_descriptions>
</file_handling>

<best_practices>
Chunk sizes matter significantly. Too small and context is lost, too large and retrieval becomes imprecise. Aim for 500-1500 tokens per chunk with some overlap.

Use descriptive metadata to enable filtering and source attribution.

Monitor relevance by logging searches that return poor results and iterating on chunking or embedding strategies.

Consider hybrid search combining vector search with keyword search for better recall on specific terms.

Update content incrementally rather than re-indexing entire namespaces when possible.
</best_practices>
</rag>
