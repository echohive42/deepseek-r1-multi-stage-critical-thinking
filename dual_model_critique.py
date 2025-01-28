import requests
import json
import os
from termcolor import colored
from datetime import datetime
import time

# you can put ":online" at the end of the model name to use automatic web search for that model
# gemini flash thinking may run into rate limits often!!
# you can use google/gemini-2.0-flash-thinking-exp:free as well for any models

# CONSTANTS
API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL_PRIMARY = "deepseek/deepseek-r1" # First model to get initial response
MODEL_CRITIC_1 = "deepseek/deepseek-r1" # First critique model
MODEL_CRITIC_2 = "deepseek/deepseek-r1" # Second critique model (example, you can change this)
OUTPUT_FILE = "iterative_critique_responses.json" # Changed output file name to reflect critique iterations
CRITIQUE_TYPE = "critical review" # Type of critique we want
NUM_ITERATIONS = 3 # Number of critique iterations (primary model is called once initially)
USER_PROMPT = "what is 2 +2?" # Example user prompt
MAX_RETRIES = 5
RETRY_DELAYS = [1, 3, 5, 7, 10]  # seconds


# Headers setup for OpenRouter API
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "HTTP-Referer": "http://localhost:8000",
    "Content-Type": "application/json"
}

def make_api_request(messages, model_name, include_reasoning=True):
    """
    Makes a request to the OpenRouter API. Now takes a list of messages and implements retry logic.

    Args:
        messages (list): List of message dictionaries for the conversation history.
        model_name (str): The name of the model to use.
        include_reasoning (bool): Whether to include reasoning in the response.

    Returns:
        dict: The JSON response from the API, or None if there was an error.
    """
    for attempt in range(MAX_RETRIES):
        try:
            print(colored(f"Making API request to OpenRouter with model: {model_name}... (attempt {attempt + 1})", "cyan"))

            payload = {
                "model": model_name,
                "messages": messages,
                "include_reasoning": include_reasoning
            }

            response = requests.post(
                BASE_URL,
                headers=HEADERS,
                json=payload
            )
            
            response_data = response.json()
            
            # Check for error in response
            if 'error' in response_data:
                error = response_data['error']
                if error.get('code') == 429 or (
                    isinstance(error.get('metadata', {}), dict) and 
                    'RESOURCE_EXHAUSTED' in str(error['metadata'].get('raw', ''))
                ):
                    print(colored(f"Rate limit/Resource exhausted error. Retrying in {RETRY_DELAYS[attempt]} seconds...", "yellow"))
                    time.sleep(RETRY_DELAYS[attempt])
                    continue
                else:
                    print(colored(f"API Error: {error}", "red"))
                    if attempt < MAX_RETRIES - 1:
                        print(colored(f"Retrying in {RETRY_DELAYS[attempt]} seconds...", "yellow"))
                        time.sleep(RETRY_DELAYS[attempt])
                        continue
                    return None

            # If we got here, check for valid response format
            if 'choices' not in response_data:
                print(colored(f"Unexpected response format: {response_data}", "red"))
                if attempt < MAX_RETRIES - 1:
                    print(colored(f"Retrying in {RETRY_DELAYS[attempt]} seconds...", "yellow"))
                    time.sleep(RETRY_DELAYS[attempt])
                    continue
                return None

            return response_data

        except requests.exceptions.RequestException as e:
            print(colored(f"Request error: {str(e)}", "red"))
            if attempt < MAX_RETRIES - 1:
                print(colored(f"Retrying in {RETRY_DELAYS[attempt]} seconds...", "yellow"))
                time.sleep(RETRY_DELAYS[attempt])
            else:
                return None
        except Exception as e:
            print(colored(f"Unexpected error: {str(e)}", "red"))
            if attempt < MAX_RETRIES - 1:
                print(colored(f"Retrying in {RETRY_DELAYS[attempt]} seconds...", "yellow"))
                time.sleep(RETRY_DELAYS[attempt])
            else:
                return None

    print(colored("Max retries reached. API request failed.", "red"))
    return None


def save_to_json(data_entry):
    """Saves data entry to JSON, now appends to a list in the file."""
    try:
        print(colored("Saving response to JSON file...", "yellow"))
        if os.path.exists(OUTPUT_FILE):
            with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
                file_data = json.load(f)
        else:
            file_data = []
        file_data.append(data_entry)
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(file_data, f, indent=2, ensure_ascii=False)
        print(colored("Response saved successfully!", "green"))
    except Exception as e:
        print(colored(f"Error saving to JSON: {str(e)}", "red"))
        print(colored(f"Error details: {e}", "red"))


