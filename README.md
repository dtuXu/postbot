# PostBot — Autonomous Delivery Robot

An autonomous LEGO EV3 / BrickPi robot that navigates a 1.2 m × 1.2 m office map, checks each office for a "restricted" sticker, finds the recipient sticker inside valid offices, drops a package on it, and finishes in the mail room — all without human input and under 3 minutes.

Built by **Team 11** for McGill's ECSE 211 *Design Principles and Methods* (Fall 2025).

**Result:** completed the full mission on the official map in about **2 min 45 s** (requirement: under 3 min), within 2% of the team's 297-hour time budget.

## How it works

| Part | Approach |
| --- | --- |
| Navigation | Proportional wall-following on an ultrasonic sensor (target ≈ 6 cm), gyro-controlled 90° turns |
| Perception | RGB colour sensor on a rotating arm; readings normalized and matched to 7 calibrated colours (nearest mean) |
| Decision logic | Finite state machine: follow corridor → door → restricted check → room scan → deliver → exit → mail room |
| Delivery | One motor releases two foam cubes in sequence by gravity |
| Safety | Rear touch sensor starts the run and acts as an emergency stop |

## Repository

| Path | What it is |
| --- | --- |
| `robot.py` | Main controller: state machine, office routine, mail-room approach |
| `tests/` | Component tests for colour detection, wall-following drive and gyro |
| `calibration/` | Scripts to sample sensor colours, compute colour means and plot drive tests |

> The scripts import `utils.brick` and `utils.sound`, the BrickPi helper library supplied by the course. It is not included here.

## Team

Aoxiang Bi · Saad Dannaoui · Mathieu Guimond · Mingyang Jin · **Ayham Nassar** (hardware & testing) · Rémi Séguin

**Stack:** Python · BrickPi · LEGO EV3/NXT motors and sensors
