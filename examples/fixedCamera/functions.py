from argparse import ArgumentParser
from roverlib.plugins.camera.camera import Camera

def setArguments(args: list = []) -> ArgumentParser:
    params = ArgumentParser()
    
    for a in args:
        params.add_argument(
            a["name"],
            type=a["type"],
            help=a["help"]
        )
    
    return params