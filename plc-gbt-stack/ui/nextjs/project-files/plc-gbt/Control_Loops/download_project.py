"""
This is an example Logix Designer SDK customer application.
It allows the user to download a Logix Designer project file into a controller.
The user will provide two arguments:
    1) Full path for the Logix Designer project file
    2) Communications path for the controller targeted for the Download

Example:
python download_project.py "C:\\ProjectDir\\MyProject.ACD" AB_ETH-1\\10.88.45.25\\Backplane\\0
"""

import asyncio
import sys

from logix_designer_sdk import ControllerMode, LogixProject, StdOutEventLogger


async def main():
    """
    Main method
    """
    if len(sys.argv) != 3:
        print(f"Usage: python {sys.argv[0]} projectFilePath commPath")
        sys.exit(1)

    project_path = sys.argv[1]
    comm_path = sys.argv[2]

    project = await LogixProject.open_logix_project(project_path, StdOutEventLogger())

    await project.set_communications_path(comm_path)

    controller_mode = await project.read_controller_mode()
    if controller_mode != ControllerMode.PROGRAM:
        print(
            f"Controller mode is {controller_mode}. Downloading is possible only if the controller is in 'Program' mode"
        )
        return

    await project.download()

    # Download modifies the project.
    # Without saving, if used file will be opened again, commands which need correlation
    # between program in the controller and opened project like LoadImageFromSDCard or StoreImageOnSDCard
    # may won't be able to succeed because project in the controller won't match opened project.
    await project.save()

    print("Download DONE.")


if __name__ == "__main__":
    asyncio.run(main())
