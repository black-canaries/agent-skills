# Convex RAG Reference

Comprehensive guide to implementing Retrieval-Augmented Generation (RAG) with Convex, including vector search, document ingestion, and LLM integration patterns.

## What is RAG?

Retrieval-Augmented Generation (RAG) combines Large Language Models with knowledge retrieval, enabling systems to:
- Search custom document collections
- Retrieve relevant context for queries
- Provide accurate, domain-specific answers
- Cite sources for generated responses
- Ground LLM outputs in factual knowledge

## RAG Implementation Approaches

Convex provides two distinct patterns for RAG implementation:

### 1. Prompt-Based RAG

Automatically searches for context before processing every user query. Context is injected directly into prompts without including search operations in message history.

**When to Use**:
- FAQ systems where queries consistently benefit from context
- Predictable search patterns
- Simple document lookup scenarios
- Systems where search should be invisible to users

**Implementation**:
```typescript
import { action } from "./_generated/server";
import { v } from "convex/values";
import { components } from "./_generated/api";

const rag = components.rag;

export const answerQuestion = action({
  args: {
    userId: v.id("users"),
    query: v.string(),
  },
  returns: v.string(),
  handler: async (ctx, args) => {
    // Search for relevant context
    const context = await rag.search(ctx, {
      namespace: args.userId, // User-specific knowledge base
      query: args.query,
      limit: 10,
    });

    // Build prompt with context
    const prompt = `Context:\n${context.text}\n\nQuestion: ${args.query}\n\nAnswer:`;

    // Call LLM with augmented prompt
    const response = await openai.chat.completions.create({
      model: "gpt-4o",
      messages: [{ role: "user", content: prompt }],
    });

    return response.choices[0].message.content || "No response generated";
  },
});
```

**Characteristics**:
- Search timing: Always before LLM call
- Message history: Original prompt + response only
- Flexibility: Predictable, consistent behavior
- Best for: Document search, knowledge bases

### 2. Tool-Based RAG

The LLM intelligently decides when to search using a dedicated tool. Search operations are included in message history, allowing dynamic context retrieval.

**When to Use**:
- Adaptive knowledge retrieval needs
- Complex multi-turn conversations
- Systems where LLM should decide when context is needed
- Dynamic knowledge management

**Implementation**:
```typescript
import { createTool } from "@convex-dev/agent";
import { Agent } from "@convex-dev/agent";
import { z } from "zod";

const searchContext = createTool({
  description: "Search for context related to the user's query in the knowledge base",
  args: z.object({
    query: z.string().describe("The search query"),
  }),
  handler: async (ctx, { query }) => {
    const context = await rag.search(ctx, {
      namespace: "global",
      query,
      limit: 10,
    });
    return context.text;
  },
});

const knowledgeAgent = new Agent(components.agent, {
  name: "Knowledge Agent",
  chat: openai.chat("gpt-4o"),
  instructions: "Answer questions using the searchContext tool when you need information from the knowledge base.",
  tools: { searchContext },
});

export const chatWithKnowledge = action({
  args: {
    threadId: v.id("threads"),
    message: v.string(),
  },
  returns: v.string(),
  handler: async (ctx, args) => {
    return await knowledgeAgent.asTextAction(ctx, {
      threadId: args.threadId,
      userMessage: args.message,
    });
  },
});
```

**Characteristics**:
- Search timing: AI-determined based on need
- Message history: Includes tool calls and results
- Flexibility: Adaptive, context-aware
- Best for: Dynamic knowledge management, conversational AI

## RAG Component Features

### Namespaces

Isolate search domains for multi-tenant or user-specific knowledge:

```typescript
// Global namespace (shared across all users)
const globalResults = await rag.search(ctx, {
  namespace: "global",
  query: "company policies",
  limit: 5,
});

// User-specific namespace
const userResults = await rag.search(ctx, {
  namespace: userId,
  query: "my documents",
  limit: 5,
});

// Team namespace
const teamResults = await rag.search(ctx, {
  namespace: `team:${teamId}`,
  query: "project documentation",
  limit: 5,
});
```

### Vector Search

Configure embedding models for semantic search:

```typescript
import { v } from "convex/values";

export const configureEmbeddings = mutation({
  args: {
    model: v.string(), // e.g., "text-embedding-3-small"
    dimensions: v.number(), // e.g., 1536
  },
  returns: v.null(),
  handler: async (ctx, args) => {
    await rag.configure(ctx, {
      embeddingModel: args.model,
      embeddingDimensions: args.dimensions,
    });
    return null;
  },
});
```

**Supported Models**:
- OpenAI: `text-embedding-3-small`, `text-embedding-3-large`
- Custom models via API

### Custom Filtering

