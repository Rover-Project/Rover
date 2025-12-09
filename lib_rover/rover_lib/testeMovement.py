from modules.movement.motor import Motor
from utils.config_manager import Config

if __name__ == "__main__":
    
    pins = Config.get("gpio")
    
    print(pins)