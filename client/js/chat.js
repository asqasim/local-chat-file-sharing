"use strict";

class Chat {

    constructor(container) {
        this.container = container;
    }

    async load() {

        try {

            const response = await fetch("/api/messages");

            const messages = await response.json();

            this.render(messages);

        }
        catch (error) {

            console.error("Failed to load messages.", error);

        }

    }

    render(messages) {

        this.container.innerHTML = "";

        for (const message of messages) {

            const bubble = document.createElement("div");

            bubble.classList.add("message");

            if (message.sender_id === "windows") {
                bubble.classList.add("message-outgoing");
            }
            else {
                bubble.classList.add("message-incoming");
            }

            bubble.textContent = message.content;

            this.container.appendChild(bubble);

        }

        this.scrollToBottom();

    }

    async send(text, sender = "windows", receiver = "android") {

        if (!text.trim()) {
            return;
        }

        try {

            await fetch("/api/messages", {
                method: "POST",

                headers: {
                    "Content-Type": "application/json",
                },

                body: JSON.stringify({
                    sender_id: sender,
                    receiver_id: receiver,
                    content: text,
                }),
            });

        }
        catch (error) {

            console.error("Failed to send message.", error);

        }

    }

    scrollToBottom() {

        this.container.scrollTop =
            this.container.scrollHeight;

    }

}

window.chat = new Chat(
    document.getElementById("chat")
);