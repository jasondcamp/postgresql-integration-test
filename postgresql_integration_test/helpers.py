import os
import re
import socket

BASEDIRS = ['/', '/usr', '/usr/local', '/opt/homebrew']


class Utils():
    @staticmethod
    def find_program(name):
        for basedir in ['usr', 'usr/local']:
            for subdir in ['bin', 'libexec', 'sbin', 'scripts']:
                path = os.path.join("/", basedir, subdir, name)
                if os.path.exists(path):
                    return path
        return None

    @staticmethod
    def get_unused_port():
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('localhost', 0))
        _, port = sock.getsockname()
        sock.close()

        return port

    @staticmethod
    def parse_version(version_str):
        version_info = (re.findall(r"Ver ([0-9.]+)\-?([+a-zA-Z0-9.-]+)? for", version_str))
        if version_info:
            (version_major, version_minor) = version_info[0][0].split('.', 1)
            version_major = int(version_major)

            if "mariadb" in version_info[0][1].lower():
                version_variant = "mariadb"
            elif version_major == 8:
                version_variant = "mysql"
            else:
                version_variant = "unknown"
        else:
            version_variant = None
            version_major = None
            version_minor = None

        return (version_variant, version_major, version_minor)
