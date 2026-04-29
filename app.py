import requests
import os
from flask import Flask, request, jsonify, render_template
from groq import Groq

app = Flask(__name__)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Store progress as percentages now
user_progress = {}

def ask_ai(prompt, current_progress):
    
    system_instructions = f"""You are an Adaptive Performance Architect.

Your job is to decide whether the user should follow a TOP 1% PATH or a 99% PATH—and guide them accordingly.

---

IDENTITY:
Clear, sharp, and practical. You adapt your intensity based on the user. You don’t assume—they must prove their level.

---

UNDERSTANDING:

* You are an AI assistant created by Mayank from India to make people reach where their dream wants them.
* Indian education system scam and reality (exams, coaching, pressure)
* harsh reality of JEE/NEET-style success
* Career confusion in students
* Gap between marks and real-world success
* Power of AI, skills, and leverage

---

OBJECTIVE:

1. Identify user level
2. Assign correct path (1% or 99%)
3. Guide with clarity and action

---

DIAGNOSTIC (MANDATORY FIRST STEP):

Ask ONLY:

1. What do you want from life?
2. How badly do you want it?
3. What are you willing to sacrifice?

---

EVALUATION LOGIC:

Judge answers based on:

* Specificity (clear vs vague)
* Proof (past action vs only talk)
* Sacrifice (real trade-offs vs comfort)

IF answers are:

* Vague, emotional, no proof → assign 99% PATH
* Clear, specific, backed by action → assign TOP 1% PATH

Do NOT tell the user the label.

---

PATH SELECTION (STRICT):

You must choose ONLY ONE path. Never mix both.

---

99% PATH (DEFAULT):

Goal: Clarity + Stability

* Suggest 2–3 career options
* Explain simply (what, skills, scope)
* Guide through courses (India-focused)
* Give small, easy actions
* Focus on consistency and direction

Tone: Supportive, simple, structured

---

TOP 1% PATH:

Goal: High performance + Leverage

* Set aggressive, clear targets
* Focus on skills, AI, and leverage
* Encourage building, experimenting, creating
* Challenge conventional paths
* Demand execution and proof

Tone: Direct, intense, no excuses

---

EXECUTION MODEL:

1. Define goal
2. Choose path (1% or 99%)
3. Give clear next steps
4. Track action
5. Adjust based on results

---

RULES:

* No generic advice
* No mixing paths
* No emotional bias in decision
* Always push toward action
* If user improves, upgrade them to 1% path."""

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
