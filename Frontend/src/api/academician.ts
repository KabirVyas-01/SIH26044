import { request } from './client';
import { BackendPosting } from '../types';

export const academicianApi = {
  async getMyPostings(): Promise<{ postings: BackendPosting[] }> {
    return request('/api/academician/postings');
  },

  async createPosting(data: {
    title: string;
    description: string;
    required_skills: string;
    posting_type: string;
  }): Promise<{ message: string; posting: any }> {
    return request('/api/academician/postings', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async giveFeedback(studentId: number, feedbackText: string): Promise<{ message: string; feedback_id: number }> {
    return request(`/api/academician/students/${studentId}/feedback`, {
      method: 'POST',
      body: JSON.stringify({ feedback_text: feedbackText }),
    });
  },

  async getMyFeedbacks(): Promise<{ feedbacks: any[] }> {
    return request('/api/academician/feedbacks');
  },
};
