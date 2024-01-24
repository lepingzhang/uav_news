# wechat-gptbot 新闻获取插件

本项目作为 `wechat-gptbot` 插件，可以根据关键字回复对应的信息。

## 安装指南

### 1. 添加插件源
在 `plugins/source.json` 文件中添加以下配置：
```
{
  "keyword_reply": {
    "repo": "https://github.com/lepingzhang/uav_news.git",
    "desc": "手动获取无人机新闻"
  }
}
```

### 2. 插件配置
在 `config.json` 文件中添加以下配置：
```
"plugins": [
  {
    "name": "uav_news",
    "command": ["无人机新闻", "无人机资讯"],
  }
]
```
