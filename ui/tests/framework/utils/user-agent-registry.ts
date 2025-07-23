/**
 * User Agent Registry
 * Phase 31 - UI Testing Framework
 */

import { UserAgent, UserRole, ExperienceLevel } from '../types';

export class UserAgentRegistry {
  private userAgents: Map<string, UserAgent> = new Map();
  
  constructor() {
    this.registerDefaultUserAgents();
  }
  
  registerUserAgent(userAgent: UserAgent): void {
    this.userAgents.set(userAgent.id, userAgent);
  }
  
  getUserAgent(id: string): UserAgent | undefined {
    return this.userAgents.get(id);
  }
  
  getUserAgentsByRole(role: UserRole): UserAgent[] {
    return Array.from(this.userAgents.values()).filter(ua => ua.role === role);
  }
  
  getAvailableUserAgents(): UserAgent[] {
    return Array.from(this.userAgents.values()).filter(ua => ua.available);
  }
  
  getRequiredUserRoles(subPhase: string): UserRole[] {
    // Return required user roles for specific sub-phase
    switch (subPhase) {
      case 'Phase 31.1':
      case 'Phase 31.2':
        return [UserRole.INDUSTRIAL_ENGINEER, UserRole.IT_ADMINISTRATOR];
      case 'Phase 31.3':
      case 'Phase 31.4':
        return [UserRole.CONTROL_TECHNICIAN, UserRole.INDUSTRIAL_ENGINEER];
      default:
        return [
          UserRole.INDUSTRIAL_ENGINEER,
          UserRole.CONTROL_TECHNICIAN,
          UserRole.IT_ADMINISTRATOR
        ];
    }
  }
  
  private registerDefaultUserAgents(): void {
    this.registerUserAgent({
      id: 'ie-001',
      name: 'John Smith',
      role: UserRole.INDUSTRIAL_ENGINEER,
      experience: ExperienceLevel.ADVANCED,
      department: 'Process Engineering',
      email: 'john.smith@company.com',
      available: true
    });
    
    this.registerUserAgent({
      id: 'ct-001',
      name: 'Sarah Johnson',
      role: UserRole.CONTROL_TECHNICIAN,
      experience: ExperienceLevel.INTERMEDIATE,
      department: 'Operations',
      email: 'sarah.johnson@company.com',
      available: true
    });
    
    this.registerUserAgent({
      id: 'pm-001',
      name: 'Michael Brown',
      role: UserRole.PLANT_MANAGER,
      experience: ExperienceLevel.EXPERT,
      department: 'Management',
      email: 'michael.brown@company.com',
      available: true
    });
    
    this.registerUserAgent({
      id: 'it-001',
      name: 'Lisa Davis',
      role: UserRole.IT_ADMINISTRATOR,
      experience: ExperienceLevel.ADVANCED,
      department: 'Information Technology',
      email: 'lisa.davis@company.com',
      available: true
    });
    
    this.registerUserAgent({
      id: 'ext-001',
      name: 'Robert Wilson',
      role: UserRole.EXTERNAL_VALIDATOR,
      experience: ExperienceLevel.EXPERT,
      department: 'Quality Assurance',
      email: 'robert.wilson@external-qa.com',
      available: true
    });
  }
} 