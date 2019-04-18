"""PytSite Theme API Functions
"""
__author__ = 'Oleksandr Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'

from typing import Dict as _Dict
from os import path as _path, unlink as _unlink, chdir as _chdir, getcwd as _getcwd, rmdir as _rmdir
from shutil import rmtree as _rmtree, move as _move
from zipfile import ZipFile as _ZipFile
from glob import glob as _glob
from pytsite import reg as _reg, logger as _logger, util as _util, reload as _reload, plugman as _plugman, pip as _pip, \
    semver as _semver
from . import _theme, _error

_themes_path = _path.join(_reg.get('paths.root'), 'themes')

# All registered themes
_fallback_theme_name = {}  # type: _Dict[str, _theme.Theme]

# Default theme
_default = None  # type: _theme.Theme

# Currently loaded theme
_loaded = None  # type: _theme.Theme


def _extract_archive(src_file_path: str, dst_dir_path):
    """Extract theme archive
    """
    # Extract all files
    with _ZipFile(src_file_path) as z_file:
        z_file.extractall(dst_dir_path)

    # Check if the archive contents only single directory, move its files up
    orig_cwd = _getcwd()
    _chdir(dst_dir_path)
    files_list = _glob('*')
    if len(files_list) == 1 and _path.isdir(files_list[0]):
        top_directory = files_list[0]
        _chdir(top_directory)

        f_names = _glob('*') + _glob('.*')
        for f_name in f_names:
            if f_name not in ('.', '..'):
                _move(f_name, dst_dir_path)

        _chdir('..')
        _rmdir(top_directory)

    _chdir(orig_cwd)

    _logger.debug("Theme files successfully extracted from file '{}' to directory '{}'".
                  format(src_file_path, dst_dir_path))


def themes_path():
    """Get absolute filesystem path to themes location
    """
    return _themes_path


def get(package_name: str = None) -> _theme.Theme:
    """Get a theme
    """
    if not _fallback_theme_name:
        raise _error.NoThemesRegistered()

    if not package_name:
        return _loaded or _default

    try:
        return _fallback_theme_name[package_name]
    except KeyError:
        raise _error.ThemeNotRegistered(package_name)


def switch(package_name: str):
    """Switch current theme
    """
    if package_name not in _fallback_theme_name:
        raise _error.ThemeNotRegistered(package_name)

    # Switch only if it really necessary
    if package_name != get().package_name:
        _reg.put('theme.current', package_name)  # Mark theme as current
        _reg.put('theme.compiled', False)  # Mark that assets compilation needed
        _reload.reload()


def register(package_name: str) -> _theme.Theme:
    """Register a theme
    """
    global _default

    if package_name in _fallback_theme_name:
        raise _error.ThemeAlreadyRegistered(package_name)

    theme = _theme.Theme(package_name)

    if not _default or theme.package_name == _reg.get('theme.current'):
        _default = theme

    _fallback_theme_name[package_name] = theme

    return theme


def get_all() -> _Dict[str, _theme.Theme]:
    """Get all registered themes
    """
    return _fallback_theme_name


def load(package_name: str = None) -> _theme.Theme:
    """Load theme
    """
    global _loaded

    # Only one theme can be loaded
    if _loaded:
        raise _error.ThemeLoadError("Cannot load theme '{}', because another theme '{}' is already loaded".
                                    format(package_name, _loaded.package_name))

    # Load theme
    _loaded = get(package_name).load()

    return _loaded


def install(archive_path: str, delete_zip_file: bool = True):
    """Install a theme from a zip-file
    """
    _logger.debug('Requested theme installation from zip-file {}'.format(archive_path))

    # Create temporary directory
    tmp_dir_path = _util.mk_tmp_dir(subdir='theme')

    try:
        # Extract archive to the temporary directory
        _extract_archive(archive_path, tmp_dir_path)

        # Try to initialize the theme to ensure everything is okay
        theme = _theme.Theme('tmp.theme.{}'.format(_path.basename(tmp_dir_path)))

        # Install required pip packages
        for pkg_name, pkg_version in theme.requires['packages'].items():
            _logger.info("Theme '{}' requires pip package '{} {}', going to install it".
                         format(theme.name, pkg_name, pkg_name, pkg_version))
            _pip.install(pkg_name, pkg_version, True, _reg.get('debug'))

        # Install required plugins
        for p_name, p_version in theme.requires['plugins'].items():
            if not _plugman.is_installed(p_name, _semver.VersionRange(p_version)):
                _logger.info("Theme '{}' requires plugin '{}', installing...".format(theme.name, p_name, p_version))
                _plugman.install(p_name, _semver.VersionRange(p_version))

        # Theme has been successfully initialized, so now it can be moved to the 'themes' package
        dst_path = _path.join(_themes_path, theme.name)
        if _path.exists(dst_path):
            _logger.warn("Existing theme installation at '{}' will be replaced with new one".format(dst_path))
            _rmtree(dst_path)

        # Move directory to the final location
        _move(tmp_dir_path, dst_path)
        _logger.debug("'{}' has been successfully moved to '{}'".format(tmp_dir_path, dst_path))

        _reload.reload()

    finally:
        # Remove temporary directory
        if _path.exists(tmp_dir_path):
            _rmtree(tmp_dir_path)

        # Remove ZIP file
        if delete_zip_file:
            _unlink(archive_path)


def uninstall(package_name: str):
    """Uninstall a theme
    """
    theme = get(package_name)

    if theme.name == get().name:
        raise RuntimeError('Cannot uninstall current theme, please switch to another theme before uninstallation')

    del _fallback_theme_name[package_name]
    _rmtree(theme.path)

    _logger.info("Theme '{}' has been successfully uninstalled from '{}'".format(theme.name, theme.path))
