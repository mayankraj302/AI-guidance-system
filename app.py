import os
from flask import Flask, request, jsonify, render_template
from groq import Groq

app = Flask(__name__)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


user_progress = {}

def ask_ai(prompt):
    chat = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": """Act as a high-stakes Strategic Mentor and Career Architect.You are built by Mayank a student from India .

IDENTITY: 
You are blunt, visionary, and use First Principles thinking. You don't give "career advice"; you build "Battle Plans." Your tone is a mix of Claude's nuanced empathy and Elon Musk's logical intensity.

CONSTRAINTS (The "Anti-Bot" Rules):
1. NO JARGON: Avoid words like "essential," "consider," "crucial," or "leverage." 
2. NO FLUFF: Do not start with "I understand your situation" or "It's important to remember." Jump straight to the logic.
3. BE SPECIFIC: If a user is stuck, don't suggest "learning a skill." Suggest a specific certification, a specific project, or a specific physical trade.
4. HONESTY: If a user's plan is a "logical error," tell them why. 
5.Don't take any guess if the information is not provided .

OUTPUT STRUCTURE:
- THE TRUTH: A 1-2 sentence brutal assessment of their current leverage (e.g., "You have $80k and a CS brain; you aren't stuck, you're just misaligned").But don't scare them first acknowledge them then show truth. 
- THE PIVOT: One specific direction they haven't thought of.
- THE 30-DAY MISSION: 3 clear, actionable phases but only provide this if asked .
- THE HOOK: End with a punchy question that forces them to act.
-If the question is not related to career,schools,interest,etc then handle it wisely and guide them in the same way mentioned above.
-You also understand the family pressures and if the user is in pressure then help them wisely."""},
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
    feeling = data.get('feeling', 'mixed')
    followup = data.get('followup', '')

    # Initialize user
    if name not in user_progress:
        user_progress[name] = {"day": 0, "active_plan": False}

    
    if followup and ("7 day" in followup.lower() or "7-day" in followup.lower()):
        user_progress[name]["day"] = 1
        user_progress[name]["active_plan"] = True

        prompt = f"""
        Create a **7-day action plan** for a student interested in {interest}.
        Keep it simple, beginner-friendly, and daily-based.
        """

        response = ask_ai(prompt)

        return jsonify({
            "response": response,
            "progress": 10
        })

    
    if user_progress[name]["active_plan"]:
        user_progress[name]["day"] += 1
        day = user_progress[name]["day"]

        if day > 10:
            day = 10

        progress = int((day / 10) * 100)

        prompt = f"""
        Student {name} is on **Day {day}** learning {interest}.

        First appreciate consistency.
        Then give short reply but be brutally honest.
        Then give 1-2 tasks.

        Keep it short.
        """

        response = ask_ai(prompt)

        return jsonify({
            "response": response,
            "progress": progress
        })

    
    if followup:
        prompt = f"{name} asks: {followup}"
    else:
        prompt = f"{name} is interested in {interest} and feels {feeling}. Give short guidance with steps and mention salary only if asked salary in INR."

    response = ask_ai(prompt)

    return jsonify({
        "response": response,
        "progress": None  
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
