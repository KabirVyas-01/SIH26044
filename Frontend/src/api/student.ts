import { request } from './client';
import { BackendPosting, BackendAssessmentQuestion } from '../types';

export const studentApi = {
  async getProfile(): Promise<{ profile: any }> {
    return request('/api/student/profile');
  },

  async updateProfile(data: Record<string, any>): Promise<{ message: string; updated: any }> {
    return request('/api/student/profile', {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  async uploadDocument(documentType: string, fileUrl: string): Promise<any> {
    return request('/api/student/documents', {
      method: 'POST',
      body: JSON.stringify({ document_type: documentType, file_url: fileUrl }),
    });
  },

  async getPostings(): Promise<{ postings: BackendPosting[] }> {
    return request('/api/student/postings');
  },

  async applyToPosting(postingId: number): Promise<{ message: string; application_id: number }> {
    return request(`/api/student/postings/${postingId}/apply`, {
      method: 'POST',
    });
  },

  async getMyApplications(): Promise<{ my_applications: any[] }> {
    return request('/api/student/applications');
  },

  async getSkillQuestions(skillName: string): Promise<{ skill: string; questions: BackendAssessmentQuestion[] }> {
    return request(`/api/student/assessments/${encodeURIComponent(skillName)}/questions`);
  },

  async submitSkillTest(skillName: string, answers: Record<string, string>): Promise<{ message: string; result: any }> {
    return request(`/api/student/assessments/${encodeURIComponent(skillName)}/submit`, {
      method: 'POST',
      body: JSON.stringify({ answers }),
    });
  },

  async getJobFitScore(postingId: number): Promise<any> {
    return request(`/api/student/postings/${postingId}/fit-score`);
  },

  async getJobCourseRecommendations(postingId: number): Promise<any> {
    return request(`/api/student/postings/${postingId}/recommendations`);
  },

  async analyzeResume(resumeText: string, targetRole: string = 'Software Engineer'): Promise<any> {
    return request('/api/student/ai/resume-analyzer', {
      method: 'POST',
      body: JSON.stringify({ resume_text: resumeText, target_role: targetRole }),
    });
  },

  async generateRoadmap(targetRole: string = 'Full Stack Developer'): Promise<any> {
    return request('/api/student/ai/roadmap-generator', {
      method: 'POST',
      body: JSON.stringify({ target_role: targetRole }),
    });
  },

  async getInterviewQuestions(skill: string = 'Python'): Promise<any> {
    return request('/api/student/ai/interview-prep', {
      method: 'POST',
      body: JSON.stringify({ skill }),
    });
  },
};
