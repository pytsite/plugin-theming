"""PytSite Theming Plugin
"""
__author__ = 'Oleksandr Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'


def plugin_load():
    from os import listdir, path, makedirs
    from pytsite import console, lang, update, tpl, reg, plugman
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
    lang.on_split_msg_id(_eh.on_lang_split_msg_id)

    # Assets
    assetman.register_package(__name__)
    assetman.on_split_location(_eh.on_assetman_split_location)
    assetman.t_js(__name__)
    assetman.t_less(__name__)
    assetman.js_module('theme-widget-themes-browser', 'theming@js/themes-browser')

    # App's logo URL resolver
    def logo_url(width: int = 0, height: int = 0, enlarge: bool = False):
        s = reg.get('theme.logo')
        try:
            return file.get(s).get_url(width=width, height=height, enlarge=enlarge) if s else \
                assetman.url('$theme@img/appicon.png')
        except file.error.FileNotFound:
            return assetman.url('$theme@img/appicon.png')

    # App's footer logo URL resolver
    def footer_logo_url(width: int = 0, height: int = 0, enlarge: bool = False):
        s = reg.get('theme.logo_footer')
        try:
            return file.get(s).get_url(width=width, height=height, enlarge=enlarge) if s else \
                assetman.url('$theme@img/appicon-footer.png')
        except file.error.FileNotFound:
            return assetman.url('$theme@img/appicon-footer.png')

    # Tpl globals and events listeners
    tpl.register_global('theme_logo_url', logo_url)
    tpl.register_global('theme_footer_logo_url', footer_logo_url)

    # Events handlers
    tpl.on_resolve_location(_eh.on_tpl_resolve_location)
    update.on_update_stage_2(_eh.on_update_stage_2)
    plugman.on_install_all(_eh.on_plugman_install_update_all)
    plugman.on_update_all(_eh.on_plugman_install_update_all)

    # Load default theme
    if not plugman.is_management_mode():
        _api.load()


def plugin_install():
    from plugins import assetman
    from . import _eh

    assetman.build(__name__)
    assetman.build_translations()

    _eh.on_update_stage_2()


def plugin_load_uwsgi():
    from pytsite import router
    from plugins import http_api, settings, assetman
    from . import _api, _eh, _http_api_controllers, _error, _settings_form

    # Settings
    settings.define('theme', _settings_form.Form, 'theming@appearance', 'fa fa-paint-brush')

    # Events handlers
    router.on_dispatch(_eh.on_router_dispatch)

    # HTTP API handlers
    http_api.handle('POST', 'theme', _http_api_controllers.Install, 'theming@install')
    http_api.handle('PATCH', 'theme', _http_api_controllers.Switch, 'theming@switch')
    http_api.handle('DELETE', 'theme', _http_api_controllers.Uninstall, 'theming@uninstall')

    # Assets
    assetman.preload('theming@js/theming.js', True)
