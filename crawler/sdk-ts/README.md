# RegulaAI TypeScript SDK

A fully typed TypeScript SDK for the RegulaAI GDPR compliance scanning API.

## Installation

```bash
npm install @regulaai/sdk
```

## Quick Start

```typescript
import { RegulaAIClient } from '@regulaai/sdk';

// Initialize the client with your API key
const client = new RegulaAIClient({
  baseURL: 'https://api.regulaai.com',
  apiKey: 'your-api-key-here'
});

// Scan a website for GDPR compliance
const result = await client.scanWebsite({
  url: 'https://example.com'
});

console.log(`Compliance score: ${result.score}%`);
console.log(`Violations found: ${result.violations.length}`);
```

## Authentication

The SDK supports two authentication methods:

### API Key Authentication (Recommended)

```typescript
const client = new RegulaAIClient({
  apiKey: 'your-api-key-here'
});
```

### Bearer Token Authentication

```typescript
const client = new RegulaAIClient({
  accessToken: 'your-access-token-here'
});
```

You can also set authentication after client creation:

```typescript
const client = new RegulaAIClient();

// Set API key
client.setApiKey('your-api-key-here');

// Or set access token
client.setAccessToken('your-access-token-here');
```

## API Examples

### Authentication

```typescript
// Register a new user and organisation
await client.register({
  email: 'user@example.com',
  password: 'secure-password',
  first_name: 'John',
  last_name: 'Doe',
  organisation_name: 'Example Corp',
  organisation_domain: 'example.com'
});

// Login and get access tokens
const loginResponse = await client.login({
  email: 'user@example.com',
  password: 'secure-password'
});

// Access token is automatically set after login
console.log('Logged in successfully');
```

### Website Scanning

```typescript
// Scan a single website
const scanResult = await client.scanWebsite({
  url: 'https://example.com',
  persona: 'european-user' // optional
});

console.log(`URL: ${scanResult.url}`);
console.log(`Compliance Score: ${scanResult.score}%`);
console.log(`Cookie Banner Detected: ${scanResult.cookie_banner_detected}`);
console.log(`Scan Time: ${scanResult.scan_time_ms}ms`);

// Display violations
scanResult.violations.forEach(violation => {
  console.log(`${violation.severity.toUpperCase()}: ${violation.title}`);
  console.log(`  ${violation.description}`);
});
```

### Batch Scanning

```typescript
// Scan multiple websites
const batchRequest = {
  scans: [
    { url: 'https://example1.com' },
    { url: 'https://example2.com' },
    { url: 'https://example3.com' }
  ]
};

const ndjsonResults = await client.batchScan(batchRequest);
const results = client.parseBatchScanResults(ndjsonResults);

results.forEach(result => {
  console.log(`${result.url}: ${result.score}% compliance`);
});
```

### API Key Management

```typescript
// Create a new API key
const apiKeyResponse = await client.createApiKey({
  name: 'Production API Key'
});

console.log(`New API Key: ${apiKeyResponse.api_key}`);
console.log(`Key ID: ${apiKeyResponse.id}`);
```

### Billing

```typescript
// Create a checkout session for subscription
const checkoutSession = await client.createCheckoutSession({
  success_url: 'https://your-app.com/success',
  cancel_url: 'https://your-app.com/cancel'
});

console.log(`Checkout URL: ${checkoutSession.checkout_url}`);
```

### Integrations

```typescript
// Configure Slack webhook
await client.configureSlackWebhook({
  webhook_url: 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'
});

// Configure email settings
await client.configureEmailSettings({
  resend_api_key: 're_YOUR_API_KEY',
  notification_email: 'alerts@yourcompany.com'
});

// Test email integration
await client.testEmailIntegration({
  test_email: 'test@yourcompany.com'
});

// Get integration status
const status = await client.getIntegrationStatus();
console.log(`Slack configured: ${status.slack_configured}`);
console.log(`Email configured: ${status.email_configured}`);
```

### Monitoring

```typescript
// Get Prometheus metrics
const metrics = await client.getMetrics();
console.log('Metrics:', metrics);

// Get compliance badge
const badge = await client.getBadge('example-com');
console.log('Badge SVG:', badge);
```

## Error Handling

The SDK provides comprehensive error handling:

```typescript
try {
  const result = await client.scanWebsite({
    url: 'https://example.com'
  });
} catch (error) {
  if (error.message.includes('Authentication failed')) {
    console.error('Please check your API key or access token');
  } else if (error.message.includes('Scan quota exceeded')) {
    console.error('Please upgrade your plan or wait for reset');
  } else if (error.message.includes('Rate limit exceeded')) {
    console.error('Please try again later');
  } else {
    console.error('An error occurred:', error.message);
  }
}
```

## Configuration

### Client Configuration

```typescript
const client = new RegulaAIClient({
  baseURL: 'https://api.regulaai.com', // Default: https://api.regulaai.com
  apiKey: 'your-api-key',              // Optional
  accessToken: 'your-token',           // Optional
  timeout: 30000                       // Default: 30000ms
});
```

### Runtime Configuration

```typescript
// Update base URL
client.setBaseURL('https://staging-api.regulaai.com');

// Update timeout
client.setTimeout(60000);

// Check authentication status
if (client.isAuthenticated()) {
  console.log('Client is authenticated');
}

// Get current configuration
console.log('Base URL:', client.getBaseURL());
console.log('Timeout:', client.getTimeout());
console.log('Auth method:', client.getAuthMethod());
```

## TypeScript Support

The SDK is fully typed with TypeScript:

```typescript
import { 
  RegulaAIClient, 
  ScanRequest, 
  ScanResponse, 
  Violation 
} from '@regulaai/sdk';

// All types are available
const request: ScanRequest = {
  url: 'https://example.com'
};

const response: ScanResponse = await client.scanWebsite(request);

// Violations are properly typed
response.violations.forEach((violation: Violation) => {
  // violation.severity is typed as 'critical' | 'high' | 'medium' | 'low'
  console.log(violation.severity);
});
```

## Response Types

### ScanResponse

```typescript
interface ScanResponse {
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
```

### Violation

```typescript
interface Violation {
  title: string;
  description: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  rule_id?: string;
}
```

## Development

### Building

```bash
npm run build
```

### Development Mode

```bash
npm run dev
```

### Testing

```bash
npm test
```

### Linting

```bash
npm run lint
```

### Formatting

```bash
npm run format
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run the test suite
6. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

- Documentation: [https://docs.regulaai.com](https://docs.regulaai.com)
- API Reference: [https://api.regulaai.com/docs](https://api.regulaai.com/docs)
- Issues: [https://github.com/regulaai/regulaai-sdk-typescript/issues](https://github.com/regulaai/regulaai-sdk-typescript/issues)
- Email: support@regulaai.com 