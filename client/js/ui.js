"use strict";

/*
============================================================
LocalShare UI Manager
Part 1
============================================================
*/

class UI {

    constructor() {

        this.currentPage = "chat";

        this.pages = {};

        this.navButtons = [];

        this.chatContainer = null;

        this.toastRoot = null;

        this.modalRoot = null;

    }

    initialize() {

        this.pages = {

            chat: document.getElementById("chat-page"),

            files: document.getElementById("files-page"),

            media: document.getElementById("media-page"),

            devices: document.getElementById("devices-page"),

            settings: document.getElementById("settings-page")

        };

        this.chatContainer =
            document.getElementById("chat");

        this.toastRoot =
            document.getElementById("toast-root");

        this.modalRoot =
            document.getElementById("modal-root");

        this.navButtons = [
            ...document.querySelectorAll("[data-page]")
        ];

        this.registerNavigation();

    }

    registerNavigation() {

        for (const button of this.navButtons) {

            button.addEventListener(
                "click",
                () => {

                    const page =
                        button.dataset.page;

                    this.showPage(page);

                }
            );

        }

    }

    showPage(page) {

        if (!(page in this.pages)) {

            console.warn(
                "Unknown page:",
                page
            );

            return;

        }

        this.currentPage = page;

        for (const key in this.pages) {

            this.pages[key]
                .classList
                .remove("active-page");

        }

        this.pages[page]
            .classList
            .add("active-page");

        for (const button of this.navButtons) {

            button.classList.remove("active");

            if (
                button.dataset.page === page
            ) {

                button.classList.add("active");

            }

        }

        this.updateTitle(page);

    }

    updateTitle(page) {

        const title =
            document.getElementById(
                "page-title"
            );

        const subtitle =
            document.getElementById(
                "page-subtitle"
            );

        switch (page) {

            case "chat":

                title.textContent =
                    "Chat";

                subtitle.textContent =
                    "Instant local messaging";

                break;

            case "files":

                title.textContent =
                    "Files";

                subtitle.textContent =
                    "All transferred files";

                break;

            case "media":

                title.textContent =
                    "Media";

                subtitle.textContent =
                    "Images & Videos";

                break;

            case "devices":

                title.textContent =
                    "Devices";

                subtitle.textContent =
                    "Connected devices";

                break;

            case "settings":

                title.textContent =
                    "Settings";

                subtitle.textContent =
                    "Application preferences";

                break;

        }

    }

    clearChat() {

        this.chatContainer.innerHTML = "";

    }

    addMessage(message) {

        const bubble =
            document.createElement("div");

        bubble.classList.add("message");

        if (
            message.sender_id === "windows"
        ) {

            bubble.classList.add(
                "message-outgoing"
            );

        }
        else {

            bubble.classList.add(
                "message-incoming"
            );

        }

        const content =
            document.createElement("div");

        content.className =
            "message-content";

        content.textContent =
            message.content;

        const footer =
            document.createElement("div");

        footer.className =
            "message-footer";

        const time =
            document.createElement("span");

        time.className =
            "message-time";

        time.textContent =
            this.formatTime(
                message.created_at
            );

        footer.appendChild(time);

        bubble.appendChild(content);

        bubble.appendChild(footer);

        this.chatContainer.appendChild(
            bubble
        );

        this.scrollChat();

    }

    renderMessages(messages) {

        this.clearChat();

        for (const message of messages) {

            this.addMessage(message);

        }

    }

    scrollChat() {

        this.chatContainer.scrollTop =
            this.chatContainer.scrollHeight;

    }

    formatTime(dateString) {

        const date =
            new Date(dateString);

        return date.toLocaleTimeString(
            [],
            {

                hour: "2-digit",

                minute: "2-digit"

            }
        );

    }

    showToast(text) {

        const toast =
            document.createElement("div");

        toast.className =
            "toast";

        toast.textContent =
            text;

        this.toastRoot.appendChild(
            toast
        );

        requestAnimationFrame(
            () => {

                toast.classList.add(
                    "show"
                );

            }
        );

        setTimeout(() => {

            toast.classList.remove(
                "show"
            );

            setTimeout(() => {

                toast.remove();

            }, 250);

        }, 3000);

    }

}

