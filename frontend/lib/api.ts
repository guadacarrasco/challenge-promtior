// frontend/lib/api.ts
// API base URL configured via NEXT_PUBLIC_API_URL environment variable
// Set this in your deployment platform (Railway, Vercel, etc.)
// For local development, defaults to http://localhost:8000
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function checkHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/health`);
    return response.ok;
  } catch (error) {
    return false;
  }
}

export async function sendMessage(message: string): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/chain/invoke`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ input: { query: message } }),
  });

  if (!response.ok) {
    throw new Error('Error al enviar el mensaje');
  }

  const data = await response.json();
  // LangServe returns { output: { answer, sources } }
  const output = data.output || {};
  return {
    response: output.answer || output.response || JSON.stringify(output),
    sources: output.sources || [],
  };
}

async function fallbackToNonStreaming(
  message: string,
  onChunk: (chunk: string) => void,
  onSources: (sources: any[]) => void,
  onError: (error: string) => void
): Promise<void> {
  try {
    console.log('Using fallback non-streaming endpoint');
    const response = await fetch(`${API_BASE_URL}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();

    // Emit sources if available
    if (data.sources && data.sources.length > 0) {
      onSources(data.sources);
    }

    // Emit complete response as one chunk
    if (data.response) {
      onChunk(data.response);
    }
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    onError(`Fallback failed: ${errorMessage}`);
  }
}

export async function streamMessage(
  message: string,
  onChunk: (chunk: string) => void,
  onSources: (sources: any[]) => void,
  onError: (error: string) => void
): Promise<void> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 180000); // 3 minute timeout

  try {
    console.log('Starting streaming request');
    const response = await fetch(`${API_BASE_URL}/api/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message }),
      signal: controller.signal,
    });

    clearTimeout(timeout);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const reader = response.body?.getReader();
    if (!reader) {
      // Fallback to non-streaming endpoint if body is not readable
      console.warn('Response body not readable, using fallback');
      return fallbackToNonStreaming(message, onChunk, onSources, onError);
    }

    const decoder = new TextDecoder();
    let buffer = '';
    let hasReceivedData = false;
    console.log('Streaming reader ready');

    while (true) {
      const { done, value } = await reader.read();
      if (done) {
        console.log('Stream ended');
        break;
      }

      buffer += decoder.decode(value, { stream: true });
      hasReceivedData = true;

      const lines = buffer.split('\n');
      buffer = lines[lines.length - 1];

      for (let i = 0; i < lines.length - 1; i++) {
        const line = lines[i].trim();
        if (line.startsWith('data: ')) {
          const jsonStr = line.slice(6);
          try {
            const data = JSON.parse(jsonStr);
            if (data.type === 'chunk') {
              onChunk(data.chunk);
            } else if (data.type === 'sources') {
              onSources(data.sources);
            } else if (data.type === 'error') {
              onError(data.error);
            }
          } catch (e) {
            console.error('Failed to parse streaming data:', e);
          }
        }
      }
    }

    if (!hasReceivedData) {
      throw new Error('No data received');
    }
  } catch (error) {
    clearTimeout(timeout);
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    console.error('Streaming error:', errorMessage);

    // Fallback to non-streaming endpoint
    if (!errorMessage.includes('abort')) {
      console.log('Attempting fallback...');
      try {
        await fallbackToNonStreaming(message, onChunk, onSources, onError);
      } catch (fallbackError) {
        const fallbackMsg = fallbackError instanceof Error ? fallbackError.message : 'Unknown error';
        onError(`Both streaming and fallback failed: ${fallbackMsg}`);
      }
    } else {
      onError(errorMessage);
    }
  }
}