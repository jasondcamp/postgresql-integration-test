import glob
import os
import re
import socket
import subprocess
import shutil

from postgresql_integration_test.attributes import ConfigAttribute

# Locations where PostgreSQL binaries live when they are not on PATH.
# Debian/Ubuntu only expose client wrappers in /usr/bin; initdb and
# postgres are only in the versioned directory.
SEARCH_GLOBS = [
    "/usr/lib/postgresql/*/bin",  # Debian/Ubuntu
    "/usr/pgsql-*/bin",  # RHEL/CentOS (PGDG)
    "/usr/local/opt/postgresql*/bin",  # Homebrew (Intel)
    "/opt/homebrew/opt/postgresql*/bin",  # Homebrew (Apple Silicon)
]


class Utils:
    @staticmethod
    def find_bindir():
        """Directory of a full server install, i.e. one containing postgres."""
        binary_path = shutil.which("postgres")
        if not binary_path:
            candidates = []
            for search_glob in SEARCH_GLOBS:
                candidates.extend(glob.glob(os.path.join(search_glob, "postgres")))

            if candidates:
                # Prefer the highest version (numeric sort, so 16 beats 9.6)
                def version_key(path):
                    return [int(num) for num in re.findall(r"\d+", path)]

                binary_path = sorted(candidates, key=version_key)[-1]

        return os.path.dirname(binary_path) if binary_path else None

    @staticmethod
    def find_program(name):
        # Prefer binaries co-located with the postgres server binary. Partial
        # installs (Homebrew libpq, Debian client wrappers) put some tools on
        # PATH without a usable server next to them.
        bindir = Utils.find_bindir()
        if bindir:
            candidate = os.path.join(bindir, name)
            if os.access(candidate, os.X_OK):
                return candidate

        binary_path = shutil.which(name)
        if binary_path:
            return binary_path

        raise RuntimeError(f"Error, no binary {name} found!")

    @staticmethod
    def get_unused_port():
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("localhost", 0))
        _, port = sock.getsockname()
        sock.close()

        return port

    @staticmethod
    def get_binary_version(binary_location):
        (variant, version_major, version_minor) = Utils.parse_version(
            subprocess.check_output([binary_location, "--version"]).decode(
                "utf-8"
            )
        )

        version = ConfigAttribute
        version.variant = variant
        version.major = version_major
        version.minor = version_minor

        return version

    @staticmethod
    def parse_version(version_str):
        version_info = re.findall(r"(\w+) \(PostgreSQL\) (\d+).(\d+)?", version_str)

        version_variant = None
        version_major = None
        version_minor = None
        if len(version_info) > 0:
            version_variant = version_info[0][0]
            version_major = int(version_info[0][1])
            version_minor = int(version_info[0][2])

        return (version_variant, version_major, version_minor)
