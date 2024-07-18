from CICD import CICD


def main():
    docker_path = r"需要进行打包的项目的根目录"
    images_url = "镜像仓库"
    app_name = "镜像名"
    port_mapping = "主机与dokcer的映射，如：8080:8080"
    CICD(images_url, docker_path, app_name, port_mapping)
