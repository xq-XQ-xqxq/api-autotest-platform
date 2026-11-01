# -*- coding: utf-8 -*-
"""接口层基类：加载配置、持有请求句柄"""
import os

from common.request_handler import RequestHandler
from common.yaml_handler import read_yaml

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(ROOT_DIR, "config", "config.yaml")
DATA_DIR = os.path.join(ROOT_DIR, "data")

_config = read_yaml(CONFIG_PATH)


def get_config():
    """获取全局配置"""
    return _config


def load_data(filename):
    """加载 data 目录下的测试数据文件"""
    return read_yaml(os.path.join(DATA_DIR, filename))


class BaseApi:
    """所有接口封装类的基类"""

    def __init__(self):
        env = _config.get("env", "test")
        env_cfg = _config[env]
        self.http = RequestHandler(env_cfg["base_url"], env_cfg.get("timeout", 10))
