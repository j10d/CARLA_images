# CARLA Image Generator

A Python utility for generating RGB images and semantic segmentation masks from the CARLA self-driving car simulator. This tool helps you estimate storage requirements by allowing you to generate small sample datasets first.

## Features

- Generate synchronized RGB and segmentation image pairs
- Automatic vehicle spawning with autopilot
- Command-line control over number of images
- Storage usage statistics and estimation
- Configurable output directory and CARLA server connection

## Prerequisites

1. **CARLA Simulator**: Download and run CARLA simulator
   - Download from: https://carla.org/
   - Start CARLA before running this script

2. **Python 3.7+**: Required for the script

## Installation

Install the CARLA Python package:

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install carla
```

Note: Make sure the CARLA package version matches your CARLA simulator version.

## Usage

### Basic Usage

Generate 10 sample images (default):
```bash
python generate_images.py
```

### Specify Number of Images

Generate a specific number of images:
```bash
python generate_images.py --num-images 50
```

### Custom Output Directory

Save images to a custom directory:
```bash
python generate_images.py --num-images 100 --output-dir my_dataset
```

### Connect to Remote CARLA Server

```bash
python generate_images.py --num-images 50 --host 192.168.1.100 --port 2000
```

### Adjust Capture Interval

Change the time between image captures (in seconds):
```bash
python generate_images.py --num-images 20 --interval 1.0
```

## Command-Line Arguments

- `--num-images`: Number of image pairs to generate (default: 10)
- `--output-dir`: Output directory for images (default: output)
- `--host`: CARLA server host (default: 127.0.0.1)
- `--port`: CARLA server port (default: 2000)
- `--interval`: Interval between captures in seconds (default: 0.5)

## Output Structure

Generated images are saved in the following structure:

```
output/
├── rgb/
│   ├── rgb_000000.png
│   ├── rgb_000001.png
│   └── ...
└── segmentation/
    ├── seg_000000.png
    ├── seg_000001.png
    └── ...
```

## Storage Estimation Workflow

1. **Generate a small sample** to estimate storage:
   ```bash
   python generate_images.py --num-images 10
   ```

2. **Review the statistics** displayed after generation:
   ```
   STORAGE STATISTICS
   ================================================================
   Images generated: 10 pairs (20 total files)
   Total size: 15.23 MB
   Average per pair: 1.52 MB

   STORAGE ESTIMATES FOR DIFFERENT QUANTITIES
   ================================================================
       100 image pairs: ~   152.30 MB
       500 image pairs: ~   761.50 MB
      1000 image pairs: ~     1.49 GB
      5000 image pairs: ~     7.44 GB
     10000 image pairs: ~    14.88 GB
   ```

3. **Generate full dataset** based on available storage:
   ```bash
   python generate_images.py --num-images 1000 --output-dir full_dataset
   ```

## Image Specifications

- **Resolution**: 800x600 pixels
- **Field of View**: 90 degrees
- **RGB Format**: Standard color images
- **Segmentation Format**: Semantic segmentation with CARLA's color-coded labels

## Troubleshooting

### Cannot connect to CARLA
- Make sure CARLA simulator is running
- Check that the host and port are correct
- Default CARLA port is 2000

### Module 'carla' not found
- Install the CARLA Python package: `pip install carla`
- Ensure the version matches your CARLA simulator version

### Images not being saved
- Check that you have write permissions in the output directory
- Ensure there's enough disk space available

## License

See LICENSE file for details.
