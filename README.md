INSCRIBE Web App

This is an interactive quiz game built using Flask as the web framework and Groq API for generating quiz questions, answers, and providing grammar and spelling corrections. The app allows users to generate quizzes, answer questions, and improve their responses with feedback and error corrections. Additionally, the game includes a scoring and difficulty system that adjusts based on the user's performance.
Features

    Dynamic Quiz Generation: The app generates quiz questions based on the topic the user inputs, using the Groq API.
    Cosine Similarity for Answer Checking: User answers are compared against the correct answer using cosine similarity to measure knowledge.
    Grammar and Spelling Check: The app provides grammar and spelling error feedback for user answers using Groq API.
    Scoring System: Tracks the user’s score and dynamically adjusts the difficulty level based on the correctness of their answers.
    Interactive Feedback: Offers immediate feedback on answers and provides error corrections.

Technologies Used

    Flask: The web framework used to handle routing and backend logic.
    HTML/CSS/JavaScript (jQuery): Frontend for the user interface and interaction.
    Groq API: Generates quiz questions, checks grammar, and corrects spelling.
    Cosine Similarity: Used to compare the similarity between user input and the correct answer.
    scikit-learn: Provides the cosine similarity function.

Prerequisites

Before you begin, ensure you have met the following requirements:

    Python: Ensure that Python 3.x is installed on your machine.
    Flask: You can install Flask using the command pip install Flask.
    scikit-learn: Install scikit-learn for cosine similarity calculations using pip install scikit-learn.
    Groq API: You'll need an API key for Groq and their SDK. Ensure it is installed using pip install groq.

Installation

    Clone the repository:

    bash

git clone https://github.com/ALWIN72/INSCRIBE_APP.git


Install the required dependencies:

bash

pip install -r requirements.txt

Ensure requirements.txt contains:

Flask
scikit-learn
groq

Set up the Groq API:

    Ensure you have your Groq API credentials set up correctly.
    Set the credentials in your environment or modify the groq client initialization.

Run the app:

bash

    python app.py

    Access the app: Open your web browser and navigate to http://127.0.0.1:5000/.

Usage

    Generating a Quiz:
        On the main page, enter a topic for the quiz and click "Generate Quiz."
        The app will generate a quiz question based on the topic you entered.

    Answering the Quiz:
        Type your answer in the provided text area and click "Submit Answer."
        The app will check your answer, give you feedback on your knowledge percentage, and highlight any grammar or spelling errors.

    Correcting Errors:
        If the app detects any grammar or spelling errors, click "Correct Errors" to view the corrected answer.

    Score and Difficulty Level:
        Your score and difficulty level will be displayed on the page.
        As you progress, the difficulty level will increase with each correct answer.

    Quit the Game:
        Click "Quit Game" to reset the game and return to the home page.

File Structure

bash

├── templates/
│   ├── index.html        # Main game page
│   └── game_over.html    # Page displayed after quitting the game              
├── app.py                # Flask backend logic
└── README.md             # Documentation

API Routes

    GET /: Renders the main quiz game page.
    POST /generate_quiz: Generates a new quiz based on user input (topic).
    POST /check_answer: Compares the user's answer to the correct answer using cosine similarity.
    POST /correct_errors: Corrects grammar and spelling errors in the user's answer.
    POST /quit_game: Resets the game state and ends the session.

Future Improvements

    User Authentication: Add user login/logout functionality and keep track of individual progress.
    Leaderboard: Implement a leaderboard to show the top scores among users.
    Time Limit: Add a time limit for each question to increase difficulty.
    Better Error Handling: Improve error messages and handling of external API errors.

