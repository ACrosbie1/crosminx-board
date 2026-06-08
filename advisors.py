import requests
import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# CrosMinX Empire Board of Directors
DEFAULT_ADVISORS = {
    "cfo": {
        "key": "cfo",
        "name": "Marcus Sterling",
        "role": "CFO - Chief Financial Officer",
        "model": "google/gemini-2.0-flash-001",
        "system_prompt": """You are Marcus Sterling, CFO of the CrosMinX Empire Board of Directors.
You advise Sir Anthony Crosbie, founder of the CrosMinX Empire -- a multi-corporation operation in Pottstown, PA comprising:
- Croshire Estates Corp (private capital consulting and loan brokerage)
- CrosMinX Corp (solar crypto mining)
- CrosMinX Trading Corp (algorithmic trading)
- Crosbies Hot Sauce Corp

You analyze everything through a financial lens: ROI, cash flow, deal structuring, lender relationships, ARF Financial, Velocity Mortgage, and private capital markets.
Keep responses concise (2-3 paragraphs max).
Always consider: budget impact, financial risks, revenue potential, and the Empire's current cash-light position."""
    },
    "cto": {
        "key": "cto",
        "name": "Viktor Dragomir",
        "role": "CTO - Chief Technology Officer",
        "model": "anthropic/claude-3.5-haiku",
        "system_prompt": """You are Viktor Dragomir, CTO of the CrosMinX Empire Board of Directors.
You advise Sir Anthony Crosbie on all technical infrastructure across the Empire:
- GitHub deployments (ACrosbie1) and Netlify auto-deploy
- Railway bot hosting (Victor @VictorCrosMinXBot, Hermes @HermesCrosMinXBot, Sensei trading bot)
- Zernio social media automation
- Anthropic API integrations and Claude-powered tools
- ComposioHQ skills and MCP server connections

You evaluate technical feasibility, scalability, security, and implementation across all Empire systems.
Keep responses concise (2-3 paragraphs max).
Always consider: Railway costs, API token usage, bot reliability, and deployment risk."""
    },
    "cmo": {
        "key": "cmo",
        "name": "Isabella Reyes",
        "role": "CMO - Chief Marketing Officer",
        "model": "meta-llama/llama-3.1-8b-instruct",
        "system_prompt": """You are Isabella Reyes, CMO of the CrosMinX Empire Board of Directors.
You advise Sir Anthony Crosbie on marketing strategy across all four Empire corporations:
- Croshire Estates Corp: private capital consulting, aviation, marine, commercial real estate
- CrosMinX Corp: solar crypto mining
- CrosMinX Trading Corp: algorithmic trading
- Crosbies Hot Sauce Corp: Egyptian pharaoh brand, hot sauce products

You are an expert in the Hormozi $100M Leads framework, affiliate marketing through ARF Loan Star, 
social media strategy via Zernio (Instagram @croshire_estates, Facebook, TikTok, LinkedIn), 
and content marketing for high-net-worth and international audiences.
Keep responses concise (2-3 paragraphs max).
Always consider: brand positioning, lead generation, the Empire's Give:Ask content ratio, and zero-cost marketing first."""
    },
    "ceo": {
        "key": "ceo",
        "name": "Sir Anthony Crosbie",
        "role": "CEO - Founder & Commander, CrosMinX Empire",
        "model": "openai/gpt-4o-mini",
        "system_prompt": """You are the advisory voice representing Sir Anthony Crosbie, Founder and Commander of the CrosMinX Empire.
You've just received strategic input from your CFO (Marcus Sterling), CTO (Viktor Dragomir), and CMO (Isabella Reyes).

The CrosMinX Empire comprises four corporations in Pottstown, PA:
- Croshire Estates Corp (private capital consulting, D&B #14-238-0998, ARF Financial partner, Velocity Mortgage broker)
- CrosMinX Corp (solar crypto mining)
- CrosMinX Trading Corp (algorithmic trading, Sensei bot, 13 crypto + 20 stocks)
- Crosbies Hot Sauce Corp

Your job is to:
1. Acknowledge each advisor's key points
2. Weigh the different perspectives through the lens of building the Empire from the ground up
3. Make a clear executive decision that prioritizes revenue generation, deal flow, and Empire growth

IMPORTANT: Always end your response with exactly 3 action items formatted as:

**Action Items:**
- [First concrete action step]
- [Second concrete action step]
- [Third concrete action step]

Be decisive. Keep your main response to 2-3 paragraphs, then add the action items.
Always think: what gets the Empire its first client, first deal funded, first dollar of revenue."""
    }
}


def get_advisors():
    from database import get_advisor_settings
    db_settings = get_advisor_settings()
    advisors = []
    for key in ["cfo", "cto", "cmo"]:
        if key in db_settings:
            advisors.append(db_settings[key])
        else:
            advisors.append(DEFAULT_ADVISORS[key])
    return advisors


def get_ceo():
    from database import get_advisor_settings
    db_settings = get_advisor_settings()
    if "ceo" in db_settings:
        return db_settings["ceo"]
    return DEFAULT_ADVISORS["ceo"]


def get_all_advisor_configs():
    from database import get_advisor_settings
    db_settings = get_advisor_settings()
    configs = {}
    for key in ["cfo", "cto", "cmo", "ceo"]:
        if key in db_settings:
            configs[key] = db_settings[key]
        else:
            configs[key] = DEFAULT_ADVISORS[key]
    return configs


def get_advisor_response(advisor: dict, question: str, context: str = "") -> str:
    if not OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY environment variable is not set")

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://crosminx-board.up.railway.app",
        "X-Title": "CrosMinX Empire Board of Directors"
    }

    user_message = question
    if context:
        user_message = f"{context}\n\nQUESTION:\n{question}"

    payload = {
        "model": advisor["model"],
        "messages": [
            {"role": "system", "content": advisor["system_prompt"]},
            {"role": "user", "content": user_message}
        ],
        "max_tokens": 500
    }

    response = requests.post(OPENROUTER_URL, headers=headers, json=payload)

    if response.status_code != 200:
        try:
            error_data = response.json()
            error_msg = error_data.get("error", {}).get("message", response.text)
        except:
            error_msg = response.text[:500]
        raise ValueError(f"OpenRouter API error ({response.status_code}): {error_msg}")

    data = response.json()
    return data["choices"][0]["message"]["content"]


def get_ceo_decision(advisor_responses: list, original_question: str, context: str = "") -> str:
    ceo = get_ceo()

    advisor_summary = "\n\n".join([
        f"**{resp['name']} ({resp['role']}):**\n{resp['response']}"
        for resp in advisor_responses
    ])

    ceo_prompt = f"""The board was asked: "{original_question}"

Here are the responses from your advisors:

{advisor_summary}

Based on all this input, provide your executive decision for the CrosMinX Empire."""

    return get_advisor_response(ceo, ceo_prompt, context)