Efficient document-level filtering for refined search:

```typescript
const results = await rag.search(ctx, {
  namespace: "global",
  query: "machine learning",
  limit: 10,
  filter: {
    category: "technical",
    published: true,
    author: "john@example.com",
  },
});
```

### Importance Weighting

Adjust search relevance through importance scores (0-1):

```typescript
await rag.ingest(ctx, {
  namespace: "global",
  document: {
    id: "critical-doc-1",
    content: "Critical company policy...",
    metadata: {
      importance: 1.0, // Highest priority
      category: "policy",
    },
  },
});

await rag.ingest(ctx, {
  namespace: "global",
  document: {
    id: "optional-doc-2",
    content: "Optional reading material...",
    metadata: {
      importance: 0.3, // Lower priority
      category: "reference",
    },
  },
});
```

Higher importance scores boost relevance in search results.

### Chunk Context

Retrieve surrounding chunks for enhanced context:

```typescript
const results = await rag.search(ctx, {
  namespace: "global",
  query: "authentication flow",
  limit: 5,
  includeContext: true, // Include surrounding chunks
  contextChunks: 2, // 2 chunks before and after
});

// Each result includes:
// - Main matching chunk
// - Previous chunks (context)
// - Following chunks (context)
```

## Content Ingestion Strategies

### Text Files

Process structured formats directly:

```typescript
export const ingestTextFile = action({
  args: {
    fileId: v.id("_storage"),
    namespace: v.string(),
  },
  returns: v.null(),
  handler: async (ctx, args) => {
    // Get file from storage
    const url = await ctx.storage.getUrl(args.fileId);
    if (!url) throw new Error("File not found");

    const response = await fetch(url);
    const text = await response.text();

    // Ingest with automatic chunking
    await rag.ingest(ctx, {
      namespace: args.namespace,
      document: {
        id: args.fileId,
        content: text,
        metadata: {
          type: "text",
          fileId: args.fileId,
        },
      },
    });

    return null;
  },
});
```

For unstructured text, use LLMs to restructure for better embedding quality:

```typescript
export const ingestUnstructuredText = action({
  args: {
    fileId: v.id("_storage"),
    namespace: v.string(),
  },
  returns: v.null(),
  handler: async (ctx, args) => {
    const url = await ctx.storage.getUrl(args.fileId);
    if (!url) throw new Error("File not found");

    const response = await fetch(url);
    const rawText = await response.text();

    // Use LLM to structure the text
    const structured = await openai.chat.completions.create({
      model: "gpt-4o",
      messages: [{
        role: "user",
        content: `Convert this unstructured text into clear sections with headings:\n\n${rawText}`
      }],
    });

    const structuredText = structured.choices[0].message.content || rawText;

    await rag.ingest(ctx, {
      namespace: args.namespace,
      document: {
        id: args.fileId,
        content: structuredText,
        metadata: { type: "text", processed: true },
      },
    });

    return null;
  },
});
```

### PDFs

**Recommended: Browser-side parsing** (avoids memory overhead):

```typescript
// Client-side PDF processing with PDF.js
import * as pdfjs from "pdfjs-dist";

async function extractTextFromPDF(file: File): Promise<string> {
  const arrayBuffer = await file.arrayBuffer();
  const pdf = await pdfjs.getDocument({ data: arrayBuffer }).promise;

  let fullText = "";
  for (let i = 1; i <= pdf.numPages; i++) {
    const page = await pdf.getPage(i);
    const textContent = await page.getTextContent();
    const pageText = textContent.items
      .map((item: any) => item.str)
      .join(" ");
    fullText += pageText + "\n\n";
  }

  return fullText;
}

// Send extracted text to Convex for ingestion
const text = await extractTextFromPDF(pdfFile);
await convex.action(api.rag.ingestText, {
  namespace: "user-docs",
  content: text,
  metadata: { filename: pdfFile.name },
});
```

**Alternative: Server-side with LLM** (for smaller files):

```typescript
export const ingestPDF = action({
  args: {
    fileId: v.id("_storage"),
    namespace: v.string(),
  },
  returns: v.null(),
  handler: async (ctx, args) => {
    const url = await ctx.storage.getUrl(args.fileId);
    if (!url) throw new Error("File not found");

    // Use LLM with vision to extract text
    const response = await openai.chat.completions.create({
      model: "gpt-4o",
      messages: [{
        role: "user",
        content: [
          { type: "text", text: "Extract all text from this PDF" },
          { type: "image_url", image_url: { url } },
        ],
      }],
    });

    const extractedText = response.choices[0].message.content || "";

    await rag.ingest(ctx, {
      namespace: args.namespace,
      document: {
        id: args.fileId,
        content: extractedText,
        metadata: { type: "pdf", fileId: args.fileId },
      },
    });

    return null;
  },
});
```

