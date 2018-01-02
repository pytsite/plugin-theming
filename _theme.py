"""PytSite Theme
"""
__author__ = 'Alexander Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'

from importlib import import_module as _import_module
from os import path as _path, makedirs as _makedirs
from pytsite import logger as _logger, package_info as _package_info, reg as _reg, plugman as _plugman, util as _util
from . import _error


class Theme:
    """PytSite Theme
    """

    def __init__(self, package_name: str):
        """Init
        """
        # Load package data from JSON file
        pkg_data = _package_info.data(package_name)

        self._package_name = package_name
        self._path = _package_info.resolve_package_path(package_name)
        self._name = pkg_data['name']
        self._version = pkg_data['version']
        self._description = pkg_data['description']
        self._author = pkg_data['author']
        self._url = pkg_data['url']
        self._requires = pkg_data['requires']

        self._package = None
        self._is_loaded = False

    def load(self):
        """Load the theme
        """
        from pytsite import lang, tpl
        from plugins import assetman

        # Check for required pip packages
        for pkg_spec in self._requires['packages']:
            if not _util.is_pip_package_installed(pkg_spec):
                _util.install_pip_package(pkg_spec)

        # Check for required plugins
        for plugin_spec in self._requires['plugins']:
            if not _plugman.is_installed(plugin_spec):
                _plugman.install(plugin_spec)

        # Create translations directory
        lang_dir = _path.join(self._path, 'lang')
        if not _path.exists(lang_dir):
            _makedirs(lang_dir, 0o755, True)

        # Create translation stub files
        for lng in lang.langs():
            lng_f_path = _path.join(lang_dir, '{}.yml'.format(lng))
            if not _path.exists(lng_f_path):
                with open(lng_f_path, 'wt'):
                    pass

        # Register translations package
        lang.register_package(self._package_name, 'lang')

        # Register templates package
        tpl_path = _path.join(self._path, 'tpl')
        if not _path.exists(tpl_path):
            _makedirs(tpl_path, 0o755, True)
        tpl.register_package(self._package_name, 'tpl')

        # Register assetman package
        assets_path = _path.join(self._path, 'assets')
        if not _path.exists(assets_path):
            _makedirs(assets_path, 0o755, True)
        assetman.register_package(self._package_name, 'assets')

        # Load required plugins
        for plugin_spec in self._requires['plugins']:
            _plugman.load(plugin_spec)

        # Load theme's module
        try:
            self._package = _import_module(self._package_name)
            _logger.debug("Theme '{}' successfully loaded from '{}'".format(self._package_name, self._path))
        except Exception as e:
            raise _error.ThemeLoadError("Error while loading theme package '{}': {}".format(self._package_name, e))

        # Compile assets
        if not _reg.get('theme.compiled'):
            try:
                assetman.build(self._package_name)
                assetman.build_translations()
                _reg.put('theme.compiled', True)
            except assetman.error.NoTasksDefined as e:
                _logger.warn(str(e))

        self._is_loaded = True

        return self

    @property
    def package_name(self) -> str:
        return self._package_name

    @property
    def path(self) -> str:
        return self._path

    @property
    def name(self) -> str:
        return self._name

    @property
    def version(self) -> str:
        return self._version

    @property
    def description(self) -> dict:
        return self._description

    @property
    def author(self) -> dict:
        return self._author

    @property
    def url(self) -> str:
        return self._url

    @property
    def requires(self) -> dict:
        return self._requires

    @property
    def package(self):
        return self._package

    @property
    def is_loaded(self) -> bool:
        return self._is_loaded

    @property
    def settings(self) -> dict:
        return _reg.get('theme.theme_' + self._name, {})
