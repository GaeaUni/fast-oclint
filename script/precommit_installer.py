import subprocess
import installer
import os
import re


class PrecommitInstaller:
    def __init__(self):
        self.install_precommit()
        self.install_git_config_hook()
        self.install_xcode_select()

    def install_xcode_select(self):
        result = subprocess.run("xcode-select -v".split(), encoding='utf-8').returncode
        if result != 0:
            xcode_select_path = "/Library/Developer/CommandLineTools"
            if os.path.isdir(xcode_select_path):
                subprocess.run("xcode-select --reset".split(), encoding='utf-8')
            else:
                subprocess.run("xcode-select --install".split(), encoding='utf-8')

    def install_git_config_hook(self):
        os.system("git config --global init.templateDir ~/.git-template")
        os.system("pre-commit init-templatedir ~/.git-template")

    def process(self, main_project_path):
        dev_pods = self.find_all_developer_pod_path(main_project_path)
        self.install_precommit_in_dev_pod(dev_pods)
        self.install_bootstrap_shell(main_project_path, dev_pods)
        self.install_precommit_config(dev_pods)
        # self.uninstall_precommit_in_dev_pod(dev_pods)

    def install_precommit(self):
        installer.install_brew("pre-commit")

    def install_bootstrap_shell(self, main_project_path, dev_pod_paths):
        dir = os.path.dirname(__file__)
        main_py = os.path.join(dir, "main.py")
        for path in dev_pod_paths:
            bootstrap_path = os.path.join(path, ".git/hooks/fast-oclint.sh")
            if os.path.isfile(os.path.join(path, ".git")):
                with open(os.path.join(path, ".git"), "r") as f:
                    content = f.read()
                real_git_path = re.compile("gitdir: (.*)").findall(content)[0]
                bootstrap_path = os.path.join(path, real_git_path, "hooks/fast-oclint.sh")
                bootstrap_path = os.path.realpath(bootstrap_path)
            cmd = "python3 {0} -main_project_path {1} -project_path {2}".format(repr(main_py), repr(main_project_path), repr(path))
            with open(bootstrap_path, "w") as f:
                f.write(cmd)

    def uninstall_precommit_in_dev_pod(self, dev_pods):
        for pod_path in dev_pods:
            cmd = "pre-commit uninstall"
            result = subprocess.run(
                cmd.split(), encoding='utf-8', cwd=pod_path, stdout=subprocess.PIPE).returncode
            if result != 0:
                print("pre-commit uninstall failed in {0}".format(pod_path))
            else:
                print("pre-commit uninstall success in {0}".format(pod_path))

    def install_precommit_in_dev_pod(self, dev_pods):
        for pod_path in dev_pods:
            cmd = "pre-commit install"
            result = subprocess.run(
                cmd.split(), encoding='utf-8', cwd=pod_path, stdout=subprocess.PIPE).returncode
            if result != 0:
                print("pre-commit install failed in {0}".format(pod_path))
                assert False
            else:
                print("pre-commit install success in {0}".format(pod_path))

    def install_precommit_config(self, dev_pod_paths):
        dir = os.path.dirname(__file__)
        template_path = os.path.join(dir, ".pre-commit-config.yaml.template")
        with open(template_path, "r") as f:
            template = f.read()
        for path in dev_pod_paths:
            if os.path.isfile(os.path.join(path, ".git")):
                with open(os.path.join(path, ".git"), "r") as f:
                    content = f.read()
                real_git_path = re.compile("gitdir:(.*)").findall(content)[0]
                yaml = template.format(real_git_path)
            else:
                yaml = template.format('.git')
            config_path = os.path.join(path, ".pre-commit-config.yaml")
            with open(config_path, "w") as f:
                f.write(yaml)

    def find_all_developer_pod_path(self, main_project_path):
        with open(os.path.join(main_project_path, "podfile"), "r") as f:
            content = f.read()
        dev_pods = re.compile(""":path=>['"](.*)['"]""").findall(content)
        pods = []
        for pod in dev_pods:
            if not pod.startswith("/"):
                pod = os.path.join(main_project_path, pod)
            pods.append(pod)
        return pods

def main():
    installer = PrecommitInstaller()
    path = os.getcwd()
    print("start precommit installer {0}".format(path))
    installer.process(path)


if __name__ == "__main__":
    main()
