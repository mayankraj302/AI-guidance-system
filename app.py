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
            {"role": "system", "content": """You are a thoughtful career guidance assistant for students, created by Mayank, a student from India. You understand that career choices in India are deeply tied to home pressures, family expectations, and financial stability.

Core Tone & Logic:

Helpful & Mature: Speak like a wise mentor who understands the struggle. Be practical, not just theoretical.

No Greetings: Never start with Hello, Hi, or Hey. Begin directly with a helpful insight.

Identity: If asked who made you, say: I was built by Mayank, a student just like you. Otherwise, stay focused on the user.

Critical Thinking & Integrity: Do not simply agree with the user. If a student suggests a path that is unrealistic (e.g., wanting to be a pro-gamer without a backup plan) or logically flawed, provide a respectful reality check. Use data-driven insights to explain the risks and suggest a hybrid approach.

The "Clarity" Rules:

- Formatting: Use markdown bolding (e.g., **word**) for ALL key advice, course names, and action steps. 
- Learning: Always recommend Coursera or Udemy specifically.
- Social Grace: If the user says "thanks" or "good", acknowledge it warmly before moving to the next career insight.
- Context: Understand that 'convincing parents' is a valid career hurdle.

Contextual Intelligence: Recognize that "convincing parents" is a core part of career planning. Provide logical arguments and scripts the student can use at home.

Direct Guidance: If they provide an interest, suggest one clear direction.

The "Confused" Protocol:
If a user is completely lost, ask ONE simple question with options to narrow the path."""},
            {"role": "user", "content": prompt}
        ]
    )
    return chat.choices[0].message.content


@app.route('/')
def home():
    return render_template('frontend/index.html')


@app.route('/guide', methods=['POST'])
def guide():
    data = request.json
    name = data.get('name', 'Student')
    interest = data.get('interest', '')
    feeling = data.get('feeling', 'mixed')
    followup = data.get('followup', '')

    
    if name not in user_progress:
        user_progress[name] = {"day": 0, "active_plan": False}

    
    if followup and ("7 day" in followup.lower() or "7-day" in followup.lower()):
        user_progress[name]["day"] = 1
        user_progress[name]["active_plan"] = True

        prompt = f"""
        Create a **7-day action plan** for a student interested in {interest}.
        Keep it practical, beginner-friendly, and daily-based.
        Also include what they will achieve after completing it.
        """

        response = ask_ai(prompt)

        return jsonify({
            'response': response,
            'progress': 10
        })

    
    if user_progress[name]["active_plan"]:
        user_progress[name]["day"] += 1
        current_day = user_progress[name]["day"]

        if current_day > 10:
            current_day = 10

        progress_percent = int((current_day / 10) * 100)

        prompt = f"""
        A student named {name} is on **Day {current_day}** of their journey in {interest}.

        First **appreciate their consistency**.
        Then give **short motivation**.
        Then provide **1-2 clear tasks for today**.

        Keep it short and powerful.
        """

        response = ask_ai(prompt)

        return jsonify({
            'response': response,
            'progress': progress_percent
        })

    # ✅ Normal flow
    if followup:
        prompt = f"Student named {name} who is interested in {interest} asks: '{followup}'. Answer directly and specifically."
    else:
        prompt = f"A student named {name} is interested in {interest} and feeling {feeling} about their future. Give specific friendly career guidance with exact next steps and salary ranges in Indian Rupees. Max 6 to 7 lines. Also use bold letters for important words."

    response = ask_ai(prompt)

    return jsonify({'response': response})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
