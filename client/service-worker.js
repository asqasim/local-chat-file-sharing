"use strict";

const CACHE_NAME = "localshare-v1";

const STATIC_ASSETS = [
    "/",
    "/index.html",

    "/manifest.json",

    "/css/style.css",

    "/js/app.js",

    "/favicon.ico",

    "/assets/icons/icon-192.png",
    "/assets/icons/icon-512.png",
    "/assets/icons/maskable-512.png",
    "/assets/icons/apple-touch-icon.png",
];

self.addEventListener("install", (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            return cache.addAll(STATIC_ASSETS);
        })
    );

    self.skipWaiting();
});

self.addEventListener("activate", (event) => {
    event.waitUntil(
        caches.keys().then((keys) =>
            Promise.all(
                keys
                    .filter((key) => key !== CACHE_NAME)
                    .map((key) => caches.delete(key))
            )
        )
    );

    self.clients.claim();
});

self.addEventListener("fetch", (event) => {
    if (event.request.method !== "GET") {
        return;
    }

    event.respondWith(
        caches.match(event.request).then((cachedResponse) => {
            if (cachedResponse) {
                return cachedResponse;
            }

            return fetch(event.request);
        })
    );
});