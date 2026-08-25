exports.config = {
    runner: 'local',
    port: 4723,
    path: '/',
    specs: [
        './specs/**/*.spec.js'
    ],
    exclude: [],
    maxInstances: 1,
    capabilities: [{
        platformName: 'Android',
        'appium:automationName': 'UiAutomator2',
        'appium:deviceName': 'Android Emulator',
        'appium:app': process.env.APK_PATH || './app-release.apk',
        'appium:appPackage': 'com.nutriguide.app',
        'appium:appActivity': '.MainActivity',
        'appium:autoGrantPermissions': true,
        'appium:newCommandTimeout': 300
    }],
    logLevel: 'info',
    bail: 0,
    baseUrl: 'http://localhost',
    waitforTimeout: 10000,
    connectionRetryTimeout: 120000,
    connectionRetryCount: 3,
    services: ['appium'],
    framework: 'mocha',
    reporters: ['spec'],
    mochaOpts: {
        ui: 'bdd',
        timeout: 60000
    }
};
