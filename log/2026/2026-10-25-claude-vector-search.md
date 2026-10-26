---
id: 2026-10-25-claude-001
date: 2026-10-25
platform: claude
model: claude-sonnet-4.5
session: vector-search
turn: 1
topic: designing a vector search prototype
tags: [search, embeddings, prototype]
supersedes:
---

## User

I'm trying to build a small vector search prototype. What's the simplest way to get embeddings for a few hundred documents and query them without standing up a whole database?

## Assistant

For a few hundred documents, skip the dedicated vector database entirely. Generate embeddings with any embedding API, store the vectors in an in-memory array alongside the document text, and do brute-force cosine similarity at query time — a few hundred vectors is microseconds of work.

The shape is straightforward: embed each document once, keep a list of `{ id, text, vector }`, then on a query embed the query string and rank documents by cosine similarity against every stored vector. Return the top-k.

When you outgrow a few thousand documents, that's the point to reach for a real index — either an ANN library like HNSW or a managed vector store. But the in-memory version will get you a working demo today and keeps the moving parts to one API call.
