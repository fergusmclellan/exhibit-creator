#!/usr/bin/python3
# Fergus McLellan - 02/04/2020

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import re
from sys import platform as _platform
import math
from PIL import Image, ImageDraw, ImageFont

"""
//////////////////////////////////////////////////////
Change global values for text/pixel sizes here
11Pt Courier New = 15 pixels high, 9 pixels wide
2 pixels are required for line spacing, so effective line height is 17 pixels per line
Images have 6 pixels padding to ensure text is not squashed into the sides
//////////////////////////////////////////////////////
"""
FONT_SIZE_PX = 15
LINE_HEIGHT_PX = 17
CHARACTER_WIDTH_PX = 9
BORDER_PADDING_PX = 6
"""
Exhibit max size = 950 * 600 pixels
104 characters * 9 pixels per char = 936 pixels, plus 7 pixel border at both sides = 950 pixels
34 lines of text * 17 pixels per line = 578 pixels, plus 7 pixel border at top and bottom
= 592 pixels height (max permitted = 600)
"""
LIMIT_EXHIBIT_MAX_CHAR = 104
LIMIT_EXHIBIT_MAX_LINES = 34
LIMIT_DND_HEIGHT_PX = 764
LIMIT_DND_WIDTH_PX = 950

# ImageFont needs path to the font file
if _platform == "darwin":
    # MAC OS X
    FONT_FILE_PATH = "/System/Library/Fonts/Supplemental/Courier New.ttf"
elif _platform == "win32":
    # Windows
    FONT_FILE_PATH = "C:\Windows\Fonts\cour.ttf"
else:
   exit("OS platform not defined. This was written with Windows or MAC OSX in mind.")

IMAGE_FONT = ImageFont.truetype(FONT_FILE_PATH, FONT_SIZE_PX)

LARGE_FONT = ("Verdana", 16)

class ExhibitCreatorapp(tk.Tk):

    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)

        tk.Tk.wm_title(self, "Exhibit Creator")

        container = tk.Frame(self)
        #container.pack(side="top", fill="both", expand = True)
        container.grid(row=0)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        style = ttk.Style(container)
        style.theme_use('classic')
        style.configure("TButton", background='white')
        style.configure("TLabel", background="white")

        self.frames = {}

        for F in (StartPage, BasicExhibitPage, FourOptionImagesPage, DnDImagesPage):

            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, cont):

        frame = self.frames[cont]
        frame.tkraise()


