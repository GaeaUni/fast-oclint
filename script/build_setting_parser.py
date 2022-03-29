import json
import os
import subprocess


class BuildSettingParser:
    def __init__(self, project_path, repo_name):
        self.build_setting_json = self.get_build_settings_json(project_path, repo_name)[
            0]['buildSettings']

    def get_build_settings_json(self, project_path, repo_name):
        pod_project = os.path.join(project_path, 'Pods/Pods.xcodeproj')
        cmd = "xcodebuild -json  -configuration Debug -showBuildSettings -project {0} -scheme {1}".format(
            pod_project, repo_name)
        setting_string = subprocess.check_output(
            cmd.split(), encoding='utf-8')
        return json.loads(setting_string)

    def process(self):
        paths = self.generate_search_paths_string()
        prefix = self.generate_prefix_header_string()
        sys_root = self.generate_sys_root_string()
        framework_paths = self.generate_framework_search_paths_string()
        arch = self.generate_arch_command()
        return paths + prefix + sys_root + framework_paths + arch

    def process_header_search_paths(self):
        paths = self.build_setting_json['HEADER_SEARCH_PATHS'].split(' ')
        paths = list(map(lambda x: x.replace('"', ''), paths))
        pods_header_paths = list(
            filter(lambda x: x != '' and not "XCFrameworkIntermediates" in x, paths))
        xcframework_header_paths = list(
            filter(lambda x: "XCFrameworkIntermediates" in x, paths))
        xcframework_header_paths = self.process_xcframework_headers(
            xcframework_header_paths)
        return list(map(lambda x: repr(x), pods_header_paths + xcframework_header_paths))

    def process_prefix_header(self):
        prefix_header_path = self.build_setting_json['GCC_PREFIX_HEADER']
        return os.path.join(self.get_pods_root_path(), prefix_header_path)

    def process_xcframework_headers(self, headers):
        xcframework_headers = []
        pods_root = self.get_pods_root_path()
        xcframework_dir = self.build_setting_json['PODS_XCFRAMEWORKS_BUILD_DIR']
        xcframeworks = []
        arch = self.get_architectures()
        for header in headers:
            xcframework = header.replace(xcframework_dir, '').split('/')[1]
            xcframeworks.append(xcframework)
        for xcframework in xcframeworks:
            xcframework_path = os.path.join(
                pods_root, "{0}/{0}/{0}.xcframework/ios-{1}/Headers".format(xcframework, arch))
            xcframework_headers.append(xcframework_path)
        return xcframework_headers

    def get_pods_root_path(self):
        return self.build_setting_json['PODS_ROOT']

    def get_architectures(self):
        return self.build_setting_json['PLATFORM_PREFERRED_ARCH']

    def generate_search_paths_string(self):
        paths = self.process_header_search_paths()
        return ' -I' + ' -I'.join(paths)

    def generate_sys_root_string(self):
        sys_root = self.build_setting_json['SDKROOT']
        return ' -isysroot ' + repr(sys_root)

    def generate_prefix_header_string(self):
        prefix_header_path = self.process_prefix_header()
        return ' -include ' + repr(prefix_header_path)

    def generate_framework_search_paths_string(self):
        if self.build_setting_json.get('FRAMEWORK_SEARCH_PATHS'):
            framework_search_paths = self.build_setting_json['FRAMEWORK_SEARCH_PATHS']
            paths = framework_search_paths.split(' ')
            paths = map(lambda x: x.replace('"', '\''), paths)
            paths = list(filter(lambda x: x != '', paths))
            return ' -F' + ' -F'.join(paths)
        else:
            return ''

    def generate_arch_command(self):
        arch = self.get_architectures()
        return ' -arch ' + arch
