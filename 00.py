from PIL import Image
import numpy as np
import os
import cv2

def image_to_video(data_folder):



    # Get the list of image files in the folder
    image_files = sorted([f for f in os.listdir(data_folder) if f.endswith(('.png', '.jpg', '.jpeg'))])

    # Ensure that the images are sorted in the correct order
    image_files = sorted(image_files, key=lambda x: int(x.split('_')[-1].split('.')[0]))

    # Get the first image to get dimensions
    first_image = cv2.imread(os.path.join(data_folder, image_files[0]))
    height, width, layers = first_image.shape

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'FFV1')  # Use 'XVID' for AVI format
    video_output = cv2.VideoWriter('binvid.mkv', fourcc, 1.0, (width, height))

    # Iterate through the image files and add them to the video
    for image_file in image_files:
        image_path = os.path.join(data_folder, image_file)
        img = cv2.imread(image_path)
        video_output.write(img)

    # Release the VideoWriter and close all OpenCV windows
    video_output.release()
    cv2.destroyAllWindows()

    print("Video creation completed.")

def video_to_images(video_path):
    # Create a folder to store the extracted frames
    output_folder = "data"
    os.makedirs(output_folder, exist_ok=True)

    # Open the video file
    cap = cv2.VideoCapture(video_path)

    # Get the video's frame width and height
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Read frames from the video and save them as images
    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        frame_filename = f"output_image_{str(frame_count)}.png"
        frame_path = os.path.join(output_folder, frame_filename)
        cv2.imwrite(frame_path, frame)

    # Release the VideoCapture
    cap.release()

    print(f"{frame_count} frames extracted and saved to {output_folder}.")

def remove_trailing_ones(file_path,adjust):
    # Read the content of the file
    with open(file_path, 'r') as file:
        content = file.read().rstrip()  # Remove trailing whitespaces

    # Find the last occurrence of '0' in the content
    last_zero_index = content.rfind('0')

    # If '0' is found, remove trailing '1's
    if last_zero_index != -1:
        content = content[:last_zero_index + 1]

    # Write the modified content back to the file
    with open(file_path, 'w') as file:
        file.write(content)
    open(file_path,"a").write(adjust)



def create_image_from_binary(input_file, output_prefix, image_width, image_height):
    with open(input_file, 'r') as file:
        binary_data = file.read().strip()

    # Calculate the number of images needed
    num_images = len(binary_data) // (image_width * image_height)
    if len(binary_data) % (image_width * image_height) != 0:
        num_images += 1

    # Split binary data into chunks for each image
    binary_chunks = [binary_data[i * image_width * image_height : (i + 1) * image_width * image_height]
                     for i in range(num_images)]

    for i, chunk in enumerate(binary_chunks):
        # Convert binary chunk to a NumPy array
        pixel_data = np.array(list(map(int, chunk)))

        # Check if there are fewer binary digits than pixels
        if len(pixel_data) < image_width * image_height:
            # Fill remaining pixels with white (1)
            pixel_data = np.concatenate((pixel_data, np.ones((image_width * image_height - len(pixel_data),))))
        
        # Reshape the array to match the image dimensions
        pixel_data = pixel_data.reshape((image_height, image_width)) * 255

        # Create an image from the pixel data
        image = Image.fromarray(pixel_data.astype('uint8'), 'L')

        # Save the image
        output_file = f"{output_prefix}_{i + 1}.png"
        image.save(output_file)
        print(f"Image created successfully: {output_file}")



def image_to_binary(image_path, output_file):
    # Open the image
    img = Image.open(image_path)

    # Convert the image to grayscale
    img = img.convert('L')

    # Get the width and height of the image
    width, height = img.size

    # Create a binary string to store pixel values
    binary_data = ""

    # Define a threshold for considering a pixel as white---lowe the threshhold to detect grayish black
    white_threshold = 150

    # Iterate through each pixel
    for y in range(height):
        for x in range(width):
            # Get the pixel value
            pixel_value = img.getpixel((x, y))

            # Check if the pixel is white or non-white based on the threshold
            if pixel_value >= white_threshold:
                binary_data += "1"
            else:
                binary_data += "0"


    # Write the binary data to a text file
    with open(output_file, 'a') as file:
        file.write(binary_data)

    print(f"Binary data saved to {output_file}")

def file_to_binary(file_path, output_path):
    try:
        with open(file_path, 'rb') as file:
            # Read the contents of the file
            file_content = file.read()

            # Convert the contents to binary
            binary_data = ''.join(format(byte, '08b') for byte in file_content)

            # Write the binary data to a new file
            with open(output_path, 'w') as output_file:
                output_file.write(binary_data)

        print(f"File '{file_path}' successfully converted to binary and saved to '{output_path}'.")
    except Exception as e:
        print(f"Error: {e}")

def binary_to_file(binary_path, output_path):
    try:
        with open(binary_path, 'r') as binary_file:
            # Read the binary data from the file
            binary_data = binary_file.read()

            # Convert the binary data back to bytes
            bytes_data = [int(binary_data[i:i+8], 2) for i in range(0, len(binary_data), 8)]
            byte_array = bytearray(bytes_data)

            # Write the bytes to a new file
            with open(output_path, 'wb') as output_file:
                output_file.write(byte_array)

        print(f"Binary file '{binary_path}' successfully converted back to '{output_path}'.")
    except Exception as e:
        print(f"Error: {e}")



def clear_cache(data):
    try:
        # List all files in the directory
        files = os.listdir(data)

        # Iterate through the files and remove each one
        for file_name in files:
            file_path = os.path.join(data, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"File '{file_name}' removed successfully.")

        
    except FileNotFoundError:
        print(f"Directory '{data}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
    try:
        os.remove("output_binary_file.txt")
        print("output_binary_file.txt---removed")
    except:
        pass
    try:
        os.remove("reversed_binary_data.txt")
        print("reversed_binary_data.txt---removed")
    except:
        pass





print("Menu :\n1) file to binary video\n2) binary video to original file\n3) clear cache\n")
userinp = input(">>")
if userinp == str(1):
    #
    try:
        clear_cache("data")
    except:
        pass
    #
    filename = input("Enter the filename or full location\n>>")
    input_file_path = filename
    output_file_path = 'output_binary_file.txt'
    file_to_binary(input_file_path, output_file_path)
    #
    output_image_prefix = 'data\\output_image'
    image_width = 1280
    image_height = 720
    create_image_from_binary(output_file_path, output_image_prefix, image_width, image_height)
    #
    data_folder = "data"
    image_to_video(data_folder)
elif userinp == str(2):
    open("reversed_binary_data.txt", "w").write("")
    #
    try:
        clear_cache("data")
    except:
        pass
    #

    filename = input("Enter the filename or full location\n>>")
    adjust = input("enter adjusted binary if needed or press enter\n")
    video_path = filename
    video_to_images(video_path)
    output_binary_file = 'reversed_binary_data.txt'
    i = 1
    while i>=0:
        if os.path.exists(f"data\\output_image_{str(i)}.png") == True:
            image_to_binary(f"data\\output_image_{str(i)}.png", output_binary_file)
            print(f"data\\output_image_{str(i)}.png")
        else:
            break
        i = i+1
    #
    remove_trailing_ones("reversed_binary_data.txt",adjust)
    #
    binary_file_path = 'reversed_binary_data.txt'
    reversed_output_file_path = 'reversed_output_file'
    binary_to_file(binary_file_path, reversed_output_file_path)
else:
    try:
        clear_cache("data")
    except:
        print("nothing to clear\n")