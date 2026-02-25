# SDL-3-New-Coordinates-Polar-visualizer

This project is an interactive Python application developed for a Self-Directed Learning (SDL) project covering **Chapter 3: New Coordinates** in Multivariable Calculus.  

The goal of this tool is to build intuition for **polar coordinates and coordinate transformations** by allowing users to visualize curves, regions, and geometric quantities directly in the plane.

Instead of working only symbolically, this program connects equations to geometry by showing how polar representations translate into Cartesian space and how integrals describe measurable quantities such as area and arc length.

---

## Project Objectives

This project focuses on the main learning goals of Unit 3:

- Converting between rectangular and polar coordinates
- Graphing polar curves \( r = f(\theta) \)
- Understanding regions described in polar coordinates
- Computing area using polar double integrals
- Approximating arc length of polar curves

The application emphasizes **visual understanding**, helping bridge the gap between formulas and geometric interpretation.

---

## Application Overview

The program contains four interactive modules.

---

### 1. Coordinate Conversion

Convert points between:

- Rectangular coordinates \((x, y)\)
- Polar coordinates \((r, \theta)\)

The position vector is displayed graphically to show how both coordinate systems describe the same point.

![Alt text](https://github.com/VictorGranado/SDL-3-New-Coordinates-Polar-visualizer/blob/5978af7408d06580418b097e34fde8b0c0ea5011/Screenshot%202026-02-24%20201157.png)

---

### 2. Polar Curve Plotter

Plot curves defined by:

\[
r = f(\theta)
\]

Examples include:
- Rose curves
- Cardioids
- Spirals
- Circles and limacons

The curve is rendered in the Cartesian plane, demonstrating how polar equations map into standard \(x,y\) space.

![Alt text](https://github.com/VictorGranado/SDL-3-New-Coordinates-Polar-visualizer/blob/5978af7408d06580418b097e34fde8b0c0ea5011/Screenshot%202026-02-24%20201316.png)

---

### 3. Polar Area Visualizer

Visualizes regions defined by:

\[
r_1(\theta) \le r \le r_2(\theta)
\]

and computes area using the polar double-integral formula:

\[
A=\int_{\alpha}^{\beta}\int_{r_1}^{r_2} r\,dr\,d\theta
\]

The shaded region is displayed along with:

- numerical polar integral approximation
- geometric verification using an \(xy\)-plane polygon check

This helps explain why the extra **\(r\)** factor appears in polar area integrals.

![Alt text](https://github.com/VictorGranado/SDL-3-New-Coordinates-Polar-visualizer/blob/5978af7408d06580418b097e34fde8b0c0ea5011/Screenshot%202026-02-24%20201444.png)

---

### 4. Polar Arc Length Explorer

Approximates arc length of polar curves using:

\[
L=\int_{\alpha}^{\beta}\sqrt{r(\theta)^2+\left(\frac{dr}{d\theta}\right)^2}\,d\theta
\]

The program also compares results with a chord-length approximation in Cartesian coordinates, reinforcing the geometric meaning of arc length.

![Alt text](https://github.com/VictorGranado/SDL-2-Curve-Transform-Curves-and-Parametric-Motion/blob/67a5fc092f2b421604b197e7792e453d3cb86428/Screenshot%202026-02-10%20215439.png)

---

## Installation

### Requirements
- Python 3.10+
- NumPy
- Matplotlib
- SymPy

Install dependencies:

```bash
pip install numpy matplotlib sympy
