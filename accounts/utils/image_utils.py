import logging

from PIL import Image, ExifTags

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files import File
from django.core.exceptions import ValidationError

# Logger
logger = logging.getLogger(__name__)


# private function
def _fix_exif_orientation(img: Image.Image) -> Image.Image:
    """Normalize orientation using EXIF metadata."""
    try:
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break
        exif = img._getexif()
        if exif is not None:
            orientation = exif.get(orientation)
            match orientation:
                case 3: img = img.rotate(180, expand=True)
                case 6: img = img.rotate(270, expand=True)
                case 8: img = img.rotate(90, expand=True)
    except Exception:
        pass
    return img

# private function
def _suggest_dimensions(
    aspect_ratio: float,
    number_of_suggestions: int = 2,
    base_size: int = 400,
    ratio_type: str = "width/height"
) -> list[str]:
    """
    Suggest human-friendly example dimensions based on an aspect ratio.

    Args:
        aspect_ratio (float): Expected ratio (width/height or height/width).
        number_of_suggestions (int): How many examples to return.
        base_size (int): Starting size (in px) for scaling.
        ratio_type (str): Either "width/height" or "height/width".

    Returns:
        list[str]: Example dimension strings like ["800x400", "1200x600"] for an aspect ratio of 2.0 (width/height 2:1).
    """
    suggestions = []
    for i in range(1, number_of_suggestions + 1):
        if ratio_type == "width/height":
            width = int(base_size * i)
            height = int(width / aspect_ratio)
        else:  # height/width ratio
            height = int(base_size * i)
            width = int(height / aspect_ratio)
        suggestions.append(f"{width}x{height}")
    return suggestions


def validate_image_aspectratio(
    image_field: File | InMemoryUploadedFile,
    min_ratio: float = 1.3,
    max_ratio: float = 1.6,
    label: str = "L'image",
    portrait_required: bool = False,
    landscape_required: bool = False,
    ratio_type: str = "width/height"  # or "height/width"
    ):
    """
    Validate that an uploaded image is portrait-oriented (height > width)
    and has a height/width ratio within a given range.
    
    Parameters:
        image_field (File or InMemoryUploadedFile): The uploaded image.
        min_ratio (float): Minimum acceptable aspect ratio (height/width).
        max_ratio (float): Maximum acceptable aspect ratio (height/width).
        portrait_required (bool): If True, enforce that the image must be portrait.
        landscape_required (bool): If True, enforce that the image must be landscape.
        label (str): Optional label for the image (used in error messages).
    
    Raises:
        ValidationError: If the image fails orientation or ratio validation.
    
    Usage (in a Django form or model):
        # * In a form's clean method:
        def clean_image(self):
            image = self.cleaned_data.get('image')
            validate_portrait_aspect(image, 1.2, 1.8, label="Product Image", portrait_required=True)
        # * Or in a model's clean method:
        def clean(self):
            super().clean()
            if self.image:
                validate_image_aspectratio(self.image, 1.2, 1.8, label="Product Image", portrait_required=True)
    """
    if not image_field:
        return

    try:
        with Image.open(image_field) as img:
            img = _fix_exif_orientation(img)
            width, height = img.size
            aspect_ratio = round((width / height) if ratio_type == "width/height" else (height / width), 3)
    except Exception as e:
        logger.warning(f"Failed to open image for validation: {e}")
        raise ValidationError(f"{label} est invalide ou corrompue.")

    if portrait_required and height <= width:
        raise ValidationError(f"{label} doit être verticale (hauteur > largeur).")
    elif landscape_required and width <= height:
        raise ValidationError(f"{label} doit être horizontale (largeur > hauteur).")

    if not (min_ratio <= aspect_ratio <= max_ratio):
        raise ValidationError(
            f"{label} doit avoir un ratio hauteur/largeur compris entre {min_ratio} et {max_ratio}. "
            f"Ratio actuel : {aspect_ratio}."
            f" Suggestions de dimensions : {', '.join(_suggest_dimensions(aspect_ratio, 3, 800, ratio_type))}."
        )

    return aspect_ratio