def get_critique_prompt(conversation_history, critique_type):
    """
    Generates a prompt for the critique model, now based on conversation history.

    Args:
        conversation_history (list): List of messages in the conversation so far.
        critique_type (str): The type of critique to request.

    Returns:
        str: The prompt for the critique model.
    """
    history_text = ""
    for message in conversation_history:
        role = message['role'].capitalize()
        content = message['content']
        if 'reasoning' in message and message['reasoning']:
            reasoning = message['reasoning']
            history_text += f"{role}:\nContent: {content}\nReasoning: {reasoning}\n\n"
        else:
            history_text += f"{role}: {content}\n\n"


    return f"""
You are acting as a {critique_type} AI, reviewing a conversation between a User and an AI assistant.
Your task is to provide a {critique_type} of the AI assistant's responses and reasonings in the context of the conversation so far.

--- Conversation History ---
{history_text}
--- End of Conversation History ---

Provide your {critique_type} of the AI assistant's turns in the conversation above. Focus on the last AI assistant response and reasoning, but consider the entire conversation for context.

Your {critique_type}:
"""


def main():
    try:
        if not API_KEY:
            raise ValueError("OPENROUTER_API_KEY environment variable is not set.")

        conversation_history = [] # Initialize conversation history
        print(colored(f"\n--- Starting Analysis of Prompt: {USER_PROMPT} ---", "blue"))

        # Initial user message
        conversation_history.append({"role": "user", "content": USER_PROMPT})

        # --- Get Initial Primary Model Response (Iteration 1) ---
        print(colored("\n--- Iteration 1: Getting Primary Model Response ---", "cyan"))
        primary_response_data = make_api_request([{"role": "user", "content": USER_PROMPT}], MODEL_PRIMARY)

        if not primary_response_data:
            print(colored("Failed to get initial response from primary model.", "red"))
            return

        # Process and save primary model response
        primary_message = primary_response_data['choices'][0]['message']
        primary_content = primary_message.get('content', '')
        primary_reasoning = primary_message.get('reasoning', '')

        print(colored("\nPrimary Model Response (Content):", "green"))
        print(primary_content)
        print(colored("Primary Model Response (Reasoning):", "green"))
        print(primary_reasoning)

        # Add primary model response to conversation history
        conversation_history.append({
            "role": "assistant",
            "content": primary_content,
            "reasoning": primary_reasoning,
            "model": MODEL_PRIMARY
        })

        # Save first iteration
        save_to_json({
            "iteration": 1,
            "timestamp": datetime.now().isoformat(),
            "user_prompt": USER_PROMPT,
            "conversation_history": list(conversation_history),
        })

        # --- Subsequent Critique Iterations ---
        for i in range(2, NUM_ITERATIONS + 1):  # Start from 2 since iteration 1 was the primary response
            print(colored(f"\n--- Iteration {i}: Getting Critique ---", "magenta"))
            
            # Alternate between critique models
            critique_model_name = MODEL_CRITIC_1 if i % 2 == 0 else MODEL_CRITIC_2
            print(colored(f"Using Model: {critique_model_name}", "yellow"))

            # Generate critique prompt based on all previous responses
            critique_prompt = get_critique_prompt(conversation_history, CRITIQUE_TYPE)
            print(colored("\nCritique Prompt:", "blue"))
            print(critique_prompt)

            # Make critique request
            critique_response_data = make_api_request(
                [{"role": "user", "content": critique_prompt}],
                critique_model_name
            )

            if not critique_response_data:
                print(colored(f"Failed to get critique in iteration {i}.", "red"))
                continue

            # Process critique response
            critique_message = critique_response_data['choices'][0]['message']
            critique_content = critique_message.get('content', '')
            critique_reasoning = critique_message.get('reasoning', '')

            print(colored(f"\nCritique Response (Content):", "yellow"))
            print(critique_content)
            print(colored("Critique Response (Reasoning):", "yellow"))
            print(critique_reasoning)

            # Add critique to conversation history
            conversation_history.append({
                "role": "critic",
                "content": critique_content,
                "reasoning": critique_reasoning,
                "model": critique_model_name,
                "critique_iteration": i
            })

            # Save this iteration
            save_to_json({
                "iteration": i,
                "timestamp": datetime.now().isoformat(),
                "user_prompt": USER_PROMPT,
                "conversation_history": list(conversation_history),
            })

    except ValueError as ve:
        print(colored(f"ValueError: {ve}", "red"))
    except Exception as e:
        print(colored(f"An unexpected error occurred: {str(e)}", "red"))
        print(colored(f"Error details: {e}", "red"))


if __name__ == "__main__":
    main() 