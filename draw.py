import argparse
import os
import time
import numpy as np
from PIL import ImageDraw
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent
from utils import mylogger
from datetime import datetime, timedelta
import imageio.v3 as iio
import PIL.Image as Image


class ImageToData(FileSystemEventHandler):
    def __init__(self, out=None, visualize=False, resolution=100, tolerance=5):
        """
        :param out: Output file. If not specified, it will be output.csv in the cwd.
        :param visualize:  Shows the grid after each drawing in your image viewer program. For demonstration purposes mostly.
        :param resolution: Size of each tile. The numpy output will be image size / resolution (eg 700/100; 400/100 = 7x4)
        :param tolerance: [1-99] Percent of pixels has to be black to be considered 1 in the output.
        """
        super().__init__()
        self.visualize = visualize
        self.last_modified = datetime.now()  # the file watcher often fires twice for some reason, this is to prevent that
        self.resolution = resolution
        self.tolerance = tolerance
        self.out = out or "output.csv"

        self.tol = ((resolution * resolution * 255) / 100) * (100 - tolerance)  # amount of pixels that can be white

    def convert_to_dataset(self, src_path):

        with iio.imopen(src_path, "r", extension=".png") as file:
            img = file.read()

        num = os.path.split(src_path)[1].split("_")[0]
        img = img[:, :, 0]  # taking only the red channel
        logger.debug(f"{img.shape=}")

        h = img.shape[0]
        w = img.shape[1]

        resolution = self.resolution

        assert h % resolution == 0, "Resolution is not a divisor of height"
        assert w % resolution == 0, "Resolution is not a divisor of width"

        out = np.zeros((h//resolution, w//resolution), dtype=np.uint8)

        if self.visualize:
            orig = Image.open(src_path, "r")
            drawctx = ImageDraw.Draw(orig)

        for i in range(h // resolution):
            for j in range(w // resolution):

                if self.visualize:
                    drawctx.line(((j * resolution, 0), (j * resolution, h)), fill=(255, 0, 0), width=1)
                    drawctx.line(((0, i * resolution), (w, i * resolution)), fill=(0, 255, 0), width=1)

                tile: np.ndarray = img[i * resolution:(i + 1) * resolution, j * resolution:(j + 1) * resolution]  # taking a 100x100 slice. 100 can be changed by the resolution var


                logger.debug(f"x={j},y={i}")
                logger.debug(f"{np.sum(tile)=}, {self.tol=}")
                logger.debug(np.sum(tile) < self.tol)
                # logger.debug(f"{tile=}")

                if np.sum(tile) < self.tol:  # if there are less than tol white pixels, it's black
                    logger.debug(f"black pixels at {j},{i}")
                    out[i, j] = 1

                    if self.visualize:
                        drawctx.text((j * resolution, i * resolution), f"{j},{i}", fill=(250, 0, 0))
                        # drawctx.circle((j * resolution + resolution//2, i * resolution + resolution//2), resolution//2, fill=(25, 0, 0))

                else:
                    if self.visualize:
                        drawctx.text((j * resolution, i * resolution), f"{j},{i}", fill=(0, 0, 250))

        if self.visualize:
            orig.show()
        np.set_printoptions(threshold=np.inf)
        out.nonzero()
        logger.debug(f"{out.shape=}")
        logger.info(f"\n{out=}")

        if not os.path.exists(self.out):
            with open(self.out, "w") as f:
                f.write(",".join(map(str, range(out.size))) + ",target\n")

        with open(self.out, "a") as f:
            f.write(",".join(map(str, out.flatten())) + f",{num}\n")

        white_image = np.full((h, w, 3), 255, dtype=np.uint8)
        with iio.imopen(src_path, "w", extension=".png") as file:
            file.write(white_image)

    def on_modified(self, event: FileSystemEvent):
        if event.src_path.endswith("input.png"):
            now = datetime.now()
            if now - self.last_modified > timedelta(seconds=1):
                self.last_modified = now
                logger.warning(f'{event.src_path} has been modified')
                self.convert_to_dataset(event.src_path)


def create_imgs(dir, w, h):
    orig = Image.new("RGB", (w, h), (255, 255, 255))
    for i in range(10):
        orig.save(os.path.join(dir, f"{i}_input.png"), format="PNG")


if __name__ == "__main__":

    desc = """Converts black on white pngs to datasets. 
    Run this script, then open any file named n_input.png where n is the numeral, edit it and save it. 
    The script should convert the drawing to an array of 1s and 0s."""
    parser = argparse.ArgumentParser(prog=f"Dataset maker", description=desc, epilog="Written by theonlypeti.")

    parser.add_argument("--debug", action="store_true", help="Enable debug prints. Verbose!")
    parser.add_argument("--logfile", action="store_true", help="Turns on logging to a text file.")
    parser.add_argument("--visualize", action="store_true", help="After each file modification, shows a grid with found black pixels.")
    parser.add_argument("--directory", action="store", help="Which directory to look for changes in. Default is cwd.")
    parser.add_argument("--w", action="store", help="Width of new images, if they had not been created.", default=400)
    parser.add_argument("--h", action="store", help="Height of new images, if they had not been created.", default=700)
    parser.add_argument("--resolution", action="store", help="How big tiles to split the image to. Output matrix is size/resolution", default=100)
    # parser.add_argument("--profiling", action="store_true", help="Measures the bootup time and outputs it to profile.prof.")
    args = parser.parse_args()

    logger = mylogger.init(args)

    # convert_to_dataset("1_input.png")
    directory = args.directory if args.directory else os.getcwd()
    # os.chdir(directory)
    if not os.path.exists(os.path.join(directory, "0_input.png")):
        create_imgs(directory, int(args.w), int(args.h))
        logger.info("Created 10 images for you to edit. Edit them and save them to see the results.")

    event_handler = ImageToData(visualize=args.visualize, resolution=args.resolution, tolerance=5)
    observer = Observer()
    observer.schedule(event_handler, directory, recursive=False)
    observer.start()
    logger.highlight(f"Started watching for file changes in {directory}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
