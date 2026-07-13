# Robot Rockstars 🎸🤖

Welcome to the **Robot Rockstars** repository! The bootcamp is designed to take beginners from a box of LEGO SPIKE Prime components to a competition-ready robot for the **WRO 2026 RoboMission Elementary** season (*"Robot Rockstars"*).

All programming is written in **Python using the Pybricks firmware/API**, offering professional-grade motor and gyro control out of the box.


## 🛠️ Technology Stack & Requirements

*   **Hardware:**
    *   LEGO SPIKE Prime Core Set (45678)
    *   LEGO SPIKE Prime Expansion Set (45681)
*   **Firmware:**
    *   [Pybricks](https://pybricks.com/) (replaces standard SPIKE Hub OS with standard MicroPython + Pybricks APIs).
*   **Tools:**
    *   [Pybricks Code Editor](https://code.pybricks.com/) (browser-based or desktop version).
    *   [Quarto](https://quarto.org/) (for compiling slides and index page).

---

## 📐 Domain Invariants & Rules

When modifying the code or curriculum planning documents, keep the following hard constraints in mind:
1.  **Robot Constraints (General Rules §5):** Start dimensions must be $\le 250 \times 250 \times 250$ mm. Total weight must be $\le 1.5$ kg. Only one robot/controller hub. **No wireless link** between components (Bluetooth/Wi-Fi off; program downloaded via cable).
2.  **6-Port Budget:** The stock LEGO Advanced Driving Base fills all 6 ports (2 large drive motors, 2 medium tool motors, 2 color sensors). **No ultrasonic/distance sensor is used.** Wall detection is handled via motor-stall detection and gyro orientation resetting.
3.  **Pedagogy — "Break it $\rightarrow$ Feel it $\rightarrow$ Fix it":** Introduce concepts live in class. Open with a naive approach that fails visibly (e.g., drift on open-loop driving), let the students feel the limitation, then introduce the technical solution (e.g., gyro-based straight driving) as the rescue.
4.  **Anchor-First Scoring:** Prioritize securing a reliable **~135-point anchor run** (Instruments + Cables + Bonus by avoidance + Microphone) with no active color sensing first. Then layer on the two fixed color notes (+40 points) for a gated **~175-point run** by Week 4. Randomization (+80 points) is treated as a Week-5 stretch goal.

---

## 🚀 Getting Started

-  To view the course portal locally, compile the Quarto index:
    ```bash
    quarto preview index.qmd
    ```

-  To run code on a SPIKE Prime, flash Pybricks firmware onto your hub, open the [Pybricks Code Editor](https://code.pybricks.com/).
