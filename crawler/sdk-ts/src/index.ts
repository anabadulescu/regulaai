/**
 * RegulaAI TypeScript SDK
 * 
 * A fully typed client for the RegulaAI GDPR compliance scanning API.
 * 
 * @packageDocumentation
 */

import { RegulaAIClient } from './client';
export { RegulaAIClient } from './client';
export * from './types';

// Re-export commonly used types for convenience
export type {
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
  Violation,
  RegulaAIConfig,
  AuthMethod
} from './types';

// Default export for convenience
export default RegulaAIClient; 