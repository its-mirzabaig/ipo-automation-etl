import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import CONFIG
from logger import logger

def generate_html(matches):
    mode = CONFIG["ENRICHMENT_MODE"]
    
    html = f"""
    <html>
    <body style="font-family: 'Segoe UI', sans-serif; color: #333; max-width: 600px;">
        <h2 style="color: #004d40;">🚀 High-Value IPO Alert</h2>
        <p>Found <b>{len(matches)}</b> companies > <b>${CONFIG['THRESHOLD']:,.0f}</b>.</p>
        <hr style="border: 0; border-top: 1px solid #eee;">
    """

    for m in matches:
        html += f"""
        <div style="margin-bottom: 25px; padding: 15px; border: 1px solid #e0e0e0; border-radius: 8px;">
            <h3 style="margin-top: 0; color: #00695c;">{m['symbol']} - {m['name']}</h3>
            <p><strong>💰 Value:</strong> ${m['value']:,.0f} | <strong>📅 Date:</strong> {m['date']}</p>
        """

        if mode == "AI_FULL":
            website = m.get('website', 'Not Found')
            html += f"""
            <div style="background: #f1f8e9; padding: 10px; border-left: 4px solid #33691e; margin-bottom: 10px;">
                <p style="margin:0; font-style: italic;">"{m.get('ai_summary')}"</p>
                <p style="margin:5px 0 0; font-weight: bold; color: #33691e;">Sentiment: {m.get('sentiment')}</p>
            </div>
            """
            
            if website.startswith("http"):
                html += f"""<a href="{website}" style="background: #00695c; color: white; padding: 8px 15px; text-decoration: none; border-radius: 5px; font-size: 13px;">🌐 Visit Official Website</a>"""
            else:
                html += "<p style='font-size:12px; color:#666;'>Official website not found.</p>"

        # Links Section
        if mode in ["WEB_ONLY", "AI_FULL"]:
            html += """<div style="margin-top: 15px; border-top: 1px dashed #ccc; padding-top: 10px;">
                       <b style="font-size: 12px; color: #555;">🔎 Sources:</b><ul style="padding-left: 20px; margin: 5px 0;">"""
            
            seen_urls = set()
            count = 0
            for res in m.get('search_results', []):
                if res['url'] not in seen_urls and count < 4:
                    html += f"""<li style="font-size: 12px;"><a href="{res['url']}" style="color: #0277bd;">{res['title']}</a></li>"""
                    seen_urls.add(res['url'])
                    count += 1
            html += "</ul></div>"

        html += "</div>"

    html += "</body></html>"
    return html

def send_email(matches):
    if not matches:
        logger.info("📭 No matches to email.")
        return
        
    if not CONFIG["RECEIVER_EMAILS"]:
        logger.warning("⚠️ No receiver emails configured.")
        return

    logger.info(f"📧 Sending email to {len(CONFIG['RECEIVER_EMAILS'])} recipients...")
    msg = MIMEMultipart("alternative")
    msg['Subject'] = f"🚀 IPO Alert: {len(matches)} Listings"
    msg['From'] = CONFIG["SMTP_EMAIL"]
    msg['To'] = ", ".join(CONFIG["RECEIVER_EMAILS"])

    html_body = generate_html(matches)
    msg.attach(MIMEText(html_body, 'html'))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(CONFIG["SMTP_EMAIL"], CONFIG["SMTP_PASS"])
            server.send_message(msg)
        logger.info("✅ Email successfully dispatched.")
    except Exception as e:
        logger.error(f"❌ SMTP Error: {e}")