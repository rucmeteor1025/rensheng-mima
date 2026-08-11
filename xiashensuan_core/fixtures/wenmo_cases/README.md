# 文墨校准样本

这里可保存进入自动回归的文墨天机兼容样例文本。

公开仓库默认不提交任何真实用户命例、姓名、原始分析记录或私密上下文。`manifest.json` 保持为空数组，维护者可在本地私有目录加入 fixture 做回归，但不要推送到 GitHub。公开可跑的合成样例在 `../synthetic/`（由 `scripts/gen_synthetic_fixtures.py` 生成，非真实用户）。

## 文件结构

- `*.txt`：原始文墨盘文本（仅本地私有目录，不入库）。
- `manifest.json`：保持空数组。
- 公开合成样例：`../synthetic/`。

## 入库标准

强校准样本至少需要：

- 安星码或明确文墨来源
- 性别、出生时间、真太阳时
- 完整十二宫结构
- 命主、身主、子年斗君、身宫
- 可校验的关键宫位星曜与四化

安星码 `C5FYC` 只作为来源辅助信号；没有宫位结构的分析文章不应直接作为强校准样本。

`manifest.json` 里的时间预期建议同时写原文和标准化结果，例如：

- `birth_raw`
- `calendar`
- `birth_standard_time`
- `birth_date`
- `birth_clock_time`
- `true_solar_standard_time`
- `true_solar_date`
- `true_solar_clock_time`

## 合成样例回归

合成样例由 `scripts/gen_synthetic_fixtures.py` 生成并入库到 `../synthetic/`：

```bash
python3 -B scripts/gen_synthetic_fixtures.py --verify
python3 -B scripts/wenmo_synthetic_tests.py
```

## 回归命令

```bash
python3 -B scripts/xiashensuantests.py
```
