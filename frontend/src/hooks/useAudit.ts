import { useState, useCallback } from 'react';
import { runAudit as apiRunAudit, getAudits as apiGetAudits, getAuditById as apiGetAuditById, getAuditComparison as apiGetAuditComparison } from '../api/audits';
import { AuditRequest, AuditSummary, AuditDetail, AuditComparison } from '../types';

export function useAudit() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const runAudit = useCallback(async (credentials: AuditRequest): Promise<any> => {
    setLoading(true);
    setError(null);
    try {
      const result = await apiRunAudit(credentials);
      return result;
    } catch (err: any) {
      const errMsg = err.message || 'Security audit execution failed.';
      setError(errMsg);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchAudits = useCallback(async (limit = 50, offset = 0, serverIp?: string): Promise<AuditSummary[]> => {
    setLoading(true);
    setError(null);
    try {
      const result = await apiGetAudits(limit, offset, serverIp);
      return result;
    } catch (err: any) {
      const errMsg = err.message || 'Failed to fetch audit history.';
      setError(errMsg);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchAudit = useCallback(async (id: string): Promise<AuditDetail> => {
    setLoading(true);
    setError(null);
    try {
      const result = await apiGetAuditById(id);
      return result;
    } catch (err: any) {
      const errMsg = err.message || 'Failed to retrieve audit details.';
      setError(errMsg);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchComparison = useCallback(async (id: string): Promise<AuditComparison | null> => {
    setLoading(true);
    setError(null);
    try {
      const result = await apiGetAuditComparison(id);
      return result;
    } catch (err: any) {
      const errMsg = err.message || 'Failed to retrieve audit comparison.';
      setError(errMsg);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return { loading, error, runAudit, fetchAudits, fetchAudit, fetchComparison };
}

export default useAudit;
