# LOGOS — Autonomous Robotics Team

Autonomous robotics project developed by **Team LOGOS**, representing the **Federal Institute of Bahia (IFBA)** in the **2026 Brazilian Robotics Olympiad (OBR)**.

The project focuses on autonomous line-following navigation using **Python**, **Open-RDK**, infrared line sensing, PID control, color detection, distance sensing, and dedicated logic for handling different situations found on the OBR track.

During our participation in OBR 2026, Team LOGOS received the **Extra Innovation Award**.

---

## Team

### LOGOS

- **Rafael Lima Ribeiro dos Santos** — Team Captain
- **Larissa Valentin**
- **Israel Santos**
- **Chanderson Santos**

The team developed and tested the robot with the support of the **IFBA Robotics Laboratory** and the **GSAM — Automation and Mechatronics Systems Research Group**.

We also received technical guidance and support from **Igor Lisboa**, **Henrique Scander**, and Professor **Andrea Bitencourt** throughout the development process.

---

## OBR 2026

Team LOGOS participated in the **2026 Brazilian Robotics Olympiad (OBR)** representing IFBA.

The competition required the robot to autonomously navigate a track containing different challenges such as:

- Curves
- Intersections
- Line gaps
- Sharp turns
- Color markings
- Obstacles
- Line recovery situations
- Autonomous navigation decisions

For the competition, development focused heavily on **reliability and repeatability**.

Several navigation behaviors were implemented using experimentally tested movement sequences and timing-based maneuvers when they proved more reliable under competition conditions.

This approach allowed the team to prioritize a stable robot behavior over experimental navigation techniques that had not yet been tested extensively enough for competition use.

### Achievement

> **Extra Innovation Award — OBR 2026**

The award recognized the team's technical development and innovative approach during the competition.

---

## Overview

The robot continuously reads its sensors and determines the appropriate navigation behavior according to the current track situation.

Its control architecture combines:

- PID-based line following
- Infrared line sensing
- Motor control
- Color sensing
- Distance sensing
- Track situation detection
- Autonomous decision-making
- Pre-tested special maneuvers

Normal line following is performed using PID control.

When a special condition is detected, the robot temporarily leaves the normal PID navigation flow and executes a dedicated maneuver before returning to line following.

---

## Navigation Flow

```text
Sensor Reading
      ↓
Track Situation Detection
      ↓
 ┌───────────────┐
 │ Normal Track  │
 └───────┬───────┘
         ↓
 PID Line Following

        or

 ┌──────────────────┐
 │ Special Situation│
 └────────┬─────────┘
          ↓
 Dedicated Maneuver
          ↓
 Return to Line
