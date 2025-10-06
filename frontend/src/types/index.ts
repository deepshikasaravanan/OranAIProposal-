export interface Opportunity {
  id?: string;
  title?: string;
  agency?: string;
  naics?: string;
  org_revenue_usd?: number;
  estimated_value_ok?: boolean;
  competitor_count?: number;
}

export interface ProcessResult {
  run_id?: string;
  outputs?: {
    docx?: string;
    requirements?: string;
    outlines?: string;
    gantt?: string;
    flowchart?: string;
  };
  section6_coverage?: Record<string, boolean>;
  branding_applied?: {
    brand_name?: string;
    header_right?: string;
  };
}

export interface PricingTier {
  id: string;
  name: string;
  tagline: string;
  trial?: string;
  price_month: number;
  contact?: boolean;
  highlight: boolean;
  features: string[];
}

export interface CapabilityCard {
  id: string;
  icon: string;
  title: string;
  description: string;
  status: 'active' | 'working' | 'coming-soon';
  action: string;
  onClick?: () => void;
}

export interface FileUpload {
  file: File;
  name: string;
  type: string;
  size: number;
}