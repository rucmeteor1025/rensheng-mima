# 公开合成样例（Synthetic Fixtures）

本目录包含**确定性合成**的文墨天机兼容文字盘样例，用于公开 CI 回归：

- 全部由 `scripts/gen_synthetic_fixtures.py` 生成（固定输入、固定输出）。
- **不包含任何真实用户**的出生记录、姓名、报告、日志或私密上下文。
- 每个样例覆盖一种性别/时间/地点组合，用于解析器回归（十二宫完整性、安星码、真太阳时、生年四化）。

## 重新生成

```bash
python3 -B scripts/gen_synthetic_fixtures.py --verify
```

## 回归测试

```bash
python3 -B scripts/wenmo_synthetic_tests.py
```

## 入库红线

任何贡献都不得向本目录或仓库任何位置添加真实命例。真实用户数据只允许出现在 Git 忽略的本地 `private_records/` 目录。
