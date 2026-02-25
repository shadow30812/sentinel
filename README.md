# Sentinel

## Project Overview

Sentinel is an advanced **Adaptive Streaming Multivariate Statistical Monitoring System** designed for modern, highly dynamic operating environments.

While traditional system monitors rely on static, hard-coded thresholds (e.g., "alert if CPU > 90%"), Sentinel takes an intelligent, machine-learning approach. Static thresholds often fail in contemporary workflows because a 90% CPU load might be perfectly normal during a scheduled rendering task, but highly suspicious if the system is supposed to be completely idle.

Sentinel solves this by monitoring OS hardware and system performance metrics in real-time, dynamically learning normal behavioral baselines on the fly without requiring any external, pre-trained datasets. By analyzing the relationships between metrics rather than looking at them in isolation, Sentinel can detect complex anomalies that standard tools miss.

Utilizing highly optimized dual-timescale recursive algorithms—essentially maintaining both a "short-term" and "long-term" memory of system behavior—it acts as a lightweight, unobtrusive daemon. It accurately detects both sudden system anomalies and gradual conceptual drift, seamlessly adapting its internal models to shifting system loads, new software deployments, and changing user behaviors over time.

---

## Features

### Real-Time System Monitoring

Streams and evaluates key system metrics continuously. This includes granular tracking of:

* CPU utilization
* RAM usage
* Disk I/O read/write rates
* Network I/O sent/received rates
* Motherboard thermal sensors

By gathering these simultaneously, Sentinel paints a complete, interconnected picture of the machine's immediate physical state, allowing it to discern the difference between a harmless localized file copy and a potential system-wide ransomware encryption event.

---

### Adaptive Multivariate Modeling

Rather than tracking metrics individually, Sentinel utilizes recursive covariance and mean updates to establish a continuous, multi-dimensional definition of your system's "normal" operating state.

By calculating the **Mahalanobis distance** of incoming data, it understands the correlations and variances between metrics. Unlike simple Euclidean distance, Mahalanobis distance accounts for the shape of the data distribution.

For example, high disk I/O during a network download is expected and normal, but high disk I/O paired with zero network or CPU activity might indicate a failing mechanical drive, a struggling swap file, or a rogue background process.

---

### Drift Detection (CUSUM)

Employs the CUSUM (Cumulative Sum) tracking algorithm to detect long-term, gradual shifts in system behavior.

Instead of triggering false alarms for temporary load spikes, CUSUM is highly sensitive to persistent, creeping changes—such as:

* A slow memory leak in a background service
* A fan slowly failing
* Gradual thermal degradation over months

Without this mechanism, a statistical model would eventually become obsolete and trigger constant false alarms.

When drift is confirmed, Sentinel automatically triggers model adjustments to safely realign its baseline to the new reality.

---

### Anomaly Detection & Risk Scoring

Identifies and flags extreme deviations in short-term system states.

To prevent alarm fatigue—a common issue where users simply ignore constant, overly-sensitive warnings—Sentinel uses non-linear severity accumulation to scale a "system risk pool."

Minor, fleeting anomalies are gracefully absorbed and forgiven as the pool naturally "drains" during normal operation, but sustained, high-severity spikes rapidly fill the risk pool. Once the pool overflows, it eventually triggers an active UI alert and a native audio alarm.

---

### Robust Persistence & Recovery

Sentinel automatically persists its atomic mathematical models and system state checkpoints to disk.

Using fail-safe atomic write operations (writing to a temporary file first, then seamlessly replacing the original at the OS level), it ensures that these critical save files are never corrupted, even during an unexpected power loss, kernel panic, or hard crash.

This allows the application to recover its learned baselines immediately upon restart without requiring a lengthy, resource-intensive retraining period.

---

### Daemon-like Behavior & IPC

Capable of operating silently in the system background with minimal overhead.

It includes a built-in Inter-Process Communication (IPC) wake-up mechanism via local sockets. If you attempt to launch Sentinel while it is already running in the background, the new process will simply summon the existing UI to the front and exit.

This guarantees zero port collisions, prevents memory bloat, and completely avoids redundant mathematical processing.

---

## Mathematical Foundations

Sentinel is built on robust, streaming statistical algorithms.

Rather than storing large historical datasets in memory, it iteratively updates mathematical models with every new data point $x_t$.

---

### 1. Multivariate Severity (Mahalanobis Distance)

To measure how "anomalous" the current system state is, Sentinel computes the Mahalanobis distance.

This measurement accounts for both the variance of individual metrics and the covariance (correlations) between them.

$$
D = \sqrt{(x - \mu)^T \Sigma^{-1} (x - \mu)}
$$

Where:

* $x$ is the current multi-dimensional observation vector (CPU, RAM, Disk, etc.)
* $\mu$ is the baseline mean vector
* $\Sigma^{-1}$ is the inverse covariance matrix

---

### 2. Adaptive Online Learning (Recursive Updates)

To continuously learn without unbounded memory growth, Sentinel utilizes an Exponentially Weighted Moving Average (EWMA) approach to update its models online.

#### Mean Update

$$
\mu_t = (1 - \lambda)\mu_{t-1} + \lambda x_t
$$

#### Covariance Update (Rank-1 Update)

$$
\Sigma_t = (1 - \lambda)\Sigma_{t-1} + \lambda (x_t - \mu_{t-1})(x_t - \mu_{t-1})^T
$$

Where $\lambda$ is the exponential forgetting factor (e.g., $0.01$ for short-term memory, $0.001$ for long-term memory).

