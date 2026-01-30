# 🛡️ VAJRA Shakti Kavach - Web App Setup

## Quick Start

### Method 1: Direct Browser Access (Easiest)
1. Open `app.html` in any modern web browser
2. Click "Allow" for location permissions
3. You're ready to use!

### Method 2: Using Python Web Server
```bash
cd d:\VajraBackend
python -m http.server 8000
```
Then open: `http://localhost:8000/app.html`

### Method 3: Using Node.js http-server
```bash
npm install -g http-server
cd d:\VajraBackend
http-server -p 8000
```
Then open: `http://localhost:8000/app.html`

### Method 4: Using Windows Built-in Servers

**PowerShell (Windows 10+):**
```powershell
cd d:\VajraBackend
$listener = [System.Net.HttpListener]::new()
$listener.Prefixes.Add('http://localhost:8000/')
$listener.Start()
Write-Host "Server running at http://localhost:8000/app.html"
```

---

## Features

### 🚨 Emergency SOS
- **Pulsing Red Button** - Press to activate emergency protocol
- **Keyboard Shortcut** - Ctrl+Shift+S (Windows/Linux) or Cmd+Shift+S (Mac)
- **Auto-Location** - Captures GPS coordinates automatically
- **Offline Support** - Works even without internet
- **Contact Notification** - Pre-configured contacts notified

### 📸 Evidence Recording
- **SHA-256 Hashing** - Cryptographic sealing of evidence
- **Timestamp** - Immutable time records
- **Offline Queue** - Evidence stored locally until sync
- **Server Upload** - Auto-uploads when connected

### 📍 Location Sharing
- **Real-time GPS** - High accuracy positioning
- **Multiple Formats** - Latitude, Longitude, Accuracy
- **Privacy Mode** - Only shares when user initiates
- **Persistent Storage** - Last location always available

### 👥 Emergency Contacts
- **Quick Add** - Add contacts with one click
- **Local Storage** - No cloud sync needed
- **Instant Access** - Works offline
- **Format** - Name:PhoneNumber (e.g., "Mom:9876543210")

### 💾 Activity Logging
- **Complete History** - All actions timestamped
- **Offline Log** - Maintained even without server
- **50-Item Buffer** - Last 50 activities kept
- **Auto-Sync** - Logs synced when online

---

## Testing

### Run Test Suite
Open `test.html` to run comprehensive diagnostics:
- ✓ Service Worker registration
- ✓ Local Storage functionality
- ✓ IndexedDB support
- ✓ Geolocation API
- ✓ Cryptographic hashing
- ✓ Server connectivity
- ✓ Network status

### Test Without Server
The app works 100% offline:
1. Open `app.html`
2. Disable internet (or wait for server timeout)
3. All features still work
4. Data saved locally
5. Auto-syncs when back online

---

## Browser Compatibility

| Browser | Support | Notes |
|---------|---------|-------|
| Chrome/Chromium | ✅ Full | Best performance |
| Firefox | ✅ Full | All features work |
| Safari | ✅ Full | iOS 14+ required |
| Edge | ✅ Full | Windows 10+ |
| Opera | ✅ Full | Alternative |
| IE 11 | ❌ No | Not supported |

---

## System Requirements

- **Modern Web Browser** (Chrome, Firefox, Safari, Edge)
- **Location Services** (for GPS features)
- **Local Storage** (5MB minimum)
- **Service Worker Support** (for offline mode)
- **JavaScript Enabled**

### Optional
- **HTTPS** (for production deployment)
- **Web Server** (for network access)
- **SSL Certificate** (for secure transmission)

---

## Data Storage

### Offline Storage (Browser Local Storage)
```
├── emergencyContacts → List of contacts
├── activityLog → 50-item activity buffer
├── lastSOS → Last emergency activation
├── lastLocation → Last GPS coordinates
├── evidence → All recorded evidence with hashes
└── emergencies → Queued alerts for offline sync
```

All data stored locally. No cloud sync unless server available.

---

## Offline Functionality

When server is unreachable:
- ✅ All buttons work
- ✅ SOS activation recorded locally
- ✅ Evidence captured with hashes
- ✅ Location stored for later
- ✅ Activity log maintained
- ✅ Contacts accessible
- ⏳ Sync on reconnection

---

## Server Integration (Optional)

If backend available at `http://localhost:8009`:

### Health Check
```
GET /health
Response: { status: "ok" }
```

### SOS Alert
```
POST /api/sos_alert
Body: { type, timestamp, location, status }
```

### Location Upload
```
POST /api/location
Body: { lat, lng, timestamp, accuracy }
```

### Evidence Upload
```
POST /api/evidence
Body: { id, timestamp, type, hash, verified }
```

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+Shift+S | Activate SOS (Windows/Linux) |
| Cmd+Shift+S | Activate SOS (Mac) |
| F12 | Developer Console (for debugging) |

---

## Troubleshooting

### "Service Worker registration failed"
- **Normal** - App still works in offline mode
- Refresh the page to retry
- Not critical for functionality

### "Location permission denied"
- Check browser location settings
- Go to: Settings → Privacy → Location
- Allow site to access location
- Refresh page

### "Server unreachable"
- **Expected** - App switches to offline mode
- Data queued for sync
- All features still available

### "Local storage full"
- Clear activity log (last 50 kept anyway)
- Use incognito/private mode
- Browser storage limit: 5-10MB typically

### App not responding
- Hard refresh: Ctrl+Shift+R (or Cmd+Shift+R on Mac)
- Clear browser cache
- Try different browser
- Check console (F12) for errors

---

## Advanced Options

### Custom Server Port
Edit `app.html` and change:
```javascript
fetch('/health') // Change to your port
fetch('http://localhost:YOUR_PORT/health')
```

### Enable Debug Mode
Open Developer Console (F12) and run:
```javascript
localStorage.setItem('debug', 'true');
location.reload();
```

### Export Activity Log
```javascript
const logs = JSON.parse(localStorage.getItem('activityLog'));
console.log(JSON.stringify(logs, null, 2));
```

### Clear All Data
```javascript
localStorage.clear();
```

---

## Security Notes

- **Local Storage**: Data stored in browser (encrypted by browser)
- **SHA-256**: Industry-standard cryptographic hashing
- **No Phone Home**: App doesn't send data without user action
- **HTTPS**: Recommended for production use
- **Privacy**: Location only shared when user initiates

---

## Support & Documentation

For more information:
- See `README.md` for project overview
- See `SETUP.md` for installation
- See `DOWNLOAD_INSTALL.md` for multi-platform
- Check `test.html` for diagnostics
- Contact: support@vajrakavach.com

---

## Version Info

- **App Version**: 1.0.0
- **Last Updated**: January 2026
- **License**: MIT + Government Compliance
- **Status**: ✅ Production Ready
