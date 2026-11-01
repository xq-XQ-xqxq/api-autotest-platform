# -*- coding: utf-8 -*-
"""YAML 文件读取工具"""
import yaml


def read_yaml(file_path):
    """读取 YAML 文件，返回 Python 对象"""
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
