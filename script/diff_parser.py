import subprocess
import re
import os
import json
import sys


class DiffParser:
    def __init__(self) -> None:
        pass

    def process(self, cmd, path):
        shell = "{0}/diff_detail.sh".format(os.path.dirname(__file__))
        diffString: str = subprocess.run(
            ['sh', shell, cmd], cwd=path, stdout=subprocess.PIPE, encoding='utf-8').stdout
        reg = re.compile("(?<=diff --git )[\s\S]+?(?=\ndiff --git |$)")
        diffs = reg.findall(diffString)
        jsonObj = {}
        for diff in diffs:
            fileName = self.getDiffFileName(diff, path)
            if fileName.endswith(".mm") or fileName.endswith(".m"):
                segments = self.diff2LineNumbers(diff)
                self.appendJson(jsonObj, segments, fileName)
        text = json.dumps(jsonObj, indent=4, sort_keys=True)
        return text

    def appendJson(self, jsonObj, segments, fileName):
        arr = []
        for segment in segments:
            arr.append({"startLine": segment[0], "endLine": segment[1]})
        if len(arr) > 0:
            jsonObj[fileName] = arr

    def diff2LineNumbers(self, diff: str):
        tokens = self.getDiffTokens(diff)
        i = 0
        segments = []
        size = len(tokens)
        while (i < size):
            token = tokens[i]
            if token[0] == '+' or token[0] == '-':
                j = i
                start = None
                end = None
                while (j < size and (tokens[j][0] == '+' or tokens[j][0] == '-')):
                    token = tokens[j]
                    if token[2] and start == None:
                        start = token[2]
                    if token[2]:
                        end = token[2]
                    j += 1
                if start == None and j < size:
                    start = tokens[j][2]
                if end == None and j < size:
                    end = tokens[j][2]
                i = j
                if start and end:
                    segments.append((int(start), int(end)))
            else:
                i += 1
        return segments

    def getDiffFileName(self, diff: str, path: str):
        result = re.match("^a(\S+)", diff)
        filePath = path + result.group(1)
        return filePath

    def getDiffTokens(self, diff: str):
        lines = diff.split('\n')
        tokens = []
        for line in lines:
            result = re.match("^([+-]|\s)\s*?(\d+)?\s+(\d+)?:", line)
            if not result:
                continue
            tokens.append((result.group(1), result.group(2), result.group(3)))
        return tokens
