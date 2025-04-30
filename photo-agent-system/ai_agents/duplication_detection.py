import json
from datastructures.image_description import ImageDescription
from infrence_provider.infrence_provider_factory import InferenceProviderFactory


class DuplicationDetection:

    def __init__(self):
        self.inference = InferenceProviderFactory().create_provider()
        self.image_descriptions: list[ImageDescription] = []
        self.tools = {}
        self.llm_temp = 0.7
        print("DuplicationDetection constructed")

    def detect_duplicate_descriptions(self, descriptions: list[ImageDescription]) -> dict:
        """
        Detects potentially duplicate image descriptions using the LLM.

        Args:
            descriptions: A list of ImageDescription objects to analyze.

        Returns:
            A dictionary containing duplicate_groups and an analysis_summary.
            If less than two descriptions are provided, returns an empty duplicate_groups list.
        """
        if len(descriptions) < 2:
            return {
                "duplicate_groups": [],
                "analysis_summary": "Input contains less than two descriptions, no comparison possible."
            }

        # Prepare the data for the LLM (selecting only the necessary fields)
        input_data_for_llm = []
        for desc in descriptions:
            input_data_for_llm.append({
                "filename": desc.get("filename"),
                "forencic_analysis": desc.get("forencic_analysis"),
                "text_content": desc.get("text_content"),
            })

        # Construct the prompt
        prompt = "\n".join([
            "Analyze the following list of image descriptions to identify potential duplicates.",
            "A duplicate means the descriptions likely refer to the same or nearly identical images/scenes, based on high semantic similarity in their 'summary', 'scene', and 'setting' fields.",
            "Minor differences in wording are acceptable as long as the core meaning is the same.",
            "",
            "Input Data:",
            json.dumps(input_data_for_llm, indent=2),
            "",
            "Task:",
            "Identify groups of descriptions that are potential duplicates of each other.",
            "Return your findings ONLY in the following JSON format:",
            json.dumps({
                "duplicate_groups": [
                    {
                        "filenames": ["filename1.ext", "filename_duplicate.ext"],
                        "reason": "Brief explanation why these are considered duplicates.",
                        "group_header": "Group header for categorization.",
                    }
                    # Add more groups if applicable
                ],
                "analysis_summary": "A brief overall summary of the analysis."
            }, indent=2),
            "",
            "- Each group must contain at least two filenames.",
            "- If no duplicates are found, return an empty duplicate_groups list.",
            "- Do not include any text besides the JSON output."
        ])

        # Call the LLM inference provider
        response = self.inference.infer(
            prompt=prompt,
            format={"type": "json_object"},
            temperature=self.llm_temp,
            modelOverride='llama-3.1-8b-instant'
        )
        print(f"LLM Response received:\n{response}")

        # Clean up potential markdown markers and parse JSON response
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        if response.endswith("```"):
            response = response[:-3]
        response = response.strip()

        try:
            parsed_output = json.loads(response)
        except Exception as e:
            print(f"Error parsing LLM JSON response: {e}")
            return {
                "duplicate_groups": [],
                "analysis_summary": "Failed to parse LLM JSON response.",
                "error": True,
                "raw_response": response
            }

        # Validate basic structure from LLM output.
        if "duplicate_groups" not in parsed_output or not isinstance(parsed_output["duplicate_groups"], list):
            print("LLM response structure invalid.")
            return {
                "duplicate_groups": [],
                "analysis_summary": "Invalid LLM response structure.",
                "error": True,
                "raw_response": response
            }

        return parsed_output
