# RegulaAI Integrations

This document describes the integration features available in RegulaAI for high-severity compliance violation alerts.

## Overview

RegulaAI supports two types of integrations for alerting:

1. **Slack Webhook Integration** - Send high-severity violation alerts to Slack channels
2. **Email Integration** - Send professional HTML email alerts using Resend API

Both integrations are triggered automatically when high-severity violations (critical or high) are detected during website scans.

## Slack Webhook Integration

### Setup

1. **Create a Slack App**:
   - Go to [api.slack.com/apps](https://api.slack.com/apps)
   - Click "Create New App" → "From scratch"
   - Give your app a name and select your workspace

2. **Configure Incoming Webhooks**:
   - In your app settings, go to "Incoming Webhooks"
   - Toggle "Activate Incoming Webhooks" to On
   - Click "Add New Webhook to Workspace"
   - Select the channel where you want to receive alerts
   - Copy the webhook URL

3. **Configure in RegulaAI**:
   ```bash
   curl -X POST "http://localhost:8000/integrations/slack" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"webhook_url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"}'
   ```

### Message Format

Slack messages include:
- 🚨 High Severity Alert header
- Domain name and compliance score
- Top 3 issues with severity levels
- Timestamp and "View in Dashboard" button

### Example Message

```
🚨 High Severity Compliance Alert

Domain: example.com
Compliance Score: 65%

Top Issues Found:
1. Missing Cookie Consent Banner (HIGH)
2. Incomplete Privacy Policy (CRITICAL)
3. No Data Processing Agreement (MEDIUM)

[View in Dashboard] button
```

## Email Integration

### Setup

1. **Get Resend API Key**:
   - Sign up at [resend.com](https://resend.com)
   - Go to API Keys section
   - Create a new API key
   - Copy the API key

2. **Configure in RegulaAI**:
   ```bash
   curl -X POST "http://localhost:8000/integrations/email" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "resend_api_key": "re_YOUR_API_KEY",
       "notification_email": "alerts@yourcompany.com"
     }'
   ```

### Email Template

Emails are sent using a professional HTML template that includes:
- RegulaAI branding and logo
- High-severity alert badge
- Domain information and compliance score
- Top 3 issues with severity indicators
- Call-to-action button to view full report
- Quick action recommendations

### Email Features

- **Responsive Design**: Works on desktop and mobile
- **Professional Branding**: RegulaAI logo and styling
- **Severity Indicators**: Color-coded severity levels
- **Actionable Content**: Clear next steps and recommendations
- **Dashboard Integration**: Direct link to full scan report

## API Endpoints

### Configure Slack Webhook

```http
POST /integrations/slack
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "webhook_url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
}
```

**Response:**
```json
{
  "message": "Slack webhook configured successfully"
}
```

### Configure Email Settings

```http
POST /integrations/email
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "resend_api_key": "re_YOUR_API_KEY",
  "notification_email": "alerts@yourcompany.com"
}
```

**Response:**
```json
{
  "message": "Email settings configured successfully"
}
```

### Test Email Integration

```http
POST /integrations/test-email
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "test_email": "test@yourcompany.com"
}
```

**Response:**
```json
{
  "message": "Test email sent successfully"
}
```

### Get Integration Status

```http
GET /integrations/status
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "slack_configured": true,
  "email_configured": true,
  "notification_email": "alerts@yourcompany.com"
}
```

## Automatic Triggering

Integrations are automatically triggered when:

1. A scan detects high-severity violations (critical or high)
2. The organisation has configured at least one integration
3. The scan completes successfully

### Trigger Conditions

- **Slack**: Triggered if `slack_webhook_url` is configured
- **Email**: Triggered if both `resend_api_key` and `notification_email` are configured
- **Both**: Can be triggered simultaneously

### Notification Content

Both integrations include:
- **Domain**: The scanned website domain
- **Score**: Compliance score (0-100)
- **Top Issues**: Top 3 high-severity violations
- **Severity**: Critical, High, Medium, Low indicators
- **Timestamp**: When the alert was generated

## Testing

### Test Script

Use the provided test script to verify your integrations:

```bash
python test_integrations.py
```

This script allows you to:
1. Test Slack webhook with sample data
2. Test email integration with sample data
3. Test the notification manager
4. Run all tests together

### Manual Testing

You can also test integrations manually:

1. **Test Slack**:
   ```bash
   curl -X POST "https://hooks.slack.com/services/YOUR/WEBHOOK/URL" \
     -H "Content-Type: application/json" \
     -d '{"text": "Test message from RegulaAI"}'
   ```

2. **Test Resend**:
   ```bash
   curl -X POST "https://api.resend.com/emails" \
     -H "Authorization: Bearer re_YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "from": "alerts@regulaai.com",
       "to": ["test@yourcompany.com"],
       "subject": "Test Email",
       "html": "<h1>Test</h1>"
     }'
   ```

## Security Considerations

### API Key Security

- **Resend API Key**: Stored encrypted in the database
- **Slack Webhook URL**: Stored as-is (Slack webhooks are public URLs)
- **Access Control**: Only organisation owners can configure integrations

### Data Privacy

- **Email Content**: Contains only violation information, no sensitive data
- **Slack Messages**: Include domain and violation details only
- **Audit Logging**: All integration configuration changes are logged

### Rate Limiting

- **Slack**: Respects Slack's rate limits
- **Resend**: Respects Resend's rate limits
- **Error Handling**: Failed notifications don't block scan responses

## Troubleshooting

### Common Issues

1. **Slack Webhook Not Working**:
   - Verify the webhook URL is correct
   - Check if the Slack app is installed in your workspace
   - Ensure the channel exists and the app has access

2. **Email Not Sending**:
   - Verify the Resend API key is valid
   - Check if the email address is correct
   - Ensure your Resend account has sending permissions

3. **Notifications Not Triggering**:
   - Verify integrations are configured
   - Check if high-severity violations are detected
   - Review application logs for errors

### Debug Mode

Enable debug logging to troubleshoot issues:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Log Files

Check the application logs for integration-related errors:
- Slack webhook failures
- Email sending errors
- Configuration issues

## Best Practices

### Configuration

1. **Use Dedicated Channels**: Create separate Slack channels for different environments
2. **Test First**: Always test integrations before going live
3. **Monitor Alerts**: Set up monitoring for integration failures
4. **Regular Updates**: Keep API keys and webhook URLs up to date

### Content

1. **Actionable Alerts**: Include clear next steps in notifications
2. **Consistent Formatting**: Use consistent styling across all notifications
3. **Relevant Information**: Only include necessary violation details
4. **Dashboard Links**: Always include links to full reports

### Security

1. **Rotate Keys**: Regularly rotate Resend API keys
2. **Access Control**: Limit who can configure integrations
3. **Audit Logs**: Monitor configuration changes
4. **Error Handling**: Don't expose sensitive information in error messages

## Support

For integration support:

1. **Documentation**: Check this document first
2. **Test Script**: Use `test_integrations.py` for debugging
3. **Logs**: Review application logs for errors
4. **API Status**: Check Slack and Resend status pages
5. **Contact**: Reach out to the development team

## Future Enhancements

Planned improvements:

1. **Webhook Signatures**: Add signature verification for Slack webhooks
2. **Custom Templates**: Allow customisation of email templates
3. **Multiple Channels**: Support multiple Slack channels per organisation
4. **Scheduled Reports**: Send periodic compliance reports
5. **Integration Dashboard**: Web UI for managing integrations 