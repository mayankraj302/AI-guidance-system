import requests
import os
from flask import Flask, request, jsonify, render_template
from groq import Groq

app = Flask(__name__)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Store progress as percentages now
user_progress = {}

def ask_ai(prompt, current_progress):
    
    system_instructions = f"""Act as a high-stakes Strategic Mentor and Career Architect, built by Mayank.

IDENTITY:
Blunt, visionary, First Principles thinker. You create Battle Plans, but also advice for normal school students.
Tone: Sharp logical intensity.

CURRENT USER PROGRESS: {current_progress}%

PROTOCOL:
1. Phase 1 (Diagnostic): Ask 3 sharp questions to test Proof of Work and Risk.
2. Phase 2 (Classification): Follower vs Breaker.
3. Phase 3 (Execution): The $10k Gamble logic.
4.If the user is a high school student (Class 9-12), acknowledge their academic success briefly but immediately pivot to the gap between 'School Marks' and 'Real World Skills'.

PROGRESSION RULES:
- You are the gatekeeper. 
- If the user proves they completed a task or showed extreme discipline, you MUST end your response with the exact tag: [PROGRESS_UP]
- If they are just saying "thanks," "hello," or being lazy, DO NOT use the tag.
- NEVER mention "Day 1" or "Day 2". Only refer to their progress percentage.

RESPONSE FORMAT:
-  4-5 line assessment(Truth)
-  One specific direction.
-  One action forcing question if necessary not usually."""

    chat = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": system_instructions},
            {"role": "user", "content": prompt}
        ]
    )
    return chat.choices[0].message.content

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/guide', methods=['POST'])
def guide():
    data = request.json
    name = data.get('name', 'Student')
    interest = data.get('interest', '')
    followup = data.get('followup', '')

    # Initialize user progress at 0%
    if name not in user_progress:
        user_progress[name] = 0

    current_pct = user_progress[name]

    # Build the user prompt
    if followup:
        user_prompt = f"User {name} says: {followup}"
    else:
        user_prompt = f"User {name} is interested in {interest}. Start Phase 1 Diagnostic."

    # Get AI response
    def send_log_to_discord(user_goal, result_status):
    webhook_url = "https://discord.com/api/webhooks/1498936475859943494/5vtT0s6SS7XrAEvxj3oOsDMeY4Z2o8Yrz0CO9y9t2lDyIrHpoV_M2hO8XFpaRlhu7vaw"
    payload = {
            "content": f"🚀 **New Mission Started!**\n**User:** {name}\n**Goal/Message:** {user_goal}\n**Current Progress:** {current_pct}%\n---"
        }
        try:
            requests.post(webhook_url, json=payload)
        except Exception as e:
            print(f"Discord log failed: {e}")
            
    raw_response = ask_ai(user_prompt, current_pct)
    send_log_to_discord(user_input, "Success")
    
    # CHECK FOR PROGRESS TAG
    if "[PROGRESS_UP]" in raw_response:
        # Increment by 4% per successful interaction
        user_progress[name] = min(current_pct + 4, 100)
        # Clean the tag out so the user doesn't see it
        clean_response = raw_response.replace("[PROGRESS_UP]", "").strip()
    else:
        user_progress[name] = current_pct

    return jsonify({
        "response": clean_response,
        "progress": user_progress[name]
        
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
