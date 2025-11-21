/**
 * Health check endpoint
 * Returns basic health status of the application
 */
export async function handler(event, context) {
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'GET, OPTIONS',
    'Content-Type': 'application/json',
  };

  if (event.httpMethod === 'OPTIONS') {
    return {
      statusCode: 200,
      headers,
      body: '',
    };
  }

  if (event.httpMethod !== 'GET') {
    return {
      statusCode: 405,
      headers,
      body: JSON.stringify({ error: 'Method not allowed' }),
    };
  }

  // Check environment variables
  const hasOpenAIKey = !!process.env.OPENAI_API_KEY;
  const hasPineconeKey = !!process.env.PINECONE_API_KEY;
  const indexName = process.env.PINECONE_INDEX_NAME || 'system-design-rag';

  const health = {
    status: 'ok',
    timestamp: new Date().toISOString(),
    environment: {
      openai: hasOpenAIKey ? 'configured' : 'missing',
      pinecone: hasPineconeKey ? 'configured' : 'missing',
      indexName: indexName,
    },
    version: '1.0.0',
  };

  return {
    statusCode: 200,
    headers,
    body: JSON.stringify(health),
  };
}