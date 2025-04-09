import json
from typing import List
from image_analyst_agent import ImageAnalystAgent
from datastructures.image_description import ImageDescription
from datastructures.image_carrier import ImageCarrier
from datastructures.agent_instruction import AgentInstruction
from pydantic import BaseModel
from infrence_provider.infrence_provider_factory import InferenceProviderFactory


class Plan(BaseModel):
    plan: str
    agentPrompts: list[AgentInstruction]


class AgentManager:
    """Plans and manages tasks between multiple agents."""

    def __init__(self):
        self.inference = InferenceProviderFactory().create_provider()
        self.agents: list[ImageAnalystAgent] = []
        self.tools = {}

    def plan_task(self, taskPrompt: str, criteria: List[str], image_carriers: List[ImageCarrier]) -> Plan:
        print("Planning task")

        planPrompt = f"""
            You are provided {len(image_carriers)} images.
            For each image, assign an agent to analyse and rate the image, based on the 'Deletion criteria'.
            Provide the agent with instructional prompt.
            
            Now create a plan to solve this task.
            The plan should contain instructions for each agent, based on the 'Prompt template' and must contain the 'Deletion criteria'.

            ---

            Prompt template:
            {taskPrompt}

            ---

            Deletion criteria:
            {criteria}
            
            ---
            
            Image filenames:
            {', '.join([carrier.filename for carrier in image_carriers])}
            """

        response = self.inference.infer(
            prompt=planPrompt, format=Plan.model_json_schema())

        plan = Plan.model_validate_json(response)

        for agentInstruction in plan.agentPrompts:

            image = list(
                filter(lambda x: (x.filename == agentInstruction.filename), image_carriers))[0]
            self.agents.append(ImageAnalystAgent(
                agentInstruction, image, self.inference))
        return plan

    def execute_task(self) -> list:
        """
        Execute a task using the multi-agent system.

        Args:
            task_description (str): Natural language description of the task

        Returns:
            dict: Result of the task execution
        """
        print("Executing agents")
        imageDescriptions = []
        for agent in self.agents:
            desc: ImageDescription = agent.execute()
            imageDescriptions.append(desc)

        dict_descriptions = [desc.dict() for desc in imageDescriptions]
        json_string = json.dumps(dict_descriptions)
        return json_string
