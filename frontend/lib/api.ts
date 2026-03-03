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

async function fallbackToNonStreaming(
  message: string,
  onChunk: (chunk: string) => void,
  onSources: (sources: any[]) => void,
  onError: (error: string) => void
): Promise<void> {
  try {
    console.log('Using fallback non-streaming invoke endpoint');
    const response = await fetch(`${API_BASE_URL}/chain/invoke`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ input: { query: message } }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log('Fallback response:', data);

    // LangServe returns { output: { answer, sources } }
    const output = data.output || {};

    // Emit sources if available
    if (output.sources && output.sources.length > 0) {
      onSources(output.sources);
    }

    // Emit complete response as one chunk
    if (output.answer) {
      onChunk(output.answer);
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
    console.log('Starting LangServe streaming request to /chain/stream');
    const response = await fetch(`${API_BASE_URL}/chain/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ input: { query: message } }),
      signal: controller.signal,
    });

    clearTimeout(timeout);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const reader = response.body?.getReader();
    if (!reader) {
      // Fallback to non-streaming invoke endpoint
      console.warn('Response body not readable, using non-streaming invoke');
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
            console.log('Received from LangServe:', data);
            
            // LangServe streams objects with { output: { answer: string, sources: any[] } }
            const output = data.output || data;
            
            if (output.answer) {
              // Can be partial or full answer from the stream
              onChunk(output.answer);
            }
            
            if (output.sources && output.sources.length > 0) {
              onSources(output.sources);
            }
            
            if (output.error) {
              onError(output.error);
            }
          } catch (e) {
            console.error('Failed to parse streaming data:', e);
          }
        }
      }
    }

    if (!hasReceivedData) {
      throw new Error('No data received from stream');
    }
  } catch (error) {
    clearTimeout(timeout);
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    console.error('Streaming error:', errorMessage);

    // Fallback to non-streaming endpoint
    if (!errorMessage.includes('abort')) {
      console.log('Attempting fallback to non-streaming...');
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