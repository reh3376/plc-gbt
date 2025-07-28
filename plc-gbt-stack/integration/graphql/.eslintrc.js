module.exports = {
  parser: '@typescript-eslint/parser',
  plugins: ['@typescript-eslint'],
  extends: ['eslint:recommended', '@typescript-eslint/recommended'],
  env: {
    node: true,
    es2020: true,
  },
  parserOptions: {
    ecmaVersion: 2020,
    sourceType: 'module',
  },
  ignorePatterns: [
    'dist/',
    'node_modules/',
    '**/*.md',
    '**/*.mdx',
    '**/*.MD',
    '**/*.MDX',
  ],
  rules: {
    // Add any custom rules here
  },
};
