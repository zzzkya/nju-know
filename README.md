# 南大知道 NJU Know · MVP 0.1

独立学生项目，与南京大学官方无隶属关系。

## 环境
Python 3.10+（建议 3.11 或 3.12）

## 本地运行
```bash
python -m venv .venv
# macOS/Linux: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```
打开 http://127.0.0.1:5000 。首次启动是空列表，这是预期行为。

## 导入公开信息（先阅读网站的使用规则并核实授权）
```bash
python collector.py
```
采集器只读取三个站点的一个公开列表页，尽可能提取带日期的站内文章链接；它仅作教学原型，**不保证抓取完整或准确**。采集结果需要抽查，不要直接未经审核对公众发布。不会自动定时请求。

## 测试
```bash
python -m unittest discover -s tests -v
```

## API
`GET /api/posts?q=AI&category=学术`，以及 `GET /health`。

## 上线前必须完成
- 核实网站 robots、使用条款、转载许可与站点联系渠道，指定规范的 User-Agent；确保限流、失败重试退避和数据最小化。
- 加入审核后台、采集错误记录、来源可信度和下架机制；区分公告日期、活动日期、截止日期。
- 迁移到托管 PostgreSQL，设置备份恢复、部署参数、安全检查、日志监控。
- 建立明示的隐私政策、投稿/纠错方式、非官方声明，按实际服务地区核查备案与合规要求。
- 添加缓存、分页、防恶意搜索、XSS/SQL注入测试和CI；审查第三方依赖。
- 根据发布地区选择适当的定时任务和托管服务；避免把本地 SQLite 当作多实例生产数据库。

## 项目结构
- `app.py` Flask 服务器和 SQLite 数据模型
- `collector.py` 保守的页面列表抓取器（手动执行）
- `templates/index.html` 首页
- `static/style.css` 网站样式
- `tests/` 单元测试
