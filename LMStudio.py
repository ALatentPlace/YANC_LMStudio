import requests
import re
import comfy.model_management as model_management
import lmstudio as lms
from torchvision.transforms.functional import to_pil_image
from io import BytesIO
from tempfile import NamedTemporaryFile
import torchvision.transforms as T


class YANCLMSTUDIO:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "prompt": ("STRING", {"forceInput": True}),
                "model_identifier": ("STRING", {"default": ""}),
                "draft_model": ("STRING", {"default": ""}),
                "system_message": ("STRING", {
                    "multiline": True,
                    "default": "You are an AI assistant specialized in generating detailed and creative image prompts for AI image generation. Your task is to expand a given user prompt into a well-structured, vivid, and highly descriptive prompt while ensuring that all terms from the original prompt are included. Enhance the visual quality and artistic impact by adding relevant details, but do not omit or alter any key elements provided by the user. Follow the given instructions or guidelines and respond only with the refined prompt."
                }),
                "reasoning_tag": ("STRING", {"default": "think"}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "ip": ("STRING", {"default": "localhost"}),
                "port": ("INT", {"default": 1234}),
                "temperature": ("FLOAT", {"default": 0.7, "min": 0.1, "max": 1.0}),
                "max_tokens": ("INT", {"default": 600, "min": -1, "max": 0xffffffffffffffff}),
                "unload_llm": ("BOOLEAN", {"default": False}),
                "unload_comfy_models": ("BOOLEAN", {"default": False})
            },
            "optional":
                {
                    "image": ("IMAGE", {"forceInput": True})
            },
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("Extended Prompt", "Reasoning")

    OUTPUT_NODE = False

    FUNCTION = "do_it"

    CATEGORY = "YANC/😼 LMStudio"

    def do_it(self, prompt, model_identifier, draft_model, system_message, reasoning_tag, seed, ip, port, temperature, max_tokens, unload_llm, unload_comfy_models, image=None):

        if unload_comfy_models:
            model_management.unload_all_models()
            model_management.soft_empty_cache(True)

        server_api_host = f"{ip}:{port}"

        result = ""
        reasoning = ""

        with lms.Client(server_api_host) as client:

            model = client.llm.model(model_identifier)

            if image is None:
                try:
                    chat = lms.Chat(system_message)
                    chat.add_user_message(prompt)

                    content = str(model.respond(chat, config={
                        "temperature": temperature,
                        "maxTokens": max_tokens,
                        "draftModel": draft_model
                    }))
                except:
                    print(
                        "Prediction error: Trying alternative approach to prevent prediction error based on wrong template type.")
                    chat = lms.Chat()
                    chat.add_user_message(
                        f"{system_message}: User input: {prompt}")

                    content = str(model.respond(chat, config={
                        "temperature": temperature,
                        "maxTokens": max_tokens,
                        "draftModel": draft_model
                    }))

                # Separate the reasoning block.
                result = re.sub(rf"<{reasoning_tag}>.*?</{reasoning_tag}>", "",
                                content, flags=re.DOTALL).strip()
                reasoning = re.sub(
                    rf".*<{reasoning_tag}>(.*?)</{reasoning_tag}>.*", r"\1", content, flags=re.DOTALL).strip()
            else:
                info = model.get_info()
                if not info.vision:
                    if unload_llm:
                        model.unload()

                    raise Exception(
                        "The loaded model is not vision enabled. Please try another model.")

                image_new = image.squeeze(0).permute(2, 0, 1)
                image_pil = to_pil_image(image_new)

                with NamedTemporaryFile(suffix=".jpg", delete=False) as temp:
                    image_pil.save(temp, format="JPEG")
                    temp.flush()
                    image_handle = client.files.prepare_image(temp.name)

                chat = lms.Chat()
                chat.add_user_message(
                    prompt, images=[image_handle])
                result = model.respond(chat)
                reasoning = result

            if unload_llm:
                model.unload()

        return (result, reasoning,)


NODE_CLASS_MAPPINGS = {
    "> LMStudio": YANCLMSTUDIO,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "> LMStudio": "😼> LMStudio",
}
