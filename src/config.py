from configparser import ConfigParser

class Config():
    def __init__(self):
        self.direction = None
        self.config = ConfigParser()

    def init(self, direction):
        self.direction = direction
        try:
            self.config.read(direction)
            self.config['env:kilats']
            return True
        except: return False

    def read(self):
        return self.config

config = Config()