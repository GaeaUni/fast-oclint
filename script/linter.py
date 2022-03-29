
import subprocess
from compile_json_generator import compile_commands_json_path
import os
import installer


class CommitFilesLinter:
    def __init__(self):
        self.install()

    def install(self):
        installer.install_brew("oclint")
        installer.install_python_module("bs4")

    def process(self, commit_diffs=None):
        path = os.path.dirname(compile_commands_json_path)
        cmd = "oclint-json-compilation-database -v -- -report-type html -o {0}/oclint.html".format(
            path)
        cmd += self.line_rule()
        result = subprocess.run(
            cmd.split(), cwd=path, encoding='utf-8')
        html_path = "{0}/oclint.html".format(path)
        if commit_diffs:
            violate_count = self.filter_ourself_commit_lines(
                commit_diffs, html_path)
            print("violate count: {0}".format(violate_count))
        if result.returncode >= 6:
            print("OCLint return compile error", result.stdout)
            self.open_html(html_path)
            assert False
        else:
            print("OCLint return compile success")
            self.open_html(html_path)
        return result

    def open_html(self, path):
        os.system("open {0}".format(path))

    def filter_ourself_commit_lines(self, line_diffs, html_path):
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(open(html_path), "html.parser")
        for tr in soup.select("tbody > tr")[1:]:
            file = tr.select("td")[0].string
            line = int(tr.select("td")[1].string.split(":")[0])
            priority = tr.select("td")[4].string
            if priority == "error":
                continue
            diff_lines = line_diffs[file]
            removable = True
            for diff_line in diff_lines:
                start_line = diff_line["startLine"]
                end_line = diff_line["endLine"]
                if start_line <= line and line <= end_line:
                    removable = False
                    break
            if not removable:
                tr.attrs["bgcolor"] = "0xff0000"
                # tr.decompose()
        with open(html_path, "w") as f:
            f.write(str(soup))
        return len(soup.select("tbody > tr")) - 1

    def line_rule(self):
        return " -rc=LONG_LINE=150 "