---

### 3. Numerical Stability (Matrix Regularization)

If system metrics remain perfectly static (e.g., 0 network traffic), the covariance matrix $\Sigma$ can become singular and mathematically impossible to invert.

To prevent division-by-zero errors, Sentinel automatically applies Tikhonov-style regularization by adding a tiny epsilon $\epsilon$ to the diagonal (Identity matrix $I$):

$$
\Sigma_{reg} = \Sigma + \epsilon I
$$

---

### 4. Concept Drift Detection (CUSUM)

To detect slow, structural changes in system behavior (like a memory leak), the engine uses the Cumulative Sum (CUSUM) algorithm.

It tracks persistent deviations above a sensitivity parameter $k$.

$$
C_t = \max(0, C_{t-1} + (S_t - k))
$$

Where $S_t$ is the current anomaly Severity score.

If $C_t$ exceeds a predefined threshold, the system declares "drift" and copies the stable long-term model over the volatile short-term model to re-anchor the baseline.

---

### 5. Non-Linear Risk Accumulation

To avoid "alarm fatigue" from single, split-second CPU spikes, Sentinel maintains a "Risk Pool" ($R_t$).

The pool drains over time during normal operation but fills quadratically when the system exhibits high severity.

If Severity ($S_t$) > $1.0$ (Anomalous behavior):

$$
R_t = R_{t-1} + 4.0(S_t - 1.0)^2
$$

If Severity ($S_t$) $\le 1.0$ (Normal behavior):

$$
R_t = R_{t-1} \times 0.95
$$

The risk decays by 5% every tick until it safely returns to 0.

---

## Prerequisites & Installation

### Python

3.11 or higher is strictly required due to advanced typing annotations and significant underlying standard library performance improvements.

### Operating System

Designed primarily for Linux environments, though core mathematical engines are platform-agnostic.

Linux is preferred due to the precise, low-overhead hardware polling capabilities exposed by the psutil library on UNIX-like virtual file systems (e.g., /proc and /sys).

### Required Packages

Listed comprehensively in `requirements.txt`.

Key dependencies include:

* numpy for matrix operations
* psutil for hardware polling
* PySide6 with pyqtgraph for the high-performance graphical interface

It is highly recommended to install Sentinel's dependencies within a virtual environment to avoid conflicts with global system packages.

Before installing, ensure your pip is up to date.

```bash
# Optional: Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade pip and install required dependencies
python3 -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## Building

To compile Sentinel into a standalone Linux executable using Nuitka, use the provided `build.sh` script.

This is the recommended way to deploy Sentinel for daily use, as it drastically reduces startup time, improves runtime efficiency, and eliminates the need to manage Python environments on target machines.

```bash
chmod +x build.sh
./build.sh
```

The build script automates a complex compilation pipeline to transform Python scripts into a highly portable, native executable, performing the following operations:

### Asset Validation

Validates the existence and integrity of application icons and UI assets before attempting compilation.

### C-Level Compilation

Invokes Nuitka to translate the entire Python codebase into pure C code, which is then compiled into a single, highly optimized execution binary.

This provides a massive performance boost over standard interpreted Python and drastically reduces startup times compared to basic bundlers like PyInstaller.

### Targeted Exclusion

It intentionally excludes large, unnecessary scientific modules (like pandas and matplotlib) that are often bundled by default by underlying mathematical dependencies.

By aggressively pruning these, it effectively minimizes binary bloat and keeps the memory footprint exceptionally low.

### Symbol Stripping

Strips debug symbols from the final compiled binary to further reduce the payload size and obfuscate the executable.

### Desktop Integration

Automatically generates and installs a standard Linux `.desktop` file locally in `~/.local/share/applications`, allowing for immediate system integration, application drawer searchability, and easy pinning to your taskbar or application dock.

---

## Usage

Once built, you can run Sentinel directly from your desktop environment's application drawer, or execute it via the terminal using:

```bash
python main.py
```

(if running from source)

Upon first launch, Sentinel will enter a mandatory "Training Mode" for a set duration (defaulting to 30 minutes).

During this time, it silently gathers a baseline of your system's resting state. It is highly recommended to use your computer normally during this period so Sentinel can accurately map your typical variance.

Once training is complete, the UI will shift to a live monitoring view featuring high-performance, real-time plotting graphs for both:

* Instantaneous System Severity (in blue)
* Accumulated Risk (in red)

The UI will also display a dynamic text status indicator (Normal, Elevated, or Anomaly) depending on the current risk assessment.

---

## Basic Shortcuts & Controls

### A

Auto-scale the boundary graphs within the visualization plotting view.

If a massive anomaly temporarily warps the Y-axis scale of the graph, pressing 'A' will snap the view back to fit the current data perfectly.

### Ctrl+Q

Force quit.

This bypasses the backgrounding behavior, safely stops the background engine thread, saves the final state to disk to ensure no data loss, and fully terminates the application process.

### Minimize to Background (Hide)

By clicking the hide button (or closing the window via your OS window manager), the User Interface is hidden, but the system analysis, data collection, and mathematical pipeline remain running invisibly in the background.

### Custom Retraining

If you know your system is about to enter a completely new, sustained workload (e.g., starting a massive 3D rendering job, compiling a huge codebase, or launching a demanding game), you can use the UI dropdown to manually trigger a retraining phase.

This intentionally flushes the old models, forcing Sentinel to establish a new, temporary baseline tailored specifically to the current intensive state, ensuring you aren't bombarded with false alarms during expected heavy usage.
