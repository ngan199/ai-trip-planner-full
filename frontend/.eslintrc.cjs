module.exports = {
root: true,
parser: "@typescript-eslint/parser",
plugins: ["@typescript-eslint", "react", "react-hooks", "import"],
extends: [
"eslint:recommended",
"plugin:@typescript-eslint/recommended",
"plugin:react/recommended",
"plugin:react-hooks/recommended",
"plugin:import/recommended",
"plugin:import/typescript",
"prettier"
],
settings: { react: { version: "detect" } },
rules: {
    "prettier/prettier": "warn",
    "react/react-in-jsx-scope": "off",
    "@typescript-eslint/no-explicit-any": "error" // Disallow 'any' explicitly
  }
};