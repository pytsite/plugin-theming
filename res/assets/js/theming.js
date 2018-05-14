require(['assetman', 'jquery'], function (assetman, $) {
    assetman.definePackageAlias('default', $('meta[name="pytsite-theme"]').attr('content'));
});
