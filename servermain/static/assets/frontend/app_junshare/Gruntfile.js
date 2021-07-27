module.exports = function(grunt){
    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),
        watch: {
            files: [
                '**/*.js',
                '!junshare.min.js'
            ],
            tasks: ['uglify']
        },
        uglify: {
            options: {
                banner: '/*! <%= pkg.name %> <%= grunt.template.today("yyyy-mm-dd") %> */\n'
            },
            build: {
                src: [
                    'storagon/app.js',
                    'storagon/App_filter.js',
                    'filemanager_ver2/route.js',
                    'page/route.js',
                    'user/route.js',
                    'layout/headerView.js',
                    'user/authenticateView.js',
                    'user/sidebarView.js',
                    'user/accountView.js',
                    'user/billView.js',
                    'user/sessionView.js',
                    'user/exchangePointView.js',
                    'user/affiliateView.js',
                    'user/resellerView.js',
                    'user/redeemView.js',
                    'premium/route.js',
                    'premium/premiumView.js',
                    'premium/paymentView.js',
                    'storagon/ClientAPI_service.js',
                    'storagon/RESTFullAPI_service.js'
                ],
                dest: '<%= pkg.name %>.min.js'
            }
        }
    });

    grunt.loadNpmTasks('grunt-contrib-uglify');
    grunt.registerTask('default', ['uglify']);
};
