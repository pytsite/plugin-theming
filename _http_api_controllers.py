"""PytSite Theme HTTP API
"""
__author__ = 'Oleksandr Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'

from os import close as os_close
from werkzeug.datastructures import FileStorage
from pytsite import routing, lang, http, util
from plugins import auth
from . import _api


class Install(routing.Controller):
    def exec(self):
        if not auth.get_current_user().is_admin:
            raise self.forbidden()

        file = self.args.pop('file')  # type: FileStorage

        if not file:
            # It is important to return all input arguments back (except file, of course)
            self.args.update({'error': lang.t('theming@theme_file_not_provided')})
            raise self.server_error(response=http.JSONResponse(dict(self.args)))

        if file.mimetype != 'application/zip':
            # It is important to return all input arguments back (except file, of course)
            self.args.update({'error': lang.t('theming@only_zip_files_supported')})
            raise self.server_error(response=http.JSONResponse(dict(self.args)))

        # Save received file to temporary directory
        tmp_file_id, tmp_file_path = util.mk_tmp_file('.zip')
        file.save(tmp_file_path)
        os_close(tmp_file_id)

        # Install theme from ZIP file
        try:
            _api.install(tmp_file_path)
        except Exception as e:
            self.args.update({'error': lang.t('theming@theme_installation_failed', {'msg': str(e)})})
            raise self.server_error(response=http.JSONResponse(dict(self.args)))

        # It is important to return all input arguments back (except file, of course)
        self.args.update({
            'message': lang.t('theming@wait_theme_being_installed'),
            'eval': 'setTimeout(function() {window.location.reload()}, 3000)',
        })

        return self.args


class Switch(routing.Controller):
    def exec(self):
        if not auth.get_current_user().is_admin:
            raise self.forbidden()

        _api.switch(self.arg('package_name'))

        return {'status': True}


class Uninstall(routing.Controller):
    def exec(self):
        if not auth.get_current_user().is_admin:
            raise self.forbidden()

        _api.uninstall(self.arg('package_name'))

        return {'status': True}
