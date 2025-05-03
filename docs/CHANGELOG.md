# Changelog

## [Unreleased]
### Added
- 新增输出格式选项功能
  - 支持JSON格式输出（默认）
  - 支持纯文本输出
  - 支持剪贴板复制
- 新增剪贴板操作错误处理
  - 处理剪贴板访问失败情况
  - 提供详细的错误信息和可能原因

### Changed
- 客户端requirements.txt新增pyperclip依赖

### Files Changed
- `client-requirements.txt`: 添加pyperclip依赖
- `src/client.py`: 添加输出格式处理逻辑和剪贴板错误处理 