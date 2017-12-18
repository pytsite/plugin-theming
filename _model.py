"""PytSite Language UI ODM Models
"""
__author__ = 'Alexander Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'

from pytsite import lang as _lang
from plugins import odm as _odm


class Translation(_odm.model.Entity):
    def _setup_fields(self):
        self.define_field(_odm.field.String('message_id', required=True))
        self.define_field(_odm.field.String('translation', required=True))
        self.define_field(_odm.field.String('language', required=True, default=_lang.get_current()))

    def _setup_indexes(self):
        self.define_index([('message_id', _odm.I_ASC), ('language', _odm.I_ASC)], True)
