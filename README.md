# Team B-Tide Solution Plan

# 1. Your Team at a Glance

## Team Name / Tagline  

Team Tide

*Real-time, AI incident monitoring meets distributed cloud intelligence*

## Team Members  
| Name | GitHub Handle | Role(s) |
|-------|---------------|---------|
| Kenneth Mead | Xerner | Code Guy |
| Erik Hu | erikhu1 |  |
| Axel Lichtner | Axellichtner93 |  |
| Leonardo Ferrari | padaleto |  |
| Donghyun Kim | smwkbgmn | Code Kid & Ideabank |

## Challenge  
*Which challenge have you decided to compete for?*

SDV Lab

## Core Idea  
*What is your rough solution idea?*

Similar to how Google Maps and Waze report traffic and accidents, our application will report and alert the driver 
of objects of interest. Such as
- police
- road conditions and hazards
The difference between Google Maps and Waze and our application is ours relies on the power of the ADAS system to detect these objects, identify them, and report them to a central server.

In addition, our application will report when a driver decides to leave the vehicle. This couples with the first feature to essentially report when an obstacle caused the autonomous drive to become undesirable for customers.

In user story format
- As a driver, I want to be alerted when there is a police car ahead of me so that I can slow down and avoid getting a ticket.
- As a city ordinator, I want to know if the cities robo-taxi service is being used so I know if the cities millions of dollars spent on the service is being used effectively

*Sketch something that helps understand e.g. mermaid chart*

---

# 2. How Do You Work

## Development Process  
*Brief overview of your development process.*

Our team has three sub-teams
- Carla Simulation Team
  - Kenny Mead
  - Leonardo Ferrari

- Notification Application Team
  - Donghyun Kim
  - Axel Lichtner

- Infotainment Team
  - Erik Hu

We will use these Eclipse tools
- Carla
- uProtocol
- MQTT or Zenoh
- Ankaios

Contract between applications
- A contract will be created that defines the output of the Carla Simulation Team. The Application Team will then use this contract to develop their application.

Coding standards
- We will use VS Code
- We will use the VS Code black formatter extension for Python code. This will make Git diffs as small as possible
- We will use the VS Code pylance extension for linting Python code
- We will use type hints in Python code
- We will use Docker devcontainers to ensure everyone has the same development environment
- We will use Sonarqube for static code analysis and security vulnerability detection 
- We will use CodeQL for static code analysis to identify potential vulnerabilities and improve code quality. CodeQL is configured to analyze the codebase for security issues and other defects. 

We have a branch protection rule preventing pushes to main. This way code is always opened on a feature branch and put in a pull request for review

### Planning & Tracking  
*How do you plan and track progress?*

We will use Github Projects to track open todo items using the Kanban view. We will use Git and Github pull requests to track changes and code reviews.

### Quality Assurance  
*How do you ensure quality (e.g., testing, documentation, code reviews)?*

- One person from one team always reviews the code from the other team. At least one review is required before merging a pull request.
- Comments are written showing the intention of the code.
- We will try our best to write self-documenting code. That is code that explains itself (e.g. human-readable variables) so that other developers know how to use it with having little to no documentation.
- We will write unit tests for core logic of the Carla app and the Notification app
- When we have a working prototype, we will write script(s) to automatically run through the prototype and check if everything is working as expected (integration/acceptance testing).

## Communication  
*How does your team communicate?*

5 minute standups every hour. Other than that, over the table ad-hoc discussions. We will use Slack for digital communication.

## Decision Making
*How are decisions made in your team?*

- We huddled in a meeting room and discussed all the ideas we had. We then agreed on which ideas were the most desirable and feasible.
- Diagrams or descriptive comments are made before code is written. 
- Any ideas are run by at least two other team members before being turned into real implementation.
- Any decision that affects both teams, is discussed with both teams before being implemented.
