"""PytSite Theme Settings Form
"""
__author__ = 'Alexander Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'

import re as _re
from pytsite import lang as _lang, html as _html
from plugins import widget as _widget, file as _file, settings as _settings, http_api as _http_api, \
    file_ui as _file_ui
from . import _api

_TRANSLATION_MSG_ID_RE = _re.compile('^translation_[a-z0-9._@]+')


class _ThemesBrowser(_widget.Abstract):
    def __init__(self, uid: str, **kwargs):
        """Init
        """
        super().__init__(uid, **kwargs)

        self._data['http-api-ep-switch'] = _http_api.endpoint('theming@switch')
        self._data['http-api-ep-uninstall'] = _http_api.endpoint('theming@uninstall')
        self._js_module = 'theme-widget-themes-browser'

    def _get_element(self, **kwargs) -> _html.Element:
        cont = _html.TagLessElement()

        cont.append(_html.H2(_lang.t('theming@installed_themes')))

        table = cont.append(_html.Table(css='table table-striped table-bordered table-hover'))

        t_head = table.append(_html.Tr())
        t_head.append(_html.Th(_lang.t('theming@name')))
        t_head.append(_html.Th(_lang.t('theming@version')))
        t_head.append(_html.Th(_lang.t('theming@author')))
        t_head.append(_html.Th(_lang.t('theming@url')))
        t_head.append(_html.Th(_lang.t('theming@actions')))

        t_body = table.append(_html.TBody())
        for theme in _api.get_all().values():
            tr = t_body.append(_html.Tr())
            tr.append(_html.Td(theme.name))
            tr.append(_html.Td(theme.version))
            tr.append(_html.Td(_html.A(theme.author['name'], href=theme.author['url'], target='_blank')))
            tr.append(_html.Td(_html.A(theme.url, href=theme.url, target='_blank')))

            actions = _html.TagLessElement(child_sep='&nbsp;')

            if _api.get().name != theme.name:
                # 'Switch' button
                btn_switch = _html.A(title=_lang.t('theming@switch_to_this_theme'), href='#', role='button',
                                     css='btn btn-default btn-xs button-switch', data_package_name=theme.package_name)
                btn_switch.append(_html.I(css='fa fa-power-off'))
                actions.append(btn_switch)

                # 'Uninstall' button
                btn_delete = _html.A(title=_lang.t('theming@uninstall_theme'), href='#', role='button',
                                     css='btn btn-danger btn-xs button-uninstall', data_package_name=theme.package_name)
                btn_delete.append(_html.I(css='fa fa-trash'))
                actions.append(btn_delete)

            tr.append(_html.Td(actions))

        return cont


class Form(_settings.Form):
    def _on_setup_widgets(self):
        # Label
        self.add_widget(_widget.static.HTML(
            uid='upload_header',
            weight=10,
            em=_html.H2(_lang.t('theming@install_or_update_theme'))
        ))

        # Upload theme input
        self.add_widget(_widget.input.File(
            uid='file',
            weight=11,
            max_files=1,
            upload_endpoint=_http_api.endpoint('theming@install'),
        ))

        # Themes browser
        self.add_widget(_ThemesBrowser(
            uid='themes',
            weight=20,
        ))

        # Label
        self.add_widget(_widget.static.HTML(
            uid='theme_settings_header',
            weight=30,
            em=_html.H2(_lang.t('theming@theme_settings')),
        ))

        # Logo
        self.add_widget(_file_ui.widget.ImagesUpload(
            uid='setting_logo',
            weight=31,
            label=_lang.t('theming@logo'),
            skip_missing=True,
        ))

        # Favicon
        self.add_widget(_file_ui.widget.ImagesUpload(
            uid='setting_favicon',
            weight=40,
            label=_lang.t('theming@favicon'),
            skip_missing=True,
        ))

        super()._on_setup_widgets()
