/**
 * Simple test script for RegulaAI TypeScript SDK
 * Run with: node test-sdk.js
 */

const { RegulaAIClient } = require('./dist/index.js');

async function testSDK() {
    console.log('Testing RegulaAI TypeScript SDK...\n');

    // Initialize client
    const client = new RegulaAIClient({
        baseURL: 'http://localhost:8000',
        // apiKey: 'your-api-key-here' // Uncomment and add your API key
    });

    try {
        // Test 1: Check if client is properly initialized
        console.log('✓ Client initialized');
        console.log(`Base URL: ${client.getBaseURL()}`);
        console.log(`Timeout: ${client.getTimeout()}ms`);
        console.log(`Auth method: ${client.getAuthMethod()}`);
        console.log(`Authenticated: ${client.isAuthenticated()}\n`);

        // Test 2: Get metrics (no auth required)
        console.log('Testing metrics endpoint...');
        const metrics = await client.getMetrics();
        console.log('✓ Metrics endpoint working');
        console.log(`Metrics length: ${metrics.length} characters\n`);

        // Test 3: Get badge (no auth required)
        console.log('Testing badge endpoint...');
        const badge = await client.getBadge('test-site');
        console.log('✓ Badge endpoint working');
        console.log(`Badge type: ${typeof badge}\n`);

        // Test 4: Test scan endpoint (requires authentication)
        console.log('Testing scan endpoint (requires authentication)...');
        try {
            const scanResult = await client.scanWebsite({
                url: 'https://example.com'
            });
            console.log('✓ Scan endpoint working');
            console.log(`Scan result: ${JSON.stringify(scanResult, null, 2)}\n`);
        } catch (error) {
            console.log('⚠ Scan endpoint requires authentication');
            console.log(`Error: ${error.message}\n`);
        }

        console.log('🎉 SDK test completed successfully!');

    } catch (error) {
        console.error('✗ SDK test failed:', error.message);
        process.exit(1);
    }
}

// Run the test
testSDK().catch(console.error); 