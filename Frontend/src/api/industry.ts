import { request } from './client';
import { BackendPosting, BackendApplicant } from '../types';

export const industryApi = {
  async getMyPostings(): Promise<{ postings: BackendPosting[] }> {
    return request('/api/industry/postings');
  },

  async createPosting(data: {
    title: string;
    description: string;
    required_skills: string;
    posting_type: string;
  }): Promise<{ message: string; posting: any }> {
    return request('/api/industry/postings', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async getApplicants(postingId: number): Promise<{
    posting: any;
    applicant_count: number;
    applicants: BackendApplicant[];
  }> {
    return request(`/api/industry/postings/${postingId}/applicants`);
  },

  async updateApplicantStatus(applicationId: number, status: 'shortlisted' | 'rejected' | 'selected'): Promise<any> {
    return request(`/api/industry/applications/${applicationId}/status`, {
      method: 'PATCH',
      body: JSON.stringify({ status }),
    });
  },
};
