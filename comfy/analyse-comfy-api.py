import asyncio
import os
from pathlib import Path

from API import comfy


generation_parameters = {"positive_prompt": "a cat walking on a fence", "width": 256, "height": 256, "prefix": "icon"}


def icon(object_name):
    return f"""
        generate a simple black and white icon of a {object_name}
    """


async def main():
    cwd = os.path.dirname(__file__)
    workflow_path = os.path.join(cwd, "api.json")
    service = comfy.ComfyUIService(workflow_path=workflow_path)
    service.prepare_workflow(generation_parameters)


if __name__ == "__main__":
    asyncio.run(main())
