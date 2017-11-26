"""PytSite Theme Event Handlers
"""
import subprocess as _subprocess
from typing import Optional as _Optional
from os import path as _path
from pytsite import metatag as _metatag, console as _console, lang as _lang
from plugins import assetman as _assetman, file as _file, odm as _odm, settings as _settings
from . import _api

__author__ = 'Alexander Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'


def router_dispatch():
    """pytsite.router.dispatch
    """
    if not _assetman.is_package_registered(_api.get().package_name):
        return

    # Set current theme package
    _metatag.t_set('pytsite-theme', _api.get().package_name)

    # Set favicon URL
    favicon_fid = _settings.get('theme.favicon')
    if favicon_fid:
        try:
            f = _file.get(favicon_fid)
            _metatag.t_set('link', rel='icon', type=f.mime, href=f.get_url(width=50, height=50))
        except _file.error.FileNotFound:
            pass
    else:
        _metatag.t_set('link', rel='icon', type='image/png', href=_assetman.url('$theme@img/favicon.png'))


def lang_translate(language: str, package_name: str, msg_id: str) -> _Optional[str]:
    """pytsite.lang.translate
    """
    if package_name == _api.get().package_name:
        e = _odm.find('theme_translation') \
            .eq('language', language) \
            .eq('message_id', '{}@{}'.format(package_name, msg_id)) \
            .first()

        return e.f_get('translation') if e else None

    return None


def lang_split_msg_id(msg_id: str):
    if '@' not in msg_id:
        msg_id = '$theme@' + msg_id

    if '$theme' in msg_id:
        msg_id = msg_id.replace('$theme', _api.get().package_name)

    return msg_id


def tpl_split_location(location: str) -> str:
    if '@' not in location:
        location = '$theme@' + location

    if '$theme' in location:
        location = location.replace('$theme', _api.get().package_name)

    return location


def assetman_split_location(location: str):
    if '@' not in location:
        location = '$theme@' + location

    if '$theme' in location:
        location = location.replace('$theme', _api.get().package_name)

    return location

def update_stage_2():
    # Update all installed themes, if applicable
    for theme in _api.get_registered().values():
        if _path.exists(_path.join(theme.path, '.git')):
            _console.print_info(_lang.t('theming@updating_theme', {'name': theme.name}))
            _subprocess.call(['git', '-C', theme.path, 'pull'])
