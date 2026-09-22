import { request } from './client';
import { User, UserRole } from '../types';

export const authApi = {
  async login(role: UserRole, email: string, password: string): Promise<{ message: string; user: User }> {
    const rolePaths: Record<UserRole, string> = {
      student: '/api/auth/students/login',
      industry: '/api/auth/industries/login',
      institute: '/api/auth/institutes/login',
      academician: '/api/auth/academicians/login',
    };
    return request(rolePaths[role], {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  },

  async signup(role: UserRole, payload: Record<string, any>): Promise<{ message: string; user: User }> {
    const rolePaths: Record<UserRole, string> = {
      student: '/api/auth/students/signup',
      industry: '/api/auth/industries/signup',
      institute: '/api/auth/institutes/signup',
      academician: '/api/auth/academicians/signup',
    };
    return request(rolePaths[role], {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  async getMe(): Promise<{ user: User | null }> {
    try {
      return await request('/api/auth/me', { method: 'GET' });
    } catch {
      return { user: null };
    }
  },

  async logout(): Promise<{ message: string }> {
    return request('/api/auth/logout', { method: 'POST' });
  },

  async sendOtp(email: string): Promise<{ message: string; demo_otp?: string }> {
    return request('/api/auth/send-otp', {
      method: 'POST',
      body: JSON.stringify({ email }),
    });
  },

  async verifyOtp(email: string, otp: string): Promise<{ message: string }> {
    return request('/api/auth/verify-otp', {
      method: 'POST',
      body: JSON.stringify({ email, otp }),
    });
  },

  async forgotPassword(email: string): Promise<{ message: string; is_demo?: boolean; demo_otp?: string }> {
    return request('/api/auth/forgot-password', {
      method: 'POST',
      body: JSON.stringify({ email }),
    });
  },

  async resetPassword(email: string, otp: string, new_password: string): Promise<{ message: string }> {
    return request('/api/auth/reset-password', {
      method: 'POST',
      body: JSON.stringify({ email, otp, new_password }),
    });
  },

  async getNotifications(): Promise<{ notifications: import('../types').NotificationItem[] }> {
    try {
      return await request('/api/auth/notifications', { method: 'GET' });
    } catch {
      return { notifications: [] };
    }
  },
};
