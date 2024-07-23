import docker
import logging
import subprocess
from docker.errors import ImageNotFound, APIError
from common.init_yaml import yaml_data

# 配置日志记录器
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DeployDocker:

    def __init__(self, file_path, app_name, remote_docker_url=""):
        self.file_path = file_path
        self.app_name = app_name
        self.remote_docker_url = remote_docker_url
        self.client = docker.from_env()

    def run_tests(self):
        """运行单元测试"""
        "python -m unittest discover tests"
        logger.info("开始运行单元测试...")
        test_command = ["python", "-m", "unittest", "discover", "tests"]
        result = subprocess.run(test_command, cwd=self.file_path, capture_output=True, text=True)
        if result.returncode != 0:
            logger.error(f"单元测试失败:\n{result.stdout}\n{result.stderr}")
            return False
        logger.info("单元测试通过")
        return True

    def static_code_analysis(self):
        """运行静态代码分析"""
        logger.info("开始运行静态代码分析...")
        analysis_command = ["pylint", self.file_path]
        result = subprocess.run(analysis_command, capture_output=True, text=True)
        if result.returncode != 0:
            logger.warning(f"静态代码分析发现问题:\n{result.stdout}")
        else:
            logger.info("静态代码分析通过")
        return True  # 即使有警告也继续流程

    def check_and_remove_image(self):
        try:
            images = self.client.images.list(name=self.app_name)
            for image in images:
                if f'{self.app_name}:latest' in image.tags:
                    logger.info(f"找到镜像 {self.app_name}")
                    self.client.images.remove(image.tags[0], force=True)
                    logger.info(f"已删除镜像 {self.app_name}")
                    break
                else:
                    logger.info(f"未找到镜像 {self.app_name}")
        except ImageNotFound:
            logger.info(f"未找到镜像 {self.app_name}")
        except APIError as e:
            logger.error(f"删除镜像时发生错误: {str(e)}")

    def docker_build(self):
        self.check_and_remove_image()
        try:
            image, build_logs = self.client.images.build(
                path=self.file_path,
                tag=self.app_name,
                rm=True
            )
            for line in build_logs:
                if 'stream' in line:
                    logger.info(line['stream'].strip())
            logger.info(f"镜像 {self.app_name} 构建完成")
            return image.id
        except APIError as e:
            logger.error(f"构建镜像时发生错误: {str(e)}")
            return None

    def tag_image(self, image_id, repository, tag):
        try:
            image = self.client.images.get(image_id)
            full_tag = f"{self.remote_docker_url}/{repository}:{tag}"
            image.tag(full_tag, tag=tag)
            logger.info(f"成功为镜像打标签: {full_tag}")
        except ImageNotFound:
            logger.error(f"未找到镜像 ID: {image_id}")
        except APIError as e:
            logger.error(f"打标签时发生错误: {str(e)}")

    def get_latest_version(self, repository):
        try:
            logger.info(f"{self.remote_docker_url}/{repository}")
            tags = self.client.images.list(name=repository)
            logger.info(tags)
            if not tags:
                return "v0"
            image_tags = tags[0].tags
            if not image_tags:
                return "v0"
            logger.info(image_tags)
            version = image_tags[-1].split(':')[-1]
            if version:
                return f"v{version}"
            else:
                return "v0"
        except APIError as e:
            logger.error(f"获取最新版本时发生错误: {str(e)}")
            return "v0"

    def get_all_versions(self, repository):
        try:
            images = self.client.images.list(name=f"{self.remote_docker_url}/{repository}")
            versions = []
            for image in images:
                for tag in image.tags:
                    version = tag.split(':')[-1]
                    if version.startswith('v'):
                        versions.append(version)
            return sorted(versions, key=lambda x: int(x[1:]), reverse=True)
        except APIError as e:
            logger.error(f"获取所有版本时发生错误: {str(e)}")
            return []

    def remove_old_versions(self, repository, keep=1):
        versions = self.get_all_versions(repository)
        if len(versions) <= keep:
            return

        for version in versions[keep:]:
            try:
                image_name = f"{self.remote_docker_url}/{repository}:{version}"
                self.client.images.remove(image_name, force=True)
                logger.info(f"已删除旧版本镜像: {image_name}")
            except ImageNotFound:
                logger.warning(f"未找到镜像: {image_name}")
            except APIError as e:
                logger.error(f"删除镜像 {image_name} 时发生错误: {str(e)}")

    def increment_version(self, version):
        version_num = version.replace("v", "")
        if version_num == "latest":
            return "v1"
        return f"v{int(version_num) + 1}"

    def login_registry(self):
        try:
            self.client.login(
                username=yaml_data['images_repository_info']['username'],
                password=yaml_data['images_repository_info']['password'],
                registry=self.remote_docker_url
            )
            logger.info(f"成功登录到镜像仓库 {self.remote_docker_url}")
        except APIError as e:
            logger.error(f"登录镜像仓库时发生错误: {str(e)}")
            raise

    def push_remote_image(self, repository, tag):
        if not self.remote_docker_url:
            raise Exception("未设置远程镜像仓库地址")

        full_tag = f"{self.remote_docker_url}/{repository}:{tag}"

        try:
            self.login_registry()
            logger.info(f"开始推送镜像到 {full_tag}")

            for line in self.client.api.push(full_tag, stream=True, decode=True):
                if 'status' in line:
                    logger.info(f"{line['status']} - {line.get('progress', '')}")
                elif 'error' in line:
                    logger.error(f"错误: {line['error']}")
                else:
                    logger.info(line)

            logger.info(f"镜像成功推送到 {full_tag}")
            return full_tag
        except APIError as e:
            logger.error(f"推送镜像时发生错误: {str(e)}")

    def update_deployment(self, full_tag):
        """更新Kubernetes部署"""
        logger.info(f"开始更新Kubernetes部署...")
        # 这里应该使用Kubernetes API或kubectl命令来更新部署
        # 以下是一个示例,实际使用时需要根据您的Kubernetes配置进行调整
        update_command = ["kubectl", "set", "image", f"deployment/{self.app_name}", f"{self.app_name}={full_tag}"]
        result = subprocess.run(update_command, capture_output=True, text=True)
        if result.returncode != 0:
            logger.error(f"更新部署失败:\n{result.stderr}")
            return False
        logger.info("Kubernetes部署已更新")
        return True

    def deploy_docker(self, repository):
        # 运行测试
        # if not self.run_tests():
        #     logger.error("单元测试失败,部署终止")
        #     return

        # 运行静态代码分析
        # if not self.static_code_analysis():
        #     logger.warning("静态代码分析发现问题,但继续部署")
        # self.check_and_remove_image()
        # 构建镜像
        image_id = self.docker_build()
        if not image_id:
            logger.error("镜像构建失败,部署终止")
            return

        # 获取新版本号并打标签
        version = self.get_latest_version(repository)
        new_version = self.increment_version(version)
        logger.info(f"新版本号: {new_version}")
        self.tag_image(image_id, repository, new_version)

        # 推送镜像
        full_tag = self.push_remote_image(repository, new_version)
        if not full_tag:
            logger.error("推送镜像失败,部署终止")
            return

        # 删除旧版本镜像
        # self.remove_old_versions(repository, keep=1)

        # 更新Kubernetes部署
        # if self.update_deployment(full_tag):
        #     logger.info("部署完成")
        # else:
        #     logger.error("部署失败")

        return full_tag


def main():
    docker_url = "registry.cn-shenzhen.aliyuncs.com/wenjj_images"
    de = DeployDocker("E:\work\github\dongxia_ai_web", "dongxia_ai_web", remote_docker_url=docker_url)
    de.deploy_docker("dongxia_ai_web")
