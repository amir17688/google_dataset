__all__ = ('MashEnvs')

class MashEnvs(object):
    def __init__(self, config_file = False, config = {}):
        if config_file:
            self.config_file = config_file
            # Read the entire file into a dictionary
            self.config = dict()

            for line in self.config_file.readlines():
                if line[0] != '#' and '=' in line:
                    self.config.update(line.split('=', 1))
        else:
            self.config = config
                    
    def add_env(self, key, value):
        self.config[key] = value

    def remove_env(self, key):
        del self.config[key]

    def get_env(self):
        return self.config

    
