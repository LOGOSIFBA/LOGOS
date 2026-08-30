# LOGOS — Autonomous Robotics Team

Autonomous robotics project developed by **Team LOGOS**, representing the **Federal Institute of Bahia (IFBA)** in the **2026 Brazilian Robotics Olympiad (OBR)**.

The project integrates **software development, electronics, mechanical design, embedded systems, sensors, control algorithms, and autonomous navigation** into a complete mobile robotic platform designed to solve the challenges proposed by the OBR Rescue Line competition.

During our participation in **OBR 2026**, Team LOGOS received the **Extra Innovation Award**.

---

## Team LOGOS

- **Rafael Lima Ribeiro dos Santos**
- **Larissa Valentin**
- **Israel Santos**
- **Chanderson Santos**

The project was developed with support from the **IFBA Robotics Laboratory** and the **GSAM — Automation and Mechatronics Systems Research Group**.

We also received technical guidance, knowledge, and support from:

- **Igor Lisboa**
- **Henrique Scander**
- **Prof. Andrea Bitencourt**

Their support was fundamental throughout the development, testing, and preparation of the robot for the competition.

---

## OBR 2026

Team LOGOS participated in the **2026 Brazilian Robotics Olympiad — Rescue Line**, representing the Federal Institute of Bahia.

The competition requires the development of an autonomous robot capable of navigating a track containing several challenges.

These include situations such as:

- Straight-line navigation
- Curves
- Sharp 90-degree turns
- Intersections
- Line gaps
- Color markings
- Obstacles
- Lost-line recovery
- Ramps and changes in terrain
- Autonomous decision-making
- Rescue-related challenges

The development of the robot required the integration of multiple engineering areas rather than only software.

The project involved:

- Programming
- Electronics
- Mechanical design
- Embedded systems
- Sensor integration
- Motor control
- Control systems
- Physical prototyping
- Testing and calibration

---

## Achievement

### OBR 2026 — Extra Innovation Award

Team LOGOS received the:

> 🏆 **Extra Innovation Award — OBR 2026**

The recognition made our first participation in the Brazilian Robotics Olympiad even more significant and reflected the work carried out throughout the development of the robot.

---

# Robot Overview

The LOGOS robot is an autonomous mobile robotic platform designed to interpret its environment through different sensors and make navigation decisions in real time.

Its operation combines three major areas:

1. **Software and autonomous control**
2. **Electronics and hardware integration**
3. **Mechanical design and prototyping**

The final system was built through continuous integration between these areas.

---

# Software

The main control software was developed in **Python** using **Open-RDK** for communication with the robot hardware.

The software architecture separates the main control loop from navigation, PID control, motor commands, and movement-related logic.

The robot continuously:

1. Reads its sensors
2. Identifies the current track situation
3. Selects an appropriate behavior
4. Controls the motors
5. Returns to normal line following when possible

---

## Navigation Flow

~~~text
             Sensors
                │
                ▼
       Environment Reading
                │
                ▼
      Situation Identification
                │
        ┌───────┴────────┐
        │                │
        ▼                ▼
 Normal Track      Special Situation
        │                │
        ▼                ▼
 PID Following     Dedicated Maneuver
        │                │
        └───────┬────────┘
                ▼
           Motor Control
                │
                ▼
          Next Reading
~~~

---

# PID Line Following

During normal track conditions, the robot uses a **PID controller** to maintain alignment with the line.

The infrared sensor provides information about the line position.

The PID controller calculates the tracking error and continuously corrects the motor speeds.

Conceptually:

~~~text
Line Position
     │
     ▼
Tracking Error
     │
     ▼
PID Controller
     │
     ▼
Motor Correction
     │
 ┌───┴───┐
 ▼       ▼
Left    Right
Motor   Motor
~~~

This improves robot stability during:

- Straight sections
- Smooth curves
- Direction corrections
- Continuous line tracking

---

# Track Handling

The robot contains dedicated logic for situations where normal PID following is not enough.

## 90-Degree Turns

Specific infrared sensor patterns are used to detect possible sharp turns.

When a candidate is detected, the robot temporarily leaves normal line-following mode and performs a dedicated maneuver.

---

## Line Gaps

The robot can identify situations where the line temporarily disappears.

Instead of immediately considering the track lost, the robot attempts to continue forward and detect the line again.

---

## Lost-Line Recovery

When the robot completely loses the line, recovery logic attempts to locate the track and resume normal navigation.

---

## Color Detection

Color sensors are used to identify special markings on the track.

These markings can modify the robot's navigation decisions.

Red detection can also be used as a stopping condition.

---

## Obstacle Detection

A distance sensor allows the robot to identify obstacles positioned in front of it.

Dedicated obstacle-handling logic can then be executed before the robot returns to the original track.

---

# Competition Strategy

During development, several navigation strategies were studied and tested.

One of the most important engineering decisions was prioritizing:

- Reliability
- Repeatability
- Predictable behavior
- Physical testing

For several special maneuvers, the competition version of the robot used **time-based movement sequences**.

Although more advanced approaches such as odometry were also studied during development, time-based behaviors had accumulated significantly more physical testing before the competition.

This created an important engineering trade-off:

~~~text
More Advanced Strategy
        vs.
More Tested Strategy
~~~

For OBR 2026, reliability was considered more important than introducing a technique that had not yet received the same amount of validation on the physical robot.

---

# Electronics

The electronics system is responsible for connecting the computational control logic to the physical robot.

The robot integrates:

- Motor control
- Infrared line sensing
- Color sensing
- Distance sensing
- Power distribution
- Embedded processing
- Hardware communication

The electronic architecture was developed to allow the software to obtain environmental information and independently control the robot's actuators.

---

## Sensor Integration

