# Government Sector Development Guidelines

## Overview
This configuration applies to projects within government and public sector organizations, specifically for the ex-GPT system at Korea Expressway Corporation. These guidelines ensure compliance with public sector standards, security requirements, and operational protocols.

## Core Principles

### Security-First Development
- All code must adhere to government-grade security standards
- Implement data protection measures at every layer
- Personal information detection and protection mechanisms mandatory
- Access control and permission systems must be integrated from the start
- Human-in-the-loop verification for sensitive operations
- Monthly security audits and personal data scanning protocols

### Regulatory Compliance
- Follow Korean data protection laws and regulations
- Implement audit logging for all system operations
- Ensure traceable decision-making processes
- Maintain compliance with internal governance standards
- Document all security-related implementations

### Operational Requirements
- Real-time document management capabilities
- Integration with existing legacy systems (WizeNut, mobile office, travel/approval/finance systems)
- Scalable architecture supporting government-scale operations
- High availability and disaster recovery protocols
- Performance monitoring and optimization capabilities

## Technical Architecture Constraints

### Integration Requirements
- Must integrate with existing WizeNut permission structure
- Support for existing user hierarchy and access controls
- Backward compatibility with legacy document management systems
- API-based integration with mobile office applications
- Real-time data synchronization capabilities

### Performance Standards
- Sub-second response times for document queries
- Concurrent user support for government-scale deployment
- Efficient GPU resource utilization (H100 server optimization)
- Scalable vector database operations
- Real-time document processing and indexing

### Data Management
- Centralized document repository management
- Version control for regulatory documents
- Automated duplicate detection and filtering
- Real-time document update propagation
- Hierarchical access control implementation

## Development Guidelines

### Code Structure
- Modular architecture supporting role-based access
- Clear separation between data processing and presentation layers
- Comprehensive error handling and logging
- Standardized API design patterns
- Documentation for all government-specific implementations

### Testing Requirements
- Government-grade security testing protocols
- Performance testing under load conditions
- Integration testing with legacy systems
- User acceptance testing with actual government users
- Compliance verification testing

### Deployment Considerations
- Phased deployment approach (July 1st target)
- Rollback capabilities for system updates
- Monitoring and alerting systems
- Backup and recovery procedures
- Maintenance window planning
