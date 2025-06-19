# OpenAPI Spec & TypeScript SDK Guide

This guide covers the implementation of OpenAPI spec exposure and TypeScript SDK generation for the RegulaAI API.

## Features Implemented

### 1. OpenAPI Spec Exposure

The FastAPI application now exposes a comprehensive OpenAPI specification with:

- **Proper tagging**: All endpoints are organized into logical groups (Auth, Scans, Billing, Integrations, Settings, Monitoring)
- **Custom OpenAPI generation**: Using `fastapi.openapi.utils.get_openapi` for enhanced spec generation
- **Enhanced metadata**: Contact information, server configurations, and detailed descriptions
- **Automatic documentation**: Available at `/docs` and `/redoc` endpoints

### 2. TypeScript SDK Generator

A complete TypeScript SDK has been created with:

- **Fully typed client**: Complete TypeScript definitions for all API endpoints
- **Multiple authentication methods**: Support for API key and bearer token authentication
- **Comprehensive error handling**: Proper error types and messages
- **NPM package ready**: Configured for publishing to npm as `@regulaai/sdk`

## OpenAPI Spec Features

### Endpoint Organization

All endpoints are tagged for better organization:

- **Auth**: User registration and authentication
- **Scans**: Website scanning and compliance checking
- **Billing**: Subscription and payment management
- **Integrations**: Slack and email notification setup
- **Settings**: API key management
- **Monitoring**: Metrics and badges

### Custom OpenAPI Generation

The app uses a custom OpenAPI generator that:

```python
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="RegulaAI Scanner API",
        version="0.1.0",
        description="Complete API for scanning websites for GDPR compliance with authentication, billing, and integrations",
        routes=app.routes,
    )
    
    # Add custom info
    openapi_schema["info"]["contact"] = {
        "name": "RegulaAI Support",
        "email": "support@regulaai.com",
        "url": "https://regulaai.com"
    }
    
    # Add servers
    openapi_schema["servers"] = [
        {
            "url": "http://localhost:8000",
            "description": "Local development server"
        },
        {
            "url": "https://api.regulaai.com",
            "description": "Production server"
        }
    ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
```

### Accessing the OpenAPI Spec

- **JSON format**: `GET /openapi.json`
- **YAML format**: `GET /openapi.yaml`
- **Interactive docs**: `GET /docs` (Swagger UI)
- **Alternative docs**: `GET /redoc` (ReDoc)

## TypeScript SDK Features

### Installation

```bash
npm install @regulaai/sdk
```

### Basic Usage

```typescript
import { RegulaAIClient } from '@regulaai/sdk';

const client = new RegulaAIClient({
  baseURL: 'https://api.regulaai.com',
  apiKey: 'your-api-key-here'
});

// Scan a website
const result = await client.scanWebsite({
  url: 'https://example.com'
});

console.log(`Compliance score: ${result.score}%`);
```

### Authentication Methods

#### API Key Authentication (Recommended)

```typescript
const client = new RegulaAIClient({
  apiKey: 'your-api-key-here'
});
```

#### Bearer Token Authentication

```typescript
const client = new RegulaAIClient({
  accessToken: 'your-access-token-here'
});
```

#### Runtime Authentication

```typescript
const client = new RegulaAIClient();

// Set API key
client.setApiKey('your-api-key-here');

// Or set access token
client.setAccessToken('your-access-token-here');
```

### Available Methods

#### Authentication
- `register(request: RegisterRequest)`: Register new user and organisation
- `login(request: LoginRequest)`: Login and get access tokens

#### Scanning
- `scanWebsite(request: ScanRequest)`: Scan single website
- `batchScan(request: BatchScanRequest)`: Scan multiple websites
- `parseBatchScanResults(ndjsonData: string)`: Parse batch results

#### Settings
- `createApiKey(request: ApiKeyCreateRequest)`: Create new API key

#### Billing
- `createCheckoutSession(request: CheckoutSessionRequest)`: Create subscription checkout

#### Integrations
- `configureSlackWebhook(request: SlackWebhookRequest)`: Setup Slack alerts
- `configureEmailSettings(request: EmailSettingsRequest)`: Setup email alerts
- `testEmailIntegration(request: TestIntegrationRequest)`: Test email setup
- `getIntegrationStatus()`: Get integration status

#### Monitoring
- `getMetrics()`: Get Prometheus metrics
- `getBadge(siteId: string)`: Get compliance badge

### Error Handling

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

## Development and Testing

### Testing OpenAPI Spec

```bash
# Test OpenAPI spec generation
python test_openapi.py

# Start the server and access docs
uvicorn app:app --reload
# Then visit http://localhost:8000/docs
```

### Building the SDK

```bash
cd sdk-ts

# Install dependencies
npm install

# Build the SDK
npm run build

# Test the SDK
node test-sdk.js
```

### SDK Generation from OpenAPI Spec

```bash
# Generate SDK from running API server
python generate_sdk.py http://localhost:8000

# Or use the build script
cd sdk-ts
./build.sh
```

## File Structure

```
crawler/
├── app.py                          # FastAPI app with OpenAPI configuration
├── test_openapi.py                 # OpenAPI spec testing script
├── generate_sdk.py                 # SDK generation script
├── sdk-ts/                         # TypeScript SDK
│   ├── package.json               # NPM package configuration
│   ├── tsconfig.json              # TypeScript configuration
│   ├── README.md                  # SDK documentation
│   ├── build.sh                   # Build script
│   ├── test-sdk.js                # SDK test script
│   └── src/
│       ├── index.ts               # Main SDK exports
│       ├── types.ts               # TypeScript type definitions
│       └── client.ts              # Main client class
└── OPENAPI_SDK_GUIDE.md           # This guide
```

## Publishing the SDK

### Local Development

```bash
cd sdk-ts
npm link
# In another project: npm link @regulaai/sdk
```

### Publishing to NPM

```bash
cd sdk-ts
npm login
npm publish
```

### Version Management

```bash
cd sdk-ts
npm version patch  # or minor/major
npm publish
```

## Configuration Options

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
```

## Type Safety

The SDK provides full TypeScript support:

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

## Best Practices

### API Key Management

1. Store API keys securely (environment variables, secret management)
2. Rotate API keys regularly
3. Use different keys for different environments

### Error Handling

1. Always wrap API calls in try-catch blocks
2. Handle specific error types appropriately
3. Implement retry logic for transient failures

### Performance

1. Reuse client instances when possible
2. Use batch scanning for multiple websites
3. Implement proper timeout handling

### Security

1. Never log API keys or access tokens
2. Use HTTPS in production
3. Validate all input data

## Troubleshooting

### Common Issues

1. **Authentication errors**: Check API key format and permissions
2. **Rate limiting**: Implement exponential backoff
3. **Network issues**: Check timeout settings and connectivity
4. **Type errors**: Ensure TypeScript version compatibility

### Debug Mode

```typescript
// Enable debug logging
const client = new RegulaAIClient({
  baseURL: 'https://api.regulaai.com',
  apiKey: 'your-api-key',
  timeout: 60000  // Increase timeout for debugging
});
```

## Support

- **Documentation**: [https://docs.regulaai.com](https://docs.regulaai.com)
- **API Reference**: [https://api.regulaai.com/docs](https://api.regulaai.com/docs)
- **SDK Issues**: [https://github.com/regulaai/regulaai-sdk-typescript/issues](https://github.com/regulaai/regulaai-sdk-typescript/issues)
- **Email**: support@regulaai.com 