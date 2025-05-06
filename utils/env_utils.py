from environ import Env

def get_debug():
    env = Env()
    env.read_env()
    return env.bool('DEBUG')

def get_settings_module():
    env = Env()
    env.read_env()
    return env.str('SETTINGS_MODULE')