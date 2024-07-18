# FlawlessCICD是什么：
    本地可使用的的CI/CD持续集成（Continuous Integration）和持续交付/部署（Continuous Delivery/Deployment），以最方便快捷的方式将本地项目部署到服务器上

# 使用方法：
    创建conf/FlawlessCICD.yaml配置文件，
    内容：
        images_repository_info: # 镜像仓库登录信息
          username: 用户名
          password: 密码
        
        server_info:    # 部署项目的服务器信息
          host: ip
          username: 用户名
          password: 密码
    安装：
        pip install FlawlessCICD
    使用：
        


# fix:
    如果报错docker.credentials.errors.StoreError: docker-credential-desktop not installed or not available in PATH
    解决方法1：
        先登录试试
    解决方法2：
        import os
        os.environ['DOCKER_CREDENTIAL_HELPER'] = "/path/to/docker-credential-desktop"
        self.client = docker.from_env()
    解决方法3：
        检查Docker配置： 检查~/.docker/config.json文件（在Windows上可能是%USERPROFILE%\.docker\config.json）
        将credsStore设置成""，即："credsStore": ""
    解决方法4：
        import docker
        client = docker.from_env(credstore_env={"DOCKER_CREDENTIAL_HELPER": "/path/to/docker-credential-desktop"})