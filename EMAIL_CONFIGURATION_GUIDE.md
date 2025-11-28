# Email Configuration Guide for Dashboard

## Overview
The dashboard can send email alerts when critical errors occur during pipeline processing. This guide explains how to set up email alerts.

---

## Email Alert Setup Options

### Option 1: Gmail (Recommended for beginners)

**Step 1: Enable 2-Factor Authentication**
1. Go to https://myaccount.google.com/
2. Click "Security" in the left menu
3. Scroll to "2-Step Verification"
4. Click "Enable" and follow the prompts
5. Verify your phone number

**Step 2: Generate App Password**
1. Go to https://myaccount.google.com/apppasswords
2. In "Select app", choose "Mail"
3. In "Select device", choose "Windows Computer" (or your device)
4. Click "Generate"
5. Google will show you a 16-character password
6. **COPY THIS PASSWORD** - you'll need it for the dashboard

**Step 3: Enter in Dashboard Settings**
- **SMTP Server:** `smtp.gmail.com`
- **SMTP Port:** `587`
- **Sender Email:** Your Gmail address (e.g., `your_email@gmail.com`)
- **Sender Password:** The 16-character app password from Step 2 (NOT your Gmail password)
- **Recipient Email(s):** Email(s) to receive alerts (e.g., `admin@example.com`)

**Step 4: Test Configuration**
- Click "🔧 Test Email Configuration"
- You should get a success message
- Check your recipient inbox for test email (may take 30 seconds)

---

### Option 2: Outlook/Microsoft 365

**Step 1: Enable App Password (if using 2FA)**
1. Go to https://account.microsoft.com/
2. Click "Security" 
3. Set up "Two-step verification"
4. Generate an app password

**Step 2: Enter in Dashboard Settings**
- **SMTP Server:** `smtp.office365.com`
- **SMTP Port:** `587`
- **Sender Email:** Your Outlook email (e.g., `your_email@outlook.com`)
- **Sender Password:** Your Outlook password or app password
- **Recipient Email(s):** Email(s) to receive alerts

---

### Option 3: Company Email (Outlook/Exchange)

**Contact your IT department for:**
- SMTP Server address (e.g., `mail.company.com`)
- SMTP Port (typically 587 or 25)
- Your email username
- Your email password

**Enter in Dashboard Settings:**
- **SMTP Server:** Company SMTP address
- **SMTP Port:** Port provided by IT
- **Sender Email:** Your company email
- **Sender Password:** Your company email password
- **Recipient Email(s):** Alert recipients

---

### Option 4: Other Email Providers

**Common SMTP Settings:**

| Provider | SMTP Server | Port | TLS |
|----------|-------------|------|-----|
| Gmail | smtp.gmail.com | 587 | Yes |
| Outlook | smtp.office365.com | 587 | Yes |
| Yahoo | smtp.mail.yahoo.com | 587 | Yes |
| iCloud | smtp.mail.me.com | 587 | Yes |
| SendGrid | smtp.sendgrid.net | 587 | Yes |

---

## Security Best Practices

### 1. Never Share Your App Password
- Keep your sender password secure
- Don't share the password with others
- Don't commit it to version control

### 2. Use App Passwords (Not Account Password)
- Gmail: Use 16-character app password
- Outlook: Use app password if available
- Never use your actual account password

### 3. Limit Recipients
- Only add email addresses that need alerts
- Keep recipient list small and relevant

### 4. Test Before Production
- Click "Test Email Configuration" before running pipelines
- Verify test emails arrive in recipient inboxes
- Check spam/junk folders if not received

### 5. Disable if Not Needed
- Uncheck "Enable Email Alerts on Critical Errors" if not using
- This prevents unnecessary SMTP connections

---

## What Gets Emailed

When a critical error occurs during pipeline processing:

**Email contains:**
- Error message and stack trace
- Symbol that failed
- Timestamp of error
- Pipeline configuration details
- Dashboard screenshot (if available)

**Example Error Email Subject:**
```
[ALERT] Stock Pipeline Error - AAPL Failed
```

---

## Troubleshooting

### "Authentication Failed" Error
- ✓ Verify sender email is correct
- ✓ Check app password is correct (16 characters for Gmail)
- ✓ Ensure 2-Factor Authentication is enabled
- ✓ For Gmail: Make sure you generated the app password, not using account password

### "Connection Timeout" Error
- ✓ Check SMTP server address is correct
- ✓ Verify SMTP port is correct (usually 587)
- ✓ Check your firewall/network allows outgoing email
- ✓ Some corporate networks block email - check with IT

### "Recipients Not Receiving Emails"
- ✓ Check spam/junk folder
- ✓ Add sender to contacts to avoid spam filtering
- ✓ Verify recipient email addresses are typed correctly (comma-separated)
- ✓ Check recipient email filters

### "Configuration Saved But Alerts Not Sending"
- ✓ Make sure "Enable Email Alerts on Critical Errors" is checked
- ✓ Run a test pipeline with an invalid symbol to trigger error
- ✓ Check logs for email sending errors
- ✓ Test configuration again

---

## Multiple Recipients

To send alerts to multiple people:

1. In **Recipient Email(s)** field, enter emails separated by commas:
   ```
   admin@example.com, ops@example.com, devops@example.com
   ```

2. No spaces after commas (optional but recommended)

3. Each recipient gets the same email

---

## FAQ

**Q: Can I use my personal Gmail password?**
A: No, Gmail blocks app login with regular password. Use 16-character app password from Step 2.

**Q: Will sending emails slow down the pipeline?**
A: No, emails are sent asynchronously. Pipeline continues running.

**Q: What if email fails to send?**
A: Error is logged locally. Pipeline continues. You can retry from logs.

**Q: Can I change email settings while pipeline is running?**
A: Yes, settings are saved immediately. Next error will use new settings.

**Q: How often will I get emails?**
A: Only when critical errors occur. Not for every symbol completion.

**Q: Can I send to email distribution lists?**
A: Yes, if your email provider supports it. Treat it like a regular email address.

---

## Example Configurations

### Gmail Setup (Complete Example)
```
SMTP Server:    smtp.gmail.com
SMTP Port:      587
Sender Email:   myemail@gmail.com
Sender Password: abcd efgh ijkl mnop  (16-char app password)
Recipients:     admin@company.com
```

### Outlook Setup (Complete Example)
```
SMTP Server:    smtp.office365.com
SMTP Port:      587
Sender Email:   myname@outlook.com
Sender Password: MyOutlookPassword123
Recipients:     admin@company.com, ops@company.com
```

### Company Email Setup (Complete Example)
```
SMTP Server:    mail.company.com
SMTP Port:      587
Sender Email:   jdoe@company.com
Sender Password: MyCompanyPassword123
Recipients:     alerts@company.com
```

---

## Settings Persistence

Email configuration is automatically saved when you click "💾 Save Settings".

Configuration is stored at: `~/.pipeline_dashboard_config.json`

---

## Disabling Email Alerts

To disable email alerts:
1. Uncheck "Enable Email Alerts on Critical Errors"
2. Click "💾 Save Settings"
3. No emails will be sent until re-enabled

---

## Support

If you continue experiencing issues:

1. Check dashboard logs for error messages
2. Verify SMTP credentials with provider
3. Test using another email client first
4. Consult your email provider's documentation

---

**Last Updated:** November 28, 2025

