# 🤖 Human-Following Robot and Autonomous Car using Raspberry Pi Pico H

## 📸 Project Showcase

### 🎥 Video Demonstration
Watch the working demo of our human-following robot in action:

➡️ [Click to watch on YouTube](https://your-video-link-here.com)

> Replace the above link with your actual video URL after uploading to YouTube or Google Drive.

---

### 🖼️ Robot Car Pictures

Below are images of our robot prototype:

![Front View of Robot Car](https://github.com/moyen-ahmed/follwing-robot-with-raspberry-pi-/blob/main/report/1753279231897.jpg?raw=true)


![Side View of Robot Car](https://github.com/moyen-ahmed/follwing-robot-with-raspberry-pi-/blob/main/report/1753279231910.jpg?raw=true)

> 📌 Put your images in a folder named `images/` inside your GitHub repo, or use direct image links like `https://i.imgur.com/yourImage.jpg`.

---

## 🔍 Abstract

This project presents a **low-cost autonomous robot car** that follows a human or object using a **Raspberry Pi Pico H** microcontroller. Equipped with **ultrasonic sensors** and **Bluetooth connectivity**, it detects obstacles, adjusts its motion, and can be controlled remotely through a mobile app.

Rather than relying on complex machine learning models, the system uses **standard reactive control logic** to maintain a safe following distance and navigate its environment.

---

## 🧠 Features

- Follows humans or objects using ultrasonic distance sensing
- Avoids collisions with reactive logic (no AI)
- Bluetooth-controlled via Android/iOS app
- Driven by 4 DC motors with dual H-Bridge drivers
- Compact and low-power embedded system
- Designed for retail settings like malls or supermarkets

---

## 🛠️ Hardware Components

| Component                     | Description                                                                 |
|------------------------------|-----------------------------------------------------------------------------|
| Raspberry Pi Pico H          | Main controller, dual-core ARM Cortex M0+                                  |
| HC-SR04 Ultrasonic Sensor    | Measures distance for obstacle detection and following logic               |
| L298N Motor Driver           | Drives 4 DC geared motors                                                   |
| SG90 Servo Motor             | Provides 180° rotational control for sensor sweep                           |
| Bluetooth Module (HC-05/06)  | Connects with mobile app for remote control                                |
| 4× DC Geared Motors          | Drives the robot using differential drive                                   |
| Dual 7.4V Li-ion Battery     | Powers the motors and board                                                |
| Breadboard and Wiring        | For circuit prototyping and assembly                                        |

---

## ⚙️ Working Principle

1. **Initialization**: Configures GPIOs and PWM for motor and sensor control.
2. **Sensor Sweep**: Uses servo to detect object position (Left, Center, Right).
3. **Target Detection**:
   - If object is left/right → turns in that direction.
   - If object is centered → adjusts distance.
4. **Distance Adjustment**:
   - Too close → Moves backward.
   - Too far → Moves forward.
   - In range → Stops.

---

## 🧩 System Architecture

### 📦 Block Diagram

Power is supplied through two 7.4V Li-ion batteries. The Raspberry Pi Pico H handles all logic:
- Reads distance from ultrasonic sensors
- Sends PWM signals to motor drivers
- Interfaces with Bluetooth module for mobile commands

### 🔄 Flow Chart Overview

The robot:
- Detects the target using sensor sweep
- Determines direction and distance
- Moves accordingly while avoiding obstacles

---

## ⚡ Limitations

- **No object recognition**: Any object in range might be followed.
- **Sensor issues**: Affected by temperature, humidity, and surface reflectivity.
- **No path planning**: Limited to simple forward, back, and turn logic.
- **Reaction delay**: Loop delay may affect fast obstacle response.
- **Limited runtime**: Battery lasts about 1–2 hours per charge.

---

## 🚀 Future Vision

- Integrate AI-based object tracking using TinyML or OpenMV.
- Add SLAM-based path planning with LiDAR/depth sensors.
- Implement voice-controlled interaction using lightweight LLMs.
- Create collaborative swarm carts for shared retail spaces.
- Use solar or regenerative energy to extend battery life.

---

## 📱 Mobile App Integration

- Start / Stop the robot remotely
- Reconfigure settings via Bluetooth (Android/iOS)
- Monitor basic status information

---

## 📚 References

> A detailed list of references is available in the final section of the project report PDF.

---

## 👥 Contributors

- **Ishtiak Ahmed Moyen** – North South University  
- **Istiaque Ahemed** – North South University  
- **Rakib Rayhan** – North South University  
- **Md Kayes Mia** – North South University  
- **Supervisor**: Dr. Mohammad Abdul Qayum (Assistant Professor)

---

## 🏁 Conclusion

This project successfully demonstrates how a **Raspberry Pi Pico H** can be used to develop a **reactive human-following robot** suitable for retail environments. While current limitations exist, its modular and extensible design makes it ideal for future upgrades involving AI, voice control, and autonomous navigation.

---
