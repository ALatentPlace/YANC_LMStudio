# YANC_LMStudio

A custom node for a LMStudio integration into ComfyUI.

## Features

- Prompts can be sent to LMStudio via HTTP API endpoint.
- Handles 400 errors during API requests, attempting alternative approaches if needed.
- Supports system messages for structured prompting.
- Allows configuration of model identifiers and parameters like temperature and max_tokens.
- Includes optional model unloading in LMStudio and ComfyUI after usage.

## Installation

To install the required dependencies browse to your custom_nodes folder inside of ComfyUI, open a command line and clone this repository:
```bash
git clone https://github.com/ALatentPlace/YANC_LMStudio.git
```
I will try to get it also to the ComfyUI Manager as soon as possible.

## Usage

The node will put itself in the folders of my other node collection (YANC). You will then find it in the subfolder "LMStudio".

## Configuration Options

- `prompt`: The input prompt to be sent to the AI model inside of LMStudio.
- `model_identifier`: Identifier for the specific model used. Can be found in LMStudio.
- `system_message`: A multi-line system prompt that sets instructions to the LLM.
- `seed`: Random seed (0 by default). Set it to fixed to prevent generations.
- `ip`: Hostname or IP address of the LMStudio service.
- `port`: Port number to connect to.
- `temperature`: Controls randomness in output, between 0.1 and 1.0.
- `max_tokens`: Maximum length of the generated response.

## Model Handling

- `unload_llm`: Boolean flag to unload the LLM after use (default: False).
- `unload_comfy_models`: Boolean flag to unload COMFY models before sending a request to LMStudio (default: False).

## Error Handling

- Status code 400 errors are caught and handled with alternative approaches when possible. This is to prevent prediction errors in LMStudio, which are usually caused by the system message.
- Automatic removal of the \<think> block of Deepseek.