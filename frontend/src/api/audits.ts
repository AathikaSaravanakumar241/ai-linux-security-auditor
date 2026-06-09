import apiClient from './client';
import { AuditDetail, AuditSummary, AuditRequest, AuditComparison } from '../types';

/**
 * Executes a security audit on a remote server.
 */
export const runAudit = (credentials: AuditRequest): Promise<any> => {
  return apiClient.post('/audits', credentials);
};

/**
 * Fetches audit run logs history.
 */
export const getAudits = (limit: number = 50, offset: number = 0, serverIp?: string): Promise<AuditSummary[]> => {
  const params: any = { limit, offset };
  if (serverIp) {
    params.server_ip = serverIp;
  }
  return apiClient.get('/audits', { params });
};

/**
 * Fetches detail report and findings for a specific audit.
 */
export const getAuditById = (auditId: string): Promise<AuditDetail> => {
  return apiClient.get(`/audits/${auditId}`);
};

/**
 * Fetches comparison results with the previous audit for the same server.
 */
export const getAuditComparison = (auditId: string): Promise<AuditComparison | null> => {
  return apiClient.get(`/audits/${auditId}/comparison`);
};

/**
 * Performs a backend health check query.
 */
export const healthCheck = (): Promise<any> => {
  return apiClient.get('/health');
};