class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)

        label = ttk.Label(self, text="Start Page", font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        basicExhibitButton = ttk.Button(self, text="Basic Exhibit Creation",
            command=lambda: controller.show_frame(BasicExhibitPage))
        basicExhibitButton.pack()

        fourOptionsToImagesButton = ttk.Button(self, text="Options to Images",
            command=lambda: controller.show_frame(FourOptionImagesPage))
        fourOptionsToImagesButton.pack()

        dndImagesButton = ttk.Button(self, text="DnD Images",
            command=lambda: controller.show_frame(DnDImagesPage))
        dndImagesButton.pack()


class BasicExhibitPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        label = ttk.Label(self, text="Basic Exhibit Creation", font=LARGE_FONT)
        label.grid(row=0, column=0)

        homeButton = ttk.Button(self, text="Back to Home",
            command=lambda: controller.show_frame(StartPage))
        homeButton.grid(row=0, column=1)

        self.exhibitTextEntry = tk.Text(self, bg='white', borderwidth=2, relief=tk.SUNKEN,
            height=LIMIT_EXHIBIT_MAX_LINES, width=LIMIT_EXHIBIT_MAX_CHAR)
        self.exhibitTextEntry.grid(row=1, column=1)

        self.FilenameVar = tk.StringVar()

        selectFileLocationButton = ttk.Button(self, text="Select save file location",
            command=self.show_file_dialog)
        selectFileLocationButton.grid(row=2, column=1, sticky='W')

        filenameLabel = ttk.Label(self, text="Filename (path .png):")
        filenameLabel.grid(row=3, column=0, sticky='E')

        self.filename = tk.Entry(self, textvariable=self.FilenameVar, width=50)
        self.filename.grid(row=3, column=1, sticky='W')

        createImageButton = ttk.Button(self, text="Create image file",
            command=self.process_exhibit_text)
        createImageButton.grid(row=5, column=1)

    def show_file_dialog(self):
        filename_and_path = filedialog.asksaveasfilename(initialdir = ".",
            title = "Select file", filetypes = (("png files","*.png"), ("all files","*.*")))
        self.FilenameVar.set(filename_and_path)

    def process_exhibit_text(self):
        self.exhibit_text=self.exhibitTextEntry.get("1.0",'end-1c')
        self.image_file_name=self.filename.get()
        self.max_line_width = find_len_longest_line(self.exhibit_text)
        self.no_of_lines = find_number_of_lines_in_text(self.exhibit_text)

        if self.max_line_width > LIMIT_EXHIBIT_MAX_CHAR:
            messagebox.showerror(title="Error!", message="One or more lines of text are too wide \
                (check lines for wrapped text). Please resolve")
        elif self.no_of_lines > LIMIT_EXHIBIT_MAX_LINES:
            messagebox.showerror(title="Error!",
                message="There are too many lines of text (check for text disappearing off bottom \
                    of text box). Please resolve")
        elif not len(self.image_file_name) > 0:
            messagebox.showerror(title="Error!",
                message="Please specify filepath and name to use for image.")
        else:
            create_image_from_text(self.exhibit_text, self.image_file_name, self.max_line_width,
                self.no_of_lines)
            messagebox.showinfo(title="Completed", message=("Image file created: " + \
                self.image_file_name))


class FourOptionImagesPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = ttk.Label(self, text="4 Option to Images Page - Coming Soon!!!", font=LARGE_FONT)
        #label.pack(pady=10,padx=10)

        homeButton = ttk.Button(self, text="Back to Home",
                            command=lambda: controller.show_frame(StartPage))
        #homeButton.pack()


class DnDImagesPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.exhibit_max_line_width = 0
        self.exhibit_max_lines = 0
        self.options_max_line_width = 0
        self.options_max_lines = 0
        self.number_of_options = 0

        self.MainExhibitTextVar = tk.StringVar()
        self.MainExhibitTextVar.set('')
        self.FilenameVar = tk.StringVar()
        self.OptionSizeVar = tk.StringVar()
        self.OptionSizeVar.set('Total Options size pixels=')
        self.ExhibitSizeVar = tk.StringVar()
        self.ExhibitSizeVar.set('Exhibit size pixels=')
        # Cannot find a way to change text content without using StringVar
        # StringVar does not seem to work with lists or loops, so need to
        # define all Option variables and text boxes individually
        self.Option1TextVar = tk.StringVar()
        self.Option2TextVar = tk.StringVar()
        self.Option3TextVar = tk.StringVar()
        self.Option4TextVar = tk.StringVar()
        self.Option5TextVar = tk.StringVar()
        self.Option6TextVar = tk.StringVar()
        self.Option7TextVar = tk.StringVar()
        self.Option8TextVar = tk.StringVar()
        self.Option9TextVar = tk.StringVar()
        self.Option10TextVar = tk.StringVar()

        self.grid_rowconfigure((1,2,3,4,5,6,7,8,9,10), minsize=65, uniform=65)

        self.frame_label = ttk.Label(self, text="DnD Images Creation", background='white',
            font=LARGE_FONT)
        self.frame_label.grid(row=0, column=0)

        self.home_button = ttk.Button(self, text="Back to Home",
            command=lambda: controller.show_frame(StartPage))
        self.home_button.grid(row=0, column=1)

        self.options_label = ttk.Label(self, text="DnD Options", background='white',
            font=LARGE_FONT)
        self.options_label.grid(row=1, column=2)

        self.reset_text_button = ttk.Button(self, text="Reset Options Text",
            command=self.reset_text)
        self.reset_text_button.grid(row=1, column=0)

        self.select_text_button = ttk.Button(self, text="Create Option Using Selected Text",
            command=self.text_selection_into_option)
        self.select_text_button.grid(row=2, column=0)

        self.manual_text_label = ttk.Label(self, text="Manual Option Text Entry:",
            background='white')
        self.manual_text_label.grid(row=3, column=0, sticky='s')

        self.dnd_manual_text_option = tk.Text(self, bg='white', borderwidth=2, relief=tk.SUNKEN,
            height=3, width=int(LIMIT_EXHIBIT_MAX_CHAR/2)-1)
        self.dnd_manual_text_option.grid(row=4, column=0, sticky='n')

        self.manual_text_button = ttk.Button(self,
            text="Create Option Using Manual Text (Distractor)",
            command=self.manual_text_into_option)
        self.manual_text_button.grid(row=5, column=0, sticky='n')

        self.dnd_main_text_entry = tk.Text(self, bg='white', borderwidth=2,
            relief=tk.SUNKEN, height=LIMIT_EXHIBIT_MAX_LINES, width=LIMIT_EXHIBIT_MAX_CHAR)
        self.dnd_main_text_entry.grid(row=1, column=1, rowspan=7)

        # Cannot find a way to change text content without using StringVar
        # StringVar does not seem to work with lists or loops, so need to
        # define all variables and text boxes individually
        self.dnd_text_option1 = tk.Label(self, textvariable=self.Option1TextVar, width=50,
            height=3, borderwidth=2, relief="groove", justify='left', anchor='w')
        self.dnd_text_option1.grid(row=1, column=2, sticky='NEWS')

        self.dnd_text_option2 = tk.Label(self, textvariable=self.Option2TextVar, width=50,
            height=3, borderwidth=2, relief="groove", justify='left', anchor='w')
        self.dnd_text_option2.grid(row=2, column=2, sticky='NEWS')

        self.dnd_text_option3 = tk.Label(self, textvariable=self.Option3TextVar, width=50,
            height=3, borderwidth=2, relief="groove", justify='left', anchor='w')
        self.dnd_text_option3.grid(row=3, column=2, sticky='NEWS')

        self.dnd_text_option4 = tk.Label(self, textvariable=self.Option4TextVar, width=50,
            height=3, borderwidth=2, relief="groove", justify='left', anchor='w')
        self.dnd_text_option4.grid(row=4, column=2, sticky='NEWS')

        self.dnd_text_option5 = tk.Label(self, textvariable=self.Option5TextVar, width=50,
            height=3, borderwidth=2, relief="groove", justify='left', anchor='w')
        self.dnd_text_option5.grid(row=5, column=2, sticky='NEWS')

        self.dnd_text_option6 = tk.Label(self, textvariable=self.Option6TextVar, width=50,
            height=3, borderwidth=2, relief="groove", justify='left', anchor='w')
        self.dnd_text_option6.grid(row=6, column=2, sticky='NEWS')

        self.dnd_text_option7 = tk.Label(self, textvariable=self.Option7TextVar, width=50,
            height=3, borderwidth=2, relief="groove", justify='left', anchor='w')
        self.dnd_text_option7.grid(row=7, column=2, sticky='NEWS')

        self.dnd_text_option8 = tk.Label(self, textvariable=self.Option8TextVar, width=50,
            height=3, borderwidth=2, relief="groove", justify='left', anchor='w')
        self.dnd_text_option8.grid(row=8, column=2, sticky='NEWS')

        self.dnd_text_option9 = tk.Label(self, textvariable=self.Option9TextVar, width=50,
            height=3, borderwidth=2, relief="groove", justify='left', anchor='w')
        self.dnd_text_option9.grid(row=9, column=2, sticky='NEWS')

        self.dnd_text_option10 = tk.Label(self, textvariable=self.Option10TextVar, width=50,
            height=3, borderwidth=2, relief="groove", justify='left', anchor='w')
        self.dnd_text_option10.grid(row=10, column=2, sticky='NEWS')

        self.optionSizeLabel = tk.Label(self, textvariable=self.OptionSizeVar, width=30, height=1,
            borderwidth=2, relief="sunken", justify='left', anchor='w')
        self.optionSizeLabel.grid(row=6, column=0)

        self.exhibitSizeLabel = tk.Label(self, textvariable=self.ExhibitSizeVar, width=30,
            height=1, borderwidth=2, relief="sunken", justify='left', anchor='w')
        self.exhibitSizeLabel.grid(row=7, column=0)

        self.select_file_location_button = ttk.Button(self, text="Select save file location",
            command=self.show_file_dialog)
        self.select_file_location_button.grid(row=8, column=1, sticky='WS')

        self.filename_label = ttk.Label(self, text="Filename (path .png):", background='white')
        self.filename_label.grid(row=9, column=0, sticky='NE')

        self.filename = tk.Entry(self, textvariable=self.FilenameVar, width=50)
        self.filename.grid(row=9, column=1, sticky='NW')

        self.create_image_button = ttk.Button(self, text="Create image files",
            command=self.process_text_to_images)
        self.create_image_button.grid(row=10, column=1)


    def reset_text(self):
        self.Option1TextVar.set('')
        self.Option2TextVar.set('')
        self.Option3TextVar.set('')
        self.Option4TextVar.set('')
        self.Option5TextVar.set('')
        self.Option6TextVar.set('')
        self.Option7TextVar.set('')
        self.Option8TextVar.set('')
        self.Option9TextVar.set('')
        self.Option10TextVar.set('')
        self.options_max_line_width = 0
        self.options_max_lines = 0
        self.number_of_options = 0

    def manual_text_into_option(self):
        manual_text = self.dnd_manual_text_option.get("1.0",'end-1c')
        if len(manual_text) > 0:
            if self.number_of_options == 10:
                messagebox.showerror(title="Error!", message="All options used.")
                return
            self.option_text = manual_text
            option_text_into_lines = self.option_text.split('\n')
            self.this_option_no_of_lines = len(option_text_into_lines)
            self.proposed_target_text_length = 0
            for option_line in option_text_into_lines:
                self.this_option_line_width = len(option_line)
                if self.this_option_line_width > self.proposed_target_text_length:
                    self.proposed_target_text_length = self.this_option_line_width
            if self.this_option_no_of_lines > self.options_max_lines:
                self.proposed_option_lines = self.this_option_no_of_lines
            else:
                self.proposed_option_lines = self.options_max_lines
            # not used by manual option text, so set to 0 to ignore in size calculations
            self.proposed_text_start_line = 0
            self.calc_proposed_area_required()
            if self.proposed_total_width_pixels > LIMIT_DND_WIDTH_PX:
                messagebox.showerror(title="Error!",
                message="This selection will make the exhibit width too large to fit in the item.")
                return
            elif self.proposed_total_height_pixels > LIMIT_DND_HEIGHT_PX:
                messagebox.showerror(title="Error!",
                message="This selection will make the combined exhibit and Options height too large to fit in the item.")
                return

            # If new proposed size is OK, proceed with committing changes
            self.exhibit_height_pixels = self.proposed_exhibit_height_pixels
            self.exhibit_width_pixels = self.proposed_exhibit_width_pixels
            self.options_height_pixels = self.proposed_options_height_pixels
            self.options_width_pixels = self.proposed_options_width_pixels

            self.update_option()
            self.dnd_manual_text_option.delete("1.0",'end-1c')
        else:
            messagebox.showerror(title="Error!", message="No text was entered in Manual option box")

    def text_selection_into_option(self):

        # Capture selection text
        if self.dnd_main_text_entry.tag_ranges('sel'):
            self.MainExhibitTextVar = self.dnd_main_text_entry.get("1.0",'end-1c')
            if self.number_of_options == 10:
                messagebox.showerror(title="Error!", message="All options used.")
                return

            exhibit_text_into_lines = self.MainExhibitTextVar.split('\n')
            if len(exhibit_text_into_lines) > LIMIT_EXHIBIT_MAX_LINES:
                messagebox.showerror(title="Error!",
                    message="There are too many lines in the main exhibit.")
                return
            elif len(exhibit_text_into_lines) > self.exhibit_max_lines:
                self.exhibit_max_lines = len(exhibit_text_into_lines)

            for exhibit_line in exhibit_text_into_lines:
                exhibit_line_width = len(exhibit_line)
                if exhibit_line_width > LIMIT_EXHIBIT_MAX_CHAR:
                    messagebox.showerror(title="Error!",
                        message="One or more lines in the main exhibit are already too long. Please split any lines which have wrapped text.")
                    return
                if exhibit_line_width > self.exhibit_max_line_width:
                    self.exhibit_max_line_width = exhibit_line_width

            self.selected_text = self.dnd_main_text_entry.get(tk.SEL_FIRST, tk.SEL_LAST)
            option_text_into_lines = self.selected_text.split('\n')
            self.this_option_no_of_lines = len(option_text_into_lines)
            if self.this_option_no_of_lines > 3:
                messagebox.showerror(title="Error!",
                    message="More than 3 lines of text in DnD option is not recommended. Having 1 option with > 3 lines means that ALL options and targets need to be > 3 lines in height. DnD may not fit into Exam Developer.")
                return
            else:
                selected_text_start, selected_text_stop = self.dnd_main_text_entry.tag_ranges('sel')
                selected_text_start_line, selected_text_start_pos = str(selected_text_start).split('.')
                selected_text_start_line = int(selected_text_start_line)
                selected_text_start_pos = int(selected_text_start_pos)
                self.proposed_text_start_line = selected_text_start_line
                selected_text_stop_line, selected_text_stop_pos = str(selected_text_stop).split('.')
                selected_text_stop_line = int(selected_text_stop_line)
                selected_text_stop_pos = int(selected_text_stop_pos)
                length_of_selected_text = selected_text_stop_pos - selected_text_start_pos
                for option_line in option_text_into_lines:
                    self.this_option_line_width = len(option_line)
                    if self.this_option_line_width > (int(LIMIT_EXHIBIT_MAX_CHAR/2)-1):
                        messagebox.showerror(title="Error!",
                            message="More than 50 characters per line in a DnD option is not recommended. > 50 characters means that options cannot be laid out in 2 or more columns below the main DnD image. You are going to have to fudge this if you want > 50 characters per option.")
                        return
                    else:
                        if self.this_option_line_width > length_of_selected_text:
                            length_of_selected_text = self.this_option_line_width
                if self.this_option_no_of_lines > self.options_max_lines:
                    self.proposed_option_lines = self.this_option_no_of_lines
                else:
                    self.proposed_option_lines = self.options_max_lines

                self.proposed_target_text_length = length_of_selected_text
                self.calc_proposed_area_required()
                if self.proposed_total_width_pixels > LIMIT_DND_WIDTH_PX:
                    messagebox.showerror(title="Error!",
                        message="This selection will make the exhibit width too large to fit in the item.")
                    return
                elif self.proposed_total_height_pixels > LIMIT_DND_HEIGHT_PX:
                    messagebox.showerror(title="Error!",
                        message="This selection will make the combined exhibit and Options height too large to fit in the item.")
                    return

                # If new proposed size is OK, proceed with committing changes
                self.exhibit_height_pixels = self.proposed_exhibit_height_pixels
                self.exhibit_width_pixels = self.proposed_exhibit_width_pixels
                self.options_height_pixels = self.proposed_total_height_pixels
                self.options_width_pixels = self.proposed_total_options_width_pixels

                text_replacement = ' _____ '
                self.dnd_main_text_entry.delete(tk.SEL_FIRST, tk.SEL_LAST)
                self.dnd_main_text_entry.insert(selected_text_start, text_replacement)

                self.option_text = self.selected_text
                self.update_option()

        else:
            messagebox.showerror(title="Error!", message="No text was selected")


    def calc_proposed_area_required(self):
        # calculate main exhibit size in pixels
        self.exhibit_text=self.dnd_main_text_entry.get("1.0",'end-1c')
        target_pattern = re.compile(r'_____')
        max_length = 0
        number_of_lines_with_options = 0
        text_by_lines = self.exhibit_text.split('\n')
        number_of_lines = len(text_by_lines)
        for index, line in enumerate(text_by_lines):
            number_of_targets = 0
            targets = target_pattern.findall(line)
            if len(targets) > 0:
                number_of_lines_with_options = number_of_lines_with_options + 1
                number_of_targets = len(targets)

                non_target_text_length = len(line) - (number_of_targets * 5)
                if index == (self.proposed_text_start_line - 1):
                    # new target is to be added to this line
                    number_of_targets = number_of_targets + 1
                line_length = non_target_text_length + \
                    (number_of_targets * self.proposed_target_text_length)
            else:
                line_length = len(line)

            if line_length > max_length:
                max_length = line_length
        if self.proposed_text_start_line > 0:
            # this is a new target in exhibit: add one to the number of height_no_targets
            number_of_lines_with_options = number_of_lines_with_options + 1

        self.proposed_exhibit_height_pixels = ((number_of_lines - number_of_lines_with_options)*
            LINE_HEIGHT_PX)   + (number_of_lines_with_options * ((self.proposed_option_lines *
            LINE_HEIGHT_PX) + (2 * (BORDER_PADDING_PX + 3)))) + (2 * (BORDER_PADDING_PX))
        self.proposed_exhibit_width_pixels = (max_length * CHARACTER_WIDTH_PX) + \
            (2 * BORDER_PADDING_PX)
        print("proposed exhibit height (pixels): " + str(self.proposed_exhibit_height_pixels))
        print("proposed exhibit width (pixels): " + str(self.proposed_exhibit_width_pixels))

        # calculate size in pixels needed for an option
        if self.proposed_target_text_length > self.options_max_line_width:
            proposed_option_max_text_length = self.proposed_target_text_length
        else:
            proposed_option_max_text_length = self.options_max_line_width

        if self.proposed_option_lines > self.options_max_lines:
            proposed_option_max_lines = self.proposed_option_lines
        else:
            proposed_option_max_lines = self.options_max_lines

        self.proposed_options_height_pixels = (proposed_option_max_lines * LINE_HEIGHT_PX) + \
            (2* (BORDER_PADDING_PX))
        self.proposed_options_width_pixels = (max_length * CHARACTER_WIDTH_PX) + \
            (2* (BORDER_PADDING_PX))

        print("proposed option height (pixels): " + str(self.proposed_options_height_pixels))
        print("proposed option width (pixels): " + str(self.proposed_options_width_pixels))

        proposed_number_of_options = self.number_of_options + 1

        # allow 5 pixels spacing between sides and options, and between columns
        if self.proposed_options_width_pixels < ((LIMIT_DND_WIDTH_PX - 20) / 3):
            # can arrange options side by side in 3 columns
            options_in_a_row = 3
            options_in_a_column = math.ceil(proposed_number_of_options /options_in_a_row)
        elif self.proposed_options_width_pixels < ((LIMIT_DND_WIDTH_PX - 15) / 2):
            # can arrange options side by side in 2 columns
            options_in_a_row = 2
            options_in_a_column = math.ceil(proposed_number_of_options /options_in_a_column)
        else:
            # need to arrange options in a single column
            options_in_a_row = 1
            options_in_a_column = proposed_number_of_options

        # allow 5 pixels spacing between rows, and at top and bottom of option area
        self.proposed_total_options_height_pixels = (options_in_a_column * \
            (self.proposed_options_height_pixels + 5)) + 5
        self.proposed_total_options_width_pixels = (options_in_a_row * \
            (self.proposed_options_width_pixels + 5)) + 5

        self.proposed_total_height_pixels = self.proposed_total_options_height_pixels + \
            self.proposed_exhibit_height_pixels
        if self.proposed_total_options_width_pixels > self.proposed_exhibit_width_pixels:
            self.proposed_total_width_pixels = self.proposed_total_options_width_pixels
        else:
            self.proposed_total_width_pixels =  self.proposed_exhibit_width_pixels


    def update_option(self):
        if self.this_option_no_of_lines > self.options_max_lines:
            self.options_max_lines = self.this_option_no_of_lines
        if self.this_option_line_width > self.options_max_line_width:
            self.options_max_line_width = self.this_option_line_width

        self.OptionSizeVar.set("Total Options size pixels=" + str(self.options_width_pixels) + \
            "*" + str(self.options_height_pixels))
        self.ExhibitSizeVar.set("Exhibit size pixels=" + str(self.exhibit_width_pixels) + \
            "*" + str(self.exhibit_height_pixels))
        if not len(self.Option1TextVar.get()) > 1:
            self.Option1TextVar.set(self.option_text)
            self.number_of_options = 1
        elif not len(self.Option2TextVar.get()) > 1:
            self.Option2TextVar.set(self.option_text)
            self.number_of_options = 2
        elif not len(self.Option3TextVar.get()) > 1:
            self.Option3TextVar.set(self.option_text)
            self.number_of_options = 3
        elif not len(self.Option4TextVar.get()) > 1:
            self.Option4TextVar.set(self.option_text)
            self.number_of_options = 4
        elif not len(self.Option5TextVar.get()) > 1:
            self.Option5TextVar.set(self.option_text)
            self.number_of_options = 5
        elif not len(self.Option6TextVar.get()) > 1:
            self.Option6TextVar.set(self.option_text)
            self.number_of_options = 6
        elif not len(self.Option7TextVar.get()) > 1:
            self.Option7TextVar.set(self.option_text)
            self.number_of_options = 7
        elif not len(self.Option8TextVar.get()) > 1:
            self.Option8TextVar.set(self.option_text)
            self.number_of_options = 8
        elif not len(self.Option9TextVar.get()) > 1:
            self.Option9TextVar.set(self.option_text)
            self.number_of_options = 9
        elif not len(self.Option10TextVar.get()) > 1:
            self.Option10TextVar.set(self.option_text)
            self.number_of_options = 10


    def show_file_dialog(self):
        filename_and_path = filedialog.asksaveasfilename(initialdir = ".",
            title = "Select file",filetypes = (("png files","*.png"),("all files","*.*")))
        self.FilenameVar.set(filename_and_path)


    def process_text_to_images(self):
        self.exhibit_text=self.dnd_main_text_entry.get("1.0",'end-1c')
        self.proposed_text_start_line = 0
        self.calc_proposed_area_required()
        self.exhibit_height_pixels = self.proposed_exhibit_height_pixels
        self.exhibit_width_pixels = self.proposed_exhibit_width_pixels

        image_text = re.sub('_____', ('_'*self.options_max_line_width), self.exhibit_text)
        self.image_file_name=self.filename.get()
        create_variable_spacing_image(image_text, self.image_file_name,
            self.exhibit_width_pixels, self.exhibit_height_pixels, self.options_max_lines)
        if len(self.Option1TextVar.get()) > 1:
            this_option_text = self.Option1TextVar.get()
            this_option_filename = re.sub('.png', '_option1.png', self.image_file_name)
            create_image_from_text(this_option_text, this_option_filename,
                self.options_max_line_width, self.options_max_lines)
        if len(self.Option2TextVar.get()) > 1:
            this_option_text = self.Option2TextVar.get()
            this_option_filename = re.sub('.png', '_option2.png', self.image_file_name)
            create_image_from_text(this_option_text, this_option_filename,
                self.options_max_line_width, self.options_max_lines)
        if len(self.Option3TextVar.get()) > 1:
            this_option_text = self.Option3TextVar.get()
            this_option_filename = re.sub('.png', '_option3.png', self.image_file_name)
            create_image_from_text(this_option_text, this_option_filename,
                self.options_max_line_width, self.options_max_lines)
        if len(self.Option4TextVar.get()) > 1:
            this_option_text = self.Option4TextVar.get()
            this_option_filename = re.sub('.png', '_option4.png', self.image_file_name)
            create_image_from_text(this_option_text, this_option_filename,
                self.options_max_line_width, self.options_max_lines)
        if len(self.Option5TextVar.get()) > 1:
            this_option_text = self.Option5TextVar.get()
            this_option_filename = re.sub('.png', '_option5.png', self.image_file_name)
            create_image_from_text(this_option_text, this_option_filename,
                self.options_max_line_width, self.options_max_lines)
        if len(self.Option6TextVar.get()) > 1:
            this_option_text = self.Option6TextVar.get()
            this_option_filename = re.sub('.png', '_option6.png', self.image_file_name)
            create_image_from_text(this_option_text, this_option_filename,
                self.options_max_line_width, self.options_max_lines)
        if len(self.Option7TextVar.get()) > 1:
            this_option_text = self.Option7TextVar.get()
            this_option_filename = re.sub('.png', '_option7.png', self.image_file_name)
            create_image_from_text(this_option_text, this_option_filename,
                self.options_max_line_width, self.options_max_lines)
        if len(self.Option8TextVar.get()) > 1:
            this_option_text = self.Option8TextVar.get()
            this_option_filename = re.sub('.png', '_option8.png', self.image_file_name)
            create_image_from_text(this_option_text, this_option_filename,
                self.options_max_line_width, self.options_max_lines)
        if len(self.Option9TextVar.get()) > 1:
            this_option_text = self.Option9TextVar.get()
            this_option_filename = re.sub('.png', '_option9.png', self.image_file_name)
            create_image_from_text(this_option_text, this_option_filename,
                self.options_max_line_width, self.options_max_lines)
        if len(self.Option10TextVar.get()) > 1:
            this_option_text = self.Option10TextVar.get()
            this_option_filename = re.sub('.png', '_option10.png', self.image_file_name)
            create_image_from_text(this_option_text, this_option_filename,
                self.options_max_line_width, self.options_max_lines)

        messagebox.showinfo(title="Completed", message=("Image files created: " + \
            self.image_file_name))


def find_number_of_lines_in_text(text):
    number_of_lines = 0

    if len(str(text)) > 0 and 'nan' not in str(text):
        text_to_lines = text.split('\n')
        number_of_lines = len(text_to_lines)

    return number_of_lines


def find_len_longest_line(text):
    longest_line = 0

    if len(str(text)) > 0 and 'nan' not in str(text):
        for line in text.split('\n'):
            length = len(line)
            if length > longest_line:
                 longest_line = length

    return longest_line


def create_image_from_text(text, image_filename, max_len_of_text, max_lines):
    text_pixel_width = (max_len_of_text * CHARACTER_WIDTH_PX) + (2*BORDER_PADDING_PX)
    text_pixel_height = (max_lines * LINE_HEIGHT_PX) + (2*BORDER_PADDING_PX)

    img = Image.new('RGB', (text_pixel_width, text_pixel_height), color = ('white'))

    drawing = ImageDraw.Draw(img)
    drawing.text((BORDER_PADDING_PX, BORDER_PADDING_PX), text, font=IMAGE_FONT, fill=('black'))
    drawing.rectangle([(0,0), (text_pixel_width, text_pixel_height)], fill=None, outline='black',
        width=2)
    # border appears as only 1 pixel width along right and bottom sides, so draw an extra line
    drawing.line((1, text_pixel_height-2, text_pixel_width-1, text_pixel_height-2), width=1,
        fill='black')
    drawing.line((text_pixel_width-2, 1, text_pixel_width-2, text_pixel_height-1), width=1,
        fill='black')
    img.save(image_filename)


def create_variable_spacing_image(text, image_filename, image_width_in_pixels,
    image_height_in_pixels, lines_per_option):

    text_start_height = BORDER_PADDING_PX
    img = Image.new('RGB', (image_width_in_pixels, image_height_in_pixels), color=('white'))
    target_pattern = re.compile(r'_____')
    drawing = ImageDraw.Draw(img)
    text_by_lines = text.split('\n')
    for line in text_by_lines:

        targets = target_pattern.findall(line)
        if len(targets) > 0:
            text_start_height = text_start_height + BORDER_PADDING_PX + 3
            drawing.text((BORDER_PADDING_PX, text_start_height), line, font=IMAGE_FONT, fill=('black'))
            text_start_height = text_start_height + (lines_per_option * LINE_HEIGHT_PX) + \
                BORDER_PADDING_PX + 3
        else:
            drawing.text((BORDER_PADDING_PX, text_start_height), line, font=IMAGE_FONT, fill=('black'))
            text_start_height = text_start_height + LINE_HEIGHT_PX

    drawing.rectangle([(0, 0), (image_width_in_pixels, image_height_in_pixels)], fill=None,
        outline='black', width=2)
    # border appears as only 1 pixel width along right and bottom sides,
    # so draw an extra line on other 2 sides
    drawing.line((1, image_height_in_pixels-2, image_width_in_pixels-1, image_height_in_pixels-2),
        width=1, fill='black')
    drawing.line((image_width_in_pixels-2, 1, image_width_in_pixels-2, image_height_in_pixels-1),
        width=1, fill='black')
    img.save(image_filename)


APP = ExhibitCreatorapp()
APP.mainloop()
