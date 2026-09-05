/**
 * Unified API Client for AI Teacher Platform
 * Connects frontend screens to Flask backend endpoints through Vite reverse proxy.
 */

export interface ApiResponse<T = any> {
  data: T | null;
  error: string | null;
  status: number;
}

const DEFAULT_TIMEOUT_MS = 20000;

export async function apiClient<T = any>(
  endpoint: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), DEFAULT_TIMEOUT_MS);

  const cleanEndpoint = endpoint.startsWith('/') ? endpoint : '/' + endpoint;
  const url = cleanEndpoint.startsWith('/api') ? cleanEndpoint : '/api/v1' + cleanEndpoint;

  const headers: Record<string, string> = {
    Accept: 'application/json',
    ...(options.headers as Record<string, string>),
  };

  if (!(options.body instanceof FormData) && !headers['Content-Type']) {
    headers['Content-Type'] = 'application/json';
  }

  try {
    const response = await fetch(url, {
      ...options,
      headers,
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    let data: T | null = null;
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      data = await response.json();
    } else {
      const text = await response.text();
      data = text as unknown as T;
    }

    if (!response.ok) {
      const errorMsg =
        (data && typeof data === 'object' && 'error' in (data as any) && (data as any).error) ||
        (data && typeof data === 'object' && 'message' in (data as any) && (data as any).message) ||
        ('Request failed with status ' + response.status);
      return { data: null, error: String(errorMsg), status: response.status };
    }

    return { data, error: null, status: response.status };
  } catch (err: any) {
    clearTimeout(timeoutId);
    if (err.name === 'AbortError') {
      return { data: null, error: 'Request timed out after 20 seconds.', status: 408 };
    }
    return { data: null, error: err.message || 'Network request failed.', status: 500 };
  }
}
