# LOGOS

Autonomous robotics project developed in Python, focused on line following, sensor-based navigation, and autonomous handling of different track situations.

The robot uses **Open-RDK**, PID control, odometry, line sensors, color sensors, and distance sensing to make navigation decisions in real time.

## Features

* PID-based line following
* Differential drive control
* Odometry-based movement estimation
* Intersection detection
* 90-degree turn handling
* Line gap detection
* Lost-line recovery
* Obstacle detection and avoidance
* Color marking detection
* 180-degree turn handling
* Controlled movement using distance and rotation

## Technologies

* Python
* Open-RDK
* PID Control
* Differential Drive Odometry
* Sensor-based Navigation

## Project Structure

```text
LOGOS/
├── line_codes/
│   ├── CommandDriver.py
│   ├── line_functions.py
│   ├── main.py
│   ├── odometry.py
│   ├── pid.py
│   ├── desonesto/
│   └── honesto/
│
├── testes_cam/
│   └── pattern.png
│
└── .gitattributes
```

## Core Modules

### `main.py`

Main execution loop responsible for coordinating sensor readings, motor control, odometry updates, PID line following, and special navigation behaviors.

### `line_functions.py`

Contains the main navigation logic, including intersection handling, 90-degree turns, obstacle avoidance, line recovery, gap crossing, and color-based behaviors.

### `pid.py`

Implements the PID controller used to keep the robot aligned with the line.

### `odometry.py`

Estimates the robot's position and orientation based on motor movement.

### `CommandDriver.py`

Handles motor commands used during normal movement and special maneuvers.

## Navigation Flow

The robot continuously reads its sensors and selects the appropriate behavior.

```text
Sensor Reading
      ↓
Situation Detection
      ↓
Normal Line Following
      or
Special Maneuver
      ↓
Motor Control
      ↓
Odometry Update
```

During normal conditions, the robot follows the line using PID control.

When a special situation is detected, such as an obstacle, intersection, line gap, or color marking, the robot executes the corresponding maneuver before returning to normal line following.

## Running the Project

The project requires a configured Open-RDK environment and compatible robot hardware.

Navigate to the main code directory:

```bash
cd line_codes
```

Run:

```bash
python main.py
```

Sensor and motor serial numbers must match the devices connected to the robot.

## Development Status

The project is currently under active development.

Navigation strategies, sensor handling, and movement logic are continuously being tested and improved.

## Authors

LOGOS Robotics Team
