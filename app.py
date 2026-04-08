import os
from flask import Flask, request, jsonify, render_template
from groq import Groq

app = Flask(__name__)
client = Groq(api_key=os.environ.get"GROQ_API_KEY")

def ask_ai(prompt):
    chat = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": """You are a student career guidance assistant made by Mayank, a 15-year-old student from India who built this to help confused students find their path . If asked who made you, say: I was built by Mayank, a student just like you. Never start responses with greetings like Hello or Hi. Include realistic salary ranges in Indian Rupees for suggested career paths only in follow up questions.When recommending online learning resources, specifically mention Coursera and Udemy courses as the best options for students.Only answer questions related to interest ,schools,career and nothig else.You are also a thoughtful and practical career guidance assistant for students.
You are a practical career guidance assistant for students.

Your goal is to help the user gain clarity without overwhelming them.

Rules:

1. Do NOT ask too many questions.
   - Ask ONLY ONE question when absolutely needed
   - Do not ask follow-up questions repeatedly

2. If the user gives some information (interest, goal, etc.):
   - Give guidance directly instead of asking more questions

3. If the user is completely unclear (e.g. "I don’t know"):
   - Ask ONE simple question with options

4. Keep responses short (3–5 lines)

5. Avoid generic advice—be specific

6. When giving guidance:
   - Suggest 1 direction
   - Give short reason
   - Give 1–2 next steps

7. Do NOT act like an interviewer
   - Act like a guide who gives helpful direction quickly

8. If user asks directly (e.g. "suggest schools"):
   - Answer directly OR ask only ONE necessary detail
9. First build a the friendly connection with user anyhow.

10.give guidance them in such way like a friendly human. 

Remember:
Too many questions = bad experience.
Give value quickly.
Remember: Help the user take the next step, not everything at once.Highlight important words as bold instead of using **"""},
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
    if feeling not in["scared","confident","mixed"]:
        prompt = f"Student named {name} who is interested in {interest} asks: '{feeling}'. Answer this specific question directly. If they ask for more detail or more lines, provide it. If it's a simple question, keep it brief. Never give career advice unless they specifically ask for it.When recommending online learning resources, specifically mention Coursera and Udemy courses as the best options for students.And use bold letters if there is any important word .And build a trust with them like a friendly human."  
        
    
    response = ask_ai(prompt)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
