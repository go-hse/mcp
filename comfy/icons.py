import asyncio
import os
from pathlib import Path

from API import comfy


cwd = os.path.dirname(__file__)
workflow_path = os.path.join(cwd, "api.json")


def icon_prompt(object_name):
    return f"""
        generate a grayscale isometric icon of {object_name}
    """


async def icons(object_names):
    service = comfy.ComfyUIService(workflow_path=workflow_path)

    generation_parameters = {
        "positive_prompt": "a cube",
        "width": 256,
        "height": 256,
        "prefix": "icon",
        "batch_size": 2,
        "subfolder": "gray",
    }
    for object_name in object_names:
        generation_parameters["positive_prompt"] = icon_prompt(object_name=object_name)
        generation_parameters["prefix"] = object_name
        # service.prepare_workflow(generation_parameters)
        await service.generate_image(generation_parameters)


if __name__ == "__main__":
    object_names = [
        "light_bulb",
        "computer",
        "smartphone",
        "printer",
        "cube",
        "3 cubes",
        "robot",
        "industrial robot",
        "plane",
        "rose",
        "house",
        "factory",
        "fire",
        "man",
        "work man",
        "office man",
        "woman",
    ]
    asyncio.run(icons(object_names=object_names))
