# Import the Tkinter module
import tkinter as tk
import traceback

class MyTinkerApp:

    def __init__(self,root):
        self.root=root
        self.root.title("My First Tkinter App")
        self.root.geometry("400x400")
        self.root.resizable(True, True)
    
        self.label=tk.Label(root, text="Hello, Tkinter!")
        self.label.pack(pady=10)
        
        self.button=tk.Button(root,text="This is a first button", command=self.on_click_command)
        self.button.pack(pady=10)
        self.first_btn_label=tk.Label(root,text="")
        self.first_btn_label.pack(pady=10)

        self.button=tk.Button(root,text="Second Button",command=self.second_button_cmd)
        self.button.pack(pady=20)
        self.second_btn_label=tk.Label(root)
        self.second_btn_label.pack(pady=10)

    def on_click_command(self):
        self.first_btn_label.config (text="You clicked the first button!") 

    def second_button_cmd(self):
        self.second_btn_label.config (text="Second button clicked!")

def main():
    try:
        root = tk.Tk()
        app=MyTinkerApp(root)
        root.mainloop()
    except Exception as e:
        print("An error occurred:")
        traceback.print_exc()
        print("Did you print the padding correctly?") 
    

# Check if the script is being run directly
if __name__ == "__main__":
    main()