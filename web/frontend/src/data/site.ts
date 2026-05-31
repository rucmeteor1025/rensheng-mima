import {
  Activity,
  BrainCircuit,
  ChartNoAxesCombined,
  CheckCircle2,
  DatabaseZap,
  Eye,
  Fingerprint,
  HeartHandshake,
  LockKeyhole,
  Orbit,
  ShieldCheck,
  Sparkles,
  TrendingUp,
  UserRoundCheck
} from "lucide-react";
import type { FocusType } from "../types";

export const navItems = [
  { label: "首页", href: "/" },
  { label: "分析", href: "/analysis" },
  { label: "价格", href: "/pricing" },
  { label: "隐私", href: "/privacy" },
  { label: "关于", href: "/about" }
];

export const featureCards = [
  {
    icon: BrainCircuit,
    title: "AI 深度解析",
    text: "把八字、紫微和辅助人格层拆开再融合，不做模板拼接。"
  },
  {
    icon: Fingerprint,
    title: "性格画像",
    text: "从命盘结构到行为风格，解释你如何选择、承压、恢复。"
  },
  {
    icon: TrendingUp,
    title: "运势推演",
    text: "以阶段主题为主，不夸张断事，给出能执行的趋避建议。"
  }
];

export const analysisOptions: Array<{
  id: FocusType;
  title: string;
  price: number;
  desc: string;
}> = [
  { id: "full", title: "综合全盘", price: 29.9, desc: "八字 + 紫微 + 融合判断" },
  { id: "career", title: "事业财运", price: 19.9, desc: "职业位置、财路与机会承接" },
  { id: "relationship", title: "感情关系", price: 19.9, desc: "关系需求、相处节奏与边界" },
  { id: "wealth", title: "年度运势", price: 9.9, desc: "阶段主题、机会与风险提示" },
  { id: "brief", title: "简批体验", price: 0, desc: "免费摘要与基础盘面" }
];

export const privacyCards = [
  { icon: LockKeyhole, title: "数据加密", text: "生产版按 AES-256 加密出生信息和报告内容。" },
  { icon: DatabaseZap, title: "最小采集", text: "只采集排盘必要字段，不强制真实姓名或身份证。" },
  { icon: Eye, title: "透明使用", text: "出生信息仅用于排盘分析，不写入公开材料。" },
  { icon: UserRoundCheck, title: "完全控制", text: "支持删除记录、导出数据、撤回授权。" }
];

export const aboutPrinciples = [
  { icon: ChartNoAxesCombined, title: "数据驱动", text: "以结构化盘面和可追溯字段为基础。" },
  { icon: HeartHandshake, title: "用户至上", text: "先帮助用户读懂自己，再谈付费转化。" },
  { icon: Orbit, title: "技术为本", text: "前端、命理引擎和隐私链路分层演进。" },
  { icon: ShieldCheck, title: "温暖克制", text: "不给恐吓式断语，不替用户做重大决定。" }
];

export const architecture = [
  "命理知识引擎",
  "AI 分析模型",
  "心理映射层",
  "数据置信系统"
];

export const galleryTiles = [
  ["命宫", "紫微", "天府"],
  ["日主", "庚金", "月令"],
  ["财帛", "武曲", "禄存"],
  ["官禄", "七杀", "破军"],
  ["夫妻", "天相", "四化"],
  ["福德", "太阴", "天梁"],
  ["迁移", "天马", "外局"],
  ["疾厄", "五行", "调候"],
  ["MBTI", "行为", "压力"],
  ["星座", "外显", "情绪"],
  ["血型", "相处", "节奏"],
  ["趋避", "行动", "定力"]
];

export const kernelWords = [
  "AI", "八字", "紫微", "命宫", "日主", "四化", "十神", "财帛", "官禄", "福德",
  "大运", "流年", "MBTI", "星座", "血型", "趋避", "置信", "结构", "周期", "选择"
];

export const pricingPlans = [
  {
    title: "简批体验",
    price: "免费",
    badge: "",
    desc: "适合第一次试用，查看基础盘面和 3 条核心判断。",
    benefits: ["免费摘要", "八字四柱", "性格底色", "可删除记录"],
    cta: "立即体验"
  },
  {
    title: "单次完整版",
    price: "¥29.9",
    badge: "最受欢迎",
    desc: "适合认真阅读一份完整命盘报告。",
    benefits: ["八字命盘精解", "紫微斗数详批", "事业财运深度分析", "趋避建议"],
    cta: "解锁完整版"
  },
  {
    title: "年度会员",
    price: "¥198",
    badge: "",
    desc: "适合长期跟踪年度主题、专题报告和历史记录。",
    benefits: ["多次生成", "历史报告", "专题分析", "优先新功能"],
    cta: "即将开放"
  }
];

export const faqItems = [
  ["命理分析是否替代现实决策？", "不能。报告仅供参考，重大决策仍需结合现实信息和专业意见。"],
  ["出生信息会被公开吗？", "不会。正式版会提供删除、导出和撤回授权能力。"],
  ["支付后如何查看报告？", "支付成功后订单状态会切换为已解锁，完整报告在分析页展示。"],
  ["可以删除记录吗？", "可以。当前本地版已提供删除本次记录能力。"]
];

export const statusSteps = [
  { label: "未支付", icon: LockKeyhole },
  { label: "支付中", icon: Activity },
  { label: "已解锁", icon: CheckCircle2 },
  { label: "失败可重试", icon: Sparkles }
];
