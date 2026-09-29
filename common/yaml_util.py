# 公共工具：读取YAML文件（配置和测试数据都用它读）
import os
import yaml

# 项目根目录：本文件在common/下，往上一级就是根目录
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_yaml(relative_path):
    """传入相对项目根目录的路径，比如 'data/login.yaml'，返回解析后的字典"""
    path = os.path.join(ROOT_DIR, relative_path)
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


# 配置只读一次，其他文件 from common.yaml_util import CONFIG 直接用
CONFIG = load_yaml("config/config.yaml")
