"""PytSite Theme Settings Form
"""
__author__ = 'Oleksandr Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'

import re
import htmler
from pytsite import lang
from plugins import widget, settings, http_api, file_ui
from . import _api

_TRANSLATION_MSG_ID_RE = re.compile('^translation_[a-z0-9._@]+')


class _ThemesBrowser(widget.Abstract):
    def __init__(self, uid: str, **kwargs):
        """Init
        """
        super().__init__(uid, **kwargs)

        self._data['http-api-ep-switch'] = http_api.endpoint('theming@switch')
        self._data['http-api-ep-uninstall'] = http_api.endpoint('theming@uninstall')

    def _get_element(self, **kwargs) -> htmler.Element:
        cont = htmler.TagLessElement()

        cont.append_child(htmler.H2(lang.t('theming@installed_themes')))

        table = cont.append_child(htmler.Table(css='table table-striped table-bordered table-hover'))

        t_head = table.append_child(htmler.Tr())
        t_head.append_child(htmler.Th(lang.t('theming@name')))
        t_head.append_child(htmler.Th(lang.t('theming@version')))
        t_head.append_child(htmler.Th(lang.t('theming@author')))
        t_head.append_child(htmler.Th(lang.t('theming@url')))
        t_head.append_child(htmler.Th(lang.t('theming@actions')))

        t_body = table.append_child(htmler.Tbody())
        for theme in _api.get_all().values():
            tr = t_body.append_child(htmler.Tr())
            tr.append_child(htmler.Td(theme.name))
            tr.append_child(htmler.Td(theme.version))
            tr.append_child(htmler.Td(htmler.A(theme.author['name'], href=theme.author['url'], target='_blank')))
            tr.append_child(htmler.Td(htmler.A(theme.url, href=theme.url, target='_blank')))

            actions = htmler.TagLessElement(child_sep='&nbsp;')

            if _api.get().name != theme.name:
                # 'Switch' button
                btn_switch = htmler.A(title=lang.t('theming@switch_to_this_theme'), href='#', role='button',
                                      css='btn btn-default btn-light btn-sm button-switch',
                                      data_package_name=theme.package_name)
                btn_switch.append_child(htmler.I(css='fa fas fa-power-off'))
                actions.append_child(btn_switch)

                # 'Uninstall' button
                btn_delete = htmler.A(title=lang.t('theming@uninstall_theme'), href='#', role='button',
                                      css='btn btn-danger btn-sm button-uninstall',
                                      data_package_name=theme.package_name)
                btn_delete.append_child(htmler.I(css='fa fas fa-trash'))
                actions.append_child(btn_delete)

            tr.append_child(htmler.Td(actions))

        return cont


class Form(settings.Form):
    def _on_setup_widgets(self):
        # Label
        self.add_widget(widget.static.HTML(
            uid='upload_header',
            weight=10,
            em=htmler.H2(lang.t('theming@install_or_update_theme'))
        ))

        # Upload theme input
        self.add_widget(widget.input.File(
            uid='file',
            weight=11,
            max_files=1,
            upload_endpoint=http_api.endpoint('theming@install'),
        ))

        # Themes browser
        self.add_widget(_ThemesBrowser(
            uid='themes',
            weight=20,
        ))

        # Label
        self.add_widget(widget.static.HTML(
            uid='theme_settings_header',
            weight=30,
            em=htmler.H2(lang.t('theming@theme_settings')),
        ))

        # Logo
        self.add_widget(file_ui.widget.ImagesUpload(
            uid='setting_logo',
            weight=40,
            label=lang.t('theming@logo'),
            skip_missing=True,
        ))

        # Footer logo
        self.add_widget(file_ui.widget.ImagesUpload(
            uid='setting_logo_footer',
            weight=50,
            label=lang.t('theming@logo_footer'),
            skip_missing=True,
        ))

        # Favicon
        self.add_widget(file_ui.widget.ImagesUpload(
            uid='setting_favicon',
            weight=60,
            label=lang.t('theming@favicon'),
            skip_missing=True,
        ))

        super()._on_setup_widgets()
