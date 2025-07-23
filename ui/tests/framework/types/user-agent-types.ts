/**
 * User Agent Types and Interfaces
 * Phase 31 - UI Testing Framework
 */

export interface UserAgent {
  id: string;
  name: string;
  role: UserRole;
  experience: ExperienceLevel;
  department: string;
  email: string;
  available: boolean;
}

export enum UserRole {
  INDUSTRIAL_ENGINEER = 'industrial_engineer',
  CONTROL_TECHNICIAN = 'control_technician',
  PLANT_MANAGER = 'plant_manager',
  IT_ADMINISTRATOR = 'it_administrator',
  EXTERNAL_VALIDATOR = 'external_validator'
}

export enum ExperienceLevel {
  BEGINNER = 'beginner',
  INTERMEDIATE = 'intermediate',
  ADVANCED = 'advanced',
  EXPERT = 'expert'
}

export interface UserFeedback {
  overallSatisfaction: number; // 1-10
  easeOfUse: number; // 1-10
  visualDesign: number; // 1-10
  performance: number; // 1-10
  functionality: number; // 1-10
  wouldRecommend: boolean;
  mostLiked: string[];
  mostDisliked: string[];
  suggestions: string[];
  additionalComments: string;
} 