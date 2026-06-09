import axios, { AxiosResponse, AxiosError } from 'axios';
import { ApiResponse, ApiError } from '../types';

const apiClient = axios.create({
  // baseURL points to /api, which is either proxy-routed or managed
  baseURL: import.meta.env.VITE_API_URL || '/api',
  timeout: 120000, // 2 minutes due to SSH + Gemini analysis times
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request Interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Attach authorization headers if needed
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor unpacking StandardResponse wrapper
apiClient.interceptors.response.use(
  (response: AxiosResponse<ApiResponse>) => {
    const resBody = response.data;
    if (resBody && typeof resBody === 'object' && 'success' in resBody) {
      if (resBody.success) {
        return resBody.data; // Return the inner data directly
      } else {
        // Reject with the API error detail
        return Promise.reject(resBody.error || { code: 'API_ERROR', message: 'API returned success=false' });
      }
    }
    return response.data;
  },
  (error: AxiosError) => {
    const normalizedError: ApiError = {
      code: 'NETWORK_ERROR',
      message: 'An unexpected network or server error occurred.',
    };

    if (error.response) {
      const data = error.response.data as any;
      normalizedError.code = data?.error?.code || `HTTP_${error.response.status}`;
      normalizedError.message = data?.error?.message || error.response.statusText;
      normalizedError.details = data?.error?.details || JSON.stringify(data);
    } else if (error.request) {
      normalizedError.code = 'TIMEOUT_OR_NETWORK_FAILURE';
      normalizedError.message = 'No response was received from the server. Check your network or connection.';
    } else {
      normalizedError.message = error.message;
    }

    return Promise.reject(normalizedError);
  }
);

export default apiClient;
