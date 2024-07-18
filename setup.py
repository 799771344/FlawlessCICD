# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="FlawlessCICD",
    version="0.2.0",
    author="wen",
    author_email="799771344@qq.com",
    description="本地可使用的的CI/CD持续集成（Continuous Integration）和持续交付/部署（Continuous Delivery/Deployment），以最方便快捷的方式将本地项目部署到服务器上",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/799771344/FlawlessCICD",
    packages=find_packages(),
    install_requires=[
        "PyYAML~=6.0.1",
        "docker~=7.1.0",
        "paramiko~=3.4.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10.0',
)