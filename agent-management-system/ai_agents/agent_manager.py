import json
from typing import List
from ollama import Client, ResponseError, ChatResponse, ListResponse
from image_analyst_agent import ImageAnalystAgent
from datastructures.image_description import ImageDescription
from datastructures.image_carrier import ImageCarrier
from datastructures.agent_instruction import AgentInstruction
from pydantic import BaseModel


class Plan(BaseModel):
    plan: str
    agentPrompts: list[AgentInstruction]


class AgentManager:
    """Plans and manages tasks between multiple agents."""

    def __init__(self, model: str):
        self.model = model
        self.llm = {}
        self.agents: list[ImageAnalystAgent] = []
        self.tools = {}
        self._initialize_system()

    def _initialize_system(self):
        """Initialize the multi-agent system and tools."""

        self.llm = Client(host='http://ollama:11434')

        try:
            response: ListResponse = self.llm.list()
            for model in response.models:
                if model.model == self.model:
                    print(self.model + " already exists on disk.")
                    return
            # Pull the model if it does not exist
            print(self.model + " Now found, will pull from ollama.")
            self.llm.pull(self.model)

        except ResponseError as e:
            if e.status_code == 404:
                self.llm.pull(self.model)

    def plan_task(self, taskPrompt: str, criteria: List[str], image_carriers: List[ImageCarrier]) -> Plan:

        planPrompt = f"""
            You are provided {len(image_carriers)} images.
            Use the agents you have at your disposal.
            Use the agents to analyse and rate the images one by one, based on the criteria.
            Each agent should get 1 image to analyse and you need to make an instructional prompt for each agent so they know what to do.

            Now create a plan to solve this task.
            The plan should contain instructions for each agent, based on the prompt template.

            ---

            Prompt template:
            {taskPrompt}

            ---

            Criteria:
            {criteria}
            
            ---
            
            Image filenames:
            {', '.join([carrier.filename for carrier in image_carriers])}
            """

        response: ChatResponse = self.llm.chat(model=self.model, messages=[
            {
                'role': 'user',
                'content': planPrompt,
            }],
            format=Plan.model_json_schema(),
            options={'temperature': 0})
        # print(response)

        plan = Plan.model_validate_json(response.message.content)
        print(plan.plan)
        for agentInstruction in plan.agentPrompts:
            image = list(
                filter(lambda x: (x.filename == agentInstruction.filename), image_carriers))[0]
            self.agents.append(ImageAnalystAgent(
                self.model, agentInstruction, image))
        return plan

    def execute_task(self, task_plan_description: str, task_prompt: str, images: list) -> list:
        """
        Execute a task using the multi-agent system.

        Args:
            task_description (str): Natural language description of the task

        Returns:
            dict: Result of the task execution
        """
        pass
        imageDescriptions = []
        # try:
        for agent in self.agents:
            desc: ImageDescription = agent.execute()
            imageDescriptions.append(desc)

        dict_descriptions = [desc.dict() for desc in imageDescriptions]
        json_string = json.dumps(dict_descriptions)
        print(json_string)
        return json_string
        # except Exception as e:
        #     return {
        #         "status": "error",
        #         "message": str(e)
        #     }

    def invokeAgent(self, image):
        """Invoke an agent to analyze an image."""
        desc: ImageDescription = self.agents[0].describe_image(image.base64)
        return desc

    def callLlm(self, task_description):
        response: ChatResponse = self.llm.chat(model=self.model, messages=[
            {
                'role': 'user',
                'content': task_description,
            },
        ])
        return {
            "status": "success",
            "message": response.message.content
        }
