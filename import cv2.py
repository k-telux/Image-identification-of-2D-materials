import cv2
import numpy as np
import pyautogui
import pygetwindow as gw

# Global variables for mouse callback
start_point = None
end_point = None
drawing = False
selected_region = None

def select_area(event, x, y, flags, param):
    """
    Mouse callback function to select an area on the screen.
    """
    global start_point, end_point, drawing, selected_region

    if event == cv2.EVENT_LBUTTONDOWN:
        # Start drawing the rectangle
        start_point = (x, y)
        drawing = True

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            # Update the end point as the mouse moves
            end_point = (x, y)

    elif event == cv2.EVENT_LBUTTONUP:
        # Finish drawing the rectangle
        end_point = (x, y)
        drawing = False
        selected_region = (start_point[0], start_point[1], end_point[0] - start_point[0], end_point[1] - start_point[1])

def monitor_screen_area(x, y, width, height, grid_size):
    """
    Monitors a specific area of the screen, divides it into squares, and displays the grayscale image.
    """
    square_width = width // grid_size
    square_height = height // grid_size

    while True:
        # Get the current program's window position to exclude it
        program_window = gw.getWindowsWithTitle("Grayscale Grid")
        if program_window:
            program_window = program_window[0]
            program_rect = (
                program_window.left,
                program_window.top,
                program_window.left + program_window.width,
                program_window.top + program_window.height,
            )
        else:
            program_rect = None

        # Capture the screen area
        screenshot = pyautogui.screenshot(region=(x, y, width, height))
        screenshot = np.array(screenshot)

        # Exclude the program's window from the screenshot
        if program_rect:
            px1, py1, px2, py2 = program_rect
            px1 = max(px1 - x, 0)
            py1 = max(py1 - y, 0)
            px2 = max(px2 - x, 0)
            py2 = max(py2 - y, 0)

            # Skip capturing the area of the program's window
            screenshot[py1:py2, px1:px2] = screenshot[py1:py2, px1:px2]

        # Convert to grayscale
        gray_image = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

        # Create an empty image for the grid
        grid_image = np.zeros_like(gray_image)

        # Process each square in the grid
        for i in range(grid_size):
            for j in range(grid_size):
                # Calculate the coordinates of the square
                start_x = i * square_width
                start_y = j * square_height
                end_x = start_x + square_width
                end_y = start_y + square_height

                # Get the average grayscale value of the square
                square = gray_image[start_y:end_y, start_x:end_x]
                avg_gray = np.mean(square)

                # Fill the grid image with the average grayscale value
                grid_image[start_y:end_y, start_x:end_x] = avg_gray

        # Display the grid image
        cv2.imshow("Grayscale Grid", grid_image)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

# Main function to handle area selection and monitoring
def main():
    global selected_region

    # Create a blank window for area selection
    screen_width, screen_height = pyautogui.size()
    blank_image = np.zeros((screen_height, screen_width, 3), dtype=np.uint8)

    cv2.namedWindow("Select Area")
    cv2.setMouseCallback("Select Area", select_area)

    while True:
        temp_image = blank_image.copy()

        # Draw the rectangle as the user selects the area
        if start_point and end_point:
            cv2.rectangle(temp_image, start_point, end_point, (255, 255, 255), 2)

        cv2.imshow("Select Area", temp_image)

        # Break the loop if the area is selected
        if selected_region:
            break

        # Break the loop if 'q' is pressed
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            cv2.destroyWindow("Select Area")
            return

    cv2.destroyWindow("Select Area")

    # Start monitoring the selected area
    x, y, width, height = selected_region
    grid_size = 10  # Default grid size
    monitor_screen_area(x, y, width, height, grid_size)

if __name__ == "__main__":
    main()