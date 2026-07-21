"use strict";

class ApiClient {

    constructor(baseUrl) {
        this.baseUrl = baseUrl;
    }

    async get(path) {

        const response = await fetch(
            this.baseUrl + path,
            {
                method: "GET",
                headers: {
                    "Accept": "application/json",
                },
            },
        );

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        return response.json();
    }

    async health() {
        return this.get(CONFIG.ENDPOINTS.HEALTH);
    }

}

const api = new ApiClient(CONFIG.API_BASE);