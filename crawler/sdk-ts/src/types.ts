/**
 * TypeScript type definitions for RegulaAI API
 */

export interface ScanRequest {
  url: string;
  persona?: string;
}

export interface BatchScanRequest {
  scans: ScanRequest[];
}

export interface RegisterRequest {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  organisation_name: string;
  organisation_domain?: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface ApiKeyCreateRequest {
  name: string;
}

export interface ApiKeyResponse {
  api_key: string;
  id: number;
}

export interface CheckoutSessionRequest {
  success_url: string;
  cancel_url: string;
}

export interface CheckoutSessionResponse {
  checkout_url: string;
}

export interface SlackWebhookRequest {
  webhook_url: string;
}

export interface EmailSettingsRequest {
  resend_api_key: string;
  notification_email: string;
}

export interface TestIntegrationRequest {
  test_email: string;
}

export interface IntegrationStatusResponse {
  slack_configured: boolean;
  email_configured: boolean;
  notification_email?: string;
}

export interface Violation {
  title: string;
  description: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  rule_id?: string;
}

export interface ScanResponse {
  url: string;
  cookies: Array<{
    name: string;
    value: string;
    domain: string;
    path: string;
  }>;
  cookie_banner_detected: boolean;
  cookie_banner_selectors: string[];
  scan_time_ms: number;
  score: number;
  violations: Violation[];
}

export interface BatchScanResponse {
  url: string;
  error?: string;
  cookies?: Array<{
    name: string;
    value: string;
    domain: string;
    path: string;
  }>;
  cookie_banner_detected?: boolean;
  cookie_banner_selectors?: string[];
  scan_time_ms?: number;
  score?: number;
  violations?: Violation[];
}

export interface MessageResponse {
  message: string;
}

export interface HTTPValidationError {
  detail: Array<{
    loc: string[];
    msg: string;
    type: string;
  }>;
}

export interface HTTPError {
  detail: string;
}

export interface RegulaAIConfig {
  baseURL?: string;
  apiKey?: string;
  accessToken?: string;
  timeout?: number;
}

export type AuthMethod = 'apiKey' | 'bearer';

export interface RequestConfig {
  headers?: Record<string, string>;
  timeout?: number;
} 