from datastructures.image_description import ImageDescription
from datastructures.image_carrier import ImageCarrier
from datastructures.agent_instruction import AgentInstruction
from infrence_provider.infrence_provider import InferenceProvider


class ImageAnalystAgent():

    def __init__(self, instruction: AgentInstruction, image: ImageCarrier, infrence: InferenceProvider):
        self.instruction = instruction
        self.imageData = image
        self.tools = {}
        self.inference = infrence

    def execute(self) -> ImageDescription:
        print("Analysing image")

        message = self.inference.infer(prompt=self.instruction.prompt,
                                       image=self.imageData.base64,
                                       format=ImageDescription.model_json_schema(),
                                       temperature=0.0
                                       )

        # Convert received content to the schema
        image_analysis = ImageDescription.model_validate_json(message)
        if image_analysis.filename != self.imageData.filename:
            image_analysis.filename = self.imageData.filename
        return image_analysis
