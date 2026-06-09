/**
 * Shared TypeScript definitions matching API structures.
 */

export interface SeverityBreakdown {
  critical: number;
  high: number;
  medium: number;
  low: number;
}

export interface Finding {
  id: string;
  severity: 'Critical' | 'High' | 'Medium' | 'Low' | string;
  issue: string;
  explanation: string;
  impact: string;
  fix_command: string;
}

export interface AuditSummary {
  id: string;
  server_ip: string;
  audit_date: string;
  severity_breakdown: SeverityBreakdown;
}

export interface AuditDetail {
  id: string;
  server_ip: string;
  audit_date: string;
  raw_report: string;
  findings: Finding[];
  severity_breakdown: SeverityBreakdown;
}

export interface ApiError {
  code: string;
  message: string;
  details?: string;
}

export interface ApiResponse<T = any> {
  success: boolean;
  data: T | null;
  error: ApiError | null;
  timestamp: string;
}
