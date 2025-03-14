import requests
import subprocess
import re
import comfy.model_management as model_management


class YANCLMSTUDIO:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "prompt": ("STRING", {"forceInput": True}),
                "model_identifier": ("STRING", {"default": ""}),
                "system_message": ("STRING", {
                    "multiline": True,
                    "default": "You are an AI assistant specialized in generating detailed and creative image prompts for AI image generation. Your task is to expand a given user prompt into a well-structured, vivid, and highly descriptive prompt while ensuring that all terms from the original prompt are included. Enhance the visual quality and artistic impact by adding relevant details, but do not omit or alter any key elements provided by the user. Follow the given instructions or guidelines and respond only with the refined prompt."
                }),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "ip": ("STRING", {"default": "localhost"}),
                "port": ("INT", {"default": 1234}),
                "temperature": ("FLOAT", {"default": 0.7, "min": 0.1, "max": 1.0}),
                "max_tokens": ("INT", {"default": 600, "min": -1, "max": 0xffffffffffffffff}),
                "unload_llm": ("BOOLEAN", {"default": False}),
                "unload_comfy_models": ("BOOLEAN", {"default": False}),

            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("Extended Prompt",)

    OUTPUT_NODE = False

    FUNCTION = "do_it"

    CATEGORY = "YANC/😼 LMStudio"

    def format_url(self, ip, port):
        return f"http://{ip}:{port}/v1/chat/completions"

    def make_request(self, url, model_identifier, messages, temperature, max_tokens, last_try=False):
        headers = {"Content-Type": "application/json"}

        data = {
            "model": model_identifier,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }

        response = requests.post(url=url, headers=headers, json=data)

        if response.status_code == 400 and not last_try:
            print("Received status code 400. Trying alternative approach to prevent prediction error based on wrong template type.")
            altered_messages = [
                msg for msg in messages if msg["role"] != "system"]
            response = self.make_request(
                url, model_identifier, altered_messages, temperature, max_tokens, last_try=True)

        return response

    def do_it(self, prompt, model_identifier, system_message, seed, ip, port, temperature, max_tokens, unload_llm, unload_comfy_models):

        url = self.format_url(ip, port)

        if unload_comfy_models:
            model_management.unload_all_models()
            model_management.soft_empty_cache(True)

        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ]

        response = self.make_request(
            url, model_identifier, messages, temperature, max_tokens)

        if response.status_code == 200:
            result = response.json()["choices"][0]["message"]["content"]

            # Removing the Deepseek <think> block.
            result = re.sub(r"<think>.*?</think>", "",
                            result, flags=re.DOTALL).strip()
        else:
            raise Exception(f"Failed to get response: {response.status_code}")

        if unload_llm:
            subprocess.run(['lms', 'unload', '--all'],
                           capture_output=True,
                           text=True,
                           check=True)

        return (result,)


NODE_CLASS_MAPPINGS = {
    "> LMStudio": YANCLMSTUDIO,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "> LMStudio": "😼> LMStudio",
}
