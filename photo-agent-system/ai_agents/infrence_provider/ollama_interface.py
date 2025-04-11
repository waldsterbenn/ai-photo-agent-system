
from typing import Any, Dict
from ollama import Client, ResponseError, ChatResponse, ListResponse
from infrence_provider.infrence_provider import InferenceProvider


class OllamaInterface(InferenceProvider):
    """
    Concrete implementation for the Ollama inference provider.
    """

    def __init__(self, config: Dict[str, Any]):
        self.base_url: str = config.get(
            'base_url', 'http://localhost:11434')  # Default URL
        self.model: str = config.get('model', 'llama3')  # Default model
        self.context_window: str = config.get(
            'context_window', '32000')  # Default context windoww

        print(
            f"Initializing OllamaInterface with base_url: {self.base_url}, model: {self.model}")
        self.client = Client(
            host=self.base_url
        )

        try:
            response: ListResponse = self.client.list()
            for model in response.models:
                if model.model == self.model:
                    print(self.model + " already exists on disk.")
                    return
            # Pull the model if it does not exist
            print(self.model + " Now found, will pull from ollama.")
            self.client.pull(self.model)

        except ResponseError as e:
            if e.status_code == 404:
                self.client.pull(self.model)

    def infer(self, prompt: str, image: str = None, format: str = None, temperature: float = 0) -> str:

        msg = {
            'role': 'user',
            'content': prompt,  # TODO: Add metadata
            'images': [image]
        }
        response: ChatResponse = self.client.chat(
            model=self.model,
            format=format,
            options={'temperature': temperature,
                     "context_window": self.context_window},
            messages=[msg]
        )

        # Convert received content to the schema
        return response.message.content

    def get_provider_name(self) -> str:
        return "Ollama"

    def get_provider_llm(self) -> str:
        return self.model
