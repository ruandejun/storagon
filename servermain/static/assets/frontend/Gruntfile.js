module.exports = function(grunt){
    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),
        watch: {
            files: [
                'app/storagon/*.js'
            ],
            tasks: ['uglify']
        },
        uglify: {
            options: {
                    banner: '/*! <%= pkg.name %> <%= grunt.template.today("yyyy-mm-dd") %> */\n'
            },
            storagon: {
                    src: [
                        'app/storagon/app.js',
                        'app/storagon/App_filter.js',
                        'app/filemanager_ver2/route.js',
                        'app/page/route.js',
                        'app/user/route.js',
                        'app/layout/headerView.js',
                        'app/user/authenticateView.js',
                        'app/user/sidebarView.js',
                        'app/user/accountView.js',
                        'app/user/billView.js',
                        'app/user/sessionView.js',
                        'app/user/exchangePointView.js',
                        'app/user/affiliateView.js',
                        'app/user/resellerView.js',
                        'app/user/redeemView.js',
                        'app/premium/route.js',
                        'app/premium/premiumView.js',
                        'app/premium/paymentView.js',
                        'app/storagon/ClientAPI_service.js',
                        'app/storagon/RESTFullAPI_service.js'
                    ],
                    dest: 'app/storagon.min.js'

            },
            storagonlibrary: {
                    src: [
                        "js/clientAPI_SDK.js",
                        "js/RESTFullAPI_SDK.js"
                    ],
                    dest: 'js/storagon_library.min.js'
            },
            junshare: {
                    src: [
                        'app_junshare/storagon/app.js',
                        'app_junshare/storagon/App_filter.js',
                        'app_junshare/filemanager_ver2/route.js',
                        'app_junshare/page/route.js',
                        'app_junshare/user/route.js',
                        'app_junshare/layout/headerView.js',
                        'app_junshare/user/authenticateView.js',
                        'app_junshare/user/sidebarView.js',
                        'app_junshare/user/accountView.js',
                        'app_junshare/user/billView.js',
                        'app_junshare/user/sessionView.js',
                        'app_junshare/user/exchangePointView.js',
                        'app_junshare/user/affiliateView.js',
                        'app_junshare/user/resellerView.js',
                        'app_junshare/user/redeemView.js',
                        'app_junshare/premium/route.js',
                        'app_junshare/premium/premiumView.js',
                        'app_junshare/premium/paymentView.js',
                        'app_junshare/storagon/ClientAPI_service.js',
                        'app_junshare/storagon/RESTFullAPI_service.js'
                    ],
                    dest: 'app_junshare/junshare.min.js'

            },
            junsharelibrary: {
                    src: [
                        "js/clientAPI_SDKjunshare.js",
                        "js/RESTFullAPI_SDK.js"
                    ],
                    dest: 'js/junshare_library.min.js'
            }
        }
    });

    grunt.loadNpmTasks('grunt-contrib-uglify');
    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.registerTask('default', ['uglify']);
};
