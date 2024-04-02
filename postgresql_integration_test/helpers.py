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
        version_info = (re.findall(r"postgres \(PostgreSQL\) (\d+).(\d+)?", version_str))

        return ("postgres", version_info[0], version_info[1])
