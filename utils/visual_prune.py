import os
from utils.prune_empty import prune_empty
assert os.path.exists("../output.csv"), "output.csv not found. You probably haven't run draw.py yet"
assert os.path.exists("../outputdir"), "outputdir not found. You probably haven't run render.py yet"


"""HOW TO USE:
Run this script to check for missing images in the outputdir and remove the corresponding rows from the dataset.
To see your dataset in the form of images, run render.py first.
Then visually inspect the images in the outputdir in your file explorer.
I recommend viewing them in a grid view, sorted by name.
If you see any images that are really grotesque and you believe will only hurt the model, delete them.
After you're done, run this script to remove the corresponding rows from the dataset.
"""

dataset = prune_empty("../output.csv")
imgs = os.listdir("../outputdir")
assert len(imgs) > 0, "No images found in outputdir. You probably haven't run render.py yet"

missing_rows = []

for n, row in enumerate(range(dataset.shape[0]), start=1):
    if not f"{row:05d}.png" in imgs:
        print(f"missing {row:05d}.png")  # I sure do hope you won't have more than 99999 images
        missing_rows.append(row)

# Remove missing rows from the dataset
dataset = dataset.drop(missing_rows)
if input(f"You are about to drop {len(missing_rows)} rows from the dataset. Are you sure you want to continue? (y/n) ").lower() != "y":
    print("Aborting")
    exit()

# Save the updated dataset back to the CSV
dataset.to_csv("../output.csv", index=False)
print(f"Removed {len(missing_rows)} missing rows from the dataset")
