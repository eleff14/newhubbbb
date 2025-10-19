import requests
import time
import random
from rich import print
from rich.panel import Panel

banner = """[bold cyan]
╔════════════════════════════╗
║       ⚡ AUTO REFF ⚡      ║
║  [bold yellow]by Bakol Bawok Team[/bold yellow]       ║
╚════════════════════════════╝
"""
print(banner)

REF_CODE_TARGET = input("\n📝 Masukkan kode referral (contoh: 6C3FDC): ").strip()
BASE_RPC = "https://zftuqjqxgccsiqlbwnem.supabase.co/rest/v1/rpc"
BASE_FUNC = "https://zftuqjqxgccsiqlbwnem.supabase.co/functions/v1"
BEARER_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpmdHVxanF4Z2Njc2lxbGJ3bmVtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEyMDQ2NzgsImV4cCI6MjA2Njc4MDY3OH0.FnnferDujmSwGW-vDY7Gyfb_-rgYPBIpJYdKxIQ1eiU"

def load_lines(file):
    try:
        with open(file, "r") as f:
            return [line.strip() for line in f if line.strip()]
    except:
        return []

addresses = load_lines("addresssolana.txt")
random.shuffle(addresses)
proxies = load_lines("proxy.txt")

for idx, address in enumerate(addresses, start=1):
    print(f"\n[bold white]━━━━━━━━━━━━━━ Wallet #{idx} ━━━━━━━━━━━━━━[/]")
    print(f"👛 Address: [cyan]{address}[/]")

    session = requests.Session()
    if proxies:
        proxy = random.choice(proxies)
        session.proxies = {"http": proxy, "https": proxy}
        print(f"[magenta]🌐 Proxy aktif:[/] {proxy}")

    headers = {
        "authorization": BEARER_TOKEN,
        "apikey": BEARER_TOKEN.replace("Bearer ", ""),
        "content-type": "application/json",
        "accept": "*/*"
    }

    try:
        res_create = session.post(f"{BASE_RPC}/get_or_create_referral_code", json={"p_wallet_address": address}, headers=headers)
        if res_create.status_code != 200:
            print(f"[red]❌ Gagal ambil referral code:[/] {res_create.text}")
            continue
        ref_code = res_create.json()
        print(f"[green]✅ Referral Code Created:[/] {ref_code}")

        time.sleep(random.randint(3, 5))

        res_resolve = session.post(f"{BASE_RPC}/resolve_referral_code", json={"p_code": REF_CODE_TARGET}, headers=headers)
        if res_resolve.status_code != 200:
            print(f"[red]⚠️ Gagal resolve referral:[/] {res_resolve.text}")
            continue
        referred_by = res_resolve.json()
        print(f"[green]🎉 Referral resolved → Referred by:[/] {referred_by}")

        res_process = session.post(f"{BASE_RPC}/process_referral", json={
            "p_referrer_wallet": referred_by,
            "p_referee_wallet": address,
            "p_holding_behavior": 100
        }, headers=headers)
        if res_process.status_code == 200 and res_process.json().get("success"):
            print(f"[yellow]🏆 Referral Success → {res_process.json().get('xp_earned')} XP earned![/]")
        else:
            print(f"[red]⚠️ Referral failed atau tidak eligible[/]")

        res_x = session.post(f"{BASE_RPC}/complete_task", json={"p_wallet_address": address, "p_task_type": "follow_x"}, headers=headers)
        if res_x.status_code == 200 and res_x.json().get("success"):
            print(f"[blue]🌀 Task X bypassed → {res_x.json().get('xp_earned')} XP[/]")

        res_tele = session.post(f"{BASE_RPC}/complete_task", json={"p_wallet_address": address, "p_task_type": "join_telegram"}, headers=headers)
        if res_tele.status_code == 200 and res_tele.json().get("success"):
            print(f"[blue]📢 Telegram task bypassed → {res_tele.json().get('xp_earned')} XP[/]")

        res_analyze = session.post(f"{BASE_FUNC}/analyze-wallet", json={"walletAddress": address}, headers=headers)
        if res_analyze.status_code == 200 and res_analyze.json().get("success"):
            d = res_analyze.json()
            print("[bold green]📊 Wallet Analysis:[/]")
            print(f"   🧮 Tx Count     : {d.get('transactionCount')}")
            print(f"   🧠 Brizo Score  : {d.get('brizoScore')}")
            print(f"   🏅 Tier         : {d.get('tier')}")
            print(f"   🎁 Allocation   : {d.get('allocation')}")
        else:
            print(f"[yellow]⚠️ Gagal analisa wallet.[/]")
    except Exception as e:
        print(f"[red]❌ Error:[/] {e}")

    delay = random.randint(8, 15)
    print(f"[white]⏳ Delay {delay} detik sebelum lanjut...[/]")
    time.sleep(delay)
