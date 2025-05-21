import pathlib
from starlette.config import Config


module_path = pathlib.Path(__file__).resolve().parent

env_file = module_path / ".env"

if not env_file.exists():
    raise FileNotFoundError(f"Config .env not found at location: {env_file}")

environment = Config(env_file)
