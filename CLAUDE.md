# CLAUDE.md - AI Assistant Guide for Weekly-Plan Repository

## Project Overview

This repository contains the **Job Responsibility-Driven Weekly Work Plan Management System** requirements specification documentation. The system is designed for managing employee weekly work plans based on their job positions and core responsibilities.

**Primary Language**: Chinese (Simplified)
**Document Type**: Software Requirements Specification (需求规格说明书)
**Current Version**: V1.1
**Domain**: Work management, organizational productivity, project planning

## Repository Purpose

This repository serves as the central documentation hub for a work planning management system that:
- Defines job positions and their core responsibilities
- Maps standard task types to each responsibility
- Provides initialization data for system implementation
- Structures work planning around organizational roles

## Current Repository Structure

```
/home/user/weekly-plan/
├── README.md          # Appendix A: Job Responsibilities Initialization List (附录A)
└── CLAUDE.md          # This file - AI assistant guide
```

### File Descriptions

**README.md**
- **Purpose**: Appendix A of the requirements specification
- **Content**: Initialization checklist for 13 key job positions
- **Structure**: Hierarchical organization of positions → responsibilities → task types
- **Language**: Chinese with some English technical terms

## Document Structure & Conventions

### Hierarchical Organization

The documentation follows a consistent 3-level hierarchy:

```
### Position (岗位)
  * Core Responsibility (核心职责)
    * Standard Task Type (标准任务类型)
```

### 13 Defined Job Positions

The system currently defines these positions:

**Customer-Facing Roles:**
1. 研发工程师 (R&D Engineer)
2. 销售经理 (Sales Manager)
3. 工程交付工程师 (On-site Delivery Engineer)
4. 售后客服 (After-sales Support)
5. 技术支持工程师 (Technical Support Engineer)
6. 项目经理 (Project Manager)
7. 售前工程师 (Presales Engineer)
8. 项目总监 (Project Director)
9. 业务工程师 (Business Engineer)

**Internal Support Roles:**
10. 人力资源 (HR)
11. 财务 (Finance)
12. 行政 (Admin)
13. 信息中心 (Internal IT)

### Responsibility Structure Pattern

Each position follows this pattern:
- **Core Responsibility N**: Description (sometimes with industry context in parentheses)
  - Multiple standard task types listed as sub-items
  - Task types describe concrete, actionable work items

### Language & Terminology Conventions

1. **Mixed Language Usage**:
   - Primary content in Chinese
   - Technical abbreviations in English (R&D, ETL, SIT, UAT, PoC, WBS, etc.)
   - Some English terms in parentheses (e.g., "Code Review", "Go-live Support", "Mentor")

2. **Industry Context Markers**:
   - Industry-specific contexts noted in parentheses: "(金融)" for finance industry
   - Location-specific tasks marked: "(现场)" for on-site work
   - Work mode indicators: "(现场/远程)" for on-site/remote

3. **Document Formatting**:
   - Uses Markdown with numbered lists for positions
   - Uses bullet points (*) for responsibilities and tasks
   - Hierarchical indentation for clarity
   - English translations in parentheses for key terms

## Content Analysis & Patterns

### Task Type Categories by Role

**Development Roles** focus on:
- Requirements analysis and technical design
- Coding, testing, and code review
- Bug fixing and optimization
- Documentation

**Sales/Presales Roles** focus on:
- Customer relationship management
- Solution design and presentation
- Bidding support
- Contract and payment tracking

**Delivery Roles** focus on:
- Requirements gathering on-site
- ETL development and configuration
- System deployment and testing
- Customer training and handover

**Support Roles** focus on:
- Issue tracking and resolution
- System maintenance and upgrades
- Performance tuning
- Customer communication

**Management Roles** focus on:
- Project planning and monitoring
- Resource coordination
- Risk and change management
- Stakeholder reporting

**Internal Support Roles** focus on:
- Administrative processes
- Compliance and reporting
- Infrastructure maintenance
- Employee services

### Industry Domain Context

The system appears tailored for a **software/data product company** serving the **financial sector** (金融), with emphasis on:
- ETL (Extract, Transform, Load) processes
- Data governance and analytics
- Regulatory compliance considerations
- On-site delivery model
- Enterprise software lifecycle management

## Development Workflows

### When Adding New Positions

