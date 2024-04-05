import os
import sys
from importlib import import_module

from bald_spider.settings.settings_manager import SettingsManager


def _get_closest(path="."):
    path = os.path.abspath(path)
    return path


def _init_env():
    # 将最近的路径加入到环境变量中，在搜索配置文件时候防止报错
    closest = _get_closest()
    if closest:
        project_dir = os.path.dirname(closest)
        sys.path.append(project_dir)


def get_settings(settings="settings"):
    # 注意在这个地方，我们的_settings是SettingsManager对象，所以在打印的时候使用__str__转换打印信息
    _settings = SettingsManager({"111": 2})
    _settings.set_settings(settings)
    return _settings


def merge_settings(spider, settings):
    if hasattr(spider, "custom_settings"):
        custom_settings = getattr(spider, "custom_settings")
        settings.update_values(custom_settings)


def load_class(_path):
    """
    根据配置文件的路径动态的加载下载类
    """
    if not isinstance(_path,str):
        if callable(_path):
            return _path
        else:
            raise TypeError(f"args expected string or object,got: {type(_path)}")
    module, name = _path.rsplit(".", 1)
    mod = import_module(module)
    try:
        cls = getattr(mod, name)
    except Exception:
        raise NameError(f"Module {module!r} does not define any object named {name!r}")
    return cls
