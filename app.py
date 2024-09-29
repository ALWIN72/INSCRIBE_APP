import os
from flask import Flask, render_template, request, jsonify
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import groq

# Initialize Flask app
app = Flask(__name__)

# Initialize the Groq API client
client = groq.Groq()

# Global variables to hold game state
current_question = None
correct_answer = None
difficulty_level = 1
score = 0

# Home route (renders the main game page)
@app.route('/')
def home():
    return render_template('index.html', score=score, difficulty_level=difficulty_level)

# Route to generate a new quiz using Groq API
@app.route('/generate_quiz', methods=['POST'])
def generate_quiz():
    global current_question, correct_answer, difficulty_level

    # Get the topic entered by the user
    user_topic = request.form.get('topic')

    try:
        # Generate a topic and question using Groq API
        difficulty_descriptions = {1: "easy", 2: "medium", 3: "hard"}
        difficulty_description = difficulty_descriptions.get(difficulty_level, "easy")

        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {
                    "role": "user",
                    "content": f"Generate a {difficulty_description} topic and a question for short essay about: {user_topic}"
                }
            ],
            temperature=1,
            max_tokens=1024,
            top_p=1,
            stream=False,
        )

        response_text = response.choices[0].message.content.strip()
        if "Topic:" in response_text and "Question:" in response_text:
            topic = response_text.split("Topic:")[1].split("\n")[0].strip()
            current_question = response_text.split("Question:")[1].split("\n")[0].strip()

            # Generate the correct answer
            correct_answer = generate_correct_answer(topic)

        return jsonify({
            "question": current_question,
            "difficulty_level": difficulty_level
        })

    except Exception as e:
        return jsonify({"error": f"Error generating quiz: {str(e)}"})


# Helper function to generate the correct answer using Groq API
def generate_correct_answer(topic):
    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {
                    "role": "user",
                    "content": f"Provide a short essay about: {topic}"
                }
            ],
            temperature=0.7,
            max_tokens=150,
            top_p=1,
            stream=False,
        )
        response_text = response.choices[0].message.content.strip()
        if response_text:
            return response_text
        return "No correct answer could be generated."

    except Exception as e:
        return f"Error generating correct answer: {str(e)}"


# Route to check the user's answer using Cosine Similarity
@app.route('/check_answer', methods=['POST'])
def check_answer():
    global score, difficulty_level, current_question, correct_answer

    # Get the user's answer from the form
    user_answer = request.form.get('answer')

    # Check similarity between the user's answer and the correct answer
    similarity_score = cosine_similarity_check(correct_answer, user_answer)
    knowledge_percentage = similarity_score * 100

    # Define similarity score thresholds for each level
    level_thresholds = {
        1: 30,  # 30% for level 1
        2: 50,  # 50% for level 2
        3: 70   # 70% for level 3
    }
    current_threshold = level_thresholds.get(difficulty_level, 30)  # Default to 30% if level is unknown

    # Check grammar and spelling
    grammar_errors = grammar_check(user_answer)
    spelling_errors = spelling_check(user_answer)

    if knowledge_percentage >= current_threshold:  # User passed this level
        score += 1
        difficulty_level = min(difficulty_level + 1, 3)  # Increase difficulty but limit to max 3
        response_message = "Correct! You've advanced to the next level.>please press generate quiz for continuing"

        # Automatically generate a new question for the next level
        try:
            difficulty_descriptions = {1: "easy", 2: "medium", 3: "hard"}
            difficulty_description = difficulty_descriptions.get(difficulty_level, "easy")

            response = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[
                    {
                        "role": "user",
                        "content": f"Generate a {difficulty_description} topic and a question for a short essay about: {user_answer}"
                    }
                ],
                temperature=1,
                max_tokens=1024,
                top_p=1,
                stream=False,
            )

            response_text = response.choices[0].message.content.strip()
            if "Topic:" in response_text and "Question:" in response_text:
                topic = response_text.split("Topic:")[1].split("\n")[0].strip()
                current_question = response_text.split("Question:")[1].split("\n")[0].strip()

                # Generate the correct answer
                correct_answer = generate_correct_answer(topic)

            new_question = {
                "question": current_question,
                "difficulty_level": difficulty_level
            }

        except Exception as e:
            new_question = {"error": f"Error generating new question: {str(e)}"}
    
    else:
        response_message = f"Incorrect. You need at least {current_threshold}% accuracy to the question to pass this level."
        new_question = {}

    # Check if errors exist
    has_errors = grammar_errors or spelling_errors

    return jsonify({
        "knowledge_percentage": knowledge_percentage,
        "response_message": response_message,
        "grammar_errors": grammar_errors,
        "spelling_errors": spelling_errors,
        "score": score,
        "difficulty_level": difficulty_level,
        "has_errors": has_errors,
        "new_question": new_question
    })


# Route to correct the errors
@app.route('/correct_errors', methods=['POST'])
def correct_errors():
    user_answer = request.form.get('answer')

    # Correct grammar and spelling errors
    corrected_answer = correct_answer_grammar_and_spelling(user_answer)

    return jsonify({
        "corrected_answer": corrected_answer
    })


# Function to compute cosine similarity between the correct answer and user answer
def cosine_similarity_check(correct_answer, user_answer):
    vectorizer = CountVectorizer().fit_transform([correct_answer, user_answer])
    vectors = vectorizer.toarray()
    cosine_sim = cosine_similarity(vectors)
    return cosine_sim[0][1]


# Grammar check using Groq API
def grammar_check(text):
    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {
                    "role": "user",
                    "content": f"Check grammar errors in: {text}"
                }
            ],
            temperature=1,
            max_tokens=1024,
            top_p=1,
            stream=False,
        )

        response_text = response.choices[0].message.content.strip()
        errors = []
        if "Error" in response_text or "error" in response_text.lower():
            error_messages = response_text.split("\n")
            for error in error_messages:
                if "Error" in error or "error" in error.lower():
                    errors.append(error.strip())

        return errors

    except Exception as e:
        return [f"Error checking grammar: {str(e)}"]


# Spelling check using Groq API
def spelling_check(text):
    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {
                    "role": "user",
                    "content": f"Check spelling errors in: {text}"
                }
            ],
            temperature=1,
            max_tokens=1024,
            top_p=1,
            stream=False,
        )

        response_text = response.choices[0].message.content.strip()
        errors = []
        if "Error" in response_text or "error" in response_text.lower():
            error_messages = response_text.split("\n")
            for error in error_messages:
                if "Error" in error or "error" in error.lower():
                    errors.append(error.strip())

        return errors

    except Exception as e:
        return [f"Error checking spelling: {str(e)}"]


# Correct grammar and spelling errors using Groq API
def correct_answer_grammar_and_spelling(text):
    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {
                    "role": "user",
                    "content": f"Correct grammar and spelling errors in: {text}"
                }
            ],
            temperature=1,
            max_tokens=1024,
            top_p=1,
            stream=False,
        )

        corrected_text = response.choices[0].message.content.strip()
        return corrected_text

    except Exception as e:
        return f"Error correcting text: {str(e)}"

# Route to handle quitting the game
@app.route('/quit_game', methods=['POST'])
def quit_game():
    global score, difficulty_level, current_question, correct_answer

    # Reset game state
    score = 0
    difficulty_level = 1
    current_question = None
    correct_answer = None

    return render_template('game_over.html')

if __name__ == "__main__":
    app.run(debug=True)
