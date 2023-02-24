import shutil
import time
from tkinter import Label
from tkinter.filedialog import asksaveasfilename
import customtkinter as ct
from PIL import ImageTk, Image
from layoutExport import expLyt
from nitrateCancerModel import nitrateCancerModel


"""
set the functions and variables
"""
analysisImg = "glrMap.jpg"
analysisPdf = "glrMap.pdf"
workingImg = "working.jpg"
initialImg = "overviewLayout.jpg"
geoProImg = "geoProImg.jpg"

# intro text is in a seperate .txt and is opened and read in
fin = open("introText.txt")
introTxt = fin.read()
fin.close()


# populates the map frame with an image resized to fit
def show_image(imagefile):
    imgHeight = int(rootHeight - 20)
    imgWidth = int((8.5/11)*imgHeight)  # maintain aspect ratio

    img = Image.open(imagefile)
    img = img.resize((imgWidth, imgHeight))  # 8.5x11=2550x3300px
    image = ImageTk.PhotoImage(image=img)

    imgLabel.configure(image=image)
    # save a reference of the image to avoid garbage collection
    imgLabel.image = image


# logs the analysis to the GUI
def logAnalysis(kvalue, status):
    prefixText = {"ran": "Ran Analysis where",
                  "error": "Error: Invalid",
                  "geoerror":
                  "Geoprocessing failed. Check console for error details."}

    geoProHist.configure(state="normal")

    # 2.0 inserts most recent on top but below the "analysis history" title
    geoProHist.insert("2.0", ">    " + prefixText[status] + " K value =  "
                      + kvalue + "\n")

    geoProHist.configure(state="disabled")


# pauses processing - used in testing in place of geoprocessing
def timeDelay():
    print("starting timer")
    time.sleep(5)
    print("ending Timer")


# function called by submit button press
def runAnalysis():
    inVal = entry.get()
    # prevent issues with no value or vals out of range
    if inVal and inVal.isdigit() and int(inVal) >= 1:
        show_image(workingImg)
        kValue = int(inVal)

        # return prompt to original prompt text
        kValPrompt.configure(text="enter K value > 1", text_color="white")

        # updates GUI rather than waiting for function to complete
        root.update_idletasks()

        # run geoprocessing and export the layout
        try:
            # timeDelay()  # use in development in place of geoprocessing

            # geoprocessing - begin comment out if using timedelay
            nitrateCancerModel(kValue)
            expLyt()
            # END geoprocessing - End comment out if using timedelay

            # load the generated map
            show_image(analysisImg)

            # log history
            logAnalysis(inVal, "ran")

            # make last analysis and save buttons active
            lastButton.configure(state="normal")
            saveButton.configure(state="normal")

        except Exception as err:
            print(f"exception: {err}")
            # log history
            logAnalysis(inVal, "geoerror")
            show_image(initialImg)

    else:
        # write error to the GUI
        kValPrompt.configure(text="K value must be a number > 1",
                             text_color="red")
        # log history
        logAnalysis(inVal, "error")


# create a save file dialog
def save_file():
    # ask for new file name and directory
    newFilePath = asksaveasfilename(initialfile=f"glrMap_k{entry.get()}.pdf",
                                    initialdir="./",
                                    defaultextension=".pdf",
                                    filetypes=[("Adobe PDF", "*.pdf*"), ])
    # check that newFilePath is not empty due to cancelling the save as dialog
    if newFilePath:
        # create a copy, renamed and saved to the user selected directory
        shutil.copy(analysisPdf, newFilePath)
    else:
        return


"""
set the gui elements
"""
# set mode and color theme
ct.set_appearance_mode("dark")  # Modes: system (default), light, dark
ct.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

# set the initial window
root = ct.CTk()  # sets window widget
root.title('G777 P1 - Nitrate and Cancer Regression')

# getting screen height of display
rootHeight = root.winfo_screenheight() - 100
rootWidth = rootHeight*1.2

# set the geometry of the window and placement on screen
# width x height + fromLeft + fromTop
root.geometry(f"{rootWidth}x{rootHeight}+50+10")

# configure grid system
root.grid_rowconfigure(0, weight=1)  # 1st row grows to fill root
root.grid_columnconfigure(1, weight=1)  # 2nd column grows to fill root

