from CI.CI import DeployDocker
from CD.CD import DeployServer


def CICD(images_url, docker_path, app_name, port_mapping):
    CI = DeployDocker(docker_path, app_name, remote_docker_url=images_url)
    full_tag = CI.deploy_docker(app_name)
    CD = DeployServer()
    CD.deploy_to_server(full_tag, app_name, port_mapping)


def main():
    docker_path = r"E:\work\github\dongxia_ai_web"
    images_url = "registry.cn-shenzhen.aliyuncs.com/wenjj_images"
    app_name = "dongxia_ai_web"
    port_mapping = "8080:8080"
    CICD(images_url, docker_path, app_name, port_mapping)
