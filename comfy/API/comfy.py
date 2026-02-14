import uuid
import websocket
import json
import random
import asyncio
import requests
import os
from pathlib import Path
from datetime import datetime


"""
This is an example of how to call the ComfyUI API, which is different from the ViewComfy API.
For the ViewComfy API, see the ViewComfy_API folder: https://github.com/ViewComfy/cloud-public/tree/main/ViewComfy_API.
"""

"""
Futuristic isometric infographic, a view from above on a library with book shelfs in a cozy lighting. 
There are diverse users between the shelfs and together with a librarian on a counter.
White background, isometric, realistic, golden ratio, fake detail, trending attestation, technical sketch, schematic drawing, high quality, DSLR, Fujifilm XT3, realistic, colorful
"""


generation_parameters = {
    "positive_prompt": "a cat walking on a fence",
}


now = datetime.now()
time_string = now.strftime("%Y_%m_%d__%H_%M_%S")


class ComfyUIService:
    def __init__(self, server_address="127.0.0.1:8188", workflow_path="workflow_api.json"):
        self.server_address = server_address
        self.workflow_path = workflow_path
        self.image_dir = Path(workflow_path).parent / "images"

    async def establish_connection(self):
        client_id = str(uuid.uuid4())
        uri = f"ws://{self.server_address}/ws?clientId={client_id}"
        ws = websocket.create_connection(uri)

        return ws, self.server_address, client_id

    def load_workflow(self, workflow_path):
        if os.path.isfile(workflow_path):
            with open(workflow_path) as json_data:
                # raw_database = json.load(json_data)
                return json.load(json_data)
        else:
            raise f" {workflow_path} is not a file"

    async def queue_prompt(self, prompt, client_id, server_address):
        """Queue a workflow for execution. The prompt here is the full workflow_api.json file"""
        data = {"prompt": prompt, "client_id": client_id}
        headers = {"Content-Type": "application/json"}
        response = requests.post(f"http://{server_address}/prompt", json=data, headers=headers)
        return response.json()

    def track_progress(self, ws, prompt_id):
        """Track the progress of image generation"""
        while True:
            try:
                message = json.loads(ws.recv())
                if message["type"] == "progress":
                    """If the workflow is running print k-sampler current step over total steps"""
                    print(f"Progress: {message['data']['value']}/{message['data']['max']}")

                elif message["type"] == "executing":
                    """Print the node that is currently being executed"""
                    print(f"Executing node: {message['data']['node']}")

                elif message["type"] == "execution_cached":
                    """Print list of nodes that are cached"""
                    print(f"Cached execution: {message['data']}")

                """Check for completion"""
                if (
                    message["type"] == "executed"
                    and "prompt_id" in message["data"]
                    and message["data"]["prompt_id"] == prompt_id
                ):
                    print("Generation completed")
                    return True

            except Exception as e:
                print(f"Error processing message: {e}")
                return False

    async def get_history(self, prompt_id, server_address):
        """Fetch the output data for a completed workflow, returns a JSON with generation parameters and results filenames and directories"""
        response = requests.get(f"http://{server_address}/history/{prompt_id}")
        return response.json()

    def update_workflow(self, workflow, generation_parameters):
        id_to_class_type = {id: details["class_type"] for id, details in workflow.items()}
        k_sampler_id = [key for key, value in id_to_class_type.items() if value == "KSampler"][0]
        workflow.get(k_sampler_id)["inputs"]["seed"] = random.randint(10**14, 10**15 - 1)
        text_prompt = workflow.get(k_sampler_id)["inputs"]["positive"][0]
        workflow.get(text_prompt)["inputs"]["text"] = generation_parameters["positive_prompt"]

        saveimage_id = [key for key, value in id_to_class_type.items() if value == "SaveImage"][0]
        workflow.get(saveimage_id)["inputs"]["filename_prefix"] = generation_parameters["prefix"]

        emptyimage_id = [key for key, value in id_to_class_type.items() if value == "EmptySD3LatentImage"][0]
        workflow.get(emptyimage_id)["inputs"]["width"] = generation_parameters["width"]
        workflow.get(emptyimage_id)["inputs"]["height"] = generation_parameters["height"]
        workflow.get(emptyimage_id)["inputs"]["batch_size"] = generation_parameters["batch_size"]

        return workflow

    def prepare_workflow(self, generation_parameters):
        workflow = self.load_workflow(self.workflow_path)
        workflow = self.update_workflow(workflow, generation_parameters)
        return workflow

    def write_image(self, filename, content):

        filepath = self.image_dir / time_string
        Path(filepath).mkdir(parents=True, exist_ok=True)
        with open(filepath / filename, "wb") as file:
            file.write(content)
        print(f"get_image retrieved {time_string}/{filename}")

    async def get_image(self, filename, subfolder, folder_type, server_address):
        """Fetch results. Note that "save image" nodes will save image in the ouptut folder and "preview image" nodes will save image in the temp folder"""
        params = {"filename": filename, "subfolder": subfolder, "type": folder_type}
        response = requests.get(f"http://{server_address}/view", params=params)
        if not subfolder:
            subfolder = "images"
        self.write_image(filename=filename, content=response.content)

    async def generate_image(self, generation_parameters):
        ws, _, client_id = await self.establish_connection()

        try:
            """Update the workflow with the generation parameters"""
            workflow = self.prepare_workflow(generation_parameters)
            """Send the workflow to the server"""
            prompt_id = await self.queue_prompt(workflow, client_id, self.server_address)
            prompt_id = prompt_id["prompt_id"]

            """Track the progress"""
            completed = self.track_progress(ws, prompt_id)
            if not completed:
                print("Generation failed or interrupted")
                return None

            """Fetch the output data"""
            history = await self.get_history(prompt_id, self.server_address)
            outputs = history[prompt_id]["outputs"]

            """Get output images"""
            for node_id in outputs:
                node_output = outputs[node_id]
                images_output = []
                if "images" in node_output:
                    for image in node_output["images"]:
                        image_data = await self.get_image(
                            image["filename"],
                            image["subfolder"],
                            image["type"],
                            self.server_address,
                        )
                        images_output.append(image_data)
            return images_output

        finally:
            ws.close()


async def main():
    cwd = os.path.dirname(__file__)
    workflow_path = os.path.join(cwd, "api.json")

    service = ComfyUIService(workflow_path=workflow_path)
    images = await service.generate_image(generation_parameters)

    for i, img in enumerate(images):
        with open(f"output_{i}.png", "wb") as file:
            file.write(img)


if __name__ == "__main__":
    asyncio.run(main())
