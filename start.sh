#!/bin/bash
# Quick Start Script for VAJRA Shakti Kavach

echo "🛡️  VAJRA Shakti Kavach - Quick Start"
echo "======================================"
echo ""

# Check if running on Windows
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    echo "🪟 Windows detected"
    echo ""
    echo "Option 1: Direct Browser (Easiest)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "1. Navigate to: d:\VajraBackend"
    echo "2. Double-click: app.html"
    echo "3. Allow location permissions when prompted"
    echo ""
    
    echo "Option 2: Python Web Server"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "1. Open PowerShell in d:\VajraBackend"
    echo "2. Run: python -m http.server 8000"
    echo "3. Open: http://localhost:8000/app.html"
    echo ""
    
    echo "Option 3: This Script"
    echo "━━━━━━━━━━━━━━━━━"
    
    cd "$(dirname "$0")" || exit
    
    # Check if Python is available
    if command -v python &> /dev/null; then
        echo "✓ Python found - Starting server on port 8000..."
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "Server running at: http://localhost:8000"
        echo "App URL: http://localhost:8000/app.html"
        echo "Test URL: http://localhost:8000/test.html"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        python -m http.server 8000
    elif command -v py &> /dev/null; then
        echo "✓ Python launcher found - Starting server on port 8000..."
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "Server running at: http://localhost:8000"
        echo "App URL: http://localhost:8000/app.html"
        echo "Test URL: http://localhost:8000/test.html"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        py -m http.server 8000
    else
        echo "✗ Python not found. Please use Option 1 or 2"
        exit 1
    fi
else
    echo "🐧 Linux/macOS detected"
    echo ""
    echo "Starting Python HTTP server..."
    cd "$(dirname "$0")" || exit
    
    if command -v python3 &> /dev/null; then
        python3 -m http.server 8000
    elif command -v python &> /dev/null; then
        python -m http.server 8000
    else
        echo "✗ Python not found. Install Python 3 and try again."
        exit 1
    fi
fi
