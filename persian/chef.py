import os
from enum import Enum

from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)

base_prompt = [{
    "role": "system",
    "content": "You are an traditional chef in Iran that helps people by suggesting detailed recipes for dishes "
               "they want to cook. You can also provide tips and tricks for cooking and food preparation. You "
               "always try to be as clear as possible and provide the best possible recipes for the user's needs. "
               "You know a lot about different cuisines and cooking techniques. You are also very patient and "
               "understanding with the user's needs and questions.",
}]

model = "gpt-4o-mini"


class RecipeCategory(Enum):
    INGREDIENT_BASED_SUGGESTIONS = 1
    RECIPE_REQUESTS = 2
    RECIPE_CRITIQUES = 3


def add_guide_message(messages, category):
    if category == RecipeCategory.INGREDIENT_BASED_SUGGESTIONS.value:
        messages.append(
            {
                "role": "system",
                "content": "Your client will provide a list of ingredients they have available. You should suggest a "
                           "dish that can be prepared using only those ingredients. Do not include dishes that require "
                           "ingredients not listed by the client. If you can think of multiple dishes that fit the "
                           "criteria, suggest the most popular or easiest one to prepare. If no suitable dish comes to "
                           "mind with the given ingredients, you should politely indicate that you can't think of a "
                           "dish and offer to help with different ingredients."
            }
        )
    elif category == RecipeCategory.RECIPE_REQUESTS.value:
        messages.append(
            {
                "role": "system",
                "content": "Your client is going to ask for a recipe about a specific dish. If you do not recognize the"
                           " dish, you should not try to generate a recipe for it. Do not answer a recipe if you do not"
                           " understand the name of the dish. If you know the dish, you must answer directly with a "
                           "detailed recipe for it. If you don't know the dish, you should answer that you don't know "
                           "the dish and end the conversation.",
            }
        )
    elif category == RecipeCategory.RECIPE_CRITIQUES.value:
        messages.append(
            {
                "role": "system",
                "content": "Your client will present you with a recipe they have prepared or found. Your task is to "
                           "provide constructive feedback and suggest improvements to the recipe. Focus on enhancing "
                           "flavor, texture, and presentation while considering common dietary preferences and "
                           "restrictions. Be respectful and encouraging in your critiques, offering specific and "
                           "actionable suggestions for improving the dish. If the recipe is already excellent, provide "
                           "positive reinforcement and suggest optional tweaks to enhance it further."
            }
        )

    return messages


def stream_response(openai_client, openai_model, conv_messages):
    stream = openai_client.chat.completions.create(
        model=openai_model,
        messages=conv_messages,
        stream=True,
    )

    collected_messages = []
    for chunk in stream:
        chunk_message = chunk.choices[0].delta.content or ""
        print(chunk_message, end="")
        collected_messages.append(chunk_message)

    conv_messages.append({"role": "system", "content": "".join(collected_messages)})

    return conv_messages


def category_is_valid(category):
    try:
        _ = int(category)
        return True
    except ValueError:
        return False


def process(category, openai_client, openai_model, conv_messages):
    conv_messages = add_guide_message(conv_messages, category)

    if category == RecipeCategory.INGREDIENT_BASED_SUGGESTIONS.value:
        ingredients = input("Type the name of ingredients you want to cook food with those splits by dash(-):\n")
        conv_messages.append(
            {
                "role": "user",
                "content": f"Suggest me only a name of the dish that can make with {ingredients} ingredients without "
                           f"full recipes",
            }
        )
    elif category == RecipeCategory.RECIPE_REQUESTS.value:
        print("ali is here")
        dish = input("Type the name of the dish you want a recipe for:\n")
        conv_messages.append(
            {
                "role": "user",
                "content": f"Suggest me a detailed recipe and the preparation steps for making {dish}",
            }
        )
    elif category == RecipeCategory.RECIPE_CRITIQUES.value:
        recipe = input("Type the full recipe of the dish you want to improve:\n")
        conv_messages.append(
            {
                "role": "user",
                "content": f"Suggest a constructive critique with improvements for making the following recipe:\n"
                           f"{recipe}",
            }
        )

    stream_response(openai_client, openai_model, conv_messages)

    return


while True:

    user_input = ""
    while not category_is_valid(user_input):
        user_input = input("Hi, I'm a experienced persian chef, I can help you in the following tasks:\n"
                           "1.Ingredient-based dish suggestions\n"
                           "2.Recipe requests for specific dishes\n"
                           "3.Recipe critiques and improvement suggestions\n"
                           "Please enter the suitable number for getting any helps:\n")

    process(int(user_input), client, model, base_prompt)

    _ = input("\nType something to continue ...")
