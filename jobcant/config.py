import configparser
import os.path
from dataclasses import dataclass

CONFIG_PATH = os.path.realpath(f"{__file__}/../config.ini")


@dataclass
class Config:
    jobcan_email: str
    jobcan_client_code: str | None
    jobcan_password: str

    @classmethod
    def from_env(cls):
        try:
            return cls(
                jobcan_email=os.environ["JOBCAN_EMAIL"],
                jobcan_client_code=os.getenv("JOBCAN_CLIENT_CODE"),
                jobcan_password=os.environ["JOBCAN_PASSWORD"]
            )
        except KeyError:
            return None

    @classmethod
    def load(cls):
        if not os.path.isfile(CONFIG_PATH):
            return None

        config = configparser.ConfigParser(interpolation=None)
        config.read(CONFIG_PATH)
        return cls(
            jobcan_email=config["jobcan"]["email"],
            jobcan_client_code=config["jobcan"]["clientCode"],
            jobcan_password=config["jobcan"]["password"]
        )

    def save(self):
        config = configparser.ConfigParser(interpolation=None)
        config["jobcan"] = {
            "email": self.jobcan_email,
            "clientCode": self.jobcan_client_code or "",
            "password": self.jobcan_password
        }
        with open(CONFIG_PATH, "w") as config_file:
            config.write(config_file)
