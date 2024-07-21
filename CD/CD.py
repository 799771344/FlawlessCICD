import paramiko
import logging
from common.init_yaml import yaml_data

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DeployServer:

    def __init__(self):
        ser = yaml_data['server_info']
        self.host = ser['host']
        self.username = ser['username']
        self.password = ser['password']

    def connect_to_server(self):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(self.host, username=self.username, password=self.password)
        return ssh

    def execute_command(self, ssh, command):
        stdin, stdout, stderr = ssh.exec_command(command)
        logger.info(stdout.read().decode())
        logger.error(stderr.read().decode())

    def stop_and_remove_container(self, ssh, container_name):
        stop = f"docker stop {container_name}"
        rm = f"docker rm {container_name}"
        logger.info(f"ssh-stop: {stop}")
        logger.info(f"ssh-rm: {rm}")
        self.execute_command(ssh, stop)
        self.execute_command(ssh, rm)

    def pull_latest_image(self, ssh, image_name):
        pull = f"docker pull {image_name}"
        logger.info(f"ssh-pull: {pull}")
        self.execute_command(ssh, pull)

    def run_new_container(self, ssh, container_name, image_name, port_mapping):
        run = f"docker run -d -p {port_mapping} --name {container_name} {image_name}"
        logger.info(f"ssh-run: {run}")
        self.execute_command(ssh, run)

    def deploy_to_server(self, image_name, container_name, port_mapping):
        ssh = self.connect_to_server()
        try:
            self.stop_and_remove_container(ssh, container_name)
            self.pull_latest_image(ssh, image_name)
            self.run_new_container(ssh, container_name, image_name, port_mapping)
            logger.info("部署成功!")
        finally:
            ssh.close()


def main():
    de = DeployServer()
    de.deploy_to_server(
        'registry.cn-shenzhen.aliyuncs.com/wenjj_images/dongxia_ai_web:v6',
        "dongxia_ai_web",
        "8080:8080"
    )
