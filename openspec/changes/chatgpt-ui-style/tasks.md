## 1. CSS 变量系统重构

- [x] 1.1 在 `frontend/src/index.css` 中引入 token-* 变量系统
- [x] 1.2 添加布局变量（--sidebar-width, --header-height, --composer-min-height）
- [x] 1.3 移除所有玻璃模糊效果相关变量（--glass-*）
- [x] 1.4 设置新的背景色变量（纯色）
- [x] 1.5 添加 composer 阴影变量（--shadow-short-composer）

## 2. Header 组件新建

- [x] 2.1 创建 `frontend/src/components/layout/Header.tsx` 组件
- [x] 2.2 实现 sticky 定位，高度为 var(--header-height)
- [x] 2.3 左侧添加菜单按钮（用于移动端切换侧边栏）
- [x] 2.4 中间显示当前会话标题
- [x] 2.5 右侧添加操作按钮区域
- [x] 2.6 在 AppLayout 中集成 Header 组件

## 3. 布局组件重构

- [x] 3.1 修改 `AppLayout.tsx`，使用纯色背景，移除 backdrop-filter
- [x] 3.2 调整布局结构为：Sidebar + Main(Header + Content)
- [x] 3.3 修改 `Sidebar.tsx` 宽度为 var(--sidebar-width)
- [x] 3.4 移除 Sidebar.tsx 中的独立 Logo 区域

## 4. 侧边栏结构重构

- [x] 4.1 重构侧边栏顶部区域（新建按钮使用菜单项样式）
- [x] 4.2 新建按钮使用 group/__menu-item 样式，带图标
- [x] 4.3 会话列表区域使用 flex-1 overflow-y-auto
- [x] 4.4 添加底部区域（sticky bottom，用于登录/设置入口）
- [x] 4.5 底部区域使用 border-t 分隔

## 5. 输入框组件重构

- [x] 5.1 修改 `ChatInput.tsx` 使用 CSS Grid 布局
- [x] 5.2 设置 grid-template-areas: 'leading primary trailing'
- [x] 5.3 圆角改为 28px
- [x] 5.4 添加左侧 leading 区域（+ 按钮占位）
- [x] 5.5 中间 primary 区域为输入框
- [x] 5.6 右侧 trailing 区域为发送按钮
- [x] 5.7 使用纯白背景和细边框
- [x] 5.8 添加 shadow-short-composer 阴影效果
- [x] 5.9 发送按钮使用 rounded-full 样式

## 6. 会话列表组件重构

- [x] 6.1 会话项使用 group/__menu-item hoverable 样式
- [x] 6.2 会话项包含：图标 + 文字 + hover 操作按钮
- [x] 6.3 图标区域使用 w-6 h-6 居中
- [x] 6.4 文字区域 flex-1 truncate
- [x] 6.5 hover 时显示重命名/删除按钮
- [x] 6.6 选中状态使用背景色高亮（无边框）

## 7. 消息组件重构

- [x] 7.1 简化 `MessageBubble.tsx` 样式，移除渐变
- [x] 7.2 使用纯色背景
- [x] 7.3 简化头像样式
- [x] 7.4 用户消息使用深色背景，AI 消息使用浅色背景

## 8. 欢迎界面重构

- [x] 8.1 重设计 `MessageList.tsx` 欢迎界面
- [x] 8.2 使用大标题居中，移除图标
- [x] 8.3 移除装饰性容器
- [x] 8.4 标题样式：text-2xl font-semibold text-center

## 9. 验证和测试

- [x] 9.1 启动前端开发服务器，验证所有页面样式正常
- [x] 9.2 验证 Header 组件 sticky 效果
- [x] 9.3 验证输入框 Grid 布局和圆角
- [x] 9.4 验证侧边栏结构和底部区域
- [x] 9.5 验证会话项 hover 效果
- [x] 9.6 验证响应式布局
