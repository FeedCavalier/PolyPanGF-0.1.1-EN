"""Build an allowlisted English release and audit nested archive text."""

import hashlib
import io
import json
from pathlib import Path
import re
import zipfile


ROOT = Path(__file__).resolve().parents[1]


def audit(name, data):
    if re.search(r"[\u3400-\u9fff]", name):
        raise ValueError("Non-English archive member name")
    if name.endswith((".whl", ".zip")):
        with zipfile.ZipFile(io.BytesIO(data)) as nested:
            for member in nested.namelist():
                audit(member, nested.read(member))
        return
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return
    patterns = [
        r"[\u3400-\u9fff]",
        r"(?i)[A-Z]:[\\/]Users[\\/]",
        r"/(?:home|root|run/media)/",
        r"/opt/polypangf",
        r"(?<![\w.])(?:\d{1,3}\.){3}\d{1,3}(?![\w.])",
    ]
    # The audit source documents the patterns it searches for.
    if name.endswith("build_english_release.py"):
        return
    if any(re.search(pattern, text) for pattern in patterns):
        raise ValueError("Release privacy or language audit failed for " + name)


def main():
    files = {}
    for name in ["README.md", "CHANGELOG.md", "PRIVACY.md", "VALIDATION.md", "pyproject.toml", "environment.yml", ".gitignore"]:
        files[name] = (ROOT / name).read_bytes()
    for directory, pattern in [("src/polypangf", "*.py"), ("tests", "test_*.py"), ("dist", "*.whl")]:
        for path in (ROOT / directory).glob(pattern):
            files[path.relative_to(ROOT).as_posix()] = path.read_bytes()
    files["validation/build_english_release.py"] = Path(__file__).read_bytes()
    example = ROOT / "example" if (ROOT / "example").exists() else ROOT / "demo"
    for path in example.iterdir():
        if path.is_file() and not path.name.startswith("."):
            files["example/" + path.name] = path.read_bytes()
    for name, data in files.items():
        audit(name, data)
    files["RELEASE_AUDIT.json"] = (json.dumps({"version": "0.1.1", "language": "English", "allowlist": True, "audited_files": len(files), "privacy_findings": 0, "nested_wheel_checked": True}, indent=2) + "\n").encode()
    files["SHA256SUMS.txt"] = ("\n".join(hashlib.sha256(data).hexdigest() + "  " + name for name, data in sorted(files.items())) + "\n").encode()
    destination = ROOT / "release/PolyPanGF-0.1.1-English.zip"
    destination.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as output:
        for name, data in sorted(files.items()):
            output.writestr("PolyPanGF-0.1.1/" + name, data)
    with zipfile.ZipFile(destination) as output:
        assert output.testzip() is None
    print(json.dumps({"files": len(files), "sha256": hashlib.sha256(destination.read_bytes()).hexdigest()}))


if __name__ == "__main__":
    main()
