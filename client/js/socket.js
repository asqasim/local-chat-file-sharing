"use strict";

class SocketClient {

    constructor() {
        this.socket = null;
    }

    connect() {

        const protocol =
            window.location.protocol === "https:"
                ? "wss"
                : "ws";

        const url =
            `${protocol}://${window.location.host}/ws`;

        this.socket = new WebSocket(url);

this.socket.onopen = () => {

    document.getElementById(
        "connection-status"
    ).textContent = "Connected";

};

this.socket.onclose = () => {

    document.getElementById(
        "connection-status"
    ).textContent = "Disconnected";

    setTimeout(
        () => this.connect(),
        3000,
    );

};

        this.socket.onerror = (error) => {
            console.error(error);
        };

        this.socket.onmessage = (event) => {

            const data =
                JSON.parse(event.data);

            this.handle(data);

        };

    }

    handle(message) {

        switch (message.type) {

            case "new_message":

                if (window.chat) {
                    window.chat.load();
                }

                break;

            default:

                console.warn(
                    "Unknown websocket message:",
                    message.type,
                );

        }

    }

    sendHeartbeat() {

        if (
            this.socket &&
            this.socket.readyState === WebSocket.OPEN
        ) {

            this.socket.send("ping");

        }

    }

}

const socket = new SocketClient();