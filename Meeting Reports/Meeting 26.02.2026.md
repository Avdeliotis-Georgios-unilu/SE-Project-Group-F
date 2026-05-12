# First Meeting: Software Engineering Project Ideation

**Date:** February 26, 2026 | 13:05 – 14:20  
**Subject:** Brainstorming for Promotional CS Project

---

## 1. Objective

The goal of this meeting was to brainstorm and select a project concept to serve as an interactive, promotional exhibit for the computer science department to attract prospective students.

## 2. Brainstorming Phase: Initial Concepts

The group explored various ideas to serve as an engaging demonstration of computer science capabilities:

- **Gesture Recognition:** Using a camera to evaluate a user's aptitude for computer science fields through handshakes or movements.
- **"UniScratch":** A custom, team-built game inspired by the Scratch platform, designed to teach visitors the basics of programming.
- **Gaming & Interaction:** Exploration of Fruit Ninja-style games via camera, 2D arcade-style games, and domotic (home automation) systems.
- **Data & Analysis:** Ideas involving data analytics quizzes or hybrid apps that combine multiple data analysis tools.

## 3. Selected Project: "Improved Rock-Paper-Scissors (RPS)"

The team reached a consensus to develop a camera-based RPS game. The project challenges users to defeat an AI-powered bot in a competitive setting, serving as a dynamic showcase of how software engineering can create immersive, intelligent experiences. It bridges the gap between simple entertainment and complex data processing, highlighting the core competencies students gain in the field.

## 4. Technical Implementation & Architecture

### A. Game Flow

- The game would feature a 10-match series between the player and the bot.
- Winning is achieved by securing more victories than the bot; in the event of a draw, additional matches are played until the tie is broken.
- **Optional:** Potential rewards if the player successfully defeats the trained bot, to make it attractive.

### B. Hardware Integration

- The system will utilize a Raspberry Pi coupled with a camera.
- This setup allows the entire application to run locally on the hardware, demonstrating an edge-computing approach to the project.

### C. AI & Computer Vision

- The core of the interaction requires computer vision to recognize hand shapes (Rock, Paper, Scissors) in real-time.
- Two distinct bots will be programmed: a random bot (very easy) and a trained bot that utilizes an online-found dataset to determine the most effective play.

### D. Data Exploration & Visualization

- The system performs background analysis to log gameplay data.
- This allows for the study of bot performance, specifically assessing whether the trained bot consistently outperforms the random bot during live demonstrations, or if the dataset is accurate.
