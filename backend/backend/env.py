import pathlib
from starlette.config import Config


module_path = pathlib.Path(__file__).resolve().parent

env_file = module_path / ".env"

environment = Config(env_file) 
 