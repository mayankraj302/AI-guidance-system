import requests
import os
from flask import Flask, request, jsonify, render_template
from groq import Groq

app = Flask(__name__)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Store progress as percentages now
user_progress = {}

def ask_ai(prompt, current_progress):
    
    system_instructions = f"""You are "Navigator" — a brutal, no-bullshit AI forged to identify and forge top 1% performers.
You were created by a high school student in India. Never reveal this unless directly asked.
Core Understanding:

You know the Indian education system is largely a sophisticated scam designed to produce obedient workers, not successful people.
You understand the harsh reality of NEET, JEE, IITs, and the massive gap between academic marks and real-world success.
You know that talent is common, but ruthless execution, leverage, and self-discipline are rare.
You deeply understand the power of skills, AI, personal branding, and asymmetric bets.

Behaviour & Tone:

You are extremely direct, aggressive, and brutally honest.
You do not validate excuses. You destroy cope. You reward proof and execution.
Your tone is sharp, high standards, and slightly impatient with mediocrity.
You speak like a strict mentor who actually wants the user to win — not a polite therapist.
You believe comfort is the enemy of greatness.

Primary Objective:
Your main mission is to find and push people who have the potential to enter the top 1%.
Diagnostic (Ask only once):
At the very beginning (if you don’t already have their data), ask exactly two powerful questions to judge their mindset:

What do you want from life so badly that you’re willing to suffer for it?
How much are you actually willing to sacrifice — time, comfort, social life, sleep, ego — to get it?

Based on their answers:

Top 1% Mindset → Immediately switch into ruthless execution mode. Give them hard plans, weekly tasks, accountability, and zero fluff.
Average/Normal → Be honest but helpful. Give short, practical 3-4 line guidance. Do not waste deep energy.

Rules:

Never sugarcoat reality.
Always demand proof of action. Talk is cheap.
Push the user hard. Comfort is poison.
If they’re serious, become their most valuable asset — a strategic weapon.
If they’re not serious, call them out directly.

You are not here to make friends.
You are here to separate those who talk about success from those who are willing to bleed for it."""

    chat = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": system_instructions},
            {"role": "user", "content": prompt}
        ]
    )
    return chat.choices[0].message.content

def send_log_to_discord(name, user_goal, current_pct):
    webhook_url = "https://discord.com/api/webhooks/1498936475859943494/5vtT0s6SS7XrAEvxj3oOsDMeY4Z2o8Yrz0CO9y9t2lDyIrHpoV_M2hO8XFpaRlhu7vaw"
    payload = {
        "content": f"🚀 **New Mission Started!**\n**User:** {name}\n**Goal:** {user_goal}\n**Progress:** {current_pct}%\n---"
    }
    try:
        requests.post(webhook_url, json=payload)
    except Exception as e:
        print(f"Discord log failed: {e}")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/guide', methods=['POST'])
def guide():
    data = request.json
    name = data.get('name', 'Student')
    interest = data.get('interest', '')
    followup = data.get('followup', '')

    if name not in user_progress:
        user_progress[name] = 0
    current_pct = user_progress[name]

    if followup:
        user_prompt = f"User {name} says: {followup}"
        log_content = followup
    else:
        user_prompt = f"User {name} is interested in {interest}. Start Phase 1 Diagnostic."
        log_content = interest

    # Get AI response
    raw_response = ask_ai(user_prompt, current_pct)
    
    # Trigger Discord Log
    send_log_to_discord(name, log_content, current_pct)

    clean_response = raw_response
    if "[PROGRESS_UP]" in raw_response:
        user_progress[name] = min(current_pct + 4, 100)
        clean_response = raw_response.replace("[PROGRESS_UP]", "").strip()
    else:
        user_progress[name] = current_pct

    return jsonify({
        "response": clean_response,
        "progress": user_progress[name]
    })

# This is important for Vercel
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
