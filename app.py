# Import the Tkinter module
import tkinter as tk

def on_click_command():
    first_btn_label.config (text="You clicked the button!") 

def second_button_cmd():
    second_btn_label.config (text="Second button clicked!") 
# Define the main function to run the application
def main():
    """
    This function sets up the main window and starts the Tkinter event loop.
    """
    global label
    global first_btn_label
    global second_btn_label
    # 1. Create the main window (root window)
    # This is the top-level container that holds all other widgets.
    root = tk.Tk()

    # 2. Configure the window's properties
    # Set the title of the window.
    root.title("My First Tkinter App")
    
    # Set the initial size of the window (width x height).
    root.geometry("400x400")
    
    # Make the window non-resizable.
    root.resizable(True, True)

    # 3. Create widgets and add them to the window
    # Create a Label widget with some text.
    label = tk.Label(root, text="Hello, Tkinter!")
    
    # Pack the label to make it visible in the window.
    # The pack() method is a simple geometry manager.
    # Add some padding on the y-axis
    label.pack(pady=10)
    
    # Creating a button:
    button=tk.Button(root,text="This is a button", command=on_click_command)
    button.pack(pady=10)
    first_btn_label=tk.Label(root,text="")
    first_btn_label.pack(pady=10)

    #Second button;
    button=tk.Button(root,text="Another Button",command=second_button_cmd)
    button.pack(pady=20)
    second_btn_label=tk.Label(root)
    second_btn_label.pack(pady=10)
    # 4. Start the main event loop
    # This is the most important part. It listens for events (like clicks)
    # and keeps the window open until the user closes it.
    root.mainloop()

# Check if the script is being run directly
if __name__ == "__main__":
    main()