import { createVuetify } from 'vuetify';
import { createApp } from 'vue';
import eventBus from './bus';
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import Home from './Home.vue';
import Kitchen from './components/Kitchen.vue';

frappe.provide('frappe.PosApp');


frappe.PosApp.hsposapp = class {
    constructor({ parent }) {
        this.$parent = $(document);
        this.page = parent.page;
        this.make_body();

    }
    make_body() {
        // Force clear PWA caches, service worker, and IndexedDB once for v6 update
        if (localStorage.getItem('hspos_cache_version') !== 'v6') {
            try {
                indexedDB.deleteDatabase('highspeed_pos_db');
                if ('serviceWorker' in navigator) {
                    navigator.serviceWorker.getRegistrations().then(registrations => {
                        for (let registration of registrations) {
                            registration.unregister();
                        }
                    });
                }
                if ('caches' in window) {
                    caches.keys().then(names => {
                        for (let name of names) {
                            caches.delete(name);
                        }
                    });
                }
                localStorage.setItem('hspos_cache_version', 'v6');
                console.log('Cleared IndexedDB, Caches, and Service Worker for v6');
                window.location.reload();
                return;
            } catch (e) {
                console.error('Failed to clear cache', e);
            }
        }

        this.$el = this.$parent.find('.main-section');
        const lang = frappe.boot.lang || 'en';
        const vuetify = createVuetify(
            {
                components,
                directives,
                locale: {
                    locale: lang,
                    fallback: 'en',
                    rtl: {
                        ar: true,
                        he: true,
                        fa: true,
                        ur: true,
                    }
                },
                theme: {
                    defaultTheme: 'light',
                    themes: {
                        light: {
                            dark: false,
                            colors: {
                                background: '#FFFFFF',
                                surface: '#FFFFFF',
                                'surface-bright': '#FFFFFF',
                                'surface-light': '#EEEEEE',
                                'surface-variant': '#424242',
                                'on-surface-variant': '#EEEEEE',
                                primary: '#0097A7',
                                'primary-darken-1': '#00838F',
                                secondary: '#00BCD4',
                                'secondary-darken-1': '#0097A7',
                                accent: '#9575CD',
                                success: '#66BB6A',
                                info: '#2196F3',
                                warning: '#FF9800',
                                error: '#E86674',
                                orange: '#E65100',
                                golden: '#A68C59',
                                badge: '#F5528C',
                                customPrimary: '#085294',
                            },
                            variables: {}
                        },
                    },
                },
            }
        );
        const app = createApp(Home)
        app.use(eventBus);
        app.use(vuetify)
        app.mount(this.$el[0]);

        if (!document.querySelector('link[rel="manifest"]')) {
            const link = document.createElement('link');
            link.rel = 'manifest';
            link.href = '/manifest.json';
            document.head.appendChild(link);
        }

        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/sw.js')
                .catch(err => console.error('SW registration failed', err));
        }
    }
    setup_header() {

    }

};

frappe.PosApp.kitchen = class {
    constructor(page) {
        this.page = page;
        this.make_body();
    }
    make_body() {
        this.$el = $(this.page.body);
        this.$el.empty();

        const lang = frappe.boot.lang || 'en';
        const vuetify = createVuetify({
            components,
            directives,
            locale: {
                locale: lang,
                fallback: 'en',
                rtl: {
                    ar: true,
                    he: true,
                    fa: true,
                    ur: true,
                }
            },
            theme: {
                defaultTheme: 'dark',
                themes: {
                    dark: {
                        dark: true,
                        colors: {
                            background: '#080c14',
                            surface: '#0d1117',
                            primary: '#58a6ff',
                            secondary: '#161b22',
                            success: '#2ea44f',
                            warning: '#d29922',
                            error: '#f85149',
                        }
                    }
                }
            }
        });
        const app = createApp(Kitchen);
        app.use(eventBus);
        app.use(vuetify);
        app.mount(this.$el[0]);
    }
};
