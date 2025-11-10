#!/usr/bin/env python3
"""
CARLA Image Generator
Generates RGB images and semantic segmentation masks from CARLA simulator.
Allows users to estimate storage requirements by generating sample images.
"""

import argparse
import os
import sys
import time
import random
from pathlib import Path

try:
    import carla
except ImportError:
    print("Error: CARLA Python API not found. Please install carla package.")
    print("Install with: pip install carla")
    sys.exit(1)


class ImageGenerator:
    def __init__(self, output_dir="output", host="127.0.0.1", port=2000):
        """
        Initialize the CARLA image generator.

        Args:
            output_dir: Directory to save generated images
            host: CARLA server host
            port: CARLA server port
        """
        self.output_dir = Path(output_dir)
        self.rgb_dir = self.output_dir / "rgb"
        self.seg_dir = self.output_dir / "segmentation"
        self.host = host
        self.port = port

        # Create output directories
        self.rgb_dir.mkdir(parents=True, exist_ok=True)
        self.seg_dir.mkdir(parents=True, exist_ok=True)

        # CARLA objects
        self.client = None
        self.world = None
        self.vehicle = None
        self.rgb_camera = None
        self.seg_camera = None

        # Image storage
        self.rgb_images = []
        self.seg_images = []

    def connect(self):
        """Connect to CARLA simulator."""
        print(f"Connecting to CARLA at {self.host}:{self.port}...")
        try:
            self.client = carla.Client(self.host, self.port)
            self.client.set_timeout(10.0)
            self.world = self.client.get_world()
            print(f"Connected to CARLA (Map: {self.world.get_map().name})")
            return True
        except Exception as e:
            print(f"Error connecting to CARLA: {e}")
            print("Make sure CARLA simulator is running.")
            return False

    def spawn_vehicle(self):
        """Spawn a vehicle in the world."""
        blueprint_library = self.world.get_blueprint_library()
        vehicle_bp = blueprint_library.filter('vehicle.*')[0]

        # Get a random spawn point
        spawn_points = self.world.get_map().get_spawn_points()
        spawn_point = random.choice(spawn_points)

        print(f"Spawning vehicle: {vehicle_bp.id}")
        self.vehicle = self.world.spawn_actor(vehicle_bp, spawn_point)

        # Set autopilot for some movement
        self.vehicle.set_autopilot(True)

        return self.vehicle

    def setup_cameras(self):
        """Attach RGB and semantic segmentation cameras to the vehicle."""
        blueprint_library = self.world.get_blueprint_library()

        # RGB Camera
        rgb_bp = blueprint_library.find('sensor.camera.rgb')
        rgb_bp.set_attribute('image_size_x', '800')
        rgb_bp.set_attribute('image_size_y', '600')
        rgb_bp.set_attribute('fov', '90')

        # Semantic Segmentation Camera
        seg_bp = blueprint_library.find('sensor.camera.semantic_segmentation')
        seg_bp.set_attribute('image_size_x', '800')
        seg_bp.set_attribute('image_size_y', '600')
        seg_bp.set_attribute('fov', '90')

        # Camera transform (mounted on top of vehicle)
        camera_transform = carla.Transform(carla.Location(x=1.5, z=2.4))

        # Spawn cameras
        self.rgb_camera = self.world.spawn_actor(rgb_bp, camera_transform, attach_to=self.vehicle)
        self.seg_camera = self.world.spawn_actor(seg_bp, camera_transform, attach_to=self.vehicle)

        # Setup listeners
        self.rgb_camera.listen(lambda image: self._process_rgb_image(image))
        self.seg_camera.listen(lambda image: self._process_seg_image(image))

        print("Cameras attached to vehicle")

    def _process_rgb_image(self, image):
        """Callback for RGB camera."""
        self.rgb_images.append(image)

    def _process_seg_image(self, image):
        """Callback for segmentation camera."""
        self.seg_images.append(image)

    def generate_images(self, num_images, interval=0.5):
        """
        Generate specified number of images.

        Args:
            num_images: Number of image pairs to generate
            interval: Time interval between captures (seconds)
        """
        print(f"\nGenerating {num_images} image pairs...")

        # Clear previous images
        self.rgb_images.clear()
        self.seg_images.clear()

        # Wait for vehicle to start moving
        print("Waiting for vehicle to stabilize...")
        time.sleep(2)

        # Generate images
        start_time = time.time()
        for i in range(num_images):
            # Wait for images to be captured
            time.sleep(interval)

            # Show progress
            print(f"Captured {i+1}/{num_images} image pairs", end='\r')

        # Wait a bit more to ensure last images are captured
        time.sleep(1)

        elapsed = time.time() - start_time
        print(f"\nCaptured {len(self.rgb_images)} RGB and {len(self.seg_images)} segmentation images in {elapsed:.1f}s")

    def save_images(self):
        """Save captured images to disk."""
        print("\nSaving images to disk...")

        total_size = 0
        num_saved = min(len(self.rgb_images), len(self.seg_images))

        for i in range(num_saved):
            # Save RGB image
            rgb_path = self.rgb_dir / f"rgb_{i:06d}.png"
            self.rgb_images[i].save_to_disk(str(rgb_path))

            # Save segmentation image
            seg_path = self.seg_dir / f"seg_{i:06d}.png"
            self.seg_images[i].save_to_disk(str(seg_path))

            # Calculate size
            total_size += rgb_path.stat().st_size + seg_path.stat().st_size

            print(f"Saved {i+1}/{num_saved} image pairs", end='\r')

        print(f"\nSaved {num_saved} image pairs to {self.output_dir}")
        return num_saved, total_size

    def cleanup(self):
        """Destroy spawned actors."""
        print("\nCleaning up...")
        if self.rgb_camera:
            self.rgb_camera.destroy()
        if self.seg_camera:
            self.seg_camera.destroy()
        if self.vehicle:
            self.vehicle.destroy()
        print("Cleanup complete")


