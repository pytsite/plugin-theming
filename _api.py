"""PytSite Theme API Functions
"""
__author__ = 'Oleksandr Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'

from typing import Dict
from os import path, unlink, chdir, getcwd, rmdir
from shutil import rmtree, move
from zipfile import ZipFile
from glob import glob
from semaver import VersionRange
from pytsite import reg, logger, util, reload, plugman, pip
from . import _theme, _error

_themes_path = path.join(reg.get('paths.root'), 'themes')

# All registered themes
_fallback_theme_name = {}  # type: Dict[str, _theme.Theme]

# Default theme
_default = None  # type: _theme.Theme

# Currently loaded theme
_loaded = None  # type: _theme.Theme


def _extract_archive(src_file_path: str, dst_dir_path):
    """Extract theme archive
    """
    # Extract all files
    with ZipFile(src_file_path) as z_file:
        z_file.extractall(dst_dir_path)

    # Check if the archive contents only single directory, move its files up
    orig_cwd = getcwd()
    chdir(dst_dir_path)
    files_list = glob('*')
    if len(files_list) == 1 and path.isdir(files_list[0]):
        top_directory = files_list[0]
        chdir(top_directory)

        f_names = glob('*') + glob('.*')
        for f_name in f_names:
            if f_name not in ('.', '..'):
                move(f_name, dst_dir_path)

        chdir('..')
        rmdir(top_directory)

    chdir(orig_cwd)

    logger.debug("Theme files successfully extracted from file '{}' to directory '{}'".
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
        reg.put('theme.current', package_name)  # Mark theme as current
        reg.put('theme.compiled', False)  # Mark that assets compilation needed
        reload.reload()


def register(package_name: str) -> _theme.Theme:
    """Register a theme
    """
    global _default

    if package_name in _fallback_theme_name:
        raise _error.ThemeAlreadyRegistered(package_name)

    theme = _theme.Theme(package_name)

    if not _default or theme.package_name == reg.get('theme.current'):
        _default = theme

    _fallback_theme_name[package_name] = theme

    return theme


def get_all() -> Dict[str, _theme.Theme]:
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
    logger.debug('Requested theme installation from zip-file {}'.format(archive_path))

    # Create temporary directory
    tmp_dir_path = util.mk_tmp_dir(subdir='theme')

    try:
        # Extract archive to the temporary directory
        _extract_archive(archive_path, tmp_dir_path)

        # Try to initialize the theme to ensure everything is okay
        theme = _theme.Theme('tmp.theme.{}'.format(path.basename(tmp_dir_path)))

        # Install required pip packages
        for pkg_name, pkg_version in theme.requires['packages'].items():
            logger.info("Theme '{}' requires pip package '{} {}', going to install it".
                        format(theme.name, pkg_name, pkg_name, pkg_version))
            pip.install(pkg_name, pkg_version, True, reg.get('debug'))

        # Install required plugins
        for p_name, p_version in theme.requires['plugins'].items():
            if not plugman.is_installed(p_name, VersionRange(p_version)):
                logger.info("Theme '{}' requires plugin '{}', installing...".format(theme.name, p_name, p_version))
                plugman.install(p_name, VersionRange(p_version))

        # Theme has been successfully initialized, so now it can be moved to the 'themes' package
        dst_path = path.join(_themes_path, theme.name)
        if path.exists(dst_path):
            logger.warn("Existing theme installation at '{}' will be replaced with new one".format(dst_path))
            rmtree(dst_path)

        # Move directory to the final location
        move(tmp_dir_path, dst_path)
        logger.debug("'{}' has been successfully moved to '{}'".format(tmp_dir_path, dst_path))

        reload.reload()

    finally:
        # Remove temporary directory
        if path.exists(tmp_dir_path):
            rmtree(tmp_dir_path)

        # Remove ZIP file
        if delete_zip_file:
            unlink(archive_path)


def uninstall(package_name: str):
    """Uninstall a theme
    """
    theme = get(package_name)

    if theme.name == get().name:
        raise RuntimeError('Cannot uninstall current theme, please switch to another theme before uninstallation')

    del _fallback_theme_name[package_name]
    rmtree(theme.path)

    logger.info("Theme '{}' has been successfully uninstalled from '{}'".format(theme.name, theme.path))
