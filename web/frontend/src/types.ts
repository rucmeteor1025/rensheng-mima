export type FocusType = "full" | "career" | "relationship" | "wealth" | "brief";

export interface FortunePayload {
  year: number;
  month: number;
  day: number;
  hour: number;
  minute: number;
  gender: string;
  place: string;
  focus: FocusType | string;
  mbti?: string;
  bloodType?: string;
}

export interface SummaryLine {
  title: string;
  text: string;
}

export interface FortuneSummary {
  basic: {
    birthTime: string;
    lunar: string;
    gender: string;
    place: string;
    mode: string;
    version: string;
  };
  chart: {
    bazi: string;
    dayMaster: string;
    strength: string;
    useful: string;
    mingStar: string[] | string;
    shenPalace: string;
  };
  free: SummaryLine[];
  paidPreview: SummaryLine[];
  disclaimer: string;
}

export interface FortuneResponse {
  ok: boolean;
  reportId: string;
  summary: FortuneSummary;
  privacy: {
    storage: string;
    deleteEndpoint: string;
  };
}

export interface CheckoutOrder {
  reportId: string;
  title: string;
  price: number;
  focus: FocusType;
  createdAt: string;
}

export type FullFortuneReport = Record<string, unknown>;

export interface FullReportResponse {
  ok: boolean;
  reportId: string;
  report?: FullFortuneReport;
  error?: string;
}