const ui = new UI();

/*
============================================================
LocalShare UI Manager
Part 2
============================================================
*/

UI.prototype.renderDevices = function (devices) {

    const container =
        document.getElementById("device-list");

    if (!container) {
        return;
    }

    container.innerHTML = "";

    if (devices.length === 0) {

        container.innerHTML = `
            <div class="placeholder">
                <h3>No devices</h3>
                <p>No paired devices found.</p>
            </div>
        `;

        return;
    }

    for (const device of devices) {

        const card =
            document.createElement("div");

        card.className = "device-card";

        card.innerHTML = `

            <div class="device-avatar">
                ${device.name.charAt(0).toUpperCase()}
            </div>

            <div class="device-info">

                <strong>${device.name}</strong>

                <small>${device.platform}</small>

            </div>

            <div class="device-status ${device.online ? "online" : "offline"}">

                ${device.online ? "● Online" : "● Offline"}

            </div>

        `;

        container.appendChild(card);

    }

};


UI.prototype.renderFileMessage = function (message) {

    const bubble =
        document.createElement("div");

    bubble.className =
        "message";

    bubble.classList.add(

        message.sender_id === "windows"

            ? "message-outgoing"

            : "message-incoming"

    );

    bubble.innerHTML = `

        <div class="file-card">

            <div class="file-icon">
                📄
            </div>

            <div class="file-details">

                <strong>${message.file_name}</strong>

                <small>${message.file_size ?? ""}</small>

            </div>

        </div>

    `;

    this.chatContainer.appendChild(
        bubble
    );

};


UI.prototype.renderImageMessage = function (message) {

    const bubble =
        document.createElement("div");

    bubble.className =
        "message";

    bubble.classList.add(

        message.sender_id === "windows"

            ? "message-outgoing"

            : "message-incoming"

    );

    bubble.innerHTML = `

        <img
            class="image-preview"
            src="${message.url}"
            alt="image">

    `;

    bubble.querySelector("img")
        .addEventListener(

            "click",

            () => {

                this.openImageViewer(
                    message.url
                );

            }

        );

    this.chatContainer.appendChild(
        bubble
    );

};


UI.prototype.openImageViewer = function (url) {

    this.modalRoot.innerHTML = `

        <div class="modal-overlay">

            <div class="image-viewer">

                <button id="close-viewer">

                    ✕

                </button>

                <img src="${url}">

            </div>

        </div>

    `;

    document
        .getElementById("close-viewer")
        .addEventListener(

            "click",

            () => {

                this.modalRoot.innerHTML = "";

            }

        );

};


UI.prototype.showLoading = function () {

    this.modalRoot.innerHTML = `

        <div class="modal-overlay">

            <div class="loading-box">

                Loading...

            </div>

        </div>

    `;

};


UI.prototype.hideLoading = function () {

    this.modalRoot.innerHTML = "";

};


UI.prototype.showEmptyState = function (
    container,
    title,
    subtitle
) {

    container.innerHTML = `

        <div class="placeholder">

            <h3>${title}</h3>

            <p>${subtitle}</p>

        </div>

    `;

};


UI.prototype.updateConnectionStatus = function (
    connected
) {

    const status =
        document.getElementById(
            "connection-status"
        );

    if (!status) {
        return;
    }

    if (connected) {

        status.textContent =
            "Connected";

        status.style.color =
            "#22c55e";

    }
    else {

        status.textContent =
            "Disconnected";

        status.style.color =
            "#ef4444";

    }

};


UI.prototype.setPairingMode = function (
    enabled
) {

    const button =
        document.getElementById(
            "pair-button"
        );

    if (!button) {
        return;
    }

    button.textContent =

        enabled

            ? "Waiting for Pair..."

            : "Pair Device";

};


UI.prototype.clearModal = function () {

    this.modalRoot.innerHTML = "";

};


ui.initialize();