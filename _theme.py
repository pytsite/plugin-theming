"""PytSite Theme
"""
__author__ = 'Oleksandr Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'

from importlib import import_module as _import_module
from os import path as _path, makedirs as _makedirs
from pytsite import logger as _logger, package_info as _package_info, reg as _reg, plugman as _plugman, lang as _lang, \
    tpl as _tpl
from . import _error


class Theme:
    """PytSite Theme
    """

    def __init__(self, package_name: str):
        """Init
        """
        # Load package data from 'theme.json'
        pkg_data = _package_info.data(package_name)

        self._package_name = package_name
        self._path = _package_info.resolve_package_path(package_name)
        self._name = pkg_data['name']
        self._version = pkg_data['version']
        self._description = pkg_data['description']
        self._author = pkg_data['author']
        self._url = pkg_data['url']
        self._requires = pkg_data['requires']

        self._module = None
        self._is_loaded = False

    def load(self):
        """Load the theme
        """
        from plugins import assetman

        # Check for requirements
        try:
            _package_info.check_requirements(self._package_name)
        except _package_info.error.Error as e:
            raise RuntimeError('Error while loading theme {}: {}'.format(self._package_name, e))

        # Create translations directory
        lang_dir = _path.join(self._path, 'res', 'lang')
        if not _path.exists(lang_dir):
            _makedirs(lang_dir, 0o755, True)

        # Create translation stub files
        for lng in _lang.langs():
            lng_f_path = _path.join(lang_dir, '{}.yml'.format(lng))
            if not _path.exists(lng_f_path):
                with open(lng_f_path, 'wt'):
                    pass

        # Register translation resources
        _lang.register_package(self._package_name)

        # Register template resources
        tpl_path = _path.join(self._path, 'res', 'tpl')
        if not _path.exists(tpl_path):
            _makedirs(tpl_path, 0o755, True)
        _tpl.register_package(self._package_name)

        # Register assetman resources
        assets_path = _path.join(self._path, 'res', 'assets')
        if not _path.exists(assets_path):
            _makedirs(assets_path, 0o755, True)
        assetman.register_package(self._package_name)

        # Load required plugins
        for p_name, p_version in self._requires['plugins'].items():
            _plugman.load(p_name, p_version)

        # Load theme's module
        try:
            self._module = _import_module(self._package_name)
            if hasattr(self._module, 'theme_load') and callable(self._module.theme_load):
                self._module.theme_load()

            # theme_load_{env.type}() hook
            env_type = _reg.get('env.type')
            hook_names = ['theme_load_{}'.format(env_type)]
            if env_type == 'wsgi':
                hook_names.append('theme_load_uwsgi')
            for hook_name in hook_names:
                if hasattr(self._module, hook_name):
                    getattr(self._module, hook_name)()

            _logger.debug("Theme '{}' successfully loaded".format(self._package_name))
        except Exception as e:
            raise _error.ThemeLoadError("Error while loading theme package '{}': {}".format(self._package_name, e))

        # Compile assets
        if not _reg.get('theme.compiled'):
            assetman.setup()
            assetman.build(self._package_name)
            assetman.build_translations()
            _reg.put('theme.compiled', True)

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
    def module(self):
        return self._module

    @property
    def is_loaded(self) -> bool:
        return self._is_loaded

    @property
    def settings(self) -> dict:
        return _reg.get('theme.theme_' + self._name, {})
