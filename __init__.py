"""PytSite Theming Plugin
"""
__author__ = 'Alexander Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'


def plugin_load():
    from os import listdir, path, makedirs
    from pytsite import console, lang, update, tpl, reg
    from plugins import assetman, file
    from . import _api, _error, _eh

    themes_dir = _api.themes_path()

    # Create themes directory
    if not path.isdir(themes_dir):
        makedirs(themes_dir, 0o755)

    # Register all themes found in the themes directory
    themes_names = sorted(listdir(themes_dir))
    if themes_names:
        for name in themes_names:
            if not path.isdir(themes_dir) or name.startswith('_') or name.startswith('.'):
                continue

            try:
                _api.register('themes.' + name)
            except _error.ThemeInitError as e:
                console.print_warning("Theme '{}' wasn't registered: {}".format(name, e))
    else:
        raise _error.NoThemesFound(themes_dir)

    # Language resources
    lang.register_package(__name__)

    # Language events handlers
    lang.on_split_msg_id(_eh.lang_split_msg_id)

    # Assets
    assetman.register_package(__name__)
    assetman.on_split_location(_eh.assetman_split_location)
    assetman.t_js(__name__)
    assetman.t_less(__name__)
    assetman.js_module('theme-widget-themes-browser', 'theming@js/themes-browser')
    assetman.js_module('theme-widget-translations-edit', 'theming@js/translations-edit')

    # App's logo URL resolver
    def logo_url(width: int = 0, height: int = 0):
        s = reg.get('theme.logo')
        try:
            return file.get(s).get_url(width=width, height=height) if s else assetman.url('$theme@img/appicon.png')
        except file.error.FileNotFound:
            return assetman.url('$theme@img/appicon.png')

    # Tpl globals and events listeners
    tpl.register_global('theme_logo_url', logo_url)

    # Events handlers
    tpl.on_split_location(_eh.tpl_split_location)
    update.on_update(_eh.update)

    # Load default theme
    _api.load()


def plugin_install():
    from plugins import assetman

    assetman.build(__name__)
    assetman.build_translations()


def plugin_load_uwsgi():
    from pytsite import router
    from plugins import http_api, settings
    from . import _api, _eh, _http_api_controllers, _error, _settings_form

    # Settings
    settings.define('theme', _settings_form.Form, 'theming@appearance', 'fa fa-paint-brush')

    # Events handlers
    router.on_dispatch(_eh.router_dispatch)

    # HTTP API handlers
    http_api.handle('POST', 'theme', _http_api_controllers.Install, 'theming@install')
    http_api.handle('PATCH', 'theme', _http_api_controllers.Switch, 'theming@switch')
    http_api.handle('DELETE', 'theme', _http_api_controllers.Uninstall, 'theming@uninstall')
