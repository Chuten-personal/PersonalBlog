# Chuten 的个人博客

个人博客主页，记录学习、技术与生活。

## 访问

直接打开 `index.html` 即可在浏览器中预览。

## 撰写文章

1. 在 `_posts/` 目录下创建 Markdown 文件（如 `my-post.md`）
2. 在文件开头添加 YAML 元数据：

```markdown
---
title: 文章标题
date: 2025-02-28
---

正文内容...
```

3. 运行构建脚本生成 HTML：

```bash
pip install -r requirements.txt
python build.py              # 转换 _posts 下所有文章
python build.py post.md      # 转换指定文章
```

生成的 HTML 会输出到 `articles/` 目录，然后在首页的文章列表中添加对应链接即可。

## 技术栈

- 原生 HTML / CSS
- 响应式设计
- Python + Markdown 静态生成
