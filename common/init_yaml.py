import yaml
from common.file_path import file_path


yaml_file = "FlawlessCICD.yaml"
# 读取YAML文件
with open("{}/conf/{}".format(file_path, yaml_file), "r", encoding="utf-8") as stream:
    try:
        yaml_data = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        yaml_data = {}
        print(exc)
