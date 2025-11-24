import { OpenAI } from 'openai';
import { Pinecone } from '@pinecone-database/pinecone';

// Initialize clients
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

const pc = new Pinecone({
  apiKey: process.env.PINECONE_API_KEY,
});

const indexName = process.env.PINECONE_INDEX_NAME || 'system-design-rag';

/**
 * Main handler for query requests
 */
export async function handler(event, context) {
  // Enable CORS
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Content-Type': 'application/json',
  };

  // Handle OPTIONS request for CORS
  if (event.httpMethod === 'OPTIONS') {
    return {
      statusCode: 200,
      headers,
      body: '',
    };
  }

  // Only accept POST requests
  if (event.httpMethod !== 'POST') {
    return {
      statusCode: 405,
      headers,
      body: JSON.stringify({ error: 'Method not allowed' }),
    };
  }

  try {
    // Parse request body
    const { question, topK = 3 } = JSON.parse(event.body);

    if (!question || typeof question !== 'string') {
      return {
        statusCode: 400,
        headers,
        body: JSON.stringify({ error: 'Question is required and must be a string' }),
      };
    }

    // Step 1: Generate embedding for the question
    const embeddingResponse = await openai.embeddings.create({
      model: 'text-embedding-3-small',
      input: question,
    });

    const questionEmbedding = embeddingResponse.data[0].embedding;

    // Step 2: Search Pinecone for similar vectors
    const index = pc.index(indexName);
    const searchResults = await index.query({
      vector: questionEmbedding,
      topK: topK,
      includeMetadata: true,
    });

    // Check if we found any matches
    if (!searchResults.matches || searchResults.matches.length === 0) {
      return {
        statusCode: 200,
        headers,
        body: JSON.stringify({
          answer: "I don't have information about that topic in my knowledge base yet.",
          sources: [],
          confidence: 0,
        }),
      };
    }

    // Step 3: Prepare context from retrieved chunks
    const context = searchResults.matches
      .map((match, idx) => {
        const metadata = match.metadata || {};
        return `[Source ${idx + 1}: ${metadata.title || 'Unknown'}]\n${metadata.content || ''}`;
      })
      .join('\n\n---\n\n');

    // Step 4: Generate answer using GPT
    const systemPrompt = `You are a system design expert assistant. You have access to a curated knowledge base.

When answering:
1. Use markdown formatting extensively:
   - Use ## for main section headers
   - Use ### for subsection headers  
   - Use **bold** for key terms and important concepts
   - Use bullet points (-) for lists
   - Use numbered lists (1., 2., 3.) for sequences
   - Use code blocks with \`\`\` for code examples
   - Add blank lines between sections for readability

2. Structure your answers clearly:
   - Start with a brief overview
   - Break content into logical sections with headers
   - Use lists to organize information
   - Include code examples where relevant

3. Be comprehensive and include specific details from the context.

The context provided is from a verified knowledge base - trust it and use it fully.`;

    const userPrompt = `Context from knowledge base:\n\n${context}\n\n---\n\nQuestion: ${question}\n\nProvide a clear, accurate answer based on the context above.`;

    const completion = await openai.chat.completions.create({
      model: 'gpt-3.5-turbo',
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: userPrompt },
      ],
      temperature: 0.3,
      max_tokens: 800,
    });

    const answer = completion.choices[0].message.content;

    // Step 5: Format sources
    const sources = searchResults.matches.map((match) => {
      const metadata = match.metadata || {};
      return {
        title: metadata.title || 'Unknown',
        category: metadata.category || 'Unknown',
        similarity: match.score,
        chunkId: match.id,
        tags: metadata.tags ? metadata.tags.split(',') : [],
      };
    });

    // Calculate confidence based on top match score
    const confidence = searchResults.matches[0]?.score || 0;

    // Step 6: Return response
    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({
        answer,
        sources,
        confidence,
        question,
      }),
    };
  } catch (error) {
    console.error('Error processing query:', error);

    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({
        error: 'Internal server error',
        message: error.message,
      }),
    };
  }
}