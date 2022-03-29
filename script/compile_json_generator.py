import json
from math import ceil
import sys
import os
from build_setting_parser import BuildSettingParser

workPath = sys.path[0]
compile_commands_json_path = "{0}/../tmp/compile_commands.json".format(
    workPath)
compile_commands_json_part_path = "{0}/../tmp/{1}/compile_commands.json"


class CompileJsonGenerator:
    def __init__(self, repo_name, project_path):
        self.repo_name = repo_name
        self.project_path = project_path
        self.compile_commands_json = []

    def process(self, commit_files):
        self.init_items(commit_files)
        self.add_setting_commands()
        self.add_source_file_command()
        self.add_arc_command()
        self.add_objective_c_command()
        self.add_modules_command()
        self.write_to_tmp()

    def delete_clean_files(self, commit_files):
        with open(compile_commands_json_path, 'r') as f:
            self.compile_commands_json = json.load(f)
        result = []
        for item in self.compile_commands_json:
            if item["file"] in commit_files:
                result.append(item)
        self.compile_commands_json = result
        self.write_to_tmp()

    def init_items(self, commit_files):
        for commit_file in commit_files:
            if self.is_source_file(commit_file):
                item = self.process_file(commit_file)
                if item:
                    self.compile_commands_json.append(item)

    def write_to_tmp(self):
        os.makedirs(os.path.dirname(compile_commands_json_path), exist_ok=True)
        with open(compile_commands_json_path, 'w+') as f:
            json.dump(self.compile_commands_json, f, indent=4)

    def add_setting_commands(self):
        build_setting_parser = BuildSettingParser(
            self.project_path, self.repo_name)
        command = build_setting_parser.process()
        for item in self.compile_commands_json:
            item["command"] += command

    def add_source_file_command(self):
        for item in self.compile_commands_json:
            item["command"] += " -c " + repr(item["file"])

    def add_arc_command(self):
        for item in self.compile_commands_json:
            item["command"] += " -fobjc-arc -fobjc-weak "

    def add_objective_c_command(self):
        for item in self.compile_commands_json:
            path = item["file"]
            if self.is_cpp_file(path):
                item["command"] += " -std=gnu++14 -stdlib=libc++ -ObjC++ "
            else:
                item["command"] += " -std=gnu11 -ObjC "

    def add_modules_command(self):
        for item in self.compile_commands_json:
            item["command"] += " -fmodules "

    def is_cpp_file(self, file_path):
        if file_path.endswith(".h"):
            source_file_path = file_path.replace(".h", ".mm")
            if os.path.exists(source_file_path):
                return True
            source_file_path = file_path.replace(".h", ".cc")
            if os.path.exists(source_file_path):
                return True
            source_file_path = file_path.replace(".h", ".cpp")
            if os.path.exists(source_file_path):
                return True
            # 不存在m文件 暂时认为是c++?
            source_file_path = file_path.replace(".h", ".m")
            if not os.path.exists(source_file_path):
                return True
        elif file_path.endswith(".mm") or file_path.endswith(".cc") or file_path.endswith(".cpp"):
            return True
        return False

    def is_source_file(self, file_path):
        ext = os.path.splitext(file_path)
        if ext[1] in [".h", ".m", ".mm", ".cc", ".cpp"]:
            return True
        return False

    def process_file(self, commit_file):
        item = {}
        item["file"] = commit_file
        item["directory"] = "/"
        item["command"] = "/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/clang "
        return item

    def split_compile_json(self):
        with open(compile_commands_json_path, 'r') as f:
            self.compile_commands_json = json.load(f)
        # TODO: split compile_commands_json to multiple files
        size = 500
        part_count = self.compile_commands_json.__len__() / size
        part_count = ceil(part_count)
        compile_json = self.compile_commands_json
        part_jsons = [compile_json[i:i + size]
                      for i in range(0, len(compile_json), size)]
        for index, part_json in enumerate(part_jsons):
            part_json_path = compile_commands_json_part_path.format(
                workPath, "part_{0}".format(index))
            self.write_to_tmp(part_json)
