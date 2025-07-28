module.exports = {
  parser: '@typescript-eslint/parser',
  plugins: ['@typescript-eslint', 'react', 'react-hooks'],
  extends: [
    'eslint:recommended',
    '@typescript-eslint/recommended',
    'plugin:react/recommended',
    'plugin:react-hooks/recommended',
  ],
  env: {
    browser: true,
    node: true,
    es2020: true,
  },
  parserOptions: {
    ecmaVersion: 2020,
    sourceType: 'module',
    ecmaFeatures: {
      jsx: true,
    },
  },
  settings: {
    react: {
      version: 'detect',
    },
  },
  ignorePatterns: [
    'dist/',
    'build/',
    'lib/',
    'node_modules/',
    '.theia/',
    'plugins/',
    '**/*.md',
    '**/*.mdx',
    '**/*.MD',
    '**/*.MDX',
  ],
  rules: {
    // Add any custom rules here
    'react/react-in-jsx-scope': 'off', // Not needed in newer React versions
  },
};
