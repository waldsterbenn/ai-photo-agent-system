import json
from ollama import Client, ResponseError, ChatResponse, ListResponse
from agent_image_describer import AgentImageDescriber
from datastructures.image_description import ImageDescription


class AgentManager:
    """Plans and manages tasks between multiple agents."""

    def __init__(self):
        self.model = "gemma3:4b"
        self.llm = {}
        self.agents = [AgentImageDescriber()]
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

    def plan_task(self, task_description):
        return {
            "status": "success",
            "message": "Task planned successfully"
        }

    def execute_task(self, task_plan_description: str, images: list) -> list:
        """
        Execute a task using the multi-agent system.

        Args:
            task_description (str): Natural language description of the task

        Returns:
            dict: Result of the task execution
        """

        imageDescriptions = []
        # try:
        for image in images:
            desc = self.invokeAgent(image)
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
