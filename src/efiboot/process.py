import subprocess


def run(*cmd: str) -> subprocess.CompletedProcess[str]:
    """
    Runs a blocking process,
    if faliure occurs it will throw "subprocess.CalledProcessError"
    will not print anything, captures process output in .stdout and .stderr
    also stores return code in .returncode
    """
    return subprocess.run(cmd, check=True, capture_output=True, text=True)
