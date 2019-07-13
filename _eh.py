"""PytSite Theme Event Handlers
"""
__author__ = 'Oleksandr Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'

from pytsite import metatag, reg, plugman
from plugins import assetman, file
from . import _api


def on_app_load():
    # Load default theme
    if not plugman.is_management_mode():
        _api.load()

def on_router_dispatch():
    """pytsite.router.dispatch
    """
    if not assetman.is_package_registered(_api.get().package_name):
        return

    # Set current theme package
    metatag.t_set('pytsite-theme', _api.get().package_name)

    # Set favicon URL
    favicon_fid = reg.get('theme.favicon')
    if favicon_fid:
        try:
            f = file.get(favicon_fid)
            metatag.t_set('link', rel='icon', type=f.mime, href=f.get_url(width=50, height=50))
        except file.error.FileNotFound:
            pass
    else:
        metatag.t_set('link', rel='icon', type='image/png', href=assetman.url('$theme@img/favicon.png'))


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
