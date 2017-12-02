"""PytSite Theme Package
"""
from . import _error as error
from ._api import themes_path, register, get_registered, switch, get, load, install

__author__ = 'Alexander Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'


def _init():
    from os import listdir, path, makedirs
    from pytsite import lang, router, tpl, reg
    from plugins import assetman, settings, permissions, odm, file, http_api
    from . import _settings_form, _eh, _http_api_controllers, _model

    # Translations
    lang.register_package(__name__)
    lang.on_translate(_eh.lang_translate)

    # Register assetman package and tasks
    assetman.register_package(__name__)
    assetman.t_js(__name__ + '@**')
    assetman.t_less(__name__ + '@**')
    assetman.js_module('pytsite-theme-widget-themes-browser', 'theming@js/themes-browser')
    assetman.js_module('pytsite-theme-widget-translations-edit', 'theming@js/translations-edit')

    # App's logo URL resolver
    def logo_url(width: int = 0, height: int = 0):
        s = reg.get('theme.logo')
        try:
            return file.get(s).get_url(width=width, height=height) if s else assetman.url('$theme@img/appicon.png')
        except file.error.FileNotFound:
            return assetman.url('$theme@img/appicon.png')

    # Tpl globals
    tpl.register_global('theme_logo_url', logo_url)

    # Permissions
    permissions.define_permission('theme.manage', 'theming@manage_themes', 'app')

    # ODM models
    odm.register_model('theme_translation', _model.Translation)

    # Settings
    settings.define('theme', _settings_form.Form, 'theming@appearance', 'fa fa-paint-brush',
                    'theme.manage')

    # Event listeners
    router.on_dispatch(_eh.router_dispatch)
    lang.on_split_msg_id(_eh.lang_split_msg_id)
    tpl.on_split_location(_eh.tpl_split_location)
    assetman.on_split_location(_eh.assetman_split_location)

    # HTTP API handlers
    http_api.handle('POST', 'theme', _http_api_controllers.Install, 'theming@install')
    http_api.handle('PATCH', 'theme', _http_api_controllers.Switch, 'theming@switch')
    http_api.handle('DELETE', 'theme', _http_api_controllers.Uninstall, 'theming@uninstall')

    themes_dir = themes_path()

    # Create themes directory
    if not path.isdir(themes_dir):
        makedirs(themes_dir, 0o755)


    themes_names = sorted(listdir(themes_dir))
    if themes_names:
        # Register all themes found in the themes directory
        for name in themes_names:
            if not path.isdir(themes_dir) or name.startswith('_') or name.startswith('.'):
                continue

            register('themes.' + name)

        # Load default theme
        load()

    else:
        raise error.NoThemesFound(themes_dir)


_init()
