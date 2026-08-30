# LOGOS

Autonomous mobile robotics project developed by **Team LOGOS**, a robotics team from the **Federal Institute of Bahia (IFBA) — Salvador Campus**.

The project integrates **mechanical design, electronics, embedded systems, sensors, control algorithms, and autonomous navigation** into a line-following and rescue-oriented mobile robot.

Team LOGOS participated in the **2026 Brazilian Robotics Olympiad (OBR)**, where the team received the **Extra Innovation Award**.

---

## About Team LOGOS

LOGOS is a student robotics team from **IFBA — Instituto Federal da Bahia, Campus Salvador**.

The project was developed as a complete robotic system rather than only a software application. The robot required the integration of:

- Mechanical structure and assembly
- Motors and drivetrain
- Embedded electronics
- Motor control
- Line sensing
- Color sensing
- Distance sensing
- Autonomous navigation
- PID control
- Movement strategies
- Physical testing and calibration

Development was supported by the **GSAM — Sistema de Automação e Mecatrônica** and the **IFBA Robotics Laboratory**.

---

## OBR 2026

Team LOGOS participated in the **2026 Brazilian Robotics Olympiad (OBR)** with an autonomous robot designed for the challenges of line following, track interpretation, obstacle handling, and rescue-oriented navigation.

The 2026 team was composed of:

- **Rafael Lima Ribeiro dos Santos**
- **Larissa Valentin**
- **Israel Santos**
- **Chanderson Santos**

LOGOS represented IFBA alongside another team, **Robovante**.

---

## Achievement

### Extra Innovation Award — OBR 2026

Team LOGOS received the **Extra Innovation Award** during OBR 2026.

The award recognizes the work developed by the team as a whole throughout the design, integration, experimentation, and competition process.

---

## Support and Mentorship

The project was developed with institutional and technical support from:

- **IFBA — Instituto Federal da Bahia**
- **GSAM — Sistema de Automação e Mecatrônica**
- **IFBA Robotics Laboratory**

The team also received important technical support from:

- **Igor Lisboa**
- **Henrique Scander**

Special thanks to **Professor Andrea Bitencourt**, whose support was fundamental to the team's participation in OBR.

Her contribution included encouraging the team to participate, helping provide materials and resources, enabling access to GSAM and the Robotics Laboratory, and supporting the team throughout the preparation process.

---

## Robot Overview

The LOGOS robot is the result of the integration of multiple engineering areas.

At a high level, the system can be represented as:

    Sensors
       |
       v
    Perception
       |
       v
    Navigation Logic
       |
       +-------------------+
       |                   |
       v                   v
    PID Line          Special Track
    Following           Behaviors
       |                   |
       +---------+---------+
                 |
                 v
           Motor Control
                 |
                 v
        Mechanical System

The software currently stored in this repository represents the control and experimentation layer of a larger physical robotics project.

---

## Mechanical Design

The mechanical subsystem provides the physical platform required for navigation and interaction with the track.

The project involved work with elements such as:

- Robot chassis and structural assembly
- Motors
- Wheels
- Transmission
- Sensor positioning
- Mechanical integration with the electronics
- Mechanisms required by the robot's competition tasks

Mechanical design decisions directly affect software behavior.

Wheel traction, chassis geometry, weight distribution, sensor height, drivetrain behavior, and assembly tolerances all influence how accurately the robot can follow lines and execute maneuvers.

For this reason, movement parameters cannot be treated as purely software values: they must be validated on the physical robot.

The repository currently focuses mainly on software and experimental code and does not yet contain complete mechanical CAD documentation.

---

## Electronics

The robot combines embedded processing, sensors, motor actuation, and power electronics.

The development context includes:

- Raspberry Pi
- Motor control electronics
- Infrared line sensing
- RGB/color sensing
- Distance sensing
- Motors
- Embedded power system
- Communication between processing and robot peripherals

The software interacts with these devices through **Open-RDK**, which provides the interface used by the Python control application to access motors and sensors.

The repository itself primarily documents the software side of this integration; complete electrical schematics are not currently included.

---

## Sensors

The current main control code accesses several sensor types through Open-RDK.

### Line Sensor

The line sensor provides:

- Line detection state
- Digital sensor values
- Estimated line position

These values are used both for normal PID line following and for recognizing special track patterns.

### Color Sensors

Two color sensors are used by the current control logic.

The software checks for colors such as:

