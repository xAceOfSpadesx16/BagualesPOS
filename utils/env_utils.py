from environ import Env

env = Env()
env.read_env()

# Make SETTINGS_MODULE optional (defaults to 'base' if not set)
SETTING_MODULE: str = env.str('SETTINGS_MODULE', default='base')