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
- 新增API安全认证机制
  - 添加API密钥验证
  - 实现请求认证中间件

### Changed
- 客户端requirements.txt新增pyperclip依赖
- 重构API服务架构
  - 整合StandardAPI和StreamingAPI类
  - 移除直接的Whisper模型调用
  - 优化音频数据处理流程
  - 统一配置管理
  - 增强错误处理和日志记录
- 优化API接口
  - 改用文件上传替代base64编码
  - 简化API请求参数
  - 提高音频处理效率

### Files Changed
- `client-requirements.txt`: 添加pyperclip依赖
- `src/client.py`: 添加输出格式处理逻辑和剪贴板错误处理
- `src/app.py`: 重构API服务架构，添加安全认证，优化性能 