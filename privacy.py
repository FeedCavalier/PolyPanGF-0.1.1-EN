"""Virtualize machine-specific locations in shared result archives."""

import json
from pathlib import Path
import re
import socket


class PortableText:
    """Keep one consistent mapping across every text file in an export."""

    def __init__(self, root):
        self.mapping = {str(Path(root).resolve()): "/example/results"}
        project_directories = set()
        external_inputs = set()
        for path in Path(root).glob("*/state.json"):
            state = json.loads(path.read_text(encoding="utf-8"))
            fingerprint = state.get("fingerprint", {})
            parameters = fingerprint.get("parameters", {})
            if parameters.get("_base"):
                project_directories.add(parameters["_base"])
            external_inputs.update(fingerprint.get("inputs", {}))
        for directory in sorted(project_directories, key=len, reverse=True):
            self.mapping.setdefault(directory, "/example/project")
        for path in sorted(external_inputs):
            if not any(
                path == base or path.startswith(base.rstrip("/") + "/")
                for base in self.mapping
            ):
                self._register(path)
        self.hostnames = {
            name
            for name in [socket.gethostname(), socket.getfqdn()]
            if name and name not in ["localhost", "example"]
        }

    def _register(self, path):
        if path not in self.mapping:
            suffix = Path(path).suffix
            suffix = suffix if re.fullmatch(r"\.[A-Za-z0-9]{1,12}", suffix) else ""
            self.mapping[path] = (
                f"/example/external/file_{len(self.mapping):04d}{suffix}"
            )
        return self.mapping[path]

    def sanitize(self, value, heuristic_paths=True):
        for path, replacement in sorted(
            self.mapping.items(), key=lambda item: -len(item[0])
        ):
            for variant in {path, json.dumps(path)[1:-1]}:
                value = value.replace(variant, replacement)

        def path_match(match):
            path = match.group(0)
            if path.startswith(("/example/", "/path/to/")):
                return path
            return self._register(path)

        # Avoid URL slashes and preserve relative links inside HTML reports.
        if heuristic_paths:
            value = re.sub(
                r"(?<![:/\w<.])/(?!/)[^\s<>\"'|,\]\[{}()]+", path_match, value
            )
            value = re.sub(r"(?i)\b[A-Z]:[\\/][^\n\r\t\"'<>]+", path_match, value)
        for hostname in self.hostnames:
            value = value.replace(hostname, "example-host")
        if heuristic_paths:
            value = re.sub(
                r"(?<![\w.])(?:\d{1,3}\.){3}\d{1,3}(?![\w.])", "example-address", value
            )
        return value

    def bytes(self, data, heuristic_paths=True):
        if b"\x00" in data:
            return data
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            return data
        try:
            structured = json.loads(text)
        except json.JSONDecodeError:
            return self.sanitize(text, heuristic_paths=heuristic_paths).encode("utf-8")

        def clean(value):
            if isinstance(value, dict):
                result = {}
                private_fields = {
                    "username",
                    "user_name",
                    "login",
                    "hostname",
                    "host_name",
                    "machine_name",
                    "ip_address",
                    "home_directory",
                }
                for key, item in value.items():
                    result[self.sanitize(key)] = (
                        "example" if key.lower() in private_fields else clean(item)
                    )
                return result
            if isinstance(value, list):
                return [clean(item) for item in value]
            return self.sanitize(value) if isinstance(value, str) else value

        return (
            json.dumps(clean(structured), ensure_ascii=False, indent=2) + "\n"
        ).encode("utf-8")
