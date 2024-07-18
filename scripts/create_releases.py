import os
import zipfile
from github import Github
from datetime import datetime
import re

# Initialize GitHub API client with the token from environment variables
token = os.getenv('GITHUB_TOKEN')
g = Github(token)
# Get the repository object using the environment variable for the repo name
repo = g.get_repo(os.getenv('GITHUB_REPOSITORY'))

# Get a list of existing releases in the repository
existing_releases = {release.tag_name: release.created_at for release in repo.get_releases()}

# Define the path to the collections folder
collections_folder = './collections'
# Define the name of the global zip file
global_zip_name = 'all_collections.zip'

# Flag to track if we need to update the global release
update_global_release = False

# Initialize counters for the global release description
n_collections = 0
total_images = 0


def transform_string(input_string):
    """
    Transform a string by replacing the first underscore with ': ' and subsequent underscores with ' '.
    """
    # Define the regex pattern to find underscores
    pattern = r'_'

    # Replace the first underscore with ': ' and subsequent underscores with ' '
    transformed_string = re.sub(pattern, lambda m: ': ' if m.start() == input_string.find('_') else ' ', input_string)

    return transformed_string

# Create a global zip file that will contain all subfolders in collections
with zipfile.ZipFile(global_zip_name, 'w') as global_zip:
    # Loop through each subfolder in the collections folder
    for dir_name in os.listdir(collections_folder):
        full_dir_path = os.path.join(collections_folder, dir_name)
        # Check if it is a directory
        if os.path.isdir(full_dir_path):
            n_collections += 1  # Increment the number of collections
            # Count the number of images in the subfolder
            num_images = len([f for f in os.listdir(full_dir_path) if os.path.isfile(os.path.join(full_dir_path, f))]) - 2
            total_images += num_images  # Add to the total number of images

            # Check if a release for this subfolder already exists
            if dir_name not in existing_releases:
                # Mark to update the global release since we have a new subfolder
                update_global_release = True
                zip_name = f'{dir_name}.zip'  # Define the zip file name for the subfolder
                # Create a zip file for the subfolder
                with zipfile.ZipFile(zip_name, 'w') as zipf:
                    # Walk through the subfolder and add files to the zip file
                    for foldername, subfolders, filenames in os.walk(full_dir_path):
                        for filename in filenames:
                            file_path = os.path.join(foldername, filename)
                            arcname = os.path.relpath(file_path, collections_folder)
                            zipf.write(file_path, arcname)

                num_images_text = f'{num_images} ControlNet images'

                # Check if Cover.png exists and create markdown for it
                cover_path = os.path.join(full_dir_path, 'Cover.png')
                if os.path.exists(cover_path):
                    description = f'<img src="collections/{dir_name}/Cover.png" alt="Cover" width="30%" />\n\n{num_images_text}'
                else:
                    description = f'Release of {transform_string(dir_name)}, with {num_images_text}'

                # Create a release for the subfolder and upload the zip file
                release = repo.create_git_release(tag=dir_name, name=f'Collection {transform_string(dir_name)}', message=description)
                release.upload_asset(zip_name)
                os.remove(zip_name)  # Remove the local zip file after uploading

            # Check if the subfolder has been modified since the last release
            else:
                last_release_time = existing_releases[dir_name]
                subfolder_modified_time = datetime.fromtimestamp(os.path.getmtime(full_dir_path))
                if subfolder_modified_time > last_release_time:
                    # Mark to update the global release since we have a modified subfolder
                    update_global_release = True
                    zip_name = f'{dir_name}.zip'  # Define the zip file name for the subfolder
                    # Create a zip file for the subfolder
                    with zipfile.ZipFile(zip_name, 'w') as zipf:
                        # Walk through the subfolder and add files to the zip file
                        for foldername, subfolders, filenames in os.walk(full_dir_path):
                            for filename in filenames:
                                file_path = os.path.join(foldername, filename)
                                arcname = os.path.relpath(file_path, collections_folder)
                                zipf.write(file_path, arcname)

                    num_images_text = f'{num_images} ControlNet images'

                    # Check if Cover.png exists and create markdown for it
                    cover_path = os.path.join(full_dir_path, 'Cover.png')
                    if os.path.exists(cover_path):
                        description = f'<img src="collections/{dir_name}/Cover.png" alt="Cover" width="30%" />\n\n{num_images_text}'
                    else:
                        description = f'Release of {transform_string(dir_name)}, with {num_images_text}'

                    # Update the release for the subfolder and upload the new zip file
                    release = repo.get_release_by_tag(dir_name)
                    release.delete_release()
                    release = repo.create_git_release(tag=dir_name, name=f'Release of {dir_name}', message=description)
                    release.upload_asset(zip_name)
                    os.remove(zip_name)  # Remove the local zip file after uploading

            # Add the subfolder's files to the global zip file
            for foldername, subfolders, filenames in os.walk(full_dir_path):
                for filename in filenames:
                    file_path = os.path.join(foldername, filename)
                    arcname = os.path.relpath(file_path, collections_folder)
                    global_zip.write(file_path, arcname)

# Create and upload the global release containing all subfolders only if there are updates
if update_global_release:
    global_release = repo.get_release_by_tag('global-release') if 'global-release' in existing_releases else None
    if global_release:
        global_release.delete_release()
    global_description = f'{n_collections} pose collections, totaling {total_images} ControlNet images'
    global_release = repo.create_git_release(
        tag='global-release', 
        name='Global Release - ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 
        message=global_description, 
        draft=False, 
        prerelease=False
    )
    global_release.upload_asset(global_zip_name)
os.remove(global_zip_name)  # Remove the local global zip file after uploading
