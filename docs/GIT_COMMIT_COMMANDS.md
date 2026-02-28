# Git 提交命令

由于 Git 进程崩溃，请手动执行以下命令提交代码：

```bash
cd /home/user/webapp

# 清理 git 锁文件
rm -f .git/index.lock .git/index

# 添加修改的文件
git add source_code/app_new.py
git add OKX_POSSIDE_FIX.md

# 提交
git commit -m "fix(trading): 修复OKX开仓posSide参数错误

- 修复账户配置查询签名问题（所有私有接口都需要签名）
- 更改默认持仓模式为双向持仓（long_short_mode）
- 正确处理单向/双向持仓模式的posSide参数
- 解决错误51000: Parameter posSide error

问题：
- 之前查询账户配置时签名为空，导致查询失败
- 默认为单向持仓模式，不设置posSide参数
- 但实际账户可能是双向持仓，需要posSide参数

修复：
- 正确生成账户配置查询的签名
- 默认为双向持仓模式（更安全）
- 根据账户实际模式决定是否设置posSide

测试：
- 刷新页面重新尝试开仓
- 查看日志确认账户配置查询成功
- 小额测试（1-5 USDT）
"

# 推送到远程
git push origin genspark_ai_developer
```

**重要**：Git 提交完成后，请创建或更新 Pull Request！
