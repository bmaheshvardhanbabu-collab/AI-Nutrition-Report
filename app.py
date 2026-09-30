from flask import Flask, render_template, request
import requests
import json
import re
import os
from dotenv import load_dotenv

# ==============================
# LOAD ENVIRONMENT VARIABLES
# ==============================

load_dotenv()

app = Flask(__name__)

# ==============================
# API KEYS FROM .env
# ==============================

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

# ==============================
# API URLS
# ==============================

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
PEXELS_URL = "https://api.pexels.com/v1/search"

MODEL_NAME = "meta-llama/llama-3.1-8b-instruct"


# ==============================
# GENERATE NUTRITION REPORT
# ==============================

def generate_nutrition_report(food):

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:5000",
        "X-Title": "AI Nutrition Report"
    }

    prompt = f"""
You are an expert AI nutrition assistant.

Analyze this food or meal:

{food}

Return ONLY valid JSON.

Use exactly these keys:

food_name
calories
protein_grams
protein_percent
protein_info
carbohydrates_grams
carbohydrates_percent
carbohydrates_info
fats_grams
fats_percent
fats_info
fiber_grams
fiber_percent
fiber_info
vitamins
minerals
health_benefits
health_concerns
ai_health_insight
smarter_choice
health_score
health_score_label

Do not use markdown.
Do not use ```json.
Return only one JSON object.
"""

    data = {
        "model": MODEL_NAME,

        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a professional nutrition assistant. "
                    "Return valid JSON only."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],

        "temperature": 0.3,
        "max_tokens": 2000
    }

    try:

        response = requests.post(
            OPENROUTER_URL,
            headers=headers,
            json=data,
            timeout=120
        )

        response.raise_for_status()

        result = response.json()

        answer = result["choices"][0]["message"]["content"]

        # Remove markdown code blocks
        answer = re.sub(
            r"```json",
            "",
            answer,
            flags=re.IGNORECASE
        )

        answer = re.sub(
            r"```",
            "",
            answer
        )

        answer = answer.strip()

        # Find JSON object
        match = re.search(
            r"\{.*\}",
            answer,
            re.DOTALL
        )

        if match:
            answer = match.group(0)

        nutrition_data = json.loads(answer)

        return nutrition_data

    except json.JSONDecodeError:

        print("Invalid JSON returned by AI:")
        print(answer)

        return {
            "error": "AI returned invalid JSON. Please try again."
        }

    except Exception as e:

        print("API Error:", e)

        return {
            "error": str(e)
        }


# ==============================
# GET FOOD IMAGE
# ==============================

def get_food_image(food):

    headers = {
        "Authorization": PEXELS_API_KEY
    }

    params = {
        "query": food + " food",
        "per_page": 5,
        "orientation": "landscape"
    }

    try:

        response = requests.get(
            PEXELS_URL,
            headers=headers,
            params=params,
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

        photos = data.get(
            "photos",
            []
        )

        if not photos:
            return None

        photo = photos[0]

        return {
            "url": photo["src"]["large2x"],
            "photographer": photo["photographer"],
            "photographer_url": photo["photographer_url"],
            "pexels_url": photo["url"]
        }

    except Exception as e:

        print("Pexels Error:", e)

        return None


# ==============================
# ASK AI QUESTION
# ==============================

def ask_ai_question(food, question):

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:5000",
        "X-Title": "AI Nutrition Assistant"
    }

    prompt = f"""
Food:
{food}

Question:
{question}

Answer the question as a helpful nutrition assistant.

Only answer nutrition and food related questions.
If the question is unrelated to nutrition,
politely explain that you can only answer
nutrition-related questions.
"""

    data = {

        "model": MODEL_NAME,

        "messages": [

            {
                "role": "system",
                "content": "You are a helpful nutrition assistant."
            },

            {
                "role": "user",
                "content": prompt
            }

        ],

        "temperature": 0.5,

        "max_tokens": 800

    }

    try:

        response = requests.post(
            OPENROUTER_URL,
            headers=headers,
            json=data,
            timeout=120
        )

        response.raise_for_status()

        result = response.json()

        return result[
            "choices"
        ][0][
            "message"
        ][
            "content"
        ]

    except Exception as e:

        return f"Error: {str(e)}"


# ==============================
# HOME
# ==============================

@app.route(
    "/",
    methods=["GET", "POST"]
)
def home():

    food = ""
    nutrition = None
    food_image = None
    question = ""
    question_answer = ""
    error = ""

    if request.method == "POST":

        action = request.form.get(
            "action"
        )

        # ==========================
        # GENERATE REPORT
        # ==========================

        if action == "generate_report":

            food = request.form.get(
                "food",
                ""
            ).strip()

            if food:

                nutrition = generate_nutrition_report(
                    food
                )

                if (
                    nutrition
                    and
                    "error" in nutrition
                ):

                    error = nutrition[
                        "error"
                    ]

                    nutrition = None

                food_image = get_food_image(
                    food
                )

            else:

                error = (
                    "Please enter a food or meal."
                )

        # ==========================
        # ASK QUESTION
        # ==========================

        elif action == "ask_question":

            food = request.form.get(
                "food",
                ""
            ).strip()

            question = request.form.get(
                "question",
                ""
            ).strip()

            if food and question:

                question_answer = ask_ai_question(
                    food,
                    question
                )

                food_image = get_food_image(
                    food
                )

            else:

                error = (
                    "Please enter both food and question."
                )

    return render_template(
        "index.html",

        food=food,

        nutrition=nutrition,

        food_image=food_image,

        question=question,

        question_answer=question_answer,

        error=error
    )


# ==============================
# START FLASK
# ==============================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )