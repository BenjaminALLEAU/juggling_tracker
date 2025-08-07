# Spikeball Training Tracker

An intelligent training tool for spikeball using computer vision to analyze and automatically count your juggling passes with a yellow ball.


## Purpose

This tool is designed to accompany my spikeball training by providing:
- Accurate tracking of my juggling progress
- Detailed statistics to identify improvement areas
- Constant motivation through intermediate goals
- Analysis of rhythm consistency during gameplay

## Features

- **Automatic detection** of yellow ball in real-time using OpenCV
- **Precise counting** of juggles (detection of direction changes)
- **Training statistics**: rhythm, duration, intervals, consistency
- **Audio motivation** with beeps every 10 juggles
- **Visual trajectory tracking** of the ball
- **Performance analysis** with automatic evaluation

## Installation

### Prerequisites
- Python 3.11.1 (recommended)
- Functional webcam
- Windows (for audio notifications)

### Installation Steps

1. **Clone the project**
   ```bash
   git clone https://github.com/BenjaminALLEAU/juggling_tracker.git
   cd juggling_tracker
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate.bat
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Launch application**
   ```bash
   python juggle_counter.py
   ```

## Training Usage

### Initial Setup
1. Launch the application
2. Position yourself about 1 meter from the camera
3. Hold your yellow spikeball clearly visible
4. Start your juggling session

### Training Controls
| Key | Action |
|-----|--------|
| **SPACE** | New training set (reset counters) |
| **R** | Display detailed session statistics |
| **Q** | End training session |

### Training Metrics
- **Juggles**: Total number of successful passes
- **Touches**: Total contacts with the ball
- **Duration**: Training session time
- **Rhythm**: Passes per minute
- **Consistency**: Timing regularity between passes
- **Goals**: Progress towards milestones (10, 20, 30+ passes)

## Training Configuration

### Detection Adjustment
In `detect_yellow_ball()` to optimize for your environment:

```python
# HSV range for yellow spikeball
lower_yellow = np.array([20, 100, 100])  # Adjust based on your lighting
upper_yellow = np.array([30, 255, 255])
```

### Counting Sensitivity
In `JuggleCounter.__init__()` to customize detection:

```python
self.min_movement = 8          # Detected movement sensitivity
self.max_frames_without_ball = 10  # Tolerance if ball momentarily hidden
```

## Training Statistics

The application automatically calculates:

### Basic Metrics
- **Successful passes**: Main performance counter
- **Total touches**: All detected contacts
- **Session duration**: Total training time
- **Average rhythm**: Passes per minute

### Advanced Analysis
- **Average interval**: Mean time between passes
- **Rhythm variation**: Standard deviation of intervals
- **Consistency evaluation**: Timing regularity
- **Progress tracking**: Milestone achievement

## Performance Evaluation

| Performance | Level |
|-------------|-------|
| 100+ passes | Juggling master |
| 50+ passes | Excellent level |
| 20+ passes | Very good level |
| 10+ passes | Good progress |
| <10 passes | Learning phase |

## Training Notifications

- **Startup beep**: Audio system confirmation
- **Progress beeps**: Every 10 juggles to maintain motivation
- **End beep**: Session completion signal
- **Console messages**: Detailed feedback on each pass

## Troubleshooting

### Ball Detection
- Check uniform lighting (avoid backlighting)
- Use a standard yellow spikeball
- Avoid yellow objects in background
- Adjust HSV parameters if necessary

### Pass Counting
- Keep ball visible at all times
- Avoid movements too fast for camera
- Maintain approximately 1 meter distance from camera
- Verify camera operates at 30 FPS

### Audio
- Beeps require Windows
- Check speakers are enabled
- Console notifications appear if audio fails

### Performance
- Close resource-intensive applications
- Default resolution (640x480) optimized for fluidity
- Restart application if slowdown occurs

## Technical Operation

### Ball Detection
1. **Color conversion**: BGR to HSV image for better detection
2. **Color masking**: Isolation of yellow ball pixels
3. **Morphological cleaning**: Noise and artifact removal
4. **Contour analysis**: Circular shape identification
5. **Position calculation**: Precise center determination

### Counting Algorithm
1. **Trajectory tracking**: History of vertical positions
2. **Direction analysis**: Up/down movement detection
3. **Pass detection**: Downward → upward change = successful juggle
4. **Temporal validation**: Anti-bounce with 300ms minimum delay
5. **Confirmation**: Validation with multiple trajectory points

### Statistics Calculation
- **Real-time**: Continuous metric updates
- **Interval analysis**: Precise calculation between each pass
- **Statistical calculations**: Averages and standard deviations with NumPy
- **Automatic evaluation**: Performance classification algorithms

## Project Structure

```
juggling_tracker/
├── .venv/                 # Python virtual environment
├── juggle_counter.py      # Main application
├── requirements.txt       # Python dependencies
├── README.md             # Documentation
└── .gitignore            # Git configuration
```

## Contributing

Contributions to improve the training tool are welcome:

1. Fork the project
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Commit changes (`git commit -m 'Add training improvement'`)
4. Push to branch (`git push origin feature/improvement`)
5. Create Pull Request

### Planned Improvements
- Support for different colored balls
- Training session save and history
- Dedicated graphical interface
- Performance comparison mode
- Training data export
- Specific technique detection

## Changelog

### Version 1.0.0
- Automatic yellow spikeball detection
- Precise juggling pass counting
- Real-time training statistics
- Motivation system with progress beeps
- Visual trajectory tracking
- Performance and consistency analysis
- Complete user interface

## License

Project under MIT license. See `LICENSE` for details.

## Development Context

Developed to accompany my personal spikeball training, this tool aims to bring a scientific and motivating approach to juggling practice, a fundamental element of this sport.

**Technologies**: Python, OpenCV, NumPy  
**Platform**: Windows (optimized for audio notifications)

---

**Good training and may your statistics improve!**