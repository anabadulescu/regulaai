import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import {
  RegulaAIConfig,
  AuthMethod,
  RequestConfig,
  ScanRequest,
  ScanResponse,
  BatchScanRequest,
  RegisterRequest,
  LoginRequest,
  LoginResponse,
  ApiKeyCreateRequest,
  ApiKeyResponse,
  CheckoutSessionRequest,
  CheckoutSessionResponse,
  SlackWebhookRequest,
  EmailSettingsRequest,
  TestIntegrationRequest,
  IntegrationStatusResponse,
  MessageResponse,
  HTTPValidationError,
  HTTPError
} from './types';

/**
 * RegulaAI TypeScript SDK Client
 * 
 * A fully typed client for the RegulaAI GDPR compliance scanning API.
 * 
 * @example
 * ```typescript
 * import { RegulaAIClient } from '@regulaai/sdk';
 * 
 * const client = new RegulaAIClient({
 *   baseURL: 'https://api.regulaai.com',
 *   apiKey: 'your-api-key'
 * });
 * 
 * // Scan a website
 * const result = await client.scanWebsite({
 *   url: 'https://example.com'
 * });
 * 
 * console.log(`Compliance score: ${result.score}%`);
 * ```
 */
export class RegulaAIClient {
  private axiosInstance: AxiosInstance;
  private authMethod: AuthMethod = 'apiKey';
  private accessToken?: string;
  private apiKey?: string;

  constructor(config: RegulaAIConfig = {}) {
    this.axiosInstance = axios.create({
      baseURL: config.baseURL || 'https://api.regulaai.com',
      timeout: config.timeout || 30000,
      headers: {
        'Content-Type': 'application/json',
        'User-Agent': 'RegulaAI-SDK-TypeScript/0.1.0'
      }
    });

    // Set up authentication
    if (config.accessToken) {
      this.setAccessToken(config.accessToken);
    } else if (config.apiKey) {
      this.setApiKey(config.apiKey);
    }

    // Add response interceptor for error handling
    this.axiosInstance.interceptors.response.use(
      (response: AxiosResponse) => response,
      (error: any) => {
        if (error.response?.data) {
          // Enhance error with API response details
          error.apiError = error.response.data;
        }
        return Promise.reject(error);
      }
    );
  }

  /**
   * Set the API key for authentication
   */
  setApiKey(apiKey: string): void {
    this.apiKey = apiKey;
    this.authMethod = 'apiKey';
    this.axiosInstance.defaults.headers.common['x-api-key'] = apiKey;
    // Remove bearer token if it was set
    delete this.axiosInstance.defaults.headers.common['Authorization'];
  }

