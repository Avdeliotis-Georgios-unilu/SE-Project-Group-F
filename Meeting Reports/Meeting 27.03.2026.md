# Meeting Report: Project SE (Meeting #5)

**Date:** March 27th, 2026  
**Time:** 14:00  
**Attendance:** Everyone present

---

## 1. Topics Overview

- Overview of the workload (10-15 mins)
- Individual progress from each team member
- Integration & commits of main files
- Planning second sprint
- New ideas and next steps

---

## 2. Progress Check - Detailed Breakdown

Significant progress has been made across all core components of the project: camera integration, person detection, gesture detection, and recognition. Below is a detailed breakdown by team member:

### 2.1 Irina - Gesture Recognition System

**Accomplishments:**
- Developed a working gesture recognition program
- Successfully recognizes specific hand gestures: Rock, Paper, Scissors
- Core functionality is operational and ready for integration

**Challenges & Questions:**
- Some errors based on finger joints detection
- Readability/accuracy is relatively average (~50%)
- **Action Item:** Consider implementing efficiency testing (e.g., run gesture recognition 100 times and measure success rate)
- Need to improve accuracy metrics and reliability

---

### 2.2 Pella - UI Development & Project Management

**Accomplishments:**
- Trello board is nearly fully planned and organized
- UI design is complete with basic product mockups that look great
- Should be straightforward to integrate with the backend
- **Status:** Trello fully operational ✓

**Challenges & Questions:**
- Layout approval needed from team
- Decide on visual presentation: images vs. text labels or combination
- Integration approach with gesture recognition

---

### 2.3 Georgios - OpenCV & Raspberry Pi Integration

**Accomplishments:**
- Researched OpenCV implementation and best practices
- Implemented OpenCV code into the Raspberry Pi
- Initial setup progress on RPI

**Challenges & Questions:**
- **Critical:** Confirm if RPI is working properly
- Some dependencies may be lacking - need to verify all required packages are installed
- Need to figure out how to implement gesture recognition on RPI efficiently
- Hardware compatibility and resource constraints

---

### 2.4 Gabriel - Data Analysis & Bot Strategy

**Accomplishments:**
- Reviewed and analyzed the data
- Identified some winning patterns in the dataset

**Challenges & Questions:**
- **Data Reliability Question:** Are all data points reliable and valid?
- **Statistical Constraint:** Markov chaining (Order 1 and 2) not feasible with half of the data
- **Bot Improvement Strategy:** Two approaches to consider:
  1. Implement learning algorithm (adaptive bot)
  2. Create static algorithm/decision tree/finite state machine
  - Need team decision on which approach to pursue

---

## 3. Integration & Next Steps

- **Working component:** Camera display screen is functional
- **Next step:** Integrate camera feed with UI system
- **Team owners:** Irina + Pella to coordinate integration

---

## 4. New Ideas & Optional Features

### 4.1 Additional Gesture Integration
- If more gestures are successfully integrated, we can proceed with **Optional Feature #3 (Presentation-related)**
- Enhanced bot responses with visual representations

### 4.2 Bot Display Format
The bot answer should display gestures with ASCII art representation:

**Rock**
```
    _______
---'   ____)
      (_____)
      (_____)
      (____)
---.__(___)
```

**Paper**
```
    _______
---'   ____)____
          ______)
          _______)
         _______)
---.__________)
```

**Scissor**
```
    _______
---'   ____)____
          ______)
       __________)
      (____)
---.__(___)
```

---
