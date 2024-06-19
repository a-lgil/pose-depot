import os
import datetime
from tkinter import Tk
from tkinter.filedialog import askdirectory

def select_folder():
    root = Tk()
    root.withdraw()  # Hide the main window
    folder_path = askdirectory(title="Select the folder containing images")
    root.destroy()  # Close the tkinter window
    return folder_path

# Extract the numerical suffix from the filename
def get_suffix(image_name):
    base_name = os.path.splitext(image_name)[0]
    parts = base_name.split('_')
    if len(parts) > 1:
        try:
            return int(parts[-1])
        except ValueError:
            return 0  # Default to 0 for non-numeric or no suffix
    return 0

# Determine the category order index for sorting
def get_category_order(image_name, category_order):
    for i, prefix in enumerate(category_order):
        if image_name.lower().startswith(prefix.lower()):
            return i
    return len(category_order)  # Non-specified images go at the end

# Extract the base name (without suffix and extension)
def get_base_name(image_name):
    return os.path.splitext(image_name)[0].split('_')[0]

# Sorting function for images
def sort_images(images):
    category_order = ["Depth", "DepthHand", "Canny", "CannyHand", "Normal", "NormalHand", 
                      "OpenPoseFull", "OpenPose", "OpenPoseHand"]

    # Define sorting key
    def sort_key(image_name):
        return (get_suffix(image_name), get_category_order(get_base_name(image_name), category_order))
    
    # Sort the images
    sorted_images = sorted(images, key=sort_key)
    
    # Move 'Example' images to the end
    example_images = [img for img in sorted_images if 'example' in os.path.basename(img).lower()]
    sorted_images = [img for img in sorted_images if 'example' not in os.path.basename(img).lower()]
    sorted_images.extend(example_images)

    return sorted_images

# Create markdown content
def create_markdown():
    folder_path = select_folder()
    if not folder_path:
        print("No folder selected.")
        return

    folder_name = os.path.basename(folder_path)
    base_url = "../../../../collections/"
    pub_date = datetime.datetime.today().strftime('%Y/%m/%d')
    author = "a-lgil"

    tags = []
    if folder_name[1] == 'F':
        tags.append("Female")
    elif folder_name[1] == 'M':
        tags.append("Male")

    predefined_tags = ["Depth", "Canny", "Normal", "OpenPose"]

    gallery_urls = []
    image_paths = []
    img_url = ""
    for image in os.listdir(folder_path):
        if image.endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')):
            image_path = f"{base_url}{folder_name}/{image}"
            if image == "Cover.png":
                img_url = image_path
            else:
                image_paths.append(image_path)

            for tag in predefined_tags:
                if tag in image:
                    tags.append(tag)

    if img_url == "":
        print("Warning: Cover.png not found!")

    gallery_urls = sort_images(image_paths)
    seen = set()
    tags = [x for x in tags if not (x in seen or seen.add(x))]

    markdown_content = (
        "---\n"
        + f"title: \"Collection #{folder_name.split('_')[0]}: {folder_name.split('_')[1].replace('_', ' ')}\"\n"
        + f"pubDate: \"{pub_date}\"\n"
        + f"author: \"{author}\"\n"
        + "tags:\n"
        + "  - " + "\n  - ".join(tags) + "\n"
        + f"imgUrl: '{img_url}'\n"
        + "galleryUrls:\n"
        + "  - " + "\n  - ".join(gallery_urls) + "\n"
        + "description: ''\n"
        + "layout: '../../layouts/BlogPost.astro'\n"
        + "---\n"
    )

    output_file = os.path.join(folder_path, f"collection_{folder_name.split('_')[0]}.md")

    with open(output_file, 'w') as file:
        file.write(markdown_content)

    print(f"Markdown file '{output_file}' created successfully inside the folder '{folder_path}'.")

if __name__ == "__main__":
    create_markdown()
