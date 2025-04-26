from datastructures.image_description import ImageDescription
from datastructures.image_carrier import ImageCarrier
from datastructures.agent_instruction import AgentInstruction
from infrence_provider.infrence_provider import InferenceProvider


class ImageAnalystAgent():

    def __init__(self, instruction: AgentInstruction, image: ImageCarrier, infrence: InferenceProvider, llm_temp: float = 1.0):
        self.llm_temp = llm_temp
        self.instruction = instruction
        self.imageData = image
        self.tools = {}
        self.inference = infrence

    def execute(self) -> ImageDescription:
        print("Analysing image")
        prompt = str.join('\n', [self.instruction.prompt,
                                 "If any of these criteria are met, the image should be marked for deletion:",
                                 self.instruction.criteria],
                          "Output should strictly follow the provided JSON format.")
        message = self.inference.infer(prompt=prompt,
                                       image=self.imageData.thumbnail_base64,
                                       format=ImageDescription.model_json_schema(),
                                       temperature=self.llm_temp
                                       )

        # Convert received content to the schema
        try:
            image_analysis = ImageDescription.model_validate_json(message)
        except Exception as e:
            print(f"Error in image analysis: {e}")
            raise ValueError(
                f"Error parsing json ImageDescription: {message}")

        if image_analysis.filename != self.imageData.filename:
            image_analysis.filename = self.imageData.filename
        return image_analysis
