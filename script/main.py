
import installer
from linter import CommitFilesLinter
import argparse
from compile_json_generator import CompileJsonGenerator, compile_commands_json_path
from commit_file_parser import CommitFileParser
import os
import json
import sys
from diff_parser import DiffParser


def need_regenerate_compile_commands_json(commit_files):
    json_files = []
    if os.path.exists(compile_commands_json_path):
        with open(compile_commands_json_path, 'r') as f:
            data = json.load(f)
            for item in data:
                json_files.append(item["file"])
        for item in commit_files:
            if item not in json_files:
                return True
        return False
    else:
        return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-project_path")
    parser.add_argument("-main_project_path")
    args = parser.parse_args()
    project_path = args.project_path
    main_project_path = args.main_project_path
    
    if not project_path:
        # 获取entry_point的路径
        project_path = os.getcwd()
    if not main_project_path:
        main_project_path = os.path.dirname(project_path)

    project_path = os.path.realpath(project_path)
    main_project_path = os.path.realpath(main_project_path)

    project_name = project_path.split("/")[-1]
    commit_files = CommitFileParser(project_path).process()
    generator = CompileJsonGenerator(project_name, main_project_path)
    if need_regenerate_compile_commands_json(commit_files):
        print("generate compile_commands.json")
        generator.process(commit_files)
    else:
        print("delete files not commit")
        generator.delete_clean_files(commit_files)

    diff_parser = DiffParser()
    diff_json = json.loads(diff_parser.process(
        "git diff --cached", project_path))

    linter = CommitFilesLinter()
    linter.process(diff_json)


if __name__ == "__main__":
    main()