"""
Intro frame
"""
# create a frame to hold the intro content
introFrame = ct.CTkFrame(root)
introFrame.grid(column=1, rowspan=2, row=0, padx=10, pady=10, sticky="nsew")
introFrame.grid_columnconfigure(0, weight=1)
introFrame.grid_rowconfigure(1, weight=1)

# create title
introTitle = ct.CTkLabel(introFrame,
                         text="Cancer Rates and Nitrate in the Soil",
                         font=ct.CTkFont(size=25, weight="bold"))
introTitle.grid(row=0, padx=20, pady=(20, 10))

# create textbox widget to hold intro description
introText = ct.CTkTextbox(introFrame, padx=10, pady=10,
                          font=ct.CTkFont(family="Tahoma", size=14))
introText.grid(row=1, padx=(20, 20), pady=(20, 10), sticky="nsew")
introText.insert("0.0", introTxt)
# make box read only
introText.configure(state="disabled", wrap="word", cursor="arrow")

"""
Analysis frame
"""
# create a frame to hold the analysis input and button
analysisFrame = ct.CTkFrame(root)
analysisFrame.grid(column=1, row=2, padx=10, pady=10, sticky="nsew")
analysisFrame.grid_columnconfigure(0, weight=1)

# create frame title
currentKVal = ct.CTkLabel(analysisFrame, text="Generate Analysis",
                          font=ct.CTkFont(size=20, weight="bold"))
currentKVal.grid(row=0, padx=(20, 20), pady=(20, 10), sticky="ew")

# create label widget to hold input prompt
kValPrompt = ct.CTkLabel(analysisFrame, text="enter K value > 1")
kValPrompt.grid(row=1)  # layout on to the screen in the grid

# input box for Kvalue input
entry = ct.CTkEntry(analysisFrame, width=50, justify="center")
entry.grid(row=2)  # layout on to the screen in the grid

# submit button
submitButton = ct.CTkButton(analysisFrame, text="Submit", command=runAnalysis)
submitButton.grid(row=3, padx=(20, 20), pady=(10, 10))

# create textbox widget to hold analysis history
geoProHist = ct.CTkTextbox(analysisFrame, height=75,
                           font=ct.CTkFont(family="Tahoma", size=12))
geoProHist.grid(row=4, padx=(20, 20), pady=(10, 10), sticky="nsew")
geoProHist.insert("0.0", "Analysis History:\n")
# make box read only
geoProHist.configure(state="disabled", wrap="word", cursor="arrow")

# Save button
saveButton = ct.CTkButton(analysisFrame, text="Save Last Analysis",
                          command=save_file)
saveButton.grid(row=7, padx=(20, 20), pady=(5, 20))
saveButton.configure(state="disabled")

"""
Button frame
"""
# create a frame to hold the view buttons
buttonFrame = ct.CTkFrame(root)
buttonFrame.grid(column=1, row=3, padx=10, pady=10, sticky="nsew")
buttonFrame.grid_columnconfigure(0, weight=1)

# create frame title
btnFrameLbl = ct.CTkLabel(buttonFrame, text="Change View",
                          font=ct.CTkFont(size=20, weight="bold"))
btnFrameLbl.grid(row=0, padx=(20, 20), pady=(20, 10), sticky="ew")

# original Map button
origButton = ct.CTkButton(buttonFrame, text="View Original Map",
                          command=lambda: show_image(initialImg))
origButton.grid(row=4, padx=(20, 20), pady=(5, 5))

# View Geoprocessing Model button
geoproButton = ct.CTkButton(buttonFrame, text="View Geoprocessing Model",
                            command=lambda: show_image(geoProImg))
geoproButton.grid(row=5, padx=(20, 20), pady=(5, 5))

# View Last Analysis Ran button
lastButton = ct.CTkButton(buttonFrame, text="View Last Analysis",
                          command=lambda: show_image(analysisImg))
lastButton.grid(row=6, padx=(20, 20), pady=(5, 5))
lastButton.configure(state="disabled")

"""
Map frame
"""
# create a frame to hold the maps
mapFrame = ct.CTkFrame(root)
mapFrame.grid(column=0, rowspan=4, row=0, padx=(15, 0), pady=10)
# create label to load img file into
imgLabel = Label(mapFrame)
imgLabel.pack()

# load the initial map display
show_image(initialImg)

# loop that allows the program to run
root.mainloop()
