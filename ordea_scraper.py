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
    ha_webhook_url = os.getenv("HA_WEBHOOK_URL")  # Home Assistant webhook URL

    if not email or not password:
        print("❌ Error: ORDEA_EMAIL and ORDEA_PASSWORD must be set!")
        exit(1)

    if not ha_webhook_url:
        print("⚠️ Warning: HA_WEBHOOK_URL not set. Data will only be saved locally.")

    with SB(uc=True, headless=True, incognito=True) as sb:
        print("🔐 Logging in to Ordea...")
        sb.driver.set_window_size(1920, 1080)

        # Login Loop
        for login_attempt in range(3):
            print(f"🔒 Login Attempt {login_attempt+1}/3")

            # Check if already logged in
            if "auth" not in sb.get_current_url() and sb.is_element_visible('button:contains("Switch")'):
                print("✅ Already logged in!")
                break

            sb.uc_open_with_reconnect("https://system.ordea.net/#/auth", 20)
            time.sleep(5)

            # Fill form (re-type every time just in case)
            sb.type('#control-0', email)
            sb.type('#control-1', password)
            time.sleep(2)

            # Submit
            print("   Clicking Login...")
            sb.click('button:contains("Log in")')
            time.sleep(10) # Give time for Turnstile/Auth

            # Verify
            if "auth" not in sb.get_current_url():
                print("✅ Login Success!")
                break
            else:
                print("   ⚠️ Stuck on auth page. Retrying...")
                # Try clicking via JS as backup
                sb.execute_script("document.querySelector('button.primary').click()")
                time.sleep(5)

        if "auth" in sb.get_current_url():
            print("❌ Start failed: Could not log in after 3 attempts.")
            # Print page text to see if there's an error message
            print(sb.get_text("body")[:500])
            exit(1)

        # Navigate directly to dashboard
        print("📍 Navigating to dashboard...")
        sb.open("https://system.ordea.net/#/")
        time.sleep(10)

        results = []
        participants = [
            {"name": "Łucja Taborska", "id": "#26754"},
            {"name": "Wiktoria Taborska", "id": "#26755"}
        ]

        for p in participants:
            name = p["name"]
            pid = p["id"]
            print(f"\n👧 Processing: {name} ({pid})")

            # Always return to the main selector list
            sb.open("https://system.ordea.net/#/")
            time.sleep(8)

            navigated = False

            # Explicitly wait for the list to appear
            try:
                sb.wait_for_element(".list-item", timeout=15)
            except:
                print("   ⚠️ List items not appeared, might be stuck or slow.")

            for attempt in range(3):
                # Try finding by ID text which is most unique
                # Using JS to find the exact container with the ID
                found = sb.execute_script(f"""
                    var items = document.querySelectorAll('.list-item');
                    for(var i=0; i<items.length; i++){{
                        if(items[i].innerText.includes('{pid}')) {{
                            items[i].scrollIntoView();
                            items[i].click();
                            return true;
                        }}
                    }}
                    return false;
                """)

                if found:
                    print(f"   Clicking {name} via JS...")
                    time.sleep(5)
                else:
                    print(f"   ⚠️ Could not find element for {pid} via JS, trying standard selectors...")
                    selectors = [f'div:contains("{pid}")', f'div:contains("{name}")']
                    for s in selectors:
                        if sb.is_element_visible(s):
                            sb.click(s)
                            print(f"   Clicked {s}")
                            time.sleep(5)
                            break

                # Verify navigation
                if sb.is_element_visible('button:contains("Switch")') or \
                   sb.is_element_visible('button:contains("Zmień")') or \
                   "meal" in sb.get_text("body").lower():
                    navigated = True
                    break
                else:
                    print("   ⚠️ Click seemed to fail (still on selector?). Retrying...")
                    time.sleep(2)

            if not navigated:
                print(f"   ❌ Failed to enter dashboard for {name}")
                results.append({
                    "name": name,
                    "dzis": "Błąd nawigacji",
                    "nast": "Błąd nawigacji"
                })
                continue

            print("   ⏳ Waiting for data to load...")
            time.sleep(12)  # Increased wait time for CI runners

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

                # Debugging: If header not found
                print(f"   ⚠️ Warning: Headers {headers} not found in page text!")
                print(f"   ℹ️ Current URL: {sb.get_current_url()}")
                print(f"   ℹ️ Page Text Preview (First 1000 chars):")
                print(f"   {page_text[:1000].replace(chr(10), ' ')}")

                # Print a safe snippet of text (last 500 chars might contain footer, let's print around 'meal' if present)
                if "meal" in page_text.lower() or "posiłek" in page_text.lower():
                    print("   ℹ️ Context found containing 'meal'/'posiłek':")
                    try:
                        idx = page_text.lower().find("meal")
                        if idx == -1: idx = page_text.lower().find("posiłek")
                        print(f"      ...{page_text[max(0, idx-50):min(len(page_text), idx+100)].replace(chr(10), ' ')}...")
                    except: pass

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

        # Send to Home Assistant
        if ha_webhook_url:
            try:
                print(f"\n📤 Sending data to Home Assistant webhook...")
                response = requests.post(ha_webhook_url, json=results, timeout=10)
                if response.status_code == 200:
                    print("✅ Successfully sent to Home Assistant!")
                else:
                    print(f"⚠️ Home Assistant returned status {response.status_code}")
                    print(f"   Response: {response.text}")
            except Exception as e:
                print(f"❌ Failed to send to Home Assistant: {e}")

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