- Green
- Red

Green markings are used by the navigation logic to classify direction-related situations.

### Distance Sensor

A distance sensor is used to detect obstacles in front of the robot and trigger a dedicated obstacle-handling maneuver.

### Camera Experiments

The repository also contains experimental computer-vision code using a camera, OpenCV, and NumPy.

These files explore image thresholding, regions of interest, line position estimation, and PID calculations based on image data.

This camera code should be considered **experimental work** and is not presented here as the main navigation system used by the robot.

---

## Software Architecture

The main software is located in `line_codes/`.

The control loop combines:

1. Sensor acquisition
2. Track interpretation
3. PID line following
4. Special-condition detection
5. Motor commands
6. Movement and recovery strategies

The current main program uses Open-RDK to connect to:

- Two traction motors
- A line sensor
- A distance sensor
- Two color sensors

A `LatestCommandDriver` abstraction is used to handle motor speed commands asynchronously.

---

## PID Line Following

During normal line following, the robot uses a PID controller.

The line sensor estimates the position of the line relative to the center of the robot.

The control flow is:

    Line Sensor
         |
         v
    Line Position
         |
         v
        Error
         |
         v
         PID
         |
         v
    Motor Correction

Conceptually:

    error = target_position - measured_position

    correction = PID(error)

    left_speed  = base_speed + correction
    right_speed = base_speed - correction

The PID controller continuously adjusts the difference between the left and right motor commands to keep the robot aligned with the line.

PID line following and odometry solve different problems.

The PID controller handles **continuous trajectory correction based on the detected line**.

Odometry, when used, estimates **robot movement based on wheel displacement**.

---

## Track Handling

Normal PID control is not sufficient for every situation encountered on the track.

The current software includes logic for situations such as:

- Sharp curves and possible 90-degree situations
- Multiple possible paths
- Green markings
- 180-degree indications
- Line gaps
- Lost-line recovery
- Obstacles
- End-of-course red detection

Different situations may combine sensor information with predefined movement sequences.

---

## Competition Strategy

One of the most important engineering decisions in this project was choosing which navigation strategy to trust during competition.

During development, the team studied and implemented odometry concepts. An `Odometry` module is present in the repository and estimates robot pose from left and right motor position telemetry.

However, several special maneuvers in the competition-oriented navigation code use **time-calibrated movement sequences**.

Examples in the current code include timed:

- Rotations
- Obstacle avoidance movements
- Direction searches
- Color-marking maneuvers
- Short forward and backward movements

This was a deliberate engineering decision.

The time-based strategy had received significantly more **physical testing on the actual robot** before OBR 2026.

For competition, the priority was not selecting the most complex control method. The priority was selecting the method whose behavior was best understood and most extensively validated.

Important criteria included:

- Reliability
- Repeatability
- Known robot behavior
- Amount of physical testing
- Calibration effort
- Competition risk
- Recovery behavior

### Time-Based Movement and Odometry

Time-based movement is essentially an open-loop movement strategy: the system commands a motor action for a calibrated interval and assumes that the physical result will remain sufficiently close to what was observed during testing.

Its accuracy can be affected by:

- Surface conditions
- Wheel slip
- Mechanical differences
- Changes in traction
- Robot alignment
- Calibration
- Interaction with obstacles or track geometry

Odometry introduces a different approach.

Instead of relying exclusively on elapsed time, movement can be estimated from wheel rotation.

However, odometry is not automatically more accurate in every situation.

It is also affected by:

- Wheel slip
- Incorrect wheel dimensions
- Wheel diameter differences
- Incorrect wheel-base measurements
- Mechanical tolerances
- Measurement errors
- Accumulated pose error

Therefore, the engineering question is not simply:

> Which approach is more advanced?

A more useful question is:

> Which approach has sufficient accuracy, validation, and robustness for the current requirement?

For OBR 2026, the extensively tested strategy was the appropriate choice for several competition maneuvers.

---

## Odometry

Although several competition maneuvers use timing, the repository also contains a differential-drive odometry implementation.

The software reads motor position telemetry and converts wheel rotation into estimated wheel displacement.

For each update:

    Right Wheel Rotation ---> Right Wheel Displacement
                                      |
                                      |
    Left Wheel Rotation ----> Left Wheel Displacement
                                      |
                                      v
                            Differential-Drive Model
                                      |
                         +------------+------------+
                         |                         |
                         v                         v
                  Linear Movement             Rotation
                         |                         |
                         +------------+------------+
                                      |
                                      v
                                Robot Pose
                              (x, y, theta)

