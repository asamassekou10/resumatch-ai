/**
 * Fetch with timeout and retry logic
 * 
 * Wraps fetch with:
 * - Configurable timeout
 * - Automatic retry on failure
 * - Better error messages
 */

/**
 * Fetch with timeout
 * @param {string} url - Request URL
 * @param {Object} options - Fetch options
 * @param {number} timeout - Timeout in milliseconds (default: 120000 = 2 minutes)
 * @returns {Promise<Response>}
 */
export const fetchWithTimeout = async (url, options = {}, timeout = 120000) => {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
    });
    clearTimeout(timeoutId);
    return response;
  } catch (error) {
    clearTimeout(timeoutId);
    
    if (error.name === 'AbortError') {
      throw new Error(`Request timed out after ${timeout / 1000} seconds. The analysis is still processing - please check your history in a moment.`);
    }
    
    // Network errors
    if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
      throw new Error('Network error: Unable to connect to the server. Please check your internet connection and try again.');
    }
    
    throw error;
  }
};

/**
 * Fetch with retry logic
 * @param {string} url - Request URL
 * @param {Object} options - Fetch options
 * @param {Object} retryConfig - Retry configuration
 * @param {number} retryConfig.maxRetries - Maximum number of retries (default: 2)
 * @param {number} retryConfig.retryDelay - Delay between retries in ms (default: 1000)
 * @param {number} retryConfig.timeout - Request timeout in ms (default: 120000)
 * @returns {Promise<Response>}
 */
export const fetchWithRetry = async (
  url,
  options = {},
  retryConfig = {}
) => {
  const {
    maxRetries = 2,
    retryDelay = 1000,
    timeout = 120000,
  } = retryConfig;

  let lastError;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      const response = await fetchWithTimeout(url, options, timeout);
      
      // If response is ok, return it
      if (response.ok) {
        return response;
      }

      // For 5xx errors, retry
      if (response.status >= 500 && attempt < maxRetries) {
        console.warn(`Request failed with ${response.status}, retrying... (attempt ${attempt + 1}/${maxRetries + 1})`);
        await new Promise(resolve => setTimeout(resolve, retryDelay * (attempt + 1)));
        continue;
      }

      // For other errors, don't retry
      return response;
    } catch (error) {
      lastError = error;

      // Don't retry on timeout or abort errors
      if (error.message.includes('timed out') || error.name === 'AbortError') {
        throw error;
      }

      // Retry on network errors
      if (attempt < maxRetries && (
        error.message.includes('Failed to fetch') ||
        error.message.includes('NetworkError') ||
        error.message.includes('network')
      )) {
        console.warn(`Network error, retrying... (attempt ${attempt + 1}/${maxRetries + 1})`);
        await new Promise(resolve => setTimeout(resolve, retryDelay * (attempt + 1)));
        continue;
      }

      // If we've exhausted retries, throw the error
      if (attempt === maxRetries) {
        throw error;
      }
    }
  }

  throw lastError;
};

export default fetchWithTimeout;
