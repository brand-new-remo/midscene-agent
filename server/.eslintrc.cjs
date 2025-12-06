module.exports = {
  root: true,
  env: {
    node: true,
    es2022: true,
    jest: true,
  },
  extends: [
    'eslint:recommended',
    'airbnb-base',
    'plugin:@typescript-eslint/recommended',
    'plugin:import/recommended',
    'plugin:import/typescript',
    'plugin:promise/recommended',
  ],
  parser: '@typescript-eslint/parser',
  parserOptions: {
    ecmaVersion: 2022,
    sourceType: 'module',
  },
  plugins: [
    '@typescript-eslint',
    'import',
    'promise',
  ],
  settings: {
    'import/resolver': {
      typescript: {
        alwaysTryTypes: true,
        project: './tsconfig.json',
      },
    },
  },
  rules: {
    // TypeScript 规则
    '@typescript-eslint/no-unused-vars': [
      'error',
      {
        argsIgnorePattern: '^_',
        varsIgnorePattern: '^_',
        caughtErrorsIgnorePattern: '^_',
      },
    ],
    '@typescript-eslint/no-explicit-any': 'warn',
    '@typescript-eslint/explicit-function-return-type': [
      'error',
      {
        allowExpressions: true,
        allowTypedFunctionExpressions: true,
        allowHigherOrderFunctions: true,
      },
    ],
    '@typescript-eslint/explicit-module-boundary-types': 'error',
    '@typescript-eslint/no-non-null-assertion': 'error',
    '@typescript-eslint/prefer-nullish-coalescing': 'off',
    '@typescript-eslint/prefer-optional-chain': 'off',
    '@typescript-eslint/no-misused-promises': 'off',
    '@typescript-eslint/strict-boolean-expressions': 'off',
    '@typescript-eslint/prefer-readonly': 'off',
    '@typescript-eslint/prefer-readonly-parameter-types': 'off',
    '@typescript-eslint/no-parameter-properties': 'off',
    '@typescript-eslint/prefer-for-of': 'off',
    '@typescript-eslint/prefer-includes': 'off',
    '@typescript-eslint/prefer-string-starts-ends-with': 'off',
    '@typescript-eslint/consistent-type-imports': 'off',
    '@typescript-eslint/no-var-requires': 'off',
    '@typescript-eslint/prefer-namespace-keyword': 'off',
    '@typescript-eslint/prefer-literal-enum-member': 'off',
    '@typescript-eslint/prefer-ts-expect-error': 'off',
    '@typescript-eslint/restrict-template-expressions': 'off',

    // Import 规则
    'import/order': 'off', // 禁用，因为与 TypeScript 解析器有兼容性问题
    'import/first': 'off', // 禁用，因为与 TypeScript 解析器有兼容性问题
    'import/no-duplicates': 'off',
    'import/no-webpack-loader-syntax': 'error',
    'import/no-named-as-default-member': 'off',
    'import/no-self-import': 'off',
    'import/namespace': 'off',
    'import/default': 'off',
    'import/no-relative-packages': 'off',
    'import/no-extraneous-dependencies': 'off',
    'import/no-cycle': 'off',
    'import/no-named-as-default': 'off',
    'import/no-useless-path-segments': 'off',
    'import/no-unresolved': 'off',
    'import/extensions': 'off',

    // Promise 规则
    'promise/always-return': 'error',
    'promise/no-return-wrap': 'error',
    'promise/param-names': 'error',
    'promise/catch-or-return': 'error',
    'promise/no-nesting': 'error',
    'promise/no-new-statics': 'error',
    'promise/valid-params': 'error',

    'max-depth': 'off',
    'max-lines-per-function': [
      'error',
      {
        max: 50,
        skipComments: true,
        skipBlankLines: true,
      },
    ],
    'max-params': 'off',
    'max-statements': 'off',
    // 警告级别
    'no-console': 'warn',
    'no-debugger': 'error',
    'no-alert': 'error',
    'no-magic-numbers': [
      'warn',
      {
        ignore: [-1, 0, 1, 2],
        ignoreArrayIndexes: true,
        detectObjects: false,
        enforceConst: true,
        ignoreDefaultValues: true,
      },
    ],
    'no-throw-literal': 'error',
    'no-useless-escape': 'error',

    // 格式化相关（将由Prettier处理）
    'comma-dangle': 'off',
    'comma-spacing': 'off',
    'comma-style': 'off',
    'computed-property-spacing': 'off',
    'func-call-spacing': 'off',
    'key-spacing': 'off',
    'keyword-spacing': 'off',
    'max-len': 'off',
    'no-mixed-spaces-and-tabs': 'off',
    'no-multi-spaces': 'off',
    'no-trailing-spaces': 'off',
    'no-whitespace-before-property': 'off',
    'object-curly-spacing': 'off',
    'padded-blocks': 'off',
    'rest-spread-spacing': 'off',
    'semi-spacing': 'off',
    'space-before-blocks': 'off',
    'space-before-function-paren': 'off',
    'space-in-parens': 'off',
    'space-infix-ops': 'off',
    'space-unary-ops': 'off',
    'arrow-spacing': 'off',
    'block-spacing': 'off',
    'brace-style': 'off',
  },
  overrides: [
    {
      files: ['**/*.test.ts', '**/*.spec.ts', '**/*.test.js', '**/*.spec.js'],
      rules: {
        'max-lines-per-function': 'off',
        'max-statements': 'off',
        'no-magic-numbers': 'off',
      },
    },
    {
      files: ['dist/**/*.js', 'node_modules/**/*.js'],
      rules: {
        'no-console': 'off',
        'import/no-nodejs-modules': 'off',
      },
    },
  ],
};
