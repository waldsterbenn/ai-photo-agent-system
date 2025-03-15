from pydantic import BaseModel
from ollama import chat, Client
from datastructures.image_description import ImageDescription


class AgentImageDescriber():

    def __init__(self):
        self.model = "gemma3:4b"
        self.llm = Client(host='http://ollama:11434')
        self.prompt = """
        Analyze this image and return a detailed JSON description including objects, scene, colors and any text detected. If you cannot determine certain details, leave those fields empty.
        
        Rank the image and mark it to be deleted, if the image is raked below 5 or it meets any of the following criteria:
        1. low quality image.
        2. obscured or unclear motifs.
        3. poor lighting or exposure.
        4. poor composition or framing.
        6. irrelevant or uninteresting content.
        5. poor focus or sharpness.
        7. poor color balance or saturation.
        8. excessive noise or artifacts.
        9. closed eyes or unflattering facial expressions.        
"""
        self.tools = {}

    def describe_image(self, image_base64: str) -> ImageDescription:
        print("Describing image...")
        response = self.llm.chat(
            model=self.model,
            format=ImageDescription.model_json_schema(),
            messages=[
                {
                    'role': 'user',
                    'content': self.prompt,
                    'images': [image_base64],
                },
            ],
            # Set temperature to 0 for more deterministic output
            options={'temperature': 0},
        )

        # Convert received content to the schema
        print(response)
        image_analysis = ImageDescription.model_validate_json(
            response.message.content)
        return image_analysis
