import uuid
import websocket
import json
import random
import asyncio
import requests
import os
from pathlib import Path
from API import comfy

"""
This is an example of how to call the ComfyUI API, which is different from the ViewComfy API.
For the ViewComfy API, see the ViewComfy_API folder: https://github.com/ViewComfy/cloud-public/tree/main/ViewComfy_API.
"""

"""
Futuristic isometric infographic, a view from above on a library with book shelfs in a cozy lighting. 
There are diverse users between the shelfs and together with a librarian on a counter.
White background, isometric, realistic, golden ratio, fake detail, trending attestation, technical sketch, schematic drawing, high quality, DSLR, Fujifilm XT3, realistic, colorful
"""


generation_parameters = {"positive_prompt": "a cat walking on a fence", "prefix": "cat", "width": 256, "height": 256}


async def main():
    cwd = os.path.dirname(__file__)
    workflow_path = os.path.join(cwd, "api.json")

    service = comfy.ComfyUIService(workflow_path=workflow_path)
    await service.generate_image(generation_parameters)


if __name__ == "__main__":
    asyncio.run(main())
