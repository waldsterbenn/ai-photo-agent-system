import json
from typing import List
from datastructures.image_description import ImageDescription
from datastructures.image_carrier import ImageCarrier
from datastructures.agent_instruction import AgentInstruction
from infrence_provider.infrence_provider import InferenceProvider


class ImageAnalystAgent():

    def __init__(self, instruction: AgentInstruction, image: ImageCarrier, infrence: InferenceProvider, criteria: List[str], llm_temp: float = 1.0):
        self.llm_temp = llm_temp
        self.instruction = instruction
        self.imageData = image
        self.tools = {}
        self.inference = infrence
        self.criteria = criteria

    def execute(self) -> ImageDescription:
        print("Analysing image")
        prompt = str.join('\n', [self.instruction.prompt,
                                 "Be critical, if any of the criteria are met, the image should be marked for deletion.",
                                 "Criteria:",
                                 "---",
                                 f"[{self.criteria}]",
                                 "---",
                                 "Output should strictly follow the provided JSON schema, but do not return the schema, return a serializable JSON object based on the provided schema."])
        response = self.inference.infer(prompt=prompt,
                                        image=self.imageData.thumbnail_base64,
                                        format=ImageDescription.model_json_schema(),
                                        temperature=self.llm_temp
                                        )

        try:
            json_response = json.loads(response)
            image_analysis = ImageDescription.model_validate(json_response)
        except Exception as e:
            print(f"Error in image analysis: {e}")
            raise ValueError(
                f"Error parsing json ImageDescription: {response}")

        if image_analysis.filename != self.imageData.filename:
            image_analysis.filename = self.imageData.filename
        return image_analysis
