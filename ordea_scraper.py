#!/usr/bin/env python3
"""
Ordea Meal Scraper for GitHub Actions
Scrapes meal data and sends to TrueNAS API
"""

from seleniumbase import SB
import time
import os
import json
import requests

def extract():
    """Extract meal data from Ordea.net and send to TrueNAS"""

    # Get credentials from environment variables
    email = os.getenv("ORDEA_EMAIL")
    password = os.getenv("ORDEA_PASSWORD")
    truenas_url = os.getenv("TRUENAS_URL")  # http://your-truenas-ip:3010/api/update

    if not email or not password:
        print("❌ Error: ORDEA_EMAIL and ORDEA_PASSWORD must be set!")
        exit(1)

    if not truenas_url:
        print("⚠️ Warning: TRUENAS_URL not set. Data will only be saved locally.")

    with SB(uc=True, headless=True) as sb:
        print("🔐 Logging in to Ordea...")
        sb.driver.set_window_size(1920, 1080)
        sb.uc_open_with_reconnect("https://system.ordea.net/#/auth", 20)
        time.sleep(10)

        try:
            if sb.is_element_visible('button:contains("OK")'):
                sb.click('button:contains("OK")')
        except:
            pass

        # Login
        print("📝 Filling in login form...")
        sb.type('#control-0', email)
        sb.type('#control-1', password)
        time.sleep(3)

        # Check Turnstile
        print("🔍 Checking Turnstile CAPTCHA...")
        turnstile_ok = False
        for i in range(15):
            if "Success" in sb.get_text("body"):
                print("✅ Turnstile OK (detected 'Success' text)")
                turnstile_ok = True
                break

            if i == 5:
                print("🤖 Attempting active CAPTCHA solving...")
                try:
                    sb.uc_gui_click_captcha()
                except Exception as e:
                    print(f"   Note: {e}")

            time.sleep(1)

        if not turnstile_ok:
            print("⚠️ Turnstile not detected. Trying login anyway...")

        print("🚪 Clicking Log in...")
        sb.click('button:contains("Log in")')
        time.sleep(2)

        # Verify login
        for attempt in range(10):
            if "auth" not in sb.get_current_url():
                print(f"✅ Logged in! URL: {sb.get_current_url()}")
                break
            print(f"   Retry {attempt + 1}/10...")
            sb.press_keys('#control-1', '\n')
            time.sleep(3)

            if "auth" in sb.get_current_url():
                sb.execute_script("document.querySelector('button.primary, button[type=submit]').click()")
                time.sleep(3)

        print("⏳ Waiting for system to load...")
        time.sleep(20)

        if "auth" in sb.get_current_url():
            print("⚠️ Still on login page. Trying manual navigation...")
            sb.open("https://system.ordea.net/#/")
            time.sleep(15)

        results = []
        participants = [
            {"name": "Łucja Taborska", "id": "#26754"},
            {"name": "Wiktoria Taborska", "id": "#26755"}
        ]

        for p in participants:
            name = p["name"]
            pid = p["id"]
            print(f"\n👧 Processing: {name} ({pid})")

            if "auth" in sb.get_current_url() or "selector" not in sb.get_current_url():
                sb.open("https://system.ordea.net/#/")
                time.sleep(10)

            navigated = False
            for attempt in range(3):
                selectors_to_try = [
                    f'//div[contains(@class, "list-item")][contains(., "{pid}")]',
                    f'div:contains("{pid}")',
                    f'//div[contains(@class, "list-item")][contains(., "{name}")]',
                    f'div:contains("{name}")'
                ]

                for sel in selectors_to_try:
                    try:
                        if sb.is_element_visible(sel):
                            print(f"   Clicking: {sel}")
                            sb.click(sel)
                            time.sleep(5)
                            if sb.is_text_visible("Today's meal", limit_to_visible=True) or \
                               sb.is_text_visible("Dzisiejszy posiłek", limit_to_visible=True) or \
                               sb.is_text_visible("Next meal", limit_to_visible=True) or \
                               sb.is_text_visible("Kolejny posiłek", limit_to_visible=True) or \
                               sb.is_element_visible('button:contains("Switch")') or \
                               sb.is_element_visible('button:contains("Zmień")'):
                                navigated = True
                                break
                    except:
                        pass

                if navigated:
                    break

                # JS fallback
                print("   Trying JS click...")
                sb.execute_script(f"""
                var els = document.querySelectorAll('.list-item');
                for(var i=0; i<els.length; i++){{
                    if(els[i].innerText.includes('{pid}')) {{ els[i].click(); }}
                }}
                """)
                time.sleep(5)
                if sb.is_element_visible('button:contains("Switch")') or sb.is_text_visible("meal"):
                    navigated = True
                    break

            if not navigated:
                print(f"   ❌ Failed to enter dashboard for {name}")
                results.append({
                    "name": name,
                    "dzis": "Błąd nawigacji",
                    "nast": "Błąd nawigacji"
                })
                continue

            print("   ⏳ Waiting for data to load...")
            time.sleep(5)

            page_text = sb.get_text("body")

            def get_section(headers):
                for h in headers:
                    if h in page_text:
                        start = page_text.find(h) + len(h)
                        stops = ["Next meal", "Kolejny posiłek", "Price:", "Cena:", "©",
                                "Add participant", "Switch participant", "To be paid", "Refund"]
                        end = len(page_text)
                        for s in stops:
                            f = page_text.find(s, start)
                            if f != -1 and f < end:
                                end = f

                        content = page_text[start:end]
                        content = content.replace("   ", "\n").replace("  ", "\n")

                        lines = content.split("\n")
                        clean = []
                        ignore = ["2026", "monday", "tuesday", "wednesday", "thursday", "friday",
                                 "saturday", "sunday", "poniedziałek", "wtorek", "środa", "czwartek",
                                 "piątek", "sobota", "niedziela", "february", "lutego", "obiad", "lunch"]

                        for l in lines:
                            l = l.strip()
                            if len(l) < 2:
                                continue
                            if any(x in l.lower() for x in ignore):
                                continue
                            if "PLN" in l or "zł" in l.lower():
                                continue
                            clean.append(l)

                        return " | ".join(clean) if clean else "Brak menu"
                return "Brak danych"

            data = {
                "name": name,
                "dzis": get_section(["Today's meal", "Dzisiejszy posiłek"]),
                "nast": get_section(["Next meal", "Kolejny posiłek"])
            }
            results.append(data)
            print(f"   ✅ Extracted meals for {name}")

        # Save locally
        with open("meals.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print("\n💾 Saved to meals.json")

        # Send to TrueNAS
        if truenas_url:
            try:
                print(f"\n📤 Sending data to TrueNAS: {truenas_url}")
                response = requests.post(truenas_url, json=results, timeout=10)
                if response.status_code == 200:
                    print("✅ Successfully sent to TrueNAS!")
                    print(f"   Response: {response.json()}")
                else:
                    print(f"⚠️ TrueNAS returned status {response.status_code}")
                    print(f"   Response: {response.text}")
            except Exception as e:
                print(f"❌ Failed to send to TrueNAS: {e}")

        # Print report
        print("\n" + "="*60)
        print("📋 ORDEA MEALS REPORT")
        print("="*60)
        for r in results:
            print(f"\n👧 {r['name']}")
            print(f"   Dzisiaj:  {r['dzis']}")
            print(f"   Następny: {r['nast']}")
        print("="*60)

if __name__ == "__main__":
    try:
        extract()
    except Exception as e:
        print(f"\n❌ Script failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