### Images

Use LLM vision capabilities to generate descriptions:

```typescript
export const ingestImage = action({
  args: {
    fileId: v.id("_storage"),
    namespace: v.string(),
  },
  returns: v.null(),
  handler: async (ctx, args) => {
    const url = await ctx.storage.getUrl(args.fileId);
    if (!url) throw new Error("Image not found");

    // Generate description with vision model
    const response = await openai.chat.completions.create({
      model: "gpt-4o",
      messages: [{
        role: "user",
        content: [
          {
            type: "text",
            text: "Provide a detailed description of this image including all visible text, objects, people, and context."
          },
          {
            type: "image_url",
            image_url: { url }
          },
        ],
      }],
    });

    const description = response.choices[0].message.content || "";

    // Index description, store original image reference
    await rag.ingest(ctx, {
      namespace: args.namespace,
      document: {
        id: args.fileId,
        content: description,
        metadata: {
          type: "image",
          fileId: args.fileId, // Store for retrieval after search
          imageUrl: url,
        },
      },
    });

    return null;
  },
});
```

Store original images separately and retrieve after semantic search.

## Flexible Chunking

### Default Chunking

RAG component automatically chunks documents:

```typescript
await rag.ingest(ctx, {
  namespace: "global",
  document: {
    id: "doc-1",
    content: longDocument,
    // Default chunking applied automatically
  },
});
```

### Custom Chunking

Provide pre-chunked content for fine-grained control:

```typescript
function chunkByParagraphs(text: string): string[] {
  return text.split("\n\n").filter(p => p.trim().length > 0);
}

export const ingestWithCustomChunks = action({
  args: {
    content: v.string(),
    namespace: v.string(),
  },
  returns: v.null(),
  handler: async (ctx, args) => {
    const chunks = chunkByParagraphs(args.content);

    for (let i = 0; i < chunks.length; i++) {
      await rag.ingest(ctx, {
        namespace: args.namespace,
        document: {
          id: `doc-chunk-${i}`,
          content: chunks[i],
          metadata: {
            chunkIndex: i,
            totalChunks: chunks.length,
          },
        },
      });
    }

    return null;
  },
});
```

## Graceful Migrations

Update content without disruption:

```typescript
export const migrateDocuments = action({
  args: {
    namespace: v.string(),
  },
  returns: v.null(),
  handler: async (ctx, args) => {
    // Fetch all documents from old format
    const oldDocs = await ctx.runQuery(internal.docs.listAll, {
      namespace: args.namespace,
    });

    // Re-ingest with new format
    for (const doc of oldDocs) {
      // Delete old version
      await rag.delete(ctx, {
        namespace: args.namespace,
        documentId: doc.id,
      });

      // Ingest new version
      await rag.ingest(ctx, {
        namespace: args.namespace,
        document: {
          id: doc.id,
          content: doc.newContent,
          metadata: doc.newMetadata,
        },
      });
    }

    return null;
  },
});
```

## Complete RAG Patterns

### Multi-Source RAG

Search across multiple knowledge sources:

```typescript
export const multiSourceSearch = action({
  args: {
    query: v.string(),
    userId: v.id("users"),
  },
  returns: v.string(),
  handler: async (ctx, args) => {
    // Search multiple namespaces
    const [globalResults, userResults, teamResults] = await Promise.all([
      rag.search(ctx, {
        namespace: "global",
        query: args.query,
        limit: 5,
      }),
      rag.search(ctx, {
        namespace: args.userId,
        query: args.query,
        limit: 5,
      }),
      rag.search(ctx, {
        namespace: "team",
        query: args.query,
        limit: 5,
      }),
    ]);

    // Combine and rank results
    const allResults = [
      ...globalResults.results,
      ...userResults.results,
      ...teamResults.results,
    ].sort((a, b) => b.score - a.score);

    const topResults = allResults.slice(0, 10);
    const context = topResults.map(r => r.content).join("\n\n");

    // Generate answer with combined context
    const prompt = `Context:\n${context}\n\nQuestion: ${args.query}\n\nAnswer:`;
    const response = await openai.chat.completions.create({
      model: "gpt-4o",
      messages: [{ role: "user", content: prompt }],
    });

    return response.choices[0].message.content || "No response";
  },
});
```

### Citation-Enabled RAG

Provide sources for generated answers:

