# OpenRouter AI Model Interaction Scripts

This repository contains two Python scripts for interacting with OpenRouter's AI models, featuring retry mechanisms and different interaction patterns.

## Prerequisites

- Python 3.6+
- OpenRouter API key (set as environment variable `OPENROUTER_API_KEY`)

## Installation

1. Clone the repository
2. Install required packages:
```bash
pip install -r requirements.txt
```

## Scripts Overview

### 1. openrouter_reasoning.py

A script that makes a single call to an AI model and retrieves both the response content and reasoning.

#### Features:
- Makes API calls to OpenRouter with retry mechanism
- Includes reasoning in model responses
- Saves responses to JSON file
- Handles rate limiting and resource exhaustion
- Colored console output for better readability

#### Usage:
```bash
export OPENROUTER_API_KEY="your-api-key"
python openrouter_reasoning.py
```

#### Configuration:
- `MODEL`: Primary model (default: "deepseek/deepseek-r1")
- `MODEL_2`: Secondary model (default: "google/gemini-2.0-flash-thinking-exp:free")
- `MAX_RETRIES`: Number of retry attempts (default: 3)
- `RETRY_DELAYS`: Delay in seconds between retries (default: [1, 3, 5])

### 2. dual_model_critique.py

A more complex script that implements an iterative critique system using multiple AI models.

#### Features:
- Multi-turn conversation with alternating models
- Initial response followed by multiple critique iterations
- Maintains conversation history
- Alternates between different critique models
- Saves each iteration to JSON
- Enhanced error handling and retry mechanism

#### Usage:
```bash
export OPENROUTER_API_KEY="your-api-key"
python dual_model_critique.py
```

#### Configuration:
- `MODEL_PRIMARY`: Initial response model (default: "deepseek/deepseek-r1")
- `MODEL_CRITIC_1`: First critique model (default: "deepseek/deepseek-r1")
- `MODEL_CRITIC_2`: Second critique model (default: "deepseek/deepseek-r1")
- `NUM_ITERATIONS`: Number of critique iterations (default: 3)
- `CRITIQUE_TYPE`: Type of critique requested (default: "critical review")
- `MAX_RETRIES`: Number of retry attempts (default: 5)
- `RETRY_DELAYS`: Delay in seconds between retries (default: [1, 3, 5, 7, 10])

#### Process Flow:
1. Initial Response (Iteration 1):
   - Gets response from PRIMARY_MODEL for user prompt
2. First Critique (Iteration 2):
   - MODEL_CRITIC_1 reviews initial response
3. Second Critique (Iteration 3):
   - MODEL_CRITIC_2 reviews both initial response and first critique
4. Additional iterations alternate between critic models

## Output Files

### openrouter_reasoning.py
- Outputs to: `model_responses.json`
- Format:
```json
[
  {
    "timestamp": "ISO-8601-timestamp",
    "reasoning": "model's reasoning",
    "content": "model's response"
  }
]
```

### dual_model_critique.py
- Outputs to: `iterative_critique_responses.json`
- Format:
```json
[
  {
    "iteration": 1,
    "timestamp": "ISO-8601-timestamp",
    "user_prompt": "original prompt",
    "conversation_history": [
      {
        "role": "user/assistant/critic",
        "content": "message content",
        "reasoning": "reasoning if available",
        "model": "model name",
        "critique_iteration": "iteration number (for critiques)"
      }
    ]
  }
]
```

## Notes

- Add ":online" to model names to enable web search capability
- The Gemini model may have rate limits; adjust retry settings accordingly
- All API calls include error handling and retry mechanisms
- Both scripts use colored console output for better visibility
- JSON files are encoded in UTF-8

## Error Handling

Both scripts implement robust error handling:
- Retries on rate limits (429 errors)
- Retries on resource exhaustion
- Handles API errors gracefully
- Provides detailed error messages
- Implements exponential backoff for retries

## Environment Variables

Required:
- `OPENROUTER_API_KEY`: Your OpenRouter API key 