The current implementation maintains:

- `x`
- `y`
- `theta`

The presence of this module reflects the team's experimentation with alternative movement-control strategies, even though it was not the primary mechanism used for every competition maneuver.

---

## Project Structure

    LOGOS/
    ├── line_codes/
    │   ├── CommandDriver.py
    │   ├── line_functions.py
    │   ├── main.py
    │   ├── odometry.py
    │   ├── pid.py
    │   │
    │   ├── honesto/
    │   │   ├── bola.py
    │   │   ├── linha_erro.py
    │   │   └── roi.py
    │   │
    │   └── desonesto/
    │       ├── outrabola.py
    │       └── teste.py
    │
    ├── testes_cam/
    │   └── pattern.png
    │
    └── .gitattributes

The `honesto/`, `desonesto/`, and `testes_cam/` directories contain experimental work related to camera and vision tests and should not be interpreted as the main control architecture of the robot.

---

## Main Modules

### `line_codes/main.py`

Main runtime loop.

It connects to the robot devices through Open-RDK and coordinates:

- Line sensor readings
- Color sensor readings
- Distance sensing
- PID line following
- Special track handling
- Motor commands
- Robot stopping conditions

### `line_codes/line_functions.py`

Contains most of the navigation behaviors.

Current code includes logic related to:

- Curve candidate detection
- Color marking detection
- Gap detection
- Line recovery
- Obstacle handling
- Direction checking
- PID line following
- Motor movement helpers
- Experimental odometry-based rotations

### `line_codes/pid.py`

Implements the PID controller used during normal line following.

The implementation contains:

- Proportional term
- Integral accumulation
- Derivative term
- Time-step handling
- Output limiting

### `line_codes/odometry.py`

Implements differential-drive odometry.

Motor position telemetry is converted to left and right wheel displacement and then used to estimate:

- Linear displacement
- Angular displacement
- `x`
- `y`
- `theta`

### `line_codes/CommandDriver.py`

Provides a threaded motor command abstraction.

The driver stores the latest pending motor command and sends it through a dedicated worker thread.

---

## Technologies

The project includes or experiments with:

- Python
- Open-RDK
- Raspberry Pi
- Embedded robotics
- PID control
- Differential-drive odometry
- Infrared sensing
- RGB/color sensing
- Distance sensing
- Motor control
- OpenCV — experimental camera work
- NumPy — experimental camera work
- Mechanical and electronic integration

---

## Development and Testing

Development was strongly based on physical experimentation.

A typical robotics development cycle involved:

    Implement
       |
       v
    Test on Robot
       |
       v
    Observe Behavior
       |
       v
    Adjust Parameters / Mechanics / Logic
       |
       v
    Test Again

This was particularly important for:

- PID tuning
- Motor speeds
- Rotation times
- Obstacle avoidance
- Sensor positioning
- Green-marking detection
- Track recovery
- Mechanical adjustments

The repository should therefore be understood as part of an iterative hardware-software development process.

---

## Future Development

Possible future work includes:

- Further evaluation of odometry-based special maneuvers
- Improved motion estimation and calibration
- Additional sensor validation
- More structured hardware testing tools
- Improved navigation state organization
- Further camera and computer-vision experiments
- Better documentation of mechanical and electronic subsystems
- Automated software tests for hardware-independent logic
- Continued comparison between movement-control strategies

These items represent possible development directions and should not be interpreted as currently implemented features.

---

## Acknowledgements

Team LOGOS thanks everyone who contributed to the development and preparation of the project.

Special thanks to:

- **IFBA SSA — Instituto Federal de Educação, Ciência e Tecnologia da Bahia, Campus Salvador
- **GSAM — Sistema de Automação e Mecatrônica**
- **IFBA Robotics Laboratory**
- **Professor Andrea Cassia Peixoto Bitencourt**
- **Igor Lisboa Ramos**
- **Henrique Scander Coelho**

The team also recognizes the work of **Robovante**, which represented IFBA alongside LOGOS during OBR 2026.

---

## Team LOGOS — OBR 2026

- **Rafael Lima Ribeiro dos Santos**
- **Larissa do Nascimento Valentim de Oliveira**
- **Israel Santos Rodrigues de Carvalho**
- **Chanderson Santos de Santana**
```
