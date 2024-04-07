import os
import functools
import yaml
import subprocess
import shutil
import getpass

from postgresql_integration_test.helpers import Utils

config_settings = {}
config_settings["database"] = [
    "username",
    "password",
    "host",
    "port",
    "pg_ctl_binary",
]
config_settings["general"] = [
    "timeout_start",
    "timeout_stop",
    "log_level",
    "config_file",
]


def rgetattr(obj, attr, *args):
    def _getattr(obj, attr):
        return getattr(obj, attr, *args)

    return functools.reduce(_getattr, [obj] + attr.split("."))


def rsetattr(obj, attr, val):
    pre, _, post = attr.rpartition(".")
    return setattr(rgetattr(obj, pre) if pre else obj, post, val)


def merge_configs(config, section, section_cfg):
    for arg in config_settings[section]:
        if arg in section_cfg:
            rsetattr(config, f"{section}.{arg}", section_cfg[arg])

    return config


def load_config_file(config_file):
    if os.path.exists(config_file):
        with open(config_file, "r", encoding="utf-8") as ymlfile:
            cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)
        return cfg
    return {}


def parse_config(config, config_args):
    # See if there is a config file
    cfg = load_config_file(config.general.config_file)

    # Merge config together with args
    for section in config_settings:
        if section in cfg:
            config = merge_configs(config, section, cfg[section])

    # Merge in any class arguments
    for section in config_settings:
        config = merge_configs(config, section, config_args)

    # Get the version of PostgreSQL in case the binary has changed
    (variant, version_major, version_minor) = Utils.parse_version(
        subprocess.check_output([config.database.postgres_binary, "--version"]).decode(
            "utf-8"
        )
    )
    config.version.variant = variant
    config.version.major = version_major
    config.version.minor = version_minor

    return config


class ConfigAttribute:
    pass


class ConfigFile:
    def __init__(self, base_dir):
        self.dirs = ConfigAttribute()
        self.dirs.base_dir = base_dir
        self.dirs.data_dir = os.path.join(self.dirs.base_dir, "var")
        self.dirs.etc_dir = os.path.join(self.dirs.base_dir, "etc")
        self.dirs.tmp_dir = os.path.join(self.dirs.base_dir, "tmp")

        self.database = ConfigAttribute()
        self.database.host = "localhost"
        self.database.port = Utils.get_unused_port()
        self.database.name = getpass.getuser()
        self.database.username = getpass.getuser()
        self.database.postgres_binary = shutil.which("postgres")

        # Get the PostgreSQL variant and version
        (variant, version_major, version_minor) = Utils.parse_version(
            subprocess.check_output(
                [self.database.postgres_binary, "--version"]
            ).decode("utf-8")
        )
        self.version = ConfigAttribute()
        self.version.variant = variant
        self.version.major = version_major
        self.version.minor = version_minor

        self.general = ConfigAttribute()
        self.general.timeout_start = 30
        self.general.timeout_stop = 30
        self.general.log_level = "DEBUG"
        self.general.config_file = "postgresql-integration-test.cfg"
        self.general.cleanup_dirs = True


class ConfigInstance:
    def __init__(self, args):
        self.host = args["host"]
        self.port = args["port"]
        self.username = args["username"]
