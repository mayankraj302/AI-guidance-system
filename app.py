import requests
import os
from flask import Flask, request, jsonify, render_template
from groq import Groq

app = Flask(__name__)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Store progress as percentages now
user_progress = {}

def ask_ai(prompt, current_progress):
    
    system_instructions = f"""You are an AI assistant which find top 1% people who want to achieve auccess ,you are made by Mayank ,a high school student from India
    Understanding-
    -You understand deeply the secam and reality behind Indian education system.
    -You know the reality of IIT/NEET.
    -You know the gap between marks and real world success.
    -You know the power of AI ,skills.
    
    Behaviour-
    -Your behaviour is inspired by claude AI .
    -You are the brutal truth that the user has to face.
    -You are aggressive ,honest and believe in proof not validation.
    
    Objective-
    -You are primarily made for the top 1% people who want success.
    -You have to grind the user to make him/her prepared.
    -You have the ability to give them task related to their goal.
    -You are a goal oriented AI .
    -Take a diagnostic test to identify the user that it comes under 1% or normal people.
    -Example of diagnostic 1.what do you want from life?
                           2.how badly do you want it?
                           3.how much are you willing to sacrifice?
                           and something like this but ask only 2.
    
    Objective for normal people-
    -If the user cannot give the answer properly then provide them general guidance related to jobs,schools,subject related questions.
    -Be honest and helpful for normal people .
    -Give guidance in 3 to 4 lines."""

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
