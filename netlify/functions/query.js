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
    const { question, topK = 10 } = JSON.parse(event.body);

    if (!question || typeof question !== 'string') {
      return {
        statusCode: 400,
        headers,
        body: JSON.stringify({ error: 'Question is required and must be a string' }),
      };
    }

    console.log('Processing question:', question);

    // Step 1: Generate embedding for the question
    const embeddingResponse = await openai.embeddings.create({
      model: 'text-embedding-3-small',
      input: question,
    });

    const questionEmbedding = embeddingResponse.data[0].embedding;
    console.log('Generated question embedding');

    // Step 2: Search Pinecone for similar vectors
    const index = pc.index(indexName);
    const searchResults = await index.query({
      vector: questionEmbedding,
      topK: topK,
      includeMetadata: true,
    });

    console.log(`Found ${searchResults.matches.length} matches`);

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

    // Step 4: Generate answer using GPT-4
  const systemPrompt = `You are a system design expert assistant. You have access to a curated knowledge base of system design concepts, code examples, and best practices.

Your task is to provide detailed, accurate answers using the context provided. The context contains verified information including:
- Technical explanations and concepts
- Real code examples and configurations  
- Implementation patterns and best practices
- Links to authoritative resources

Instructions:
1. When code examples, configurations, or specific technical details exist in the context, present them directly and confidently
2. Use markdown code blocks to format any code or configuration examples
3. Provide comprehensive explanations with technical depth
4. Include specific details, algorithms, and examples from the context
5. Structure your answer clearly with the most relevant information first
6. Do not hedge or say information is missing if it clearly exists in the provided context

The context provided is from a verified knowledge base - trust it and use it fully to answer the question.`;

    const userPrompt = `Context from knowledge base:\n\n${context}\n\n---\n\nQuestion: ${question}\n\nProvide a clear, accurate answer based on the context above.`;

    const completion = await openai.chat.completions.create({
      model: 'gpt-4',
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: userPrompt },
      ],
      temperature: 0.3, // Lower temperature for more consistent, factual responses
      max_tokens: 800,
    });

    const answer = completion.choices[0].message.content;
    console.log('Generated answer');

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