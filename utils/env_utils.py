from environ import Env

env = Env()
env.read_env()

SETTING_MODULE: str = env.str('SETTINGS_MODULE')