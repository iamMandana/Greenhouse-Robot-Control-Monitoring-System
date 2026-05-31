# Secure Greenhouse Robot Control System

## Overview

The Secure Greenhouse Robot Control System is a Python desktop application designed to monitor and control an autonomous greenhouse robot through a graphical user interface (GUI).

The system combines real-time environmental monitoring, robot control, autonomous decision-making, and secure user authentication within a single platform. It was developed as part of a university project focused on autonomous secure systems and IoT security.

## Features

### Security
- User authentication system
- SHA-256 password hashing
- Account lockout after multiple failed login attempts
- Optional Two-Factor Authentication (TOTP)
- Role-Based Access Control (RBAC)
- Administrator and Operator user roles
- Password reset and account recovery through 2FA

### Robot Monitoring
- Real-time robot position tracking
- Battery level monitoring
- Robot state monitoring
- Autonomous and manual operation modes
- Emergency stop functionality
- Charging management

### Environmental Monitoring
- Temperature monitoring
- Humidity monitoring
- Soil moisture monitoring
- Light intensity monitoring
- Threshold-based warning system

### Autonomous Decision Engine
The system automatically controls:

- Cooling Fan
- Water Pump
- Heater
- Grow Lights

based on environmental sensor readings.

### Data Visualisation
- Real-time sensor dashboards
- Historical sensor graphs
- Live environmental trend monitoring using Matplotlib

### User Management
Administrators can:

- Create users
- Delete users
- Lock or unlock accounts
- Reset passwords
- Change user roles
- Manage account permissions

## System Architecture

The application follows a modular architecture consisting of:

- Authentication Module
- Robot Simulation Module
- GUI Components
- Data Visualisation Module
- User Management Module
- JSON Data Storage

This design improves maintainability, scalability, and separation of concerns.

## Technologies Used

- Python
- Tkinter
- ttk
- Matplotlib
- PyOTP
- Hashlib (SHA-256)
- JSON
- QRCode
- Pillow (PIL)

## Project Structure
project/
│
├── main.py
├── auth.py
├── robot.py
├── login_window.py
├── dashboard.py
├── robot_panel.py
├── sensors_panel.py
├── sensor_graphs.py
├── admin_panel.py
├── user_settings.py
└── users.json


## Security Design

The system implements several security principles:

- Defence in Depth
- Least Privilege
- Account Lockout Protection
- Secure Credential Storage
- Multi-Factor Authentication
- Role Separation

These measures help reduce the risk of unauthorised access and improve overall system security.

## Future Improvements

Potential future enhancements include:

- SQLite or PostgreSQL database integration
- Argon2 password hashing
- Encrypted credential storage
- Session timeout management
- Audit logging
- MQTT-based sensor communication
- Docker deployment
- Integration with physical greenhouse hardware

## Screenshots

### Login Interface
<img width="505" height="587" alt="image" src="https://github.com/user-attachments/assets/eb6ecce3-a637-441e-8a77-d3486bb1879f" />


### Dashboard & Sensor Monitoring
<img width="861" height="528" alt="image" src="https://github.com/user-attachments/assets/a45f5157-b81c-4b5c-bfad-f8cab2727da4" />


### Admin Panel
<img width="940" height="643" alt="image" src="https://github.com/user-attachments/assets/915e8769-adf9-48f1-bdb3-267568cf570a" />


### Sensor Graphs
<img width="881" height="611" alt="image" src="https://github.com/user-attachments/assets/5e071340-5362-4c8c-91be-3e894454ebe5" />

