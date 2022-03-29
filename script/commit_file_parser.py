import subprocess
import os


class CommitFileParser:
    def __init__(self, repo_path):
        self.repo_path = repo_path

    def process(self):
        files = subprocess.check_output(
            "git diff --cached --name-only".split(), cwd=self.repo_path, encoding='utf-8')
        abosulute_paths = []
        for file in files.splitlines():
            abosulute_paths.append(os.path.join(self.repo_path, file))
        return abosulute_paths
