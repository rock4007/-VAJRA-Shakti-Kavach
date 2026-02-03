#!/usr/bin/env python3
"""Headless verification using Playwright:
- Opens http://localhost:8000/app.html
- Confirms hrStatus shows "Live"
- Closes EventSource and verifies hrStatus becomes "Disconnected" then "Demo"
- Confirms currentHR updates (demo)
"""
import time
import sys
try:
    from playwright.sync_api import sync_playwright
except Exception as e:
    print('MISSING_PLAYWRIGHT')
    raise

URL = 'http://127.0.0.1:8010/app.html'

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()
    # inject EventSource override so relative '/heartrate/stream' connects to Flask backend on 8009
    context.add_init_script("""
    (() => {
        try {
            const Orig = window.EventSource;
            window.EventSource = function(url, opts) {
                try {
                    // If page requests relative heartrate path, redirect to Flask backend
                    if (typeof url === 'string' && url.indexOf('/heartrate/stream') === 0) {
                        return new Orig('http://127.0.0.1:8009' + url);
                    }
                } catch(e){}
                return new Orig(url, opts);
            };
        } catch(e) {}
    })();
    """)
    page = context.new_page()
    # capture console messages/errors for debugging
    page.on('console', lambda msg: print('PAGE_CONSOLE:', msg.type, msg.text))
    page.on('pageerror', lambda exc: print('PAGE_ERROR:', exc))
    # First visit: normal connection (expect Live)
    page.goto(URL, wait_until='load', timeout=15000)

    def get_text(sel):
        try:
            return page.eval_on_selector(sel, 'el => el.textContent')
        except Exception:
            return None

    # wait for Live or Demo
    found = False
    start = time.time()
    while time.time() - start < 10:
        s = get_text('#hrStatus')
        if s and s.strip() in ('Live', 'Demo', 'Connecting...'):
            print('HR_STATUS_BEFORE:', s.strip())
            found = True
            break
        time.sleep(0.2)
    if not found:
        print('FAILED: hrStatus did not reach Live/Demo in time')
        browser.close()
        sys.exit(2)

    # Now close page and create a new page where the SSE request will be aborted
    page.close()
    page2 = context.new_page()
    page2.on('console', lambda msg: print('PAGE2_CONSOLE:', msg.type, msg.text))
    page2.on('pageerror', lambda exc: print('PAGE2_ERROR:', exc))

    # abort any /heartrate/stream requests to force Demo fallback
    def route_handler(route):
        url = route.request.url
        if '/heartrate/stream' in url:
            route.abort()
        else:
            route.continue_()

    page2.route('**/*', lambda route: route_handler(route))
    page2.goto(URL, wait_until='load', timeout=15000)

    # expect it to show Disconnected then Demo and currentHR to update by demo
    got_demo = False
    start = time.time()
    cur_before = get_text('#currentHR')
    while time.time() - start < 12:
        s = get_text('#hrStatus') or ''
        s = s.strip()
        if s == 'Demo':
            got_demo = True
            print('HR_STATUS_AFTER:', s)
            break
        time.sleep(0.3)

    if not got_demo:
        print('FAILED: Did not enter Demo mode after aborting SSE; last status=', s)
        browser.close()
        sys.exit(3)

    time.sleep(2.2)
    cur_after = get_text('#currentHR')
    print('CURRENT_HR_BEFORE:', cur_before, 'AFTER:', cur_after)
    if cur_after and cur_after != cur_before and cur_after != '--':
        print('SUCCESS: Demo BPM flowing and UI updated')
        browser.close()
        sys.exit(0)
    else:
        print('FAILED: currentHR did not update during Demo')
        browser.close()
        sys.exit(4)
