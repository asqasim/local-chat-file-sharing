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
        this.registerEventListeners();

        this.setConnectionStatus("Offline");
    }

    async registerServiceWorker() {
        if (!("serviceWorker" in navigator)) {
            return;
        }

        try {
            await navigator.serviceWorker.register("/service-worker.js");
            console.info("Service Worker registered.");
        } catch (error) {
            console.error("Failed to register Service Worker.", error);
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

    sendMessage() {
        const message = this.elements.messageInput.value.trim();

        if (!message) {
            return;
        }

        console.log("Message:", message);

        this.elements.messageInput.value = "";
    }

    setConnectionStatus(status) {
        this.elements.connectionStatus.textContent = status;
    }
}

window.addEventListener("DOMContentLoaded", async () => {
    const app = new LocalShareApp();
    await app.initialize();
});