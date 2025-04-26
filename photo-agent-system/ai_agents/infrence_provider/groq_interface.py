import os
import json
from groq import Groq
from typing import Any, Dict, Optional
from infrence_provider.infrence_provider import InferenceProvider

config_path = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '../'))


class GroqInterface(InferenceProvider):
    """
    Concrete implementation for the Groq inference provider.
    """

    def __init__(self, config: Dict[str, Any]):

        # We rely on the docker-compose config to provide the API key as a secret.
        # The secret is mounted at /run/secrets/GROQ_API_KEY in the container.
        try:
            with open("/run/secrets/GROQ_API_KEY", "r") as f:
                self.api_key: Optional[str] = f.read().strip()
                print("API key found in /run/secrets")
        except FileNotFoundError:
            print("API key secret not found in /run/secrets")
            try:
                with open("/etc/secrets/GROQ_API_KEY", "r") as f:
                    self.api_key: Optional[str] = f.read().strip()
                    print("API key found in /etc/secrets")
            except FileNotFoundError:
                print("API key secret not found in /etc/secrets")

        if not self.api_key:
            raise ValueError(
                "Groq API key is required. Provide it in docker-compose config as a secret called GROQ_API_KEY")

        self.model: str = config.get('model', 'llama3-8b-8192')

        print(f"Initializing GroqInterface with model: {self.model}")
        self.client = Groq(api_key=self.api_key)

    def infer(self, prompt: str, image: str = None, format: str = None, temperature: float = 1.0) -> str:
        content = []
        prettyFormat = json.dumps(format, indent=2)
        # Only add text content if prompt is provided.
        if prompt:
            text = prompt
            if format:
                text += f" The return object must use this JSON schema: {prettyFormat}."
            content.append({
                "type": "text",
                "text": text
            })
            print(f"Text added to groq request")

        # Only add image content if image is provided.
        if image:
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"{self.ensure_base64_str(image)}"
                }
            })
            print(f"Image added to groq request")
        print(f"Calling grouq with chars: {len(content)}")
        response = self.client.chat.completions.create(
            messages=[{
                "role": "user",
                "content": content
            }],
            response_format={"type": "json_object"},
            model=self.model,
            temperature=temperature,
            # max_completion_tokens=1024,
            # top_p=1,
        )
        return response.choices[0].message.content or ""

    def ensure_base64_str(self, base64str) -> str:
        """
        Ensure the image string is in base64 format.
        """
        return base64str if base64str.startswith("data:image/jpeg;base64,") else f"data:image/jpeg;base64,{base64str}"

    def get_provider_name(self) -> str:
        return "Groq"

    def get_provider_llm(self) -> str:
        return self.model
