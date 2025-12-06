# 代码质量工具配置指南

本项目已配置了完整的代码质量工具链，包括 ESLint、Prettier、TypeScript 和 lint-staged，确保代码风格一致性和最佳实践。

## 📦 工具列表

- **ESLint**: 代码静态分析
  - 基于 Airbnb Base 配置
  - TypeScript 支持
  - Promise 最佳实践
  - 代码复杂度分析
  - 部分规则已针对项目现有代码进行优化调整

- **Prettier**: 代码格式化
  - 统一的代码风格
  - 支持多种文件类型（.ts, .js, .json, .md, .css, .scss）

- **lint-staged**: Git 提交前自动检查
  - 自动运行 lint 和 format
  - 只检查暂存的文件

## 🚀 快速开始

### 安装依赖

```bash
npm install
```

### 初始化 Husky（可选，用于 Git Hooks）

```bash
npm run prepare
```

## 📝 可用命令

### 代码检查

```bash
# 检查代码问题（会显示警告）
npm run lint

# 检查代码问题（不显示警告）
npm run lint:check

# 自动修复可修复的问题
npm run lint:fix
```

**当前状态**: ESLint 配置基于 Airbnb
Base，包含 TypeScript 支持和代码复杂度检查。已针对项目现有代码适当放宽部分规则（如 import/no-unresolved、import/extensions、import/cycle 等），以避免与现有代码风格冲突。后续可根据需要逐步收紧规则或进行代码重构以符合更严格的规范。

### 代码格式化

```bash
# 格式化所有文件
npm run format

# 检查格式化（不修改文件）
npm run format:check

# 强制写入格式化
npm run format:write
```

### 综合质量检查

```bash
# 运行所有检查：lint + format + typecheck
npm run quality

# 运行所有修复：lint:fix + format:write + typecheck
npm run quality:fix
```

## 🔧 配置说明

### ESLint 规则

- **Airbnb Base**: 业界最佳实践
- **TypeScript**: 基础类型检查（已放宽部分严格规则）
- **Promise**: Promise 最佳实践
- **代码复杂度**: 限制函数复杂度 ≤ 10
- **Max Params**: 限制函数参数 ≤ 4
- **Max Depth**: 限制代码块嵌套深度 ≤ 4

#### 主要规则特点：

1. **未使用变量检查**: 检查未使用的变量和导入
2. **类型强制**: 部分类型检查规则
3. **导入排序**: 自动排序和分组导入语句
4. **Promise 最佳实践**: 检查 Promise 的正确使用
5. **代码复杂度**: 控制认知复杂度和函数长度
6. **已放宽规则**:
   import/no-unresolved、import/extensions、@typescript-eslint/strict-boolean-expressions 等

#### 当前限制：

由于项目现有代码与某些 ESLint 规则存在冲突，以下规则已被禁用或调整为警告：

- `import/no-unresolved` - 已禁用
- `import/extensions` - 已禁用
- `import/namespace` - 已禁用
- `import/default` - 已禁用
- `import/no-relative-packages` - 已禁用
- `@typescript-eslint/strict-boolean-expressions` - 已禁用
- `@typescript-eslint/prefer-nullish-coalescing` - 已禁用
- 多个 TypeScript 类型检查规则 - 已禁用

**建议**: 后续可通过重构代码逐步恢复这些严格规则，提高代码质量。

### Prettier 配置

```json
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 100,
  "tabWidth": 2,
  "arrowParens": "always"
}
```

主要特点：

- 使用单引号
- 行宽限制 100 字符
- 使用分号
- 箭头函数参数加括号

## 🔄 Git 集成

### Husky + lint-staged

在 Git 提交时自动运行代码检查和格式化：

```bash
git add .
git commit -m "feat: 新功能"
```

lint-staged 会自动：

1. 对暂存的 `.ts` 和 `.js` 文件运行 `eslint --fix`
2. 对暂存的所有文件运行 `prettier --write`
3. 只有通过检查的文件才会被提交

### 跳过检查（不推荐）

```bash
git commit -m "feat: 新功能" --no-verify
```

## 📋 推荐的 VSCode 扩展

安装以下扩展以在编辑器中获得实时反馈：

```json
{
  "recommendations": [
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode",
    "ms-vscode.vscode-typescript-next"
  ]
}
```

## 🎯 开发工作流

### 日常开发

1. 编写代码
2. 保存时 VSCode 自动修复格式问题
3. 运行 `npm run lint` 检查问题
4. 运行 `npm run format` 格式化代码
5. 提交时 Husky 自动检查

### 修复所有问题

```bash
# 一键修复所有可修复的问题
npm run quality:fix
```

### 预提交检查

确保所有代码符合标准：

```bash
# 在 CI/CD 或预提交时运行
npm run quality
```

## ⚙️ 自定义规则

如需修改规则，请编辑以下文件：

- **ESLint**: `.eslintrc.js`
- **Prettier**: `.prettierrc.json`
- **忽略文件**: `.eslintignore`, `.prettierignore`

## 🚨 常见问题

### ESLint 不工作

1. 检查 VSCode ESLint 扩展是否安装
2. 确保 `eslint.config.js` 存在
3. 重启 VSCode

### Prettier 不格式化

1. 检查 VSCode Prettier 扩展是否安装
2. 确保 `.prettierrc.json` 存在
3. 在 VSCode 设置中启用 "Format On Save"

### 冲突解决

ESLint 和 Prettier 可能会有冲突，但本配置已解决：

- 所有格式化规则在 ESLint 中已禁用
- Prettier 处理所有格式化
- ESLint 只检查代码质量

## 📊 检查报告示例

```bash
$ npm run quality

> midscene-server@2.0.0 quality
> npm run lint:check && npm run format:check && npm run typecheck


✔ No issues found

✔ Checking formatting...
✔ All matched files use Prettier code style!

✔ Running typecheck...
Found 0 errors
```

## 🔗 参考资源

- [ESLint 文档](https://eslint.org/)
- [Prettier 文档](https://prettier.io/)
- [Airbnb JavaScript 风格指南](https://github.com/airbnb/javascript)
- [TypeScript ESLint](https://typescript-eslint.io/)
- [lint-staged 文档](https://github.com/lint-staged/lint-staged)

---

📝 **提示**: 建议在开发过程中定期运行 `npm run quality` 确保代码质量！