Different sensors provide complementary information to the navigation system.

### Infrared Line Sensor

Responsible for detecting:

- Line position
- Track alignment
- Curves
- Gaps
- Possible intersections
- Sharp turns

### Color Sensors

Used to detect color markings that represent special conditions on the OBR track.

### Distance Sensor

Used for obstacle detection and distance-related navigation decisions.

---

## Motor Control

The robot uses independent motor control for differential-drive navigation.

This allows the software to perform:

- Straight movement
- Curves
- In-place rotation
- Direction correction
- Special maneuvers

Different speeds can be applied to each side of the robot.

For example:

~~~text
Left Motor      Right Motor
    25              25
        Straight

Left Motor      Right Motor
    15              30
        Curve

Left Motor      Right Motor
   -20              20
        Rotation
~~~

---

# Mechanical Design and Modeling

Mechanical development was another important part of the project.

The robot had to provide a structure capable of integrating:

- Motors
- Wheels
- Sensors
- Electronic components
- Wiring
- Processing hardware
- Mechanical mechanisms

Mechanical design decisions directly affect robot performance.

Factors considered during development included:

- Component positioning
- Sensor height
- Sensor alignment
- Center of gravity
- Weight distribution
- Wheel positioning
- Structural rigidity
- Accessibility for maintenance
- Space for electronics
- Cable organization

---

## Prototyping and Iteration

The mechanical structure was not treated as an isolated part of the project.

Changes in software often required mechanical adjustments, while changes in robot geometry could influence PID tuning and sensor behavior.

The development process therefore followed an iterative cycle:

~~~text
Mechanical Design
       │
       ▼
Electronics Integration
       │
       ▼
Software Development
       │
       ▼
Physical Testing
       │
       ▼
Problem Identification
       │
       └───────────────┐
                       ▼
                    Redesign
~~~

This iterative process allowed the robot to evolve based on observations made during real track testing.

---

# System Integration

The robot can be understood as the integration of three major layers:

~~~text
┌──────────────────────────────┐
│          SOFTWARE            │
│                              │
│ PID • Navigation • Decisions │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│         ELECTRONICS          │
│                              │
│ Sensors • Motors • Control   │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│         MECHANICS            │
│                              │
│ Structure • Wheels • Layout  │
└──────────────────────────────┘
~~~

None of these areas operate independently.

The final robot is the result of their integration.

---

# Project Structure

~~~text
LOGOS/
├── line_codes/
│   ├── CommandDriver.py
│   ├── line_functions.py
│   ├── main.py
│   ├── odometry.py
│   ├── pid.py
│   └── vespera/
│
├── testes_cam/
│   └── pattern.png
│
├── .gitattributes
└── README.md
~~~

---

# Core Modules

## `main.py`

Main execution loop of the robot.

Responsibilities include:

- Open-RDK initialization
- Hardware connection
- Line sensor reading
- Color sensor reading
- Distance sensor reading
- PID line following
- Track condition detection
- Navigation coordination
- Motor control

---

## `line_functions.py`

Contains most of the navigation and track-handling logic.

Responsibilities include:

- Curve detection
- Gap detection
- Lost-line recovery
- Obstacle handling
- Special maneuvers
- Motor coordination
- Track interpretation

---

## `pid.py`

Contains the PID controller responsible for normal line following.

---

## `odometry.py`

Contains odometry and movement-estimation experiments developed during the project.

Odometry was studied as an alternative approach for movement control, although the competition strategy prioritized the maneuvers that had received the greatest amount of physical testing.

---

## `CommandDriver.py`

Provides an abstraction for sending and managing motor commands.

---

# Technologies and Areas

- Python
- Open-RDK
- Robotics
- PID Control
- Embedded Systems
- Autonomous Navigation
- Electronics
- Mechanical Design
- Sensor Integration
- Infrared Sensors
- Color Sensors
- Distance Sensors
- Motor Control
- Differential Drive
- Control Systems
- Prototyping

---

# Running the Project

The project requires:

- A configured Open-RDK environment
- Compatible robot hardware
- Correct sensor identifiers
- Correct motor identifiers

Navigate to:

~~~bash
cd line_codes
~~~

Run:

~~~bash
python main.py
~~~

Hardware identifiers must correspond to the devices connected to the robot.

---

# Development Methodology

Development was strongly based on physical testing.

Individual systems were progressively validated before integration.

The general process followed:

~~~text
Mechanical Assembly
       ↓
Electronics Integration
       ↓
Hardware Communication
       ↓
Sensor Calibration
       ↓
Motor Testing
       ↓
PID Development
       ↓
Special Maneuvers
       ↓
Track Testing
       ↓
Adjustment
       ↓
Competition Validation
~~~

This approach allowed problems to be isolated and corrected before introducing additional complexity.

---

# OBR 2026

The 2026 season represented Team LOGOS' first participation in the Brazilian Robotics Olympiad.

In addition to the technical challenges, the project provided practical experience involving:

- Engineering decisions
- Teamwork
- Problem-solving
- Debugging
- Robotics
- Software development
- Electronics
- Mechanical design
- Testing under real conditions

The experience resulted in the team's first recognition at the competition:

> 🏆 **Extra Innovation Award — OBR 2026**

---

# Future Development

Future versions of the robot may explore:

- More advanced odometry
- Sensor fusion
- Improved navigation algorithms
- More robust intersection detection
- Improved obstacle handling
- Rescue-room navigation
- Computer vision
- More advanced movement control
- Improved mechanical design

---

# Organization

**Team LOGOS**

Federal Institute of Bahia — **IFBA**

**GSAM — Automation and Mechatronics Systems Research Group**

**IFBA Robotics Laboratory**

---

# Repository

https://github.com/LOGOSIFBA/LOGOS