  /**
   * Set the access token for bearer authentication
   */
  setAccessToken(accessToken: string): void {
    this.accessToken = accessToken;
    this.authMethod = 'bearer';
    this.axiosInstance.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`;
    // Remove API key if it was set
    delete this.axiosInstance.defaults.headers.common['x-api-key'];
  }

  /**
   * Get the current authentication method
   */
  getAuthMethod(): AuthMethod {
    return this.authMethod;
  }

  /**
   * Make an authenticated request
   */
  private async request<T>(config: AxiosRequestConfig): Promise<T> {
    try {
      const response: AxiosResponse<T> = await this.axiosInstance.request(config);
      return response.data;
    } catch (error: any) {
      if (error.response?.status === 401) {
        throw new Error('Authentication failed. Please check your API key or access token.');
      }
      if (error.response?.status === 403) {
        throw new Error('Insufficient permissions for this operation.');
      }
      if (error.response?.status === 402) {
        throw new Error('Scan quota exceeded. Please upgrade your plan or wait for reset.');
      }
      if (error.response?.status === 429) {
        throw new Error('Rate limit exceeded. Please try again later.');
      }
      if (error.apiError) {
        throw new Error(error.apiError.detail || 'API request failed');
      }
      throw error;
    }
  }

  // Auth endpoints

  /**
   * Register a new user and organisation
   */
  async register(request: RegisterRequest): Promise<MessageResponse> {
    return this.request<MessageResponse>({
      method: 'POST',
      url: '/auth/register',
      data: request
    });
  }

  /**
   * Login and get access tokens
   */
  async login(request: LoginRequest): Promise<LoginResponse> {
    const response = await this.request<LoginResponse>({
      method: 'POST',
      url: '/auth/login',
      data: request
    });

    // Automatically set the access token if login is successful
    if (response.access_token) {
      this.setAccessToken(response.access_token);
    }

    return response;
  }

  // Scan endpoints

  /**
   * Scan a single website for GDPR compliance
   */
  async scanWebsite(request: ScanRequest): Promise<ScanResponse> {
    return this.request<ScanResponse>({
      method: 'POST',
      url: '/scan',
      data: request
    });
  }

  /**
   * Scan multiple websites in batch
   * Returns a stream of results in NDJSON format
   */
  async batchScan(request: BatchScanRequest): Promise<string> {
    const response = await this.axiosInstance.request({
      method: 'POST',
      url: '/batch_scan',
      data: request,
      responseType: 'text'
    });
    return response.data;
  }

  /**
   * Parse batch scan results from NDJSON format
   */
  parseBatchScanResults(ndjsonData: string): ScanResponse[] {
    return ndjsonData
      .trim()
      .split('\n')
      .map(line => JSON.parse(line))
      .filter(result => !result.error);
  }

  // Settings endpoints

  /**
   * Create a new API key
   */
  async createApiKey(request: ApiKeyCreateRequest): Promise<ApiKeyResponse> {
    return this.request<ApiKeyResponse>({
      method: 'POST',
      url: '/settings/api-keys',
      data: request
    });
  }

  // Billing endpoints

  /**
   * Create a checkout session for subscription
   */
  async createCheckoutSession(request: CheckoutSessionRequest): Promise<CheckoutSessionResponse> {
    return this.request<CheckoutSessionResponse>({
      method: 'POST',
      url: '/billing/create-checkout-session',
      data: request
    });
  }

  // Integration endpoints

  /**
   * Configure Slack webhook for high-severity alerts
   */
  async configureSlackWebhook(request: SlackWebhookRequest): Promise<MessageResponse> {
    return this.request<MessageResponse>({
      method: 'POST',
      url: '/integrations/slack',
      data: request
    });
  }

  /**
   * Configure email settings for high-severity alerts
   */
  async configureEmailSettings(request: EmailSettingsRequest): Promise<MessageResponse> {
    return this.request<MessageResponse>({
      method: 'POST',
      url: '/integrations/email',
      data: request
    });
  }

  /**
   * Test email integration
   */
  async testEmailIntegration(request: TestIntegrationRequest): Promise<MessageResponse> {
    return this.request<MessageResponse>({
      method: 'POST',
      url: '/integrations/test-email',
      data: request
    });
  }

  /**
   * Get integration status
   */
  async getIntegrationStatus(): Promise<IntegrationStatusResponse> {
    return this.request<IntegrationStatusResponse>({
      method: 'GET',
      url: '/integrations/status'
    });
  }

  // Monitoring endpoints

  /**
   * Get Prometheus metrics
   */
  async getMetrics(): Promise<string> {
    const response = await this.axiosInstance.request({
      method: 'GET',
      url: '/metrics',
      responseType: 'text'
    });
    return response.data;
  }

  /**
   * Get compliance badge for a site
   */
  async getBadge(siteId: string): Promise<string> {
    const response = await this.axiosInstance.request({
      method: 'GET',
      url: `/badge/${siteId}`,
      responseType: 'text'
    });
    return response.data;
  }

  // Utility methods

  /**
   * Check if the client is properly authenticated
   */
  isAuthenticated(): boolean {
    return !!(this.accessToken || this.apiKey);
  }

  /**
   * Get the current base URL
   */
  getBaseURL(): string {
    return this.axiosInstance.defaults.baseURL || '';
  }

  /**
   * Update the base URL
   */
  setBaseURL(baseURL: string): void {
    this.axiosInstance.defaults.baseURL = baseURL;
  }

  /**
   * Get the current timeout
   */
  getTimeout(): number {
    return this.axiosInstance.defaults.timeout || 30000;
  }

  /**
   * Update the timeout
   */
  setTimeout(timeout: number): void {
    this.axiosInstance.defaults.timeout = timeout;
  }
} 