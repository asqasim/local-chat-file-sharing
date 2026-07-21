"use strict";

class LocalShareApp {

    constructor() {

        this.elements = {

            chat: document.getElementById("chat"),

            messageInput: document.getElementById("message-input"),

            sendButton: document.getElementById("send-button"),

            attachButton: document.getElementById("attach-button"),

            fileInput: document.getElementById("file-input"),

            connectionStatus: document.getElementById("connection-status"),
        };

    }

    async initialize() {

        await this.registerServiceWorker();

        socket.connect();
        await window.chat.load();

        setInterval(
            () => socket.sendHeartbeat(),
            30000,
        );

        this.registerEventListeners();

        this.startHealthMonitor();

    }

    async registerServiceWorker() {

        if (!("serviceWorker" in navigator)) {
            return;
        }

        try {

            await navigator.serviceWorker.register(
                "/service-worker.js"
            );

        } catch (error) {

            console.error(error);

        }

    }

    registerEventListeners() {

        this.elements.sendButton.addEventListener(
            "click",
            () => this.sendMessage()
        );

        this.elements.attachButton.addEventListener(
            "click",
            () => this.elements.fileInput.click()
        );

        this.elements.messageInput.addEventListener(
            "keydown",
            (event) => {

                if (event.key === "Enter") {
                    this.sendMessage();
                }

            }
        );

    }

    async startHealthMonitor() {

        await this.checkHealth();

        setInterval(
            () => this.checkHealth(),
            CONFIG.HEALTH_CHECK_INTERVAL
        );

    }

    async checkHealth() {

        try {

            await api.health();

            this.setConnectionStatus("Connected");

        }

        catch {

            this.setConnectionStatus("Waiting for PC...");

        }

    }

    async sendMessage() {

        const text =
            this.elements.messageInput.value.trim();

        if (!text) {
            return;
        }

        await window.chat.send(text);

        this.elements.messageInput.value = "";

    }

    setConnectionStatus(status) {

        this.elements.connectionStatus.textContent =
            status;

    }

}

window.addEventListener(
    "DOMContentLoaded",
    async () => {

        const app = new LocalShareApp();

        await app.initialize();

    }
);