"use strict";

/*
=========================================================
LocalShare
Application Controller
=========================================================
*/

class App {

    constructor() {

        this.device = this.detectDevice();

        this.socketConnected = false;

    }

    async initialize() {

        console.log(
            `Starting LocalShare (${this.device})`
        );

        ui.initialize();

        await this.registerServiceWorker();

        this.registerEvents();

        socket.connect();

        await this.loadMessages();

    }

    registerEvents() {

        const sendButton =
            document.getElementById(
                "send-button"
            );

        const messageInput =
            document.getElementById(
                "message-input"
            );

        const attachButton =
            document.getElementById(
                "attach-button"
            );

        const fileInput =
            document.getElementById(
                "file-input"
            );

        sendButton.addEventListener(
            "click",
            () => this.sendMessage()
        );

        messageInput.addEventListener(
            "keydown",
            (event) => {

                if (event.key === "Enter") {

                    event.preventDefault();

                    this.sendMessage();

                }

            }
        );

        attachButton.addEventListener(
            "click",
            () => fileInput.click()
        );

        fileInput.addEventListener(
            "change",
            (event) => {

                if (
                    event.target.files.length === 0
                ) {

                    return;

                }

                ui.showToast(
                    "File upload coming next."
                );

            }
        );

    }

    async sendMessage() {

        const input =
            document.getElementById(
                "message-input"
            );

        const text =
            input.value.trim();

        if (!text) {

            return;

        }

        try {

            await fetch(
                "/api/messages",
                {

                    method: "POST",

                    headers: {

                        "Content-Type":
                            "application/json"

                    },

                    body: JSON.stringify({

                        sender_id:
                            this.device,

                        receiver_id:
                            this.device === "windows"
                                ? "android"
                                : "windows",

                        content: text

                    })

                }
            );

            input.value = "";

        }
        catch (error) {

            console.error(error);

            ui.showToast(
                "Unable to send message."
            );

        }

    }

    async loadMessages() {

        try {

            const response =
                await fetch(
                    "/api/messages"
                );

            const messages =
                await response.json();

            ui.renderMessages(
                messages
            );

        }
        catch (error) {

            console.error(error);

            ui.showToast(
                "Unable to load chat."
            );

        }

    }

    detectDevice() {

        const agent =
            navigator.userAgent.toLowerCase();

        if (

            /android|iphone|ipad/.test(agent)

        ) {

            return "android";

        }

        return "windows";

    }

    async registerServiceWorker() {

        if (

            !("serviceWorker" in navigator)

        ) {

            return;

        }

        try {

            await navigator
                .serviceWorker
                .register(
                    "/service-worker.js"
                );

        }
        catch (error) {

            console.error(error);

        }

    }

}

const app = new App();

window.addEventListener(

    "DOMContentLoaded",

    async () => {

        await app.initialize();

    }

);