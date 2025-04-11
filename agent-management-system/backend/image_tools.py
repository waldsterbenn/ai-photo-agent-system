from PIL import Image, ImageOps
from io import BytesIO
import json
import piexif


class ImageTool:

    def extract_image_metadata(self, image_data):
        """
        Extract metadata from the original image

        Args:
            image_data (bytes): Original image data

        Returns:
            dict: Extracted metadata
        """
        try:
            img = Image.open(BytesIO(image_data))
            metadata = {
                "width": img.width,
                "height": img.height,
                "format": img.format,
                "mode": img.mode,
            }

            # Extract EXIF data if available
            if hasattr(img, "_getexif") and img._getexif() is not None:
                exif_dict = piexif.load(img.info.get("exif", b""))
                # Convert binary data to readable format
                readable_exif = {}

                for ifd_name in exif_dict:
                    if ifd_name == "thumbnail":
                        continue

                    readable_exif[ifd_name] = {}
                    for tag_id, value in exif_dict[ifd_name].items():
                        tag_name = piexif.TAGS[ifd_name].get(
                            tag_id, {}).get("name", str(tag_id))

                        # Convert bytes to string if possible
                        if isinstance(value, bytes):
                            try:
                                value = value.decode('utf-8')
                            except:
                                value = str(value)

                        readable_exif[ifd_name][tag_name] = value

                metadata["exif"] = readable_exif

            return metadata
        except Exception as e:
            return {"error": f"Error extracting metadata: {str(e)}"}

    def compress_image_to_target_size(self, image_data, target_size_mb):
        """
        Compress an image to a target size in megabytes using PIL

        Args:
            image_data (bytes): Original image data
            target_size_mb (float): Target size in megabytes

        Returns:
            bytes: Compressed image data
        """
        target_size_bytes = int(target_size_mb * 1024 * 1024)

        # Open the image
        img = Image.open(BytesIO(image_data))

        # Convert to RGB if necessary (removing alpha channel)
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')

        # Start with these parameters
        quality = 95
        width, height = img.size

        # Compression approach - start with high quality and reduce
        while quality >= 20:
            output = BytesIO()
            img.save(
                output,
                format='JPEG',
                quality=quality,
                optimize=True,
                progressive=True
            )

            current_size = output.tell()

            # If size is within target, return the image
            if current_size <= target_size_bytes:
                return output.getvalue()

            # Reduce quality for next attempt
            quality -= 5

        # If quality reduction wasn't enough, start reducing dimensions
        while current_size > target_size_bytes and min(width, height) > 300:
            width = int(width * 0.9)
            height = int(height * 0.9)
            img = img.resize((width, height), Image.Resampling.LANCZOS)

            output = BytesIO()
            img.save(output, format='JPEG', quality=quality,
                     optimize=True, progressive=True)
            current_size = output.tell()

        return output.getvalue()

    def old_compress_image_to_target_size(self, image_data, target_size_mb):
        """
        Compress an image to a target size in megabytes using PIL

        Args:
            image_data (bytes): Original image data
            target_size_mb (float): Target size in megabytes

        Returns:
            bytes: Compressed image data
        """
        target_size_bytes = int(target_size_mb * 1024 * 1024)

        # Open the image
        img = Image.open(BytesIO(image_data))

        # Convert to RGB if necessary (removing alpha channel)
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')

        # Start with these parameters
        quality = 85
        width, height = img.size

        # Binary search approach for quality
        min_quality = 20
        max_quality = 95

        for attempt in range(10):
            output = BytesIO()
            img.save(
                output,
                format='JPEG',
                quality=quality,
                optimize=True,
                progressive=True
            )

            current_size = output.tell()

            # Check if we're within target
            if current_size <= target_size_bytes:
                if current_size >= target_size_bytes * 0.95 or max_quality - min_quality <= 2:
                    return output.getvalue()

            # Adjust parameters
            if current_size > target_size_bytes:
                # Reduce quality
                max_quality = quality
                quality = (min_quality + max_quality) // 2

                # If quality is already low, reduce dimensions
                if quality < 30 and min(width, height) > 800:
                    width = int(width * 0.8)
                    height = int(height * 0.8)
                    img = img.resize((width, height), Image.Resampling.LANCZOS)
            else:
                # Increase quality
                min_quality = quality
                quality = (min_quality + max_quality) // 2

        # If we couldn't reach target with quality adjustments
        while current_size > target_size_bytes and min(width, height) > 300:
            width = int(width * 0.9)
            height = int(height * 0.9)
            img = img.resize((width, height), Image.Resampling.LANCZOS)

            output = BytesIO()
            img.save(output, format='JPEG', quality=quality,
                     optimize=True, progressive=True)
            current_size = output.tell()

        return output.getvalue()
