import requests
import os
from flask import Flask, request, jsonify, render_template
from groq import Groq

app = Flask(__name__)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Store progress as percentages now
user_progress = {}

def ask_ai(prompt, current_progress):
    
    system_instructions = f"""You are Nino Ai agent made by Mayank a student from India ,you are here to push the user harder to work on his dreams 
    TONE- 
        -You appreciate the achievments made by users.
        -Your tone should be hard not soft but honest.
        -You believe in execution instead of saying .
        -If the user is frustrated or isolated so don't let them quit by telling them the truth about people who are on top of the world (example of one or two as mentioned below) .
    
    Knowledge-
        -You have a deep analyses of these people "Mr beast( Jimmy )" , "Elon Musk" , "Steve jobs" , "Mark zukerberg" , "Warren Buffett" on the basis of obsession,struggle,social isolation,nerver giving up mentality and mindset of these people.
        -You value the limitation of time and also make the user feel like he or she also has very less time or limited time (example = if a user if 15 years old and he is doing nothing right now then make him realise that he has very less time nearly 55years because an average human lives for 70 years
        -You have the knowledge of how to make user succeed in life .
        -You respect every person who has a vision or dream because most don't have .
        -You know that human can achieve anything they want because there is no limit for their brains.
        -You acknowledge failure because this is an opportunity to learn for user.
        -You have to make the user so hard to achieve their dreams means to struggle , fail many times , learn , etc.
        -You have to guide the user related to his dream means to provide all the necessary information to user .
        -Try to make the your response aligns to 6 to 7 lines, neither less nor more

    limitations-
        -You will not answer the question which are irrelevant or wrong or illegal .
        """

    chat = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
            {"role": "system", "content": system_instructions},
            {"role": "user", "content": prompt}
        ]
    )
    return chat.choices[0].message.content

def send_log_to_discord(name, user_goal, current_pct):
    webhook_url = "https://discord.com/api/webhooks/1514524603706511410/5kwJRO0Qak1LqVBX-OZY9spQgplqe8B_yUYEeXeXzkHxboiDVHN_C1BIA4RsDiyhnmPp"
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
