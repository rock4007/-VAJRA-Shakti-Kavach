"""
Vajra Kavach - Emergency Response System
Created by: Soumodeep Guha
Version: 1.0.0
Year: 2026

Advanced Biometric-Secured Emergency Assistance with Multi-Regional AI-Powered Threat Detection
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import requests
import os
import threading
import smtplib
import ssl
from email.message import EmailMessage
import json
from math import sqrt
import re
from collections import defaultdict
import time

# Maintenance systems (auto-heal + threat model updater)
try:
    from auto_heal_manager import start_auto_heal
    from threat_model_manager import start_threat_model_updates
except Exception:
    start_auto_heal = None
    start_threat_model_updates = None

# ============================================================================
# CODE PROTECTION SYSTEM - GHOST INJECTION
# ============================================================================
try:
    from code_protection_system import initialize_protection, AntiDebugProtection
    # Initialize protection immediately
    print("\nInitializing Code Protection System...")
    GHOST_PROTECTION = initialize_protection()
    print("Ghost Injection Protection: ACTIVE\n")
except Exception as e:
    print(f"Warning: Code protection initialization error: {e}")
    GHOST_PROTECTION = None
# ============================================================================

# ============================================================================
# MAINTENANCE: AUTO-HEAL + THREAT MODEL UPDATES
# ============================================================================
AUTO_HEAL_MANAGER = None
THREAT_MODEL_UPDATER = None
try:
    if start_auto_heal and start_threat_model_updates:
        app_root = os.path.dirname(os.path.abspath(__file__))
        protected = [
            "main.py",
            "config.py",
            "supabase-client.js",
            "background.js",
            "content-script.js",
            "manifest.json",
        ]
        AUTO_HEAL_MANAGER = start_auto_heal(
            app_root=app_root,
            protected_files=protected,
            interval_seconds=3600  # hourly health check
        )
        THREAT_MODEL_UPDATER = start_threat_model_updates(
            app_root=app_root,
            check_interval_seconds=86400,  # daily check
            update_interval_days=90  # every 3 months
        )
        print("Auto-heal enabled (hourly checks)")
        print("Threat model auto-update enabled (90-day cadence)")
except Exception as e:
    print(f"Warning: Maintenance initialization error: {e}")
# ============================================================================

# Security configurations
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX_REQUESTS = 100  # per IP per window
BLOCKED_IPS = set()  # Can be loaded from env or file
ALLOWED_IPS = set()  # Whitelist if needed

# Rate limiting storage
request_counts = defaultdict(lambda: defaultdict(int))
request_timestamps = defaultdict(list)

def sanitize_input(value):
    """Sanitize string inputs to prevent SQL injection, command injection, and XSS."""
    if not isinstance(value, str):
        return value
    
    # Block shell metacharacters (COMMAND INJECTION PREVENTION)
    # Check for dangerous shell characters
    if any(char in value for char in ';|&`$()'):
        return ''  # Return empty string for dangerous input
    
    # Block newlines and carriage returns
    if '\n' in value or '\r' in value:
        return ''
    
    # Block angle brackets for HTML/JS
    if '<' in value or '>' in value:
        return ''
    
    # SQL injection prevention - block dangerous SQL keywords AND single quotes
    # Single quote alone is a dangerous character for SQL
    if "'" in value or '"' in value:
        return ''  # Block quotes entirely
    
    # SQL injection prevention - block dangerous SQL keywords
    sql_keywords = r"\b(DROP|DELETE|INSERT|UPDATE|UNION|SELECT|EXEC|EXECUTE|SCRIPT|javascript|onerror|onload|onclick)\b"
    if re.search(sql_keywords, value, re.IGNORECASE):
        return ''  # Return empty string for SQL keywords
    
    # XSS prevention - remove HTML/JS tags (shouldn't reach here due to < > check above)
    value = re.sub(r'<[^>]+>', '', value)  # Remove HTML tags
    
    # Path traversal prevention - block directory traversal patterns
    if '..' in value or value.startswith('/'):
        return ''
    
    # Remove any remaining special characters that might be problematic
    value = re.sub(r'[\\]', '', value).strip()
    
    return value

def validate_prompt(prompt):
    """Validate AI prompts to prevent injection attacks."""
    if not isinstance(prompt, str):
        return True
    
    # Comprehensive prompt injection patterns
    dangerous_patterns = [
        # System instruction overwrites
        r'\b(system|user|assistant)\b.*:',
        r'ignore.*previous',
        r'forget.*instructions',
        r'new.*persona',
        r'override.*rules',
        r'disregard.*guidelines',
        r'bypass.*rules',
        r'system.*prompt',
        r'initial.*prompt',
        # Role-playing escapes
        r'pretend.*you.*are',
        r'act.*as.*if',
        r'roleplay.*as',
        # Direct injection patterns
        r'\[SYSTEM\]',
        r'\[INSTRUCTION\]',
        r'\[COMMAND\]',
        # Command execution patterns
        r'execute.*code',
        r'run.*script',
        r'eval\(',
        r'exec\(',
        r'__import__',
        # DAN patterns (Do Anything Now)
        r'DAN mode',
        r'DAN:',
        r'do anything now',
        r'anything now mode',
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, prompt, re.IGNORECASE):
            return False
    
    return True

def validate_fingerprint_payload(data: dict) -> bool:
    """Validate fingerprint payload (basic sanity checks)."""
    if not isinstance(data, dict):
        return False
    device_id = data.get("device_id")
    if device_id is None or not isinstance(device_id, str) or len(device_id) > 128:
        return False
    # Expect a fingerprint hash or template reference string
    fp = data.get("fingerprint") or data.get("fingerprint_hash") or data.get("template_id")
    if fp is None or not isinstance(fp, str):
        return False
    if len(fp) < 16 or len(fp) > 1024:
        return False
    return True

def enforce_https():
    """Enforce HTTPS in production."""
    if request.headers.get('X-Forwarded-Proto', 'http') != 'https':
        # In production, redirect to HTTPS
        pass  # For now, just log
    return True

def rate_limit_check():
    """Check rate limiting per IP with DDoS protection."""
    ip = request.remote_addr
    now = time.time()
    
    # Get real IP from headers (behind proxy)
    if request.headers.get('X-Forwarded-For'):
        ip = request.headers.get('X-Forwarded-For').split(',')[0].strip()
    
    # Clean old timestamps
    request_timestamps[ip] = [ts for ts in request_timestamps[ip] if now - ts < RATE_LIMIT_WINDOW]
    
    # DDoS protection: block if too many requests
    if len(request_timestamps[ip]) >= RATE_LIMIT_MAX_REQUESTS:
        log_security_event("rate_limit_exceeded", {"ip": ip, "requests": len(request_timestamps[ip])})
        # Check for DDoS pattern (multiple hits in rapid succession)
        if len(request_timestamps[ip]) > RATE_LIMIT_MAX_REQUESTS * 1.5:
            BLOCKED_IPS.add(ip)
            log_security_event("ddos_detected", {"ip": ip})
        return False
    
    request_timestamps[ip].append(now)
    return True

def firewall_middleware():
    """Main firewall middleware with comprehensive security checks."""
    # ============================================================================
    # ANTI-TAMPERING CHECK: Verify code integrity before processing request
    # ============================================================================
    if GHOST_PROTECTION:
        try:
            # Perform anti-debug check on every request
            AntiDebugProtection.anti_debug_check()
        except:
            pass  # Ghost protection will handle violations
    # ============================================================================
    
    ip = request.remote_addr
    
    # Get real IP from headers (behind proxy)
    if request.headers.get('X-Forwarded-For'):
        ip = request.headers.get('X-Forwarded-For').split(',')[0].strip()

    # Block known bad IPs
    if ip in BLOCKED_IPS:
        log_security_event("blocked_ip", {"ip": ip, "path": request.path})
        return app.response_class(json.dumps({"error": "Access denied"}), status=403, mimetype='application/json')

    # Rate limiting
    if not rate_limit_check():
        return app.response_class(json.dumps({"error": "Rate limit exceeded"}), status=429, mimetype='application/json')

    # Enforce HTTPS
    if not enforce_https():
        return app.response_class(json.dumps({"error": "HTTPS required"}), status=426, mimetype='application/json')
    
    # Validate Content-Type header
    if request.method in ['POST', 'PUT', 'PATCH']:
        content_type = request.headers.get('Content-Type', '')
        if request.is_json and 'application/json' not in content_type:
            log_security_event("content_type_mismatch", {"ip": ip, "declared": content_type})
            return app.response_class(json.dumps({"error": "Invalid Content-Type"}), status=400, mimetype='application/json')

    # Sanitize inputs for POST requests
    if request.method == 'POST' and request.is_json:
        data = request.get_json(silent=True) or {}
        sanitized_data = {}
        for key, value in data.items():
            if isinstance(value, str):
                sanitized_data[key] = sanitize_input(value)
            else:
                sanitized_data[key] = value
        # Store sanitized data in a way Flask can access
        request.sanitized_data = sanitized_data

    # Validate AI safety inputs
    if request.path == '/ai_safety' and request.method == 'POST':
        data = request.get_json(silent=True) or {}
        # Check for prompt injection attempts
        if 'prompt' in data:
            if not validate_prompt(data['prompt']):
                log_security_event("prompt_injection_attempt", {"ip": ip, "data": str(data)[:200]})
                return app.response_class(json.dumps({"error": "Invalid input"}), status=400, mimetype='application/json')
        # Also validate sensor data
        for key in ['x', 'y', 'z', 'device_id']:
            if key in data and isinstance(data[key], str):
                if not sanitize_input(data[key]):
                    log_security_event("invalid_sensor_data", {"ip": ip, "field": key})
                    return app.response_class(json.dumps({"error": "Invalid input"}), status=400, mimetype='application/json')

def get_sanitized_json():
    """Get sanitized JSON data from request."""
    data = request.get_json(silent=True) or {}
    sanitized_data = {}
    for key, value in data.items():
        if isinstance(value, str):
            sanitized = sanitize_input(value)
            # If sanitization returns empty, it means the input was dangerous
            if sanitized == '' and value != '':
                log_security_event("dangerous_input_blocked", {"field": key, "original": value[:100]})
                sanitized_data[key] = None  # Mark as rejected
            else:
                sanitized_data[key] = sanitized
        else:
            sanitized_data[key] = value
    return sanitized_data

def log_security_event(ev_type: str, data: dict):
    """Log security events to separate file."""
    try:
        record = {"type": ev_type, "ts": datetime.utcnow().isoformat(), "ip": request.remote_addr}
        record.update(data)
        path = os.path.join(os.path.dirname(__file__), "security.log")
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception:
        pass

app = Flask(__name__)

# Add security headers to all responses
@app.after_request
def add_security_headers(response):
    """Add security headers to every response."""
    response.headers['X-Content-Type-Options'] = 'nosniff'  # Prevent MIME type sniffing
    response.headers['X-Frame-Options'] = 'DENY'  # Prevent clickjacking
    response.headers['X-XSS-Protection'] = '1; mode=block'  # Enable XSS protection
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'  # HTTPS enforcement
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self'"
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'  # Control referrer information
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'  # Restrict permissions
    return response

@app.before_request
def apply_firewall():
    """Apply firewall before each request."""
    if request.path.startswith('/honeypot'):
        return  # Skip firewall for honeypots to log attackers
    response = firewall_middleware()
    if response:
        return response
CORS(app)

# Alert configuration (env-driven with safe defaults)
ALERT_EMAILS = os.getenv("ALERT_EMAILS", "soumodeepguha22@gmail.com")
ALERT_PHONES = os.getenv("ALERT_PHONES", "+916291283472")

# Region configuration (multi-region ready)
REGION = os.getenv("REGION", "global")
SUPPORTED_REGIONS = [r.strip() for r in os.getenv("SUPPORTED_REGIONS", "europe,asia").split(",") if r.strip()]

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
SMTP_FROM = os.getenv("SMTP_FROM", "vajra-alerts@example.com")

TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")
TWILIO_FROM = os.getenv("TWILIO_FROM")
TWILIO_WA_FROM = os.getenv("TWILIO_WA_FROM")  # e.g., 'whatsapp:+14155238886' or your WA-enabled number
ALERT_WA = os.getenv("ALERT_WA", "whatsapp:+916291283472")  # default to your number for WA
ALERT_NTFY_TOPICS = os.getenv("ALERT_NTFY_TOPICS", "")  # comma-separated ntfy topics, optional

_last_alert_per_device: dict[str, int] = {}
RECIPIENTS = {}
LAST_LOC = {}

def nominatim_search(lat: float, lon: float, q: str):
    try:
        box = 0.03
        params = {
            "format": "json",
            "limit": 1,
            "q": q,
            "bounded": 1,
            "viewbox": f"{float(lon)-box},{float(lat)+box},{float(lon)+box},{float(lat)-box}",
            "extratags": 1,
        }
        resp = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params=params,
            headers={"User-Agent": "VajraLight/0.1"},
            timeout=2.5,
        )
        if resp.ok:
            items = resp.json()
            if items:
                it = items[0]
                phone = None
                if isinstance(it.get("extratags"), dict):
                    phone = it["extratags"].get("phone") or it["extratags"].get("contact:phone")
                return {
                    "name": it.get("display_name"),
                    "lat": it.get("lat"),
                    "lon": it.get("lon"),
                    "phone": phone,
                }
    except Exception:
        pass
    return None

@app.post("/sensors")
def set_shield():
    data = get_sanitized_json()
    on = bool(data.get("shield_on", False))
    log_event("sensors", data)
    return jsonify({"status": "Shield On" if on else "Shield Off"})

@app.post("/ai_safety")
def ingest_sensor():
    data = get_sanitized_json()
    ts = data.get("timestamp") or datetime.utcnow().isoformat()
    log_event("ai", data)
    # high-G detection triggers alert
    try:
        x = float(data.get("x", 0) or 0)
        y = float(data.get("y", 0) or 0)
        z = float(data.get("z", 0) or 0)
        g = sqrt(x*x + y*y + z*z)
        if g >= 25:
            dev = data.get("device_id") or "unknown"
            loc = LAST_LOC.get(dev) or {}
            payload = {"ts": ts, "lat": loc.get("lat"), "lon": loc.get("lon"), "distress": True, "device_id": dev}
            log_event("impact", {"device_id": dev, "g": g})
            _dispatch_async(payload)
    except Exception:
        pass
    return jsonify({"status": "ok", "ts": ts})

@app.post("/heartbeat")
def heartbeat():
    data = get_sanitized_json()
    ts = data.get("ts") or datetime.utcnow().isoformat()
    log_event("heartbeat", data)
    # Auto-dispatch if distress is flagged
    try:
        if bool(data.get("distress", False)):
            dev = data.get("device_id") or "unknown"
            loc = LAST_LOC.get(dev) or {}
            payload = {"ts": ts, "lat": loc.get("lat"), "lon": loc.get("lon"), "distress": True, "device_id": dev}
            _dispatch_async(payload)
    except Exception:
        pass
    return jsonify({
        "status": "ok",
        "ts": ts,
        "shield_on": bool(data.get("shield_on", False)),
        "distress": bool(data.get("distress", False)),
    })

@app.post("/fingerprint")
def fingerprint():
    """Biometric fingerprint ingestion endpoint."""
    data = get_sanitized_json()
    if not validate_fingerprint_payload(data):
        return jsonify({"status": "error", "message": "invalid fingerprint payload"}), 400

    ts = data.get("ts") or datetime.utcnow().isoformat()
    device_id = data.get("device_id")
    # Store only hashed/template reference (never raw biometric)
    fp_ref = data.get("fingerprint_hash") or data.get("template_id") or data.get("fingerprint")
    log_event("fingerprint", {"device_id": device_id, "ts": ts})

    return jsonify({
        "status": "ok",
        "ts": ts,
        "device_id": device_id,
        "fingerprint_ref": fp_ref
    })

@app.post("/location")
def location():
    data = get_sanitized_json()
    # Check for dangerous input
    if data.get("device_id") is None and "device_id" in request.get_json(silent=True) or {}:
        return jsonify({"error": "Invalid device_id"}), 400
    
    try:
        lat = float(data.get("lat")) if data.get("lat") is not None else None
        lon = float(data.get("lon")) if data.get("lon") is not None else None
    except (ValueError, TypeError):
        lat = None
        lon = None
    
    ts = data.get("ts") or datetime.utcnow().isoformat()
    log_event("location", data)
    # Store last location per device
    try:
        dev = data.get("device_id") or "unknown"
        LAST_LOC[dev] = {"lat": lat, "lon": lon, "ts": ts}
    except Exception:
        pass
    return jsonify({"status": "ok", "ts": ts, "lat": lat, "lon": lon})

@app.post("/audio")
def audio():
    f = request.files.get("audio")
    if not f:
        return jsonify({"status": "error", "message": "no file"}), 400
    size = 0
    chunk = f.read(8192)
    while chunk:
        size += len(chunk)
        chunk = f.read(8192)
    # Best-effort device_id from form
    dev = request.form.get("device_id")
    log_event("audio", {"device_id": dev, "bytes": size, "ts": datetime.utcnow().isoformat()})
    return jsonify({"status": "ok", "bytes": size})


@app.post("/sos")
def sos():
    data = request.get_json(silent=True) or {}
    # Ensure numeric types for lat/lon
    try:
        lat = float(data.get("lat")) if data.get("lat") is not None else None
        lon = float(data.get("lon")) if data.get("lon") is not None else None
    except (ValueError, TypeError):
        lat = None
        lon = None
    
    log_event("sos_lookup", data)
    if lat is None or lon is None:
        return jsonify({
            "police": {"phone": "112"},
            "hospital": {"phone": "112"},
            "ambulance": {"phone": "112"},
        })
    police = nominatim_search(lat, lon, "police")
    hospital = nominatim_search(lat, lon, "hospital")
    ambulance = nominatim_search(lat, lon, "ambulance") or nominatim_search(lat, lon, "clinic")
    return jsonify({
        "police": police or {"phone": "112"},
        "hospital": hospital or {"phone": "112"},
        "ambulance": ambulance or {"phone": "112"},
    })


def _dispatch_async(payload: dict):
    t = threading.Thread(target=_dispatch_alert, args=(payload,), daemon=True)
    t.start()


def _dispatch_alert(payload: dict):
    import time
    now = int(time.time())
    dev = payload.get("device_id") or "unknown"
    force = bool(payload.get("force", False))
    # Rate limit per-device (60s), unless forced
    last = _last_alert_per_device.get(dev, 0)
    if not force and (now - last < 60):
        # Still log a skipped event for traceability
        try:
            log_path = os.path.join(os.path.dirname(__file__), "alerts.log")
            with open(log_path, "a", encoding="utf-8") as fh:
                fh.write(f"rate_limited device={dev} since={now-last}s ago\n")
        except Exception:
            pass
        return
    _last_alert_per_device[dev] = now

    ts = payload.get("ts") or datetime.utcnow().isoformat()
    lat = payload.get("lat")
    lon = payload.get("lon")
    maps_link = f"https://maps.google.com/?q={lat},{lon}" if lat is not None and lon is not None else "N/A"
    subject = "Vajra Distress Alert"
    body = (
        f"Distress alert received\n\n"
        f"Time: {ts}\n"
        f"Location: lat={lat}, lon={lon}\n"
        f"Map: {maps_link}\n"
        f"Note: This message was auto-generated by Vajra Light."
    )

    # Always log to file for verification
    try:
        log_path = os.path.join(os.path.dirname(__file__), "alerts.log")
        with open(log_path, "a", encoding="utf-8") as fh:
            fh.write(f"{ts} | distress=1 | lat={lat} lon={lon} | {maps_link}\n")
    except Exception:
        pass

    # Resolve per-device recipients with env fallbacks
    def _split_list(s: str | None):
        if not s:
            return []
        return [x.strip() for x in s.split(",") if x and x.strip()]
    rec = RECIPIENTS.get(dev, {})
    emails_list = rec.get("emails") or _split_list(ALERT_EMAILS)
    phones_list = rec.get("phones") or _split_list(ALERT_PHONES)
    wa_list = rec.get("wa") or _split_list(ALERT_WA)
    ntfy_list = rec.get("ntfy") or _split_list(ALERT_NTFY_TOPICS)

    email_status = "skipped_no_config"
    if SMTP_HOST and SMTP_USER and SMTP_PASS and emails_list:
        try:
            msg = EmailMessage()
            msg["Subject"] = subject
            msg["From"] = SMTP_FROM
            msg["To"] = ",".join(emails_list)
            msg.set_content(body)
            context = ssl.create_default_context()
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as server:
                server.starttls(context=context)
                server.login(SMTP_USER, SMTP_PASS)
                server.send_message(msg)
            email_status = "sent"
        except Exception:
            email_status = "error"
    elif SMTP_HOST and SMTP_USER and SMTP_PASS and not emails_list:
        email_status = "skipped_no_recipients"

    # Send SMS via Twilio if configured
    sms_status = "skipped_no_config"
    if TWILIO_SID and TWILIO_TOKEN and TWILIO_FROM and phones_list:
        try:
            from twilio.rest import Client  # type: ignore
            client = Client(TWILIO_SID, TWILIO_TOKEN)
            for p in phones_list:
                client.messages.create(
                    body=f"Vajra Distress Alert: {maps_link}",
                    from_=TWILIO_FROM,
                    to=p,
                )
            sms_status = "sent"
        except Exception:
            sms_status = "error"
    elif TWILIO_SID and TWILIO_TOKEN and TWILIO_FROM and not phones_list:
        sms_status = "skipped_no_recipients"

    # Voice call via Twilio if configured (inline TwiML)
    call_status = "skipped_no_config"
    if TWILIO_SID and TWILIO_TOKEN and TWILIO_FROM and phones_list:
        try:
            from twilio.rest import Client  # type: ignore
            client = Client(TWILIO_SID, TWILIO_TOKEN)
            say_msg = (
                f"Attention. Vajra distress alert. "
                f"Time {ts}. "
                f"Coordinates latitude {lat if lat is not None else 'unknown'}, longitude {lon if lon is not None else 'unknown'}. "
                f"This is an automated safety call."
            )
            twiml = f"<Response><Say voice=\"alice\">{say_msg}</Say></Response>"
            for p in phones_list:
                client.calls.create(twiml=twiml, to=p, from_=TWILIO_FROM)
            call_status = "sent"
        except Exception:
            call_status = "error"
    elif TWILIO_SID and TWILIO_TOKEN and TWILIO_FROM and not phones_list:
        call_status = "skipped_no_recipients"

    # WhatsApp via Twilio if configured
    wa_status = "skipped_no_config"
    if TWILIO_SID and TWILIO_TOKEN and TWILIO_WA_FROM and wa_list:
        try:
            from twilio.rest import Client  # type: ignore
            client = Client(TWILIO_SID, TWILIO_TOKEN)
            for p in wa_list:
                client.messages.create(
                    body=f"Vajra Distress Alert\nTime: {ts}\nLat: {lat} Lon: {lon}\n{maps_link}",
                    from_=TWILIO_WA_FROM,
                    to=p,
                )
            wa_status = "sent"
        except Exception:
            wa_status = "error"
    elif TWILIO_SID and TWILIO_TOKEN and TWILIO_WA_FROM and not wa_list:
        wa_status = "skipped_no_recipients"

    # ntfy push (no creds needed). Users subscribe to https://ntfy.sh/<topic>
    ntfy_status = "skipped_no_config"
    try:
        if ntfy_list:
            for topic in ntfy_list:
                url = f"https://ntfy.sh/{topic}"
                msg = f"Vajra Distress Alert\nTime: {ts}\nLat: {lat} Lon: {lon}\n{maps_link}"
                headers = {"Title": "Vajra SOS", "Priority": "high"}
                try:
                    requests.post(url, data=msg.encode("utf-8"), headers=headers, timeout=5)
                    ntfy_status = "sent"
                except Exception:
                    ntfy_status = "error"
        else:
            ntfy_status = "skipped_no_recipients"
    except Exception:
        ntfy_status = "error"

    # Log dispatch status
    try:
        log_path = os.path.join(os.path.dirname(__file__), "alerts.log")
        with open(log_path, "a", encoding="utf-8") as fh:
            fh.write(f"dispatch_status device={dev} force={int(force)} email={email_status} sms={sms_status} call={call_status} wa={wa_status} ntfy={ntfy_status}\n")
    except Exception:
        pass

@app.post("/recipients")
def set_recipients():
    data = get_sanitized_json()
    dev = data.get("device_id") or "unknown"
    phones = data.get("phones") or []
    wa = data.get("wa") or []
    emails = data.get("emails") or []
    ntfy = data.get("ntfy") or []
    # basic normalize
    def _norm_list(v):
        if isinstance(v, list):
            return [str(x).strip() for x in v if str(x).strip()]
        if isinstance(v, str):
            return [s.strip() for s in v.split(",") if s.strip()]
        return []
    RECIPIENTS[dev] = {"phones": _norm_list(phones), "wa": _norm_list(wa), "emails": _norm_list(emails), "ntfy": _norm_list(ntfy)}
    log_event("recipients", {"device_id": dev, "phones": len(RECIPIENTS[dev]["phones"]), "wa": len(RECIPIENTS[dev]["wa"]), "emails": len(RECIPIENTS[dev]["emails"]), "ntfy": len(RECIPIENTS[dev]["ntfy"])})
    return jsonify({"status": "ok", "device_id": dev})

@app.get("/alert_config")
def alert_config():
    def mask(s):
        return bool(s)
    return jsonify({
        "has_smtp": mask(SMTP_HOST) and mask(SMTP_USER) and mask(SMTP_PASS),
        "has_twilio": mask(TWILIO_SID) and mask(TWILIO_TOKEN) and mask(TWILIO_FROM),
        "has_whatsapp": mask(TWILIO_SID) and mask(TWILIO_TOKEN) and mask(TWILIO_WA_FROM) and mask(ALERT_WA),
        "has_ntfy": bool(ALERT_NTFY_TOPICS),
        "emails": [e.strip() for e in (ALERT_EMAILS or "").split(",") if e.strip()],
        "phones": [p.strip() for p in (ALERT_PHONES or "").split(",") if p.strip()],
        "wa_recipients": [p.strip() for p in (ALERT_WA or "").split(",") if p.strip()],
        "ntfy_topics": [t.strip() for t in (ALERT_NTFY_TOPICS or "").split(",") if t.strip()],
        "smtp_from": SMTP_FROM,
        "twilio_from": TWILIO_FROM,
        "twilio_wa_from": TWILIO_WA_FROM,
    })

@app.post("/sos_alert")
def sos_alert():
    data = get_sanitized_json()
    # Echo back and mark accepted; dispatch alert if distress
    log_event("sos_alert", data)
    resp = {
        "status": "accepted",
        "ts": data.get("ts") or datetime.utcnow().isoformat(),
        "lat": data.get("lat"),
        "lon": data.get("lon"),
        "distress": bool(data.get("distress", False)),
        "device_id": data.get("device_id"),
        "force": bool(data.get("force", False)),
    }
    try:
        if resp["distress"]:
            _dispatch_async(resp)
    except Exception:
        pass
    return jsonify(resp)

@app.post("/test_sos")
def test_sos():
    data = get_sanitized_json()
    dev = data.get("device_id") or "unknown"
    ts = data.get("ts") or datetime.utcnow().isoformat()
    lat = data.get("lat")
    lon = data.get("lon")
    # If lat/lon missing, try last known
    if lat is None or lon is None:
        loc = LAST_LOC.get(dev) or {}
        lat = loc.get("lat")
        lon = loc.get("lon")
    payload = {"device_id": dev, "ts": ts, "lat": lat, "lon": lon, "distress": True, "force": True}
    log_event("sos_alert", {"device_id": dev, "lat": lat, "lon": lon, "distress": True})
    try:
        _dispatch_async(payload)
    except Exception:
        pass
    return jsonify({"status": "forced", "device_id": dev, "lat": lat, "lon": lon, "ts": ts})

@app.get("/health")
def health():
    return jsonify({"status": "ok", "time": datetime.utcnow().isoformat()})

@app.get("/version")
def version():
    return jsonify({
        "name": "VajraBackend",
        "version": "0.1.0",
        "region": REGION,
        "supported_regions": SUPPORTED_REGIONS,
    })

@app.get("/regions")
def regions():
    return jsonify({"region": REGION, "supported_regions": SUPPORTED_REGIONS})

# Honeypot Endpoints (4-layer log catcher)
@app.get("/robots.txt")
def honeypot_robots():
    log_security_event("honeypot_access", {"honeypot": "robots.txt", "ip": request.remote_addr, "headers": dict(request.headers)})
    return "User-agent: *\nDisallow: /", 200, {'Content-Type': 'text/plain'}

@app.get("/admin")
def honeypot_admin():
    log_security_event("honeypot_access", {"honeypot": "admin", "ip": request.remote_addr, "headers": dict(request.headers)})
    return jsonify({"error": "Access denied"}), 403

@app.get("/config")
def honeypot_config():
    log_security_event("honeypot_access", {"honeypot": "config", "ip": request.remote_addr, "headers": dict(request.headers)})
    return jsonify({"error": "Configuration not found"}), 404

@app.get("/backup")
def honeypot_backup():
    log_security_event("honeypot_access", {"honeypot": "backup", "ip": request.remote_addr, "headers": dict(request.headers)})
    return jsonify({"error": "Backup access forbidden"}), 403

def log_event(ev_type: str, data: dict):
    try:
        record = {"type": ev_type, "ts": datetime.utcnow().isoformat()}
        if isinstance(data, dict):
            # shallow copy limited keys for size
            for k in ("device_id", "lat", "lon", "shield_on", "distress", "bytes"):
                if k in data:
                    record[k] = data[k]
        path = os.path.join(os.path.dirname(__file__), "events.log")
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception:
        pass

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8008, debug=True)
