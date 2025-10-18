module.exports = {
    testEnvironment: "jsdom",
    setupFiles: ["<rootDir>/services/frontend/src/static/js/__tests__/setup.js"],
    modulePathIgnorePatterns: [
        "<rootDir>/services/frontend/venv",
        "<rootDir>/venv",
        "<rootDir>/afas_env",
        "<rootDir>/codex_env",
        "<rootDir>/ticket006_env",
        "<rootDir>/venv_ticket006_83"
    ]
};
