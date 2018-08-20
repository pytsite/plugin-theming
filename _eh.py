"""PytSite Theme Event Handlers
"""
__author__ = 'Oleksandr Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'

import subprocess as _subprocess
from os import path as _path
from pytsite import metatag as _metatag, console as _console, lang as _lang, reg as _reg, plugman as _plugman, \
    package_info as _package_info, pip as _pip
from plugins import assetman as _assetman, file as _file
from . import _api


def on_router_dispatch():
    """pytsite.router.dispatch
    """
    if not _assetman.is_package_registered(_api.get().package_name):
        return

    # Set current theme package
    _metatag.t_set('pytsite-theme', _api.get().package_name)

    # Set favicon URL
    favicon_fid = _reg.get('theme.favicon')
    if favicon_fid:
        try:
            f = _file.get(favicon_fid)
            _metatag.t_set('link', rel='icon', type=f.mime, href=f.get_url(width=50, height=50))
        except _file.error.FileNotFound:
            pass
    else:
        _metatag.t_set('link', rel='icon', type='image/png', href=_assetman.url('$theme@img/favicon.png'))


def on_lang_split_msg_id(msg_id: str):
    if '@' not in msg_id:
        msg_id = '$theme@' + msg_id

    if '$theme' in msg_id:
        msg_id = msg_id.replace('$theme', _api.get().package_name)

    return msg_id


def on_tpl_resolve_location(location: str) -> str:
    if '@' not in location:
        location = '$theme@' + location

    if '$theme' in location:
        location = location.replace('$theme', _api.get().package_name)

    return location


def on_assetman_split_location(location: str):
    if '@' not in location:
        location = '$theme@' + location

    if '$theme' in location:
        location = location.replace('$theme', _api.get().package_name)

    return location


def on_update_stage_2():
    # Update all installed themes
    for theme in _api.get_all().values():
        if _path.exists(_path.join(theme.path, '.git')):
            _console.print_info(_lang.t('theming@updating_theme', {'name': theme.name}))
            _subprocess.call(['git', '-C', theme.path, 'pull'])


def on_plugman_install_update_all():
    # Install/update requirements for all installed themes
    for theme in _api.get_all().values():
        _console.print_info(_lang.t('theming@installing_theme_requirements', {'name': theme.name}))

        # Install or upgrade required pip packagers
        for pkg_spec in _package_info.requires_packages(theme.package_name, use_cache=False):
            _pip.install(pkg_spec, _pip.is_installed(pkg_spec))

        # Install or update required plugins
        for plugin_spec in _package_info.requires_plugins(theme.package_name, use_cache=False):
            _plugman.install(plugin_spec)
