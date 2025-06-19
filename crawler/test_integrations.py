#!/usr/bin/env python3
"""
Test script for Slack webhook and email integrations.
This script can be used to test the integrations without running a full scan.
"""

import os
import sys
import asyncio
from integrations import SlackIntegration, EmailIntegration, NotificationManager
from models import Organisation, get_db, SessionLocal

def test_slack_integration():
    """Test Slack webhook integration with a sample message."""
    webhook_url = input("Enter your Slack webhook URL: ").strip()
    
    if not webhook_url:
        print("❌ No webhook URL provided")
        return False
    
    slack = SlackIntegration(webhook_url)
    
    # Sample data
    domain = "example.com"
    score = 65
    top_issues = [
        {
            "title": "Missing Cookie Consent Banner",
            "description": "No cookie consent banner found on the website",
            "severity": "high"
        },
        {
            "title": "Incomplete Privacy Policy",
            "description": "Privacy policy is missing required GDPR sections",
            "severity": "critical"
        },
        {
            "title": "No Data Processing Agreement",
            "description": "No DPA found for third-party data processors",
            "severity": "medium"
        }
    ]
    
    print("📤 Sending test Slack message...")
    success = slack.send_violation_alert(domain, score, top_issues)
    
    if success:
        print("✅ Slack message sent successfully!")
        return True
    else:
        print("❌ Failed to send Slack message")
        return False

def test_email_integration():
    """Test email integration with a sample email."""
    resend_api_key = input("Enter your Resend API key: ").strip()
    test_email = input("Enter test email address: ").strip()
    
    if not resend_api_key or not test_email:
        print("❌ Missing API key or email address")
        return False
    
    email = EmailIntegration(resend_api_key)
    
    # Sample data
    domain = "example.com"
    score = 65
    top_issues = [
        {
            "title": "Missing Cookie Consent Banner",
            "description": "No cookie consent banner found on the website",
            "severity": "high"
        },
        {
            "title": "Incomplete Privacy Policy",
            "description": "Privacy policy is missing required GDPR sections",
            "severity": "critical"
        },
        {
            "title": "No Data Processing Agreement",
            "description": "No DPA found for third-party data processors",
            "severity": "medium"
        }
    ]
    dashboard_url = "https://app.regulaai.com/dashboard?domain=example.com"
    
    print("📧 Sending test email...")
    success = email.send_violation_alert(test_email, domain, score, top_issues, dashboard_url)
    
    if success:
        print("✅ Test email sent successfully!")
        return True
    else:
        print("❌ Failed to send test email")
        return False

def test_notification_manager():
    """Test the notification manager with sample organisation data."""
    print("\n🔧 Testing Notification Manager...")
    
    # Create a mock organisation
    class MockOrganisation:
        def __init__(self):
            self.slack_webhook_url = input("Enter Slack webhook URL (or press Enter to skip): ").strip() or None
            self.resend_api_key = input("Enter Resend API key (or press Enter to skip): ").strip() or None
            self.notification_email = input("Enter notification email (or press Enter to skip): ").strip() or None
    
    org = MockOrganisation()
    
    if not org.slack_webhook_url and not org.resend_api_key:
        print("❌ No integrations configured")
        return False
    
    notification_manager = NotificationManager(org)
    
    # Sample data
    domain = "example.com"
    score = 65
    violations = [
        {
            "title": "Missing Cookie Consent Banner",
            "description": "No cookie consent banner found on the website",
            "severity": "high"
        },
        {
            "title": "Incomplete Privacy Policy",
            "description": "Privacy policy is missing required GDPR sections",
            "severity": "critical"
        },
        {
            "title": "No Data Processing Agreement",
            "description": "No DPA found for third-party data processors",
            "severity": "medium"
        },
        {
            "title": "Missing Terms of Service",
            "description": "Terms of service page not found",
            "severity": "low"
        }
    ]
    
    print("📤 Sending notifications...")
    results = notification_manager.send_high_severity_alert(domain, score, violations)
    
    if results:
        print("✅ Notification results:")
        for channel, success in results.items():
            status = "✅ Success" if success else "❌ Failed"
            print(f"  {channel}: {status}")
        return True
    else:
        print("❌ No notifications sent (no high-severity violations)")
        return False

def main():
    """Main test function."""
    print("🚀 RegulaAI Integration Test Suite")
    print("=" * 40)
    
    while True:
        print("\nSelect a test to run:")
        print("1. Test Slack webhook")
        print("2. Test email integration")
        print("3. Test notification manager")
        print("4. Run all tests")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            test_slack_integration()
        elif choice == "2":
            test_email_integration()
        elif choice == "3":
            test_notification_manager()
        elif choice == "4":
            print("\n🔄 Running all tests...")
            test_slack_integration()
            test_email_integration()
            test_notification_manager()
        elif choice == "5":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main() 