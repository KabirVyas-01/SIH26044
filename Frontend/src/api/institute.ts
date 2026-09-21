import { request } from './client';

export const instituteApi = {
  async getDashboard(): Promise<{
    institute_stats: {
      enrolled_students: number;
      verified_students: number;
      average_skill_score: number;
      total_applications_sent: number;
      students_selected_for_jobs: number;
      students_shortlisted: number;
    };
  }> {
    return request('/api/institute/dashboard');
  },

  async getPendingVerifications(): Promise<{ pending_count: number; students: any[] }> {
    return request('/api/institute/verifications/pending');
  },

  async verifyStudent(studentId: number, status: 'verified' | 'rejected'): Promise<any> {
    return request(`/api/institute/verifications/${studentId}`, {
      method: 'POST',
      body: JSON.stringify({ status }),
    });
  },

  async getSkillDemandAnalytics(): Promise<{
    message: string;
    top_in_demand_skills: { skill: string; postings_count: number }[];
  }> {
    return request('/api/institute/analytics/skill-demand');
  },

  async getInstitutesList(): Promise<{ institutes: { id: number; name: string; admin_tpo_contact: string }[] }> {
    return request('/api/institute/list');
  },
};
