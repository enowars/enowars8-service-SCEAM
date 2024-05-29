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


if __name__ == "__main__":
    h = helper()
    h.get_dimensions()
    h.plot()
