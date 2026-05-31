import type { FortunePayload, FortuneResponse, FullFortuneReport } from "../types";

export function buildDemoFortuneResponse(payload: FortunePayload): FortuneResponse {
  const focus = String(payload.focus || "full");
  const focusLabel = focusName(focus);
  const reportId = `demo-${Date.now().toString(36)}`;

  return {
    ok: true,
    reportId,
    summary: {
      basic: {
        birthTime: `${payload.year}-${pad(payload.month)}-${pad(payload.day)} ${pad(payload.hour)}:${pad(payload.minute)}`,
        lunar: "静态演示不换算农历",
        gender: payload.gender,
        place: payload.place,
        mode: "GitHub Pages 静态演示",
        version: "人生密码 GitHub Pages Demo"
      },
      chart: {
        bazi: "己巳 丁丑 庚辰 癸未",
        dayMaster: "庚",
        strength: "身弱",
        useful: "印星、比劫",
        mingStar: ["七杀"],
        shenPalace: "福德宫"
      },
      free: [
        {
          title: "静态演示说明",
          text: "这是 GitHub Pages 上的合成示例摘要，用于展示网页流程和交互体验。真实规则引擎请在本地运行 Python 服务。"
        },
        {
          title: "整体判断",
          text: `当前选择的是「${focusLabel}」。演示版会模拟先看结构、再看场景、最后给出趋避建议的产品节奏。`
        },
        {
          title: "隐私边界",
          text: "公开网页不会上传真实出生信息，演示报告只保存在当前浏览器会话中；刷新或删除后即可清空。"
        }
      ],
      paidPreview: [
        {
          title: "完整报告预览",
          text: "完整版会拆成八字、紫微、性格、事业财运、关系与阶段建议等模块。"
        },
        {
          title: "建议",
          text: "演示版建议只用默认输入体验流程；不要在公开演示环境输入真实个人资料。"
        }
      ],
      disclaimer: "仅供文化研究、产品演示和个人反思，不替代医疗、法律、投资或心理咨询建议。"
    },
    privacy: {
      storage: "GitHub Pages 静态演示只使用当前浏览器 sessionStorage。",
      deleteEndpoint: `/api/report/${reportId}`
    }
  };
}

export function buildDemoFullReport(report: FortuneResponse): FullFortuneReport {
  return {
    风格化输出: {
      命理主输出: {
        整体判断: "这是合成完整报告，用于演示付费解锁后的信息层级。真正计算结果需要本地后端生成。",
        性格气质: "演示报告强调表达结构：先给结论，再给依据，最后给行动建议。",
        事业与财运: "实际版本会结合八字、紫微宫位和流年阶段，拆出事业路径、财务节奏与风险提示。",
        感情与婚姻: "实际版本会把关系议题从沟通方式、压力反应和相处节奏展开。",
        建议: "公开演示请使用默认输入；真实资料应只在可信本地环境或自建后端中处理。",
        总结: report.summary.disclaimer
      },
      生活版: {
        总论: report.summary.free.map((line) => `${line.title}：${line.text}`).join("\n"),
        收束: "GitHub Pages 版本证明网页端流程可用，本地版本负责真实规则引擎。"
      }
    },
    八字命理: {
      专业分析: `演示四柱：${report.summary.chart.bazi}。此处为固定合成样例，不代表真实排盘。`
    },
    紫微斗数: {
      重点宫位: `命宫主星：${Array.isArray(report.summary.chart.mingStar) ? report.summary.chart.mingStar.join("、") : report.summary.chart.mingStar}`,
      四化: "静态演示不执行真实四化计算。"
    }
  };
}

function focusName(focus: string) {
  const names: Record<string, string> = {
    brief: "免费简批",
    full: "综合全盘",
    career: "事业财运",
    relationship: "感情关系",
    wealth: "年度财富"
  };
  return names[focus] || "综合全盘";
}

function pad(value: number) {
  return String(value).padStart(2, "0");
}
