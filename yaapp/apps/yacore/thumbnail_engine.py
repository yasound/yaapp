from sorl.thumbnail.engines.pil_engine import Engine
import ImageFilter


class CustomGaussianBlur(ImageFilter.Filter):
    name = "GaussianBlur"

    def __init__(self, radius=2):
        self.radius = radius

    def filter(self, image):
        return image.gaussian_blur(self.radius)


class FxEngine(Engine):
    def create(self, image, geometry, options):
        image = super(FxEngine, self).create(image, geometry, options)
        if 'gaussianblur' in options:
            image = self.gaussianblur(image, options['gaussianblur'])
        return image

    def gaussianblur(self, image, radius=2):
        try:
            return image.filter(CustomGaussianBlur(radius=radius))
        except:
            return image
