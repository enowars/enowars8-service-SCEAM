import os
from PIL import Image
from matplotlib import pyplot as plt

backgrounds_folder = os.path.join(os.path.dirname(__file__), "backgrounds")


class helper():
    def __init__(self) -> None:
        self.backgrounds = os.listdir(backgrounds_folder)
        self.imgs = self.load_all_memory()

    def load_all_memory(self):
        return [Image.open(os.path.join(backgrounds_folder, i)) for i in self.backgrounds]

    def get_dimensions(self):
        self.widths = [i.size[0] for i in self.imgs]
        self.heights = [i.size[1] for i in self.imgs]
        self.widths_dict = {i: self.widths.count(i) for i in self.widths}
        self.heights_dict = {i: self.heights.count(i) for i in self.heights}
        # close all images
        for i in self.imgs:
            i.close()

    def plot(self):
        plt.bar(self.widths_dict.keys(), self.widths_dict.values(), width=2.0)
        plt.xlabel("Width")
        plt.ylabel("Count")
        plt.title("Width distribution")
        plt.show()

        plt.bar(self.heights_dict.keys(),
                self.heights_dict.values(), width=2.0)
        plt.xlabel("Height")
        plt.ylabel("Count")
        plt.title("Height distribution")
        plt.show()

    def stats(self):
        print("Width above 300: ", sum([1 for i in self.widths if i > 300]))
        print("Height above 300: ", sum([1 for i in self.heights if i > 300]))

    def remove_below(self, width, height):
        indices = [i for i in range(
            len(self.imgs)) if self.widths[i] < width or self.heights[i] < height]
        for i in indices:
            os.remove(os.path.join(backgrounds_folder, self.backgrounds[i]))


if __name__ == "__main__":
    h = helper()
    h.get_dimensions()
    h.remove_below(400, 400)
    # h.stats()
    # h.plot()
