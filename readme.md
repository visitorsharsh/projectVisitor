# Visitor’s Management System

## Table of Contents

- [Introduction](#introduction)
  - Purpose
  - Scope
- [Architecture](#architecture)
  - Framework Used
  - Pros
  - Cons
  - HTML files/templates
- [File System](#file-system)
- [Database Layer](#database-layer)
- [Future Backlog](#future-backlog)
- [External Resources Used](#external-resources-used)

## Introduction

### Purpose

Streamline visitor management with a comprehensive app that securely stores and manages visitor data.

### Scope

- **Visitor Registration**: Capture visitor details such as name, contact information, purpose of visit, and check-in time.
- **Check-in and Check-out Management**: Efficiently track when visitors arrive and leave premises.
- **User-Friendly Interface**: Provide an intuitive interface for both visitors and administrators to enhance user experience.

## Architecture

### Framework Used

Python with Flask framework

### Pros

- **Simplicity**: Flask is known for its simplicity and minimalistic design.
- **Flexibility**: Highly flexible, allows developers to choose components they need.
- **Pythonic**: Integrates well with other Python libraries and frameworks.
- **Extensibility**: Supports third-party extensions to add functionality.

### Cons

- **Less Opinionated**: Minimalistic design can lead to inconsistency in larger projects.
- **Limited Built-in Functionality**: Requires reliance on third-party extensions or custom code.
- **Scalability**: May not scale as well for very large applications.
- **Learning Curve for Beginners**: While easier than some frameworks, still requires learning.

### HTML files/templates

- exit.html
- feedback.html
- intro.html
- layout.html
- submit.html
- visitors.html

## File System

### Static folder

Stores static components like images and CSS files.

- **Images**:
  - Background.png
  - Fusion1.png
  - award.png
- **main.css**: CSS file.

## Database Layer

- **Database Management System**: Uses SQLite3.
- **Tables**:
  - visitors: Stores visitor details including name and purpose of visit.
  - cards: Tracks the status of visitor cards.
  - Feedback: Stores visitor feedback.

## Future Backlog

- Bigger button for touch-screen usability.
- UI improvements: Space between buttons, full-screen capability.
- Security and validation enhancements: Facial recognition, encryption, SQL injection prevention.
- Operational improvements: Deployment, backup procedures, privacy policy considerations.
- Integration: Video systems, notification systems (e.g., Teams).

## External Resources Used

- [w3schools](https://www.w3schools.com/)
- [CodePen](https://codepen.io/)
- [Bootstrap](https://getbootstrap.com/)
- [ChatGPT](https://chatgpt.com/)
