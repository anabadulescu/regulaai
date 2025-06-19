import os
import requests
import json
from typing import List, Dict, Any, Optional
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class SlackIntegration:
    """Handles Slack webhook notifications for high-severity violations."""
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
    def send_violation_alert(self, domain: str, score: int, top_issues: List[Dict[str, Any]]) -> bool:
        """
        Send a high-severity violation alert to Slack.
        
        Args:
            domain: The scanned domain
            score: Compliance score (0-100)
            top_issues: List of top 3 issues with title, description, severity
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        try:
            # Create the Slack message
            message = self._create_slack_message(domain, score, top_issues)
            
            # Send to Slack webhook
            response = requests.post(
                self.webhook_url,
                json=message,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"Slack alert sent successfully for domain: {domain}")
                return True
            else:
                logger.error(f"Failed to send Slack alert. Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending Slack alert: {str(e)}")
            return False
    
    def _create_slack_message(self, domain: str, score: int, top_issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a formatted Slack message for the violation alert."""
        
        # Create issue blocks
        issue_blocks = []
        for i, issue in enumerate(top_issues[:3], 1):
            severity_color = {
                'critical': '#dc3545',
                'high': '#fd7e14',
                'medium': '#ffc107',
                'low': '#28a745'
            }.get(issue.get('severity', 'medium').lower(), '#6c757d')
            
            issue_block = {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*{i}. {issue.get('title', 'Unknown Issue')}*"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Severity:* <span style='color:{severity_color}'>{issue.get('severity', 'Unknown').upper()}</span>"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Description:* {issue.get('description', 'No description available')}"
                    }
                ]
            }
            issue_blocks.append(issue_block)
        
        # Create the main message
        message = {
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "🚨 High Severity Compliance Alert",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Domain:* {domain}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Compliance Score:* {score}%"
                        }
                    ]
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Top Issues Found:*"
                    }
                }
            ]
        }
        
        # Add issue blocks
        message["blocks"].extend(issue_blocks)
        
        # Add footer
        message["blocks"].extend([
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Alert Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}"
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "View in Dashboard",
                            "emoji": True
                        },
                        "url": f"https://app.regulaai.com/dashboard?domain={domain}",
                        "style": "primary"
                    }
                ]
            }
        ])
        
        return message


class EmailIntegration:
    """Handles email notifications using Resend API."""
    
    def __init__(self, resend_api_key: str, from_email: str = "alerts@regulaai.com"):
        self.resend_api_key = resend_api_key
        self.from_email = from_email
        self.template_env = Environment(loader=FileSystemLoader('templates'))
    
    def send_violation_alert(self, to_email: str, domain: str, score: int, 
                           top_issues: List[Dict[str, Any]], dashboard_url: str) -> bool:
        """
        Send a high-severity violation alert email.
        
        Args:
            to_email: Recipient email address
            domain: The scanned domain
            score: Compliance score (0-100)
            top_issues: List of top 3 issues
            dashboard_url: URL to the dashboard report
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        try:
            # Render the email template
            template = self.template_env.get_template('alert_email.html')
            html_content = template.render(
                domain=domain,
                score=score,
                top_issues=top_issues[:3],
                dashboard_url=dashboard_url
            )
            
            # Send via Resend API
            response = requests.post(
                'https://api.resend.com/emails',
                headers={
                    'Authorization': f'Bearer {self.resend_api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'from': self.from_email,
                    'to': [to_email],
                    'subject': f'🚨 High Severity Compliance Alert - {domain}',
                    'html': html_content
                },
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"Email alert sent successfully to {to_email} for domain: {domain}")
                return True
            else:
                logger.error(f"Failed to send email alert. Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending email alert: {str(e)}")
            return False


class NotificationManager:
    """Manages both Slack and email notifications for high-severity violations."""
    
    def __init__(self, organisation):
        self.organisation = organisation
        self.slack_integration = None
        self.email_integration = None
        
        # Initialize Slack integration if webhook URL is configured
        if organisation.slack_webhook_url:
            self.slack_integration = SlackIntegration(organisation.slack_webhook_url)
        
        # Initialize email integration if Resend API key is configured
        if organisation.resend_api_key and organisation.notification_email:
            self.email_integration = EmailIntegration(
                organisation.resend_api_key,
                from_email="alerts@regulaai.com"
            )
    
    def send_high_severity_alert(self, domain: str, score: int, 
                                violations: List[Dict[str, Any]]) -> Dict[str, bool]:
        """
        Send high-severity alerts via configured channels.
        
        Args:
            domain: The scanned domain
            score: Compliance score (0-100)
            violations: List of all violations
            
        Returns:
            Dict with status for each notification channel
        """
        # Filter high-severity violations
        high_severity_violations = [
            v for v in violations 
            if v.get('severity', '').lower() in ['high', 'critical']
        ]
        
        if not high_severity_violations:
            logger.info(f"No high-severity violations found for domain: {domain}")
            return {}
        
        # Get top 3 issues
        top_issues = sorted(high_severity_violations, 
                          key=lambda x: {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}.get(x.get('severity', 'low').lower(), 0),
                          reverse=True)[:3]
        
        results = {}
        
        # Send Slack notification
        if self.slack_integration:
            results['slack'] = self.slack_integration.send_violation_alert(domain, score, top_issues)
        
        # Send email notification
        if self.email_integration and self.organisation.notification_email:
            dashboard_url = f"https://app.regulaai.com/dashboard?domain={domain}"
            results['email'] = self.email_integration.send_violation_alert(
                self.organisation.notification_email,
                domain,
                score,
                top_issues,
                dashboard_url
            )
        
        logger.info(f"Notification results for domain {domain}: {results}")
        return results


def test_slack_webhook(webhook_url: str) -> bool:
    """Test if a Slack webhook URL is valid."""
    try:
        test_message = {
            "text": "🔧 RegulaAI webhook test - If you see this, your webhook is working correctly!"
        }
        
        response = requests.post(
            webhook_url,
            json=test_message,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Error testing Slack webhook: {str(e)}")
        return False


def test_resend_api_key(api_key: str, test_email: str) -> bool:
    """Test if a Resend API key is valid."""
    try:
        response = requests.post(
            'https://api.resend.com/emails',
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            },
            json={
                'from': 'alerts@regulaai.com',
                'to': [test_email],
                'subject': '🔧 RegulaAI Email Test',
                'html': '<h1>RegulaAI Email Test</h1><p>If you receive this email, your Resend API key is working correctly!</p>'
            },
            timeout=10
        )
        
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Error testing Resend API key: {str(e)}")
        return False 