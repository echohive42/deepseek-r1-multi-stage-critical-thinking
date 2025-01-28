# Multi stage critical thinking with reasoning models

This repository contains two Python scripts for interacting with OpenRouter's AI models, featuring retry mechanisms and different interaction patterns.

## Prerequisites

- OpenRouter API key (set as environment variable `OPENROUTER_API_KEY`)

dual_model_critique.py

script that implements an iterative critique system using multiple AI models.

#### Features:
- Multi-turn conversation with alternating models
- Initial response followed by multiple critique iterations
- Maintains conversation history
- Alternates between different critique models
- Saves each iteration to JSON
- Enhanced error handling and retry mechanism

## 🎥 Watch How It's Built!

**[Watch the complete build process on Patreon]([[https://www.patreon.com/posts/how-to-build-o1-112197565](https://www.patreon.com/posts/multi-stage-with-120989270)])**
See exactly how this automation system was created step by step, with detailed explanations and insights into the development process.


## ❤️Join my AI community & Get 400+ AI Projects

This is one of 400+ fascinating projects in my collection! [Support me on Patreon](https://www.patreon.com/c/echohive42/membership) to get:

- 🎯 Access to 400+ AI projects (and growing daily!)
  - Including advanced projects like [2 Agent Real-time voice template with turn taking](https://www.patreon.com/posts/2-agent-real-you-118330397)
- 📥 Full source code & detailed explanations
- 📚 1000x Cursor Course
- 🎓 Live coding sessions & AMAs
- 💬 1-on-1 consultations (higher tiers)
- 🎁 Exclusive discounts on AI tools & platforms (up to $180 value)


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