```typescript
export const answerWithCitations = action({
  args: {
    query: v.string(),
    namespace: v.string(),
  },
  returns: v.object({
    answer: v.string(),
    sources: v.array(v.object({
      id: v.string(),
      title: v.string(),
      excerpt: v.string(),
    })),
  }),
  handler: async (ctx, args) => {
    const results = await rag.search(ctx, {
      namespace: args.namespace,
      query: args.query,
      limit: 5,
    });

    // Build context with source markers
    const contextParts = results.results.map((r, i) =>
      `[Source ${i+1}: ${r.metadata?.title || r.id}]\n${r.content}`
    );
    const context = contextParts.join("\n\n");

    const prompt = `Context:\n${context}\n\nQuestion: ${args.query}\n\nProvide an answer and cite sources using [Source N] format.`;

    const response = await openai.chat.completions.create({
      model: "gpt-4o",
      messages: [{ role: "user", content: prompt }],
    });

    return {
      answer: response.choices[0].message.content || "",
      sources: results.results.map((r, i) => ({
        id: r.id,
        title: r.metadata?.title || `Document ${r.id}`,
        excerpt: r.content.slice(0, 200) + "...",
      })),
    };
  },
});
```

## Best Practices

1. **Choose the Right Approach**: Use prompt-based for predictable patterns, tool-based for adaptive needs
2. **Leverage Namespaces**: Isolate knowledge bases per user/team for multi-tenant systems
3. **Process Files Appropriately**: Browser-side for PDFs, LLM vision for images/unstructured text
4. **Implement Importance Weighting**: Surface critical documents over optional content
5. **Retrieve Surrounding Chunks**: Include context chunks for coherent understanding
6. **Optimize Chunk Size**: Balance between specificity and context (typically 500-1000 tokens)
7. **Filter Strategically**: Use metadata filters to narrow search scope efficiently
8. **Monitor Search Quality**: Track search relevance and adjust embeddings/chunking as needed
9. **Handle Edge Cases**: Plan for no results, irrelevant results, and ambiguous queries
10. **Combine with Agents**: Integrate RAG with Convex Agents for powerful conversational AI

## Common Patterns

### Hybrid Search (Vector + Text)

Combine semantic and keyword search:

```typescript
const results = await rag.search(ctx, {
  namespace: "global",
  query: args.query,
  limit: 10,
  mode: "hybrid", // Vector + text search
  alpha: 0.7, // Weight towards vector (0.0 = text only, 1.0 = vector only)
});
```

### Query Expansion

Expand queries for better coverage:

```typescript
export const expandedSearch = action({
  args: { query: v.string(), namespace: v.string() },
  returns: v.string(),
  handler: async (ctx, args) => {
    // Use LLM to generate query variations
    const expansion = await openai.chat.completions.create({
      model: "gpt-4o-mini",
      messages: [{
        role: "user",
        content: `Generate 3 alternative phrasings of this query: "${args.query}"`
      }],
    });

    const queries = [
      args.query,
      ...expansion.choices[0].message.content?.split("\n") || [],
    ];

    // Search with all query variations
    const allResults = await Promise.all(
      queries.map(q => rag.search(ctx, {
        namespace: args.namespace,
        query: q,
        limit: 5,
      }))
    );

    // Deduplicate and combine results
    const uniqueResults = new Map();
    for (const results of allResults) {
      for (const result of results.results) {
        if (!uniqueResults.has(result.id) ||
            uniqueResults.get(result.id).score < result.score) {
          uniqueResults.set(result.id, result);
        }
      }
    }

    const topResults = Array.from(uniqueResults.values())
      .sort((a, b) => b.score - a.score)
      .slice(0, 10);

    const context = topResults.map(r => r.content).join("\n\n");

    // Generate answer
    const response = await openai.chat.completions.create({
      model: "gpt-4o",
      messages: [{
        role: "user",
        content: `Context:\n${context}\n\nQuestion: ${args.query}\n\nAnswer:`
      }],
    });

    return response.choices[0].message.content || "No response";
  },
});
```

### Re-ranking

Re-rank results with a more sophisticated model:

```typescript
export const rerankedSearch = action({
  args: { query: v.string(), namespace: v.string() },
  returns: v.array(v.string()),
  handler: async (ctx, args) => {
    // Initial retrieval with larger limit
    const results = await rag.search(ctx, {
      namespace: args.namespace,
      query: args.query,
      limit: 50,
    });

    // Re-rank with LLM
    const reranking = await openai.chat.completions.create({
      model: "gpt-4o",
      messages: [{
        role: "user",
        content: `Query: "${args.query}"\n\nRank these documents by relevance (return top 10 IDs):\n${
          results.results.map((r, i) =>
            `ID ${i}: ${r.content.slice(0, 200)}`
          ).join("\n\n")
        }`
      }],
    });

    // Extract ranked IDs and return top results
    // ... parse LLM response and return reranked content

    return results.results.slice(0, 10).map(r => r.content);
  },
});
```
