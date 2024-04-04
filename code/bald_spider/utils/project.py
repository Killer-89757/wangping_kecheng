from bald_spider.settings.settings_manager import SettingsManager


def get_settings(settings="settings"):
    # 注意在这个地方，我们的_settings是SettingsManager对象，所以在打印的时候使用__str__转换打印信息
    _settings = SettingsManager({"111":2})
    _settings.set_settings(settings)
    return _settings
