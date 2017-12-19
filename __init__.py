"""PytSite Theming Plugin
"""
__author__ = 'Alexander Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'


def plugin_load():
    from os import listdir, path, makedirs
    from pytsite import console, lang
    from plugins import assetman, settings
    from . import _api, _error, _eh, _settings_form

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
    lang.on_split_msg_id(_eh.lang_split_msg_id)
    lang.on_translate(_eh.lang_translate)

    # Assetman resources
    assetman.register_package(__name__)
    assetman.on_split_location(_eh.assetman_split_location)
    assetman.t_js(__name__)
    assetman.t_less(__name__)
    assetman.js_module('pytsite-theme-widget-themes-browser', 'theming@js/themes-browser')
    assetman.js_module('pytsite-theme-widget-translations-edit', 'theming@js/translations-edit')

    # Settings
    settings.define('theme', _settings_form.Form, 'theming@appearance', 'fa fa-paint-brush', 'theme.manage')

    # Load default theme
    _api.load()


def plugin_load_uwsgi():
    from pytsite import router, tpl, reg
    from plugins import assetman, permissions, odm, file, http_api
    from . import _api, _eh, _http_api_controllers, _model, _error

    # App's logo URL resolver
    def logo_url(width: int = 0, height: int = 0):
        s = reg.get('theme.logo')
        try:
            return file.get(s).get_url(width=width, height=height) if s else assetman.url('$theme@img/appicon.png')
        except file.error.FileNotFound:
            return assetman.url('$theme@img/appicon.png')

    # Tpl globals and events listeners
    tpl.register_global('theme_logo_url', logo_url)
    tpl.on_split_location(_eh.tpl_split_location)

    # Permissions
    permissions.define_permission('theme.manage', 'theming@manage_themes', 'app')

    # ODM models
    odm.register_model('theme_translation', _model.Translation)

    # Event listeners
    router.on_dispatch(_eh.router_dispatch)

    # HTTP API handlers
    http_api.handle('POST', 'theme', _http_api_controllers.Install, 'theming@install')
    http_api.handle('PATCH', 'theme', _http_api_controllers.Switch, 'theming@switch')
    http_api.handle('DELETE', 'theme', _http_api_controllers.Uninstall, 'theming@uninstall')
