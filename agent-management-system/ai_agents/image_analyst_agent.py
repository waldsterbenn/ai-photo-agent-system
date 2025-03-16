from pydantic import BaseModel
from ollama import Client
from datastructures.image_description import ImageDescription
from datastructures.image_carrier import ImageCarrier
from datastructures.agent_instruction import AgentInstruction


class ImageAnalystAgent():

    def __init__(self, model: str, prompt: AgentInstruction, image: ImageCarrier):
        self.model = model
        self.llm = Client(host='http://ollama:11434')
        self.instruction = prompt
        self.imageData = image
        self.tools = {}

    def execute(self) -> ImageDescription:
        print("Describing image...")

        msg = {
            'role': 'user',
            'content': self.instruction.prompt,  # TODO: Add metadata
            'images': [self.imageData.base64]
        }

        response = self.llm.chat(
            model=self.model,
            format=ImageDescription.model_json_schema(),
            options={'temperature': 0},
            messages=[msg]
        )

        # Convert received content to the schema
        print(response)
        image_analysis = ImageDescription.model_validate_json(
            response.message.content)
        return image_analysis
