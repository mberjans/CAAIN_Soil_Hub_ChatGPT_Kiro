module.exports = [
  {
    files: ["**/*.js"],
    languageOptions: {
      ecmaVersion: 2021,
      sourceType: "module",
    },
    rules: {
      // Basic rules for syntax checking
      "no-undef": "warn",
      "no-unused-vars": "warn",
      "semi": ["error", "always"],
      "quotes": ["error", "single"],
    },
  },
];