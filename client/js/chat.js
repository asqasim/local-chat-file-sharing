"use strict";

class Chat {

    constructor(container) {
        this.container = container;
    }

    async load() {

        const response = await fetch("/api/messages");

        const messages = await response.json();

        this.render(messages);

    }

    render(messages) {

        this.container.innerHTML = "";

        for (const message of messages) {

            const bubble =
                document.createElement("div");

            bubble.className = "message";

            bubble.textContent =
                message.content;

            this.container.appendChild(bubble);

        }

        this.container.scrollTop =
            this.container.scrollHeight;

    }

    async send(text) {

        await fetch(
            "/api/messages",
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({

                    sender_id: "android",

                    receiver_id: "windows",

                    content: text

                })
            }
        );

        await this.load();

    }

}