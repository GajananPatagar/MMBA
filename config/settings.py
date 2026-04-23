class Settings:
    def __init__(self, ram_limit_mb=900, brain_path="./data/master_brain"):
        self.ram_limit_mb = ram_limit_mb
        self.brain_path   = brain_path
        self.version      = "1.0.0"
        self.author       = "IHTM Department"
