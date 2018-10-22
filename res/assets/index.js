import $ from 'jquery';
import {lang} from '@pytsite/assetman';
import httpApi from '@pytsite/http-api';
import setupWidget from '@pytsite/widget';

setupWidget('plugins.theming._settings_form._ThemesBrowser', widget => {
    widget.em.find('.button-switch').click(function () {
        if (confirm(lang.t('theming@theme_switch_confirmation'))) {
            $(this).closest('table').find('.btn').addClass('disabled');
            $(this).find('i').removeClass().addClass('fa fa-spin fa-spinner');

            const rData = {package_name: $(this).data('packageName')};
            httpApi.patch(widget.data('httpApiEpSwitch'), rData).always(function () {
                setTimeout(function () {
                    location.reload();
                }, 1000)
            });
        }
    });

    widget.em.find('.button-uninstall').click(function () {
        if (confirm(lang.t('theming@theme_uninstall_confirmation'))) {
            $(this).closest('table').find('.btn').addClass('disabled');
            $(this).find('i').removeClass().addClass('fa fa-spin fa-spinner');

            const rData = {package_name: $(this).data('packageName')};
            httpApi.del(widget.data('httpApiEpUninstall'), rData).always(function () {
                setTimeout(function () {
                    location.reload();
                }, 1000)
            });
        }
    });
});
