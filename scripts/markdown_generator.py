import os
import datetime
from tkinter import Tk
from tkinter.filedialog import askdirectory

# Function to parse the title
def parse_title(folder):
    parts = folder.split('_')
    collection_number = parts[0]
    # Join the rest of the parts to form the title
    description = ' '.join(parts[1:])
    return f"Collection #{collection_number}: {description.replace('_', ' ')}"

# Open a dialog to select a folder
def select_folder():
    root = Tk()
    root.withdraw()  # Hide the main window
    folder_path = askdirectory(title="Select the folder containing images")
    root.destroy()  # Close the tkinter window
    return folder_path

# Main function to create the markdown file
def create_markdown():
    # Select folder using tkinter
    folder_path = select_folder()
    if not folder_path:
        print("No folder selected.")
        return
    
    folder_name = os.path.basename(folder_path)
    base_url = "../../../../collections/"

    # Get today's date in the desired format
    pub_date = datetime.datetime.today().strftime('%Y/%m/%d')

    # Set the author
    author = "a-lgil"

    # Initialize the tags based on the folder name
    tags = []
    if folder_name[1] == 'F':
        tags.append("Female")
    elif folder_name[1] == 'M':
        tags.append("Male")

    # List of predefined tags to look for in the image names
    predefined_tags = ["Depth", "Canny", "Normal", "OpenPose"]

    # Get list of images from the folder and process tags
    gallery_urls = []
    example_url = None
    img_url = ""
    for image in os.listdir(folder_path):
        if image.endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')):
            image_path = f"{base_url}{folder_name}/{image}"
            if image == "Cover.png":
                img_url = image_path
            elif image == "Example.png":
                example_url = image_path  # Store Example.png path to add it last
            else:
                gallery_urls.append(image_path)
            
            for tag in predefined_tags:
                if tag in image:
                    tags.append(tag)

    # Add Example.png as the last item in the list if it exists
    if example_url:
        gallery_urls.append(example_url)

    # Remove duplicates while preserving order
    seen = set()
    tags = [x for x in tags if not (x in seen or seen.add(x))]

    # Create the markdown content using concatenation
    markdown_content = (
        "---\n"
        + f"title: \"{parse_title(folder_name)}\"\n"
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

    # Define the output file name
    first_section = folder_name.split('_')[0]
    output_file = os.path.join(folder_path, f"collection_{first_section}.md")

    # Save to a markdown file in the selected folder
    with open(output_file, 'w') as file:
        file.write(markdown_content)

    print(f"Markdown file '{output_file}' created successfully inside the folder '{folder_path}'.")

# Run the main function
if __name__ == "__main__":
    create_markdown()
