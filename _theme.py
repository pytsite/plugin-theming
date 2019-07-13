"""PytSite Theme
"""
__author__ = 'Oleksandr Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'

from importlib import import_module
from os import path, makedirs
from semaver import VersionRange
from pytsite import logger, package_info, reg, plugman, lang, tpl
from . import _error


class Theme:
    """PytSite Theme
    """

    def __init__(self, package_name: str):
        """Init
        """
        # Load package data from 'theme.json'
        pkg_data = package_info.data(package_name)

        self._package_name = package_name
        self._path = package_info.resolve_package_path(package_name)
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
            package_info.check_requirements(self._package_name)
        except package_info.error.Error as e:
            raise RuntimeError('Error while loading theme {}: {}'.format(self._package_name, e))

        # Create translations directory
        lang_dir = path.join(self._path, 'res', 'lang')
        if not path.exists(lang_dir):
            makedirs(lang_dir, 0o755, True)

        # Create translation stub files
        for lng in lang.langs():
            lng_f_path = path.join(lang_dir, '{}.yml'.format(lng))
            if not path.exists(lng_f_path):
                with open(lng_f_path, 'wt'):
                    pass

        # Register translation resources
        lang.register_package(self._package_name)

        # Register template resources
        tpl_path = path.join(self._path, 'res', 'tpl')
        if not path.exists(tpl_path):
            makedirs(tpl_path, 0o755, True)
        tpl.register_package(self._package_name)

        # Register assetman resources
        assets_path = path.join(self._path, 'res', 'assets')
        if not path.exists(assets_path):
            makedirs(assets_path, 0o755, True)
        assetman.register_package(self._package_name)

        # Load required plugins
        for pn, pv in self._requires['plugins'].items():
            plugman.load(pn, VersionRange(pv))

        # Load theme's module
        try:
            self._module = import_module(self._package_name)
            if hasattr(self._module, 'theme_load') and callable(self._module.theme_load):
                self._module.theme_load()

            # theme_load_{env.type}() hook
            env_type = reg.get('env.type')
            hook_names = ['theme_load_{}'.format(env_type)]
            if env_type == 'wsgi':
                hook_names.append('theme_load_uwsgi')
            for hook_name in hook_names:
                if hasattr(self._module, hook_name):
                    getattr(self._module, hook_name)()

            logger.debug("Theme '{}' successfully loaded".format(self._package_name))
        except Exception as e:
            raise _error.ThemeLoadError("Error while loading theme package '{}': {}".format(self._package_name, e))

        # Compile assets
        if not reg.get('theme.compiled'):
            assetman.setup()
            assetman.build(self._package_name)
            reg.put('theme.compiled', True)

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
        return reg.get('theme.theme_' + self._name, {})
