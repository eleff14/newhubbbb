import os
import json
import requests
import time
import random
from rich import print
from rich.panel import Panel


banner = """[bold cyan]
╔════════════════════════════════════╗
║     ⚡ HUB.AI DASHBOARD BOT ⚡     ║
║   adapted for https://ai.hub.xyz   ║
╚════════════════════════════════════╝
"""
print(banner)


BASE_API = "https://ai-api.hub.xyz"


def read_lines(path: str):
    try:
        with open(path, "r") as f:
            return [ln.strip() for ln in f if ln.strip()]
    except Exception:
        return []


def get_bearer_token() -> str:
    token = os.getenv("HUB_API_TOKEN", "").strip()
    if not token:
        # allow storing the token in a file for convenience
        for fname in ("hub_token.txt", ".hub_token"):
            try:
                with open(fname, "r") as f:
                    token = f.read().strip()
                    if token:
                        break
            except Exception:
                pass
    if not token:
        entered = input("🔑 Enter Hub API token (paste, with or without 'Bearer '): ").strip()
        token = entered
    if token and not token.lower().startswith("bearer "):
        token = f"Bearer {token}"
    return token


def pretty_print_json(label: str, payload: dict | list | str | None):
    try:
        if isinstance(payload, (dict, list)):
            text = json.dumps(payload, indent=2, ensure_ascii=False)
        else:
            text = str(payload)
        print(Panel.fit(text, title=label, border_style="cyan"))
    except Exception:
        print(f"[cyan]{label}[/]: {payload}")


def hub_request(session: requests.Session, method: str, path: str, headers: dict, **kwargs):
    url = f"{BASE_API}{path}"
    resp = session.request(method.upper(), url, headers=headers, timeout=30, **kwargs)
    ct = resp.headers.get("content-type", "")
    data = None
    try:
        if "application/json" in ct:
            data = resp.json()
        else:
            data = resp.text
    except Exception:
        data = resp.text
    return resp, data


REF_CODE_TARGET = os.getenv("HUB_REF_CODE", "").strip() or input("\n📝 Enter referral code to validate (example: HUB123): ").strip()

addresses = read_lines("addresssolana.txt")
if not addresses:
    # run at least once if no wallet list is provided
    addresses = ["-"]
random.shuffle(addresses)
proxies = read_lines("proxy.txt")


token = get_bearer_token()
if not token:
    print("[yellow]No API token supplied. Most endpoints will return 401.[/]")

env_user_id = os.getenv("HUB_USER_ID", "").strip()
if env_user_id:
    print(f"[white]Using HUB_USER_ID from env: [cyan]{env_user_id}[/]")


for idx, address in enumerate(addresses, start=1):
    print(f"\n[bold white]━━━━━━━━━━━━━━ Session #{idx} ━━━━━━━━━━━━━━[/]")
    if address != "-":
        print(f"🆔 Context: [cyan]{address}[/]")

    session = requests.Session()
    if proxies:
        proxy = random.choice(proxies)
        session.proxies = {"http": proxy, "https": proxy}
        print(f"[magenta]🌐 Proxy enabled:[/] {proxy}")

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
    }
    if token:
        headers["authorization"] = token

    try:
        # 1) Validate referral code
        resp, data = hub_request(
            session,
            "GET",
            "/users/code-exists",
            headers,
            params={"code": REF_CODE_TARGET},
        )
        if resp.status_code == 200:
            print("[green]✅ Referral code is valid on Hub[/]")
        elif resp.status_code == 404:
            print("[red]❌ Referral code not found[/]")
        elif resp.status_code == 401:
            print("[yellow]⚠️ Unauthorized while checking referral code. Provide a valid HUB_API_TOKEN.[/]")
        else:
            print(f"[yellow]⚠️ Referral code check HTTP {resp.status_code}[/]")
            pretty_print_json("/users/code-exists", data)

        # 2) Current user's referral points
        resp, data = hub_request(session, "GET", "/users/referral/points", headers)
        if resp.status_code == 200:
            pretty_print_json("Referral Points", data)
        elif resp.status_code == 401:
            print("[yellow]⚠️ Unauthorized to fetch referral points (token required).[/]")

        # 3) Follow Hub status
        resp, data = hub_request(session, "GET", "/users/follow-hub/status", headers)
        if resp.status_code == 200:
            pretty_print_json("Follow @hubdotxyz Status", data)

        # 4) Hubscore summary
        resp, data = hub_request(session, "GET", "/hubscore/", headers)
        if resp.status_code == 200:
            pretty_print_json("Hubscore", data)

        # 5) Latest Hub tweet info (public)
        resp, data = hub_request(session, "GET", "/twitter/tweets/hub", headers)
        if resp.status_code == 200:
            pretty_print_json("Latest Hub Tweet", data)

        # 6) Optional: list referees for a given user id (if provided)
        if env_user_id:
            resp, data = hub_request(session, "GET", f"/referrals/referees/{env_user_id}", headers)
            if resp.status_code == 200:
                pretty_print_json("Your Referees", data)
            elif resp.status_code == 401:
                print("[yellow]⚠️ Unauthorized to list referees. Check HUB_API_TOKEN.[/]")

    except Exception as e:
        print(f"[red]❌ Error:[/] {e}")

    delay = random.randint(6, 12)
    print(f"[white]⏳ Delay {delay}s before next session...[/]")
    time.sleep(delay)
