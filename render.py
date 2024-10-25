import os.path
import pandas as pd
from PIL import Image, ImageDraw, PngImagePlugin

h = 7
w = 4
res = 20

from utils.prune_empty import prune_empty
numbers = prune_empty("output.csv")

if not os.path.exists("outputdir"):
    os.mkdir("outputdir")
for row in range(0,numbers.shape[0]):
    nums = numbers.iloc[row]
    num = numbers.loc[row].iloc[-1]
    print(f"{row=}, {num=}")
    im = Image.new('RGB', (w*res, h*res), (255, 255, 255))
    ctx = ImageDraw.Draw(im)
    for i in range(h):
        for j in range(w):
            if nums.iloc[i*w+j] == 1:


                # print(f"black at {j},{i}")
                ctx.rectangle([j*res, i*res, (j+1)*res, (i+1)*res], fill=(0, 0, 0))
    ctx.text((0, 0), f"{num}", fill=(255, 0, 0))

    # Add metadata tag
    metadata = PngImagePlugin.PngInfo()
    metadata.add_text("Number", f"{num}")

    with open(f"outputdir/{row:05d}.png", "wb") as f:
        im.save(f, "PNG", pnginfo=metadata)
