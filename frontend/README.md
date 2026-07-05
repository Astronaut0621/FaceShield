# FaceShield Frontend

Vue 3 + Vite 前端，按功能模块组织，页面与业务逻辑分离。

## 启动

```bash
npm install
npm run dev
```

## 目录结构

```text
public/                    静态资源（首页背景图等）
src/
├── main.js                应用入口
├── App.vue                根组件（布局切换）
├── config/                运行时配置
├── constants/             路由名、导航项等常量
├── router/                路由定义
├── layouts/               应用壳布局（侧边栏）
├── views/                 页面级组件（按业务域分子目录）
│   ├── home/              首页
│   ├── auth/              登录
│   ├── detective/         图片检测工作台
│   ├── result/            检测结果
│   └── history/           历史记录与详情
├── features/              功能模块（组件 + 服务）
│   ├── auth/              认证
│   ├── home/              首页模块
│   ├── detection/         检测模块
│   │   ├── components/
│   │   │   ├── upload/    上传相关组件
│   │   │   ├── result/    结果展示组件
│   │   │   └── DetectionGuidePanel.vue
│   │   └── services/
│   └── history/           历史记录模块
├── shared/                跨模块共享 UI 组件
├── stores/                轻量 reactive 状态
├── services/              HTTP 客户端
├── composables/           可复用组合式函数
├── utils/                 格式化、API 响应等工具
└── styles/                全局样式
```

## 约定

- **views/**：路由页面，负责组合 features 与 shared 组件，不写复杂业务逻辑
- **features/**：按业务域划分，各模块拥有自己的 `components/` 与 `services/`
- **shared/**：与具体业务无关的通用组件
- 路径别名：`@/` 指向 `src/`（已在 `vite.config.js` 配置）

## 演示账号

```text
username: demo
password: demo123456
```
