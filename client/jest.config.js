// jest.config.js
module.exports = {
    preset: '@vue/cli-plugin-unit-jest',
    transform: {
      '^.+\\.vue$': 'vue3-jest',
      '^.+\\.jsx?$': 'babel-jest',
    },
    testEnvironment: 'jest-environment-jsdom',
    moduleNameMapper: {
      '^@/(.*)$': '<rootDir>/src/$1', // Настройка алиаса для @
    },
  };