1. Follow the established numbering pattern (### N. 岗位：)
2. Use both Chinese and English abbreviations in parentheses
3. Define 2-5 core responsibilities per position
4. Each responsibility should have 2-6 standard task types
5. Maintain consistent indentation and markdown formatting

### When Modifying Existing Content

1. Preserve the hierarchical structure
2. Keep the existing numbering scheme
3. Maintain bilingual terminology where established
4. Ensure task types are specific and actionable
5. Consider cross-role dependencies when adding/removing tasks

### Documentation Standards

- **Consistency**: Follow existing patterns for new content
- **Clarity**: Task types should be concrete and measurable
- **Completeness**: Cover the full scope of each role's responsibilities
- **Context**: Add industry/location markers where relevant
- **Bilingual**: Include English terms for technical concepts

## Git Workflow

### Branch Strategy

- **Claude Development Branches**: Format `claude/claude-md-{session-id}`
- Current branch: `claude/claude-md-mi1pb5obcy9jdrzr-01YERyMC7E5AmxHSitA39FBe`
- All development should occur on designated Claude branches
- Push to origin with `-u` flag for new branches

### Commit Message Guidelines

- Use clear, descriptive messages
- Reference document sections when applicable
- Example: "Add Appendix A: Job Responsibilities Initialization List"
- Keep commits focused on single logical changes

### Current State

- **Branches**: 1 active branch (Claude development branch)
- **Commits**: 1 initial commit
- **Remote**: Connected to origin
- **Status**: Clean working directory

## Key Conventions for AI Assistants

### Language Handling

1. **Preserve Chinese Content**: Do not translate Chinese text unless explicitly asked
2. **Maintain Bilingual Terms**: Keep established English abbreviations (R&D, PM, UAT, etc.)
3. **Use Appropriate Terminology**: Understand both Chinese and English versions of role names
4. **Context Awareness**: Recognize industry-specific terms (ETL, SIT, UAT, WBS, PoC, etc.)

### Content Modification Guidelines

1. **Structural Integrity**: Maintain the Position → Responsibility → Task hierarchy
2. **Formatting Consistency**: Use markdown formatting matching existing style
3. **Completeness**: Ensure all positions have comprehensive responsibility coverage
4. **Practical Focus**: Task types should be actionable and measurable
5. **Balance**: Each position should have comparable detail level

### When Analyzing This Repository

1. **Document Purpose**: This is requirements specification, not implementation code
2. **Audience**: Intended for system designers, developers, and stakeholders
3. **Scope**: Currently contains only Appendix A; expect additional spec documents
4. **Version Tracking**: Documents have version numbers (currently V1.1)
5. **Data Dictionary**: This serves as the canonical reference for job positions and tasks

### Expected Future Additions

Based on the "Appendix A" designation, anticipate:
- Main requirements specification document
- Additional appendices (B, C, etc.) for:
  - System architecture
  - Data models
  - User interface specifications
  - Business rules
  - Test cases
  - Implementation guidelines
- Potentially separate language versions

## Technical Context

### System Design Implications

From the job responsibilities defined, the target system likely includes:

1. **Job Position Master Data**: Repository of positions and responsibilities
2. **Task Type Library**: Categorized by position and responsibility
3. **User/Employee Mapping**: Assignment of users to positions
4. **Work Plan Module**: Weekly planning based on responsibilities
5. **Task Tracking**: Assignment and completion tracking
6. **Reporting**: Analytics by position, responsibility, and task type

### Data Model Hints

Key entities implied by the documentation:
- **Position** (岗位)
- **Responsibility** (职责)
- **TaskType** (任务类型)
- **Employee/User**
- **WorkPlan** (工作计划)
- **Task** (具体任务)

### Integration Points

The system appears designed for organizations with:
- Multiple departments (sales, delivery, support, internal)
- Project-based work (project management roles)
- Customer delivery cycles (presales → delivery → support)
- Compliance needs (finance, HR processes)

## Common Tasks for AI Assistants

### Analysis Tasks

- **Position Coverage Analysis**: Which roles are over/under-defined
- **Task Distribution**: Number of tasks per position or responsibility
- **Cross-Role Dependencies**: Tasks that require coordination
- **Gap Analysis**: Missing responsibilities or task types

### Content Tasks

- **Adding New Positions**: Follow established patterns
- **Refining Task Types**: Making them more specific or measurable
- **Reorganizing Responsibilities**: Improving logical grouping
- **Translation Support**: Providing English equivalents when needed

### Documentation Tasks

- **Creating Additional Appendices**: Following similar structure
- **Version Management**: Updating version numbers and change logs
- **Cross-Reference Building**: Linking related responsibilities across positions
- **Glossary Creation**: Defining technical terms and abbreviations

## Quality Checklist

When modifying content, verify:

- [ ] Hierarchical structure is maintained
- [ ] Numbering is sequential and correct
- [ ] Markdown formatting is consistent
- [ ] Chinese text is grammatically correct
- [ ] English abbreviations are accurate
- [ ] Task types are specific and actionable
- [ ] Industry context markers are appropriate
- [ ] Indentation follows existing pattern
- [ ] No duplicate task types within same responsibility
- [ ] Position names use consistent formatting

## References & Context

### Document Type: 需求规格说明书 (Requirements Specification)
This is a formal software requirements document that defines what the system should do, typically including:
- Functional requirements
- Non-functional requirements
- Data definitions
- Use cases
- System constraints

### Version Control
- Current version: V1.1
- Previous versions not tracked in this repository
- Version updates should be reflected in document headers

---

**Last Updated**: 2025-11-16
**Repository**: /home/user/weekly-plan
**Current Branch**: claude/claude-md-mi1pb5obcy9jdrzr-01YERyMC7E5AmxHSitA39FBe
**AI Assistant**: This guide is maintained for Claude Code and other AI assistants working with this repository.