def format_size(size_bytes):
    """Format bytes to human-readable size."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def estimate_storage(num_images, avg_size_per_pair):
    """Estimate storage for a given number of images."""
    estimated_size = num_images * avg_size_per_pair
    return format_size(estimated_size)


def main():
    parser = argparse.ArgumentParser(
        description="Generate images and segmentation masks from CARLA simulator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate 10 sample images to estimate storage
  python generate_images.py --num-images 10

  # Generate 100 images in custom directory
  python generate_images.py --num-images 100 --output-dir my_dataset

  # Connect to remote CARLA server
  python generate_images.py --num-images 50 --host 192.168.1.100 --port 2000
        """
    )

    parser.add_argument(
        '--num-images',
        type=int,
        default=10,
        help='Number of image pairs to generate (default: 10)'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='output',
        help='Output directory for images (default: output)'
    )
    parser.add_argument(
        '--host',
        type=str,
        default='127.0.0.1',
        help='CARLA server host (default: 127.0.0.1)'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=2000,
        help='CARLA server port (default: 2000)'
    )
    parser.add_argument(
        '--interval',
        type=float,
        default=0.5,
        help='Interval between image captures in seconds (default: 0.5)'
    )

    args = parser.parse_args()

    # Create generator
    generator = ImageGenerator(
        output_dir=args.output_dir,
        host=args.host,
        port=args.port
    )

    try:
        # Connect to CARLA
        if not generator.connect():
            return 1

        # Setup scene
        generator.spawn_vehicle()
        generator.setup_cameras()

        # Generate images
        generator.generate_images(args.num_images, args.interval)

        # Save images
        num_saved, total_size = generator.save_images()

        # Print statistics
        print("\n" + "="*60)
        print("STORAGE STATISTICS")
        print("="*60)
        print(f"Images generated: {num_saved} pairs ({num_saved * 2} total files)")
        print(f"Total size: {format_size(total_size)}")

        if num_saved > 0:
            avg_size = total_size / num_saved
            print(f"Average per pair: {format_size(avg_size)}")

            # Provide estimation examples
            print("\n" + "="*60)
            print("STORAGE ESTIMATES FOR DIFFERENT QUANTITIES")
            print("="*60)
            for count in [100, 500, 1000, 5000, 10000]:
                estimate = estimate_storage(count, avg_size)
                print(f"{count:>6} image pairs: ~{estimate:>10}")

        print("="*60)

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        generator.cleanup()

    return 0


if __name__ == "__main__":
    sys.exit(main())
