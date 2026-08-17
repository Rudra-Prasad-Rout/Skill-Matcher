"""
Quick diagnostic tool to test your Google Gmail SMTP connection.
Run this script to verify your Gmail credentials:
    python test_gmail_smtp.py
"""
import os
import smtplib
from email.mime.text import MIMEText
from ai_gmail_agent import AIGmailAgent

def test_connection():
    agent = AIGmailAgent()
    print("=" * 60)
    print("TeamX S30 Platform — Google Gmail SMTP Diagnostic")
    print("=" * 60)
    print(f"Configured Sender: '{agent.sender_email}'")
    print(f"App Password set : {'YES (' + '*' * len(agent.app_password) + ')' if agent.app_password else 'NO (Missing)'}")
    
    if not agent.sender_email or not agent.app_password or "your_" in agent.sender_email:
        print("\n[!] SETUP NEEDED:")
        print("Please edit the '.env' file in this folder with your real Gmail:")
        print("  GMAIL_USER=your_real_gmail@gmail.com")
        print("  GMAIL_APP_PASSWORD=your_16_character_app_password")
        print("\nHow to get a 16-character Google App Password in 1 minute:")
        print("1. Open: https://myaccount.google.com/security")
        print("2. Ensure 2-Step Verification is turned ON")
        print("3. Open: https://myaccount.google.com/apppasswords")
        print("4. Create an App Password named 'S30 Platform'")
        print("5. Paste the 16 characters into the .env file")
        return False

    print("\nConnecting to smtp.gmail.com:587...")
    try:
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=10) as server:
            server.starttls()
            server.login(agent.sender_email, agent.app_password)
            print("[OK] Logged in to Google Gmail SMTP successfully!")
            
            # Send test email
            test_recipient = agent.sender_email
            msg = MIMEText("Hello! This is a test email from TeamX S30 Platform. Your Google Gmail integration is working perfectly!")
            msg["Subject"] = "S30 Gmail Integration Test"
            msg["From"] = agent.sender_email
            msg["To"] = test_recipient
            
            server.sendmail(agent.sender_email, test_recipient, msg.as_string())
            print(f"[OK] Test email delivered to {test_recipient}")
            return True
    except smtplib.SMTPAuthenticationError:
        print("[ERROR] Authentication failed: Google rejected the login.")
        print("Please ensure you use a 16-character Google App Password (not your regular Gmail password).")
        return False
    except Exception as e:
        print(f"[ERROR] Connection error: {e}")
        return False

if __name__ == "__main__":
    test_connection()
