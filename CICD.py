from CI.CI import DeployDocker
from CD.CD import DeployServer


def CICD(images_url, docker_path, app_name, container_name, port_mapping):
    CI = DeployDocker(docker_path, app_name, remote_docker_url=images_url)
    full_tag = CI.deploy_docker(app_name)
    CD = DeployServer()
    CD.deploy_to_server(full_tag, container_name, port_mapping)


def main():
    docker_path = r"项目根目录（包含DOCKERFILE）"
    images_url = "镜像url"
    app_name = "镜像仓库名"
    container_name = "容器名"
    port_mapping = "端口映射"
    CICD(images_url, docker_path, app_name, container_name, port_mapping)

if __name__ == '__main__':
    main()