import subprocess
import imp


def install_brew(module_name):
    cmd = "which {0}".format(module_name)
    result = subprocess.run(cmd.split(), encoding='utf-8').returncode
    if result == 0:
        return
    # brew install module_name
    cmd = "brew install {0}".format(module_name)
    result = subprocess.run(cmd.split(), encoding='utf-8').returncode
    if result != 0:
        print("brew install {0} failed".format(module_name))
        assert False


def install_python_module(module_name):
    try:
        imp.find_module(module_name)
    except ImportError:
        python_path = subprocess.check_output(
            "which python3".split(), encoding='utf-8').strip()
        cmd = "{0} -m pip install {1}".format(python_path, module_name)
        result = subprocess.run(cmd.split(), encoding='utf-8').returncode
        if result != 0:
            print("install {0} failed".format(module_name))
            assert False
