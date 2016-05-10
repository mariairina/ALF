"""
File: tm_gui.py
Defines the graphical interface used to demonstrate our machine.
"""

"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""

import wx
import random
import tm
import programs


BORDER = 2 #used around some elements, to provide a nice padding

#used to highlight the head's position on each tape
CURRENT_POS_STYLE = wx.TextAttr(wx.Colour(0, 0, 0), colBack=wx.Colour(0, 200, 255))


"""
Utility function, for making a panel with a predefined sizer, used for layouting
"""
def make_layout_panel(parent, direction, *args, **kwargs):
    panel = wx.Panel(parent, *args, **kwargs)
    panel.SetSizer(wx.BoxSizer(direction))
    return panel


"""
The main class of our graphical interface
"""
class MainWindow(wx.Frame):
    
    """
    The constructor defines all the ui elements and binds the required events.
    """
    def __init__(self, parent=None, id=wx.ID_ANY):
        wx.Frame.__init__(self, parent, id, 'Turing Machine', size=(660,440),
                          style=wx.SYSTEM_MENU|wx.CAPTION|wx.CLOSE_BOX)
                          #style used to disable window resizing

        #the frame's sizer divides it into the top part, used for controls,
        #and the bottom one, used for the tapes and the program.
        self.SetSizer(wx.BoxSizer(wx.VERTICAL))


        #===Top section (with controls)===
        controls_panel = make_layout_panel(self, wx.HORIZONTAL)
        self.Sizer.Add(controls_panel, 0, wx.EXPAND)


        program_label = wx.StaticText(controls_panel, label="Program: ") 
        controls_panel.Sizer.Add(program_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, BORDER)

        program_chooser = wx.Choice(controls_panel)
        for program in programs.plist:
            program_chooser.Append(program.name)
        controls_panel.Sizer.Add(program_chooser, 0, wx.EXPAND|wx.ALL, BORDER)
        
        
        speed_label = wx.StaticText(controls_panel, label="Simulation speed (steps/sec): ") 
        controls_panel.Sizer.Add(speed_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, BORDER)
        
        speed_input = wx.SpinCtrl(controls_panel, min=1, initial=8, value='8', size=(60,-1))
        controls_panel.Sizer.Add(speed_input, 0, wx.EXPAND|wx.ALL, BORDER)


        run_pause_button = wx.Button(controls_panel, label="Run")
        run_pause_button.Enable(False)
        controls_panel.Sizer.Add(run_pause_button, 0, wx.EXPAND|wx.ALL, BORDER)
        
        reset_button = wx.Button(controls_panel, label="Reset")
        reset_button.Enable(False)
        controls_panel.Sizer.Add(reset_button, 0, wx.EXPAND|wx.ALL, BORDER)
        #===End of top section===


        #===Main section (tapes and program)===
        main_panel = make_layout_panel(self, wx.HORIZONTAL)
        self.Sizer.Add(main_panel, 1, wx.EXPAND)

        #the tapes are added dinamically, so here we only define the support panel
        tapes_panel = make_layout_panel(main_panel, wx.VERTICAL, size=(230,-1), style=wx.BORDER_SIMPLE)
        main_panel.Sizer.Add(tapes_panel, 0, wx.EXPAND)

        program_table = wx.ListCtrl(main_panel, style=wx.LC_REPORT|wx.LC_SINGLE_SEL)
        program_table.InsertColumn(0, "State")
        program_table.InsertColumn(1, "Read")
        program_table.InsertColumn(2, "To Write")
        program_table.InsertColumn(3, "Move")
        program_table.InsertColumn(4, "Next State")
        main_panel.Sizer.Add(program_table, 1, wx.EXPAND)
        #===End of main section===


        self.Bind(wx.EVT_CHOICE, self.change_program, program_chooser)
        self.Bind(wx.EVT_BUTTON, self.run_pause, run_pause_button)
        self.Bind(wx.EVT_BUTTON, self.reset, reset_button)

        #for simplicity, we defined all elements locally, without using self,
        #and then we export only those that are needed
        self.program_chooser = program_chooser
        self.speed_input = speed_input
        self.run_pause_button = run_pause_button
        self.reset_button = reset_button
        self.tapes_panel = tapes_panel
        self.program_table = program_table
        
        self.tape_panels = list()


    def add_tape(self, value):
        tape_row = make_layout_panel(self.tapes_panel, wx.HORIZONTAL)
        self.tapes_panel.Sizer.Add(tape_row, 0, wx.EXPAND|wx.ALL, BORDER)

        label = wx.StaticText(tape_row, label="Tape #%d: " % (len(self.tape_panels)+1)) 
        tape_row.Sizer.Add(label, 1, wx.ALIGN_CENTER_VERTICAL)

        tape_entry = wx.TextCtrl(tape_row, value=value, style=wx.TE_RICH2, size=(100,-1)) 
        tape_row.Sizer.Add(tape_entry, 0, wx.EXPAND)

        gen_button = wx.Button(tape_row, label="Generate", size=(70,-1))
        tape_row.Sizer.Add(gen_button, 0, wx.EXPAND)

        #the value generator is defined as a closure in order to facilitate access to the required variables
        def value_generator(event):
            random.seed()
            value = list()
            for i in range(random.randint(4, 10)):
                value.append(random.choice(self.program.input_values))
            tape_entry.SetValue(''.join(value))
        tape_row.Bind(wx.EVT_BUTTON, value_generator, gen_button)

        self.tape_panels.append(tape_entry)
        

    def update_tape(self, tape_nr, value, current_pos):
        tape_entry = self.tape_panels[tape_nr]
        tape_entry.SetValue("")
        tape_entry.SetValue(value)
        
        if current_pos != -1:
            tape_entry.SetStyle(current_pos, current_pos+1, CURRENT_POS_STYLE)


    def add_action(self, action):
        row = self.program_table.InsertStringItem(action['id'], action['state'])
        self.program_table.SetStringItem(row, 1, ','.join(action['read_values']))
        self.program_table.SetStringItem(row, 2, ','.join(action['write_values']))
        self.program_table.SetStringItem(row, 3, ','.join(action['directions']))
        self.program_table.SetStringItem(row, 4, action['next_state'])

    
    def select_action(self, action_id):
        for id in range(0, self.program_table.GetItemCount()):
            self.program_table.Select(id, False)

        if action_id != -1:  #-1 is used when no program is running
            self.program_table.Select(action_id, True)
            self.program_table.EnsureVisible(action_id)


    def change_program(self, event):
        program_id = event.GetSelection()
        self.program = programs.plist[program_id]

        #replace the existing tapes with the ones usd by this program...
        self.tapes_panel.Sizer.Clear(True)
        self.tape_panels = list()
        for tape in self.program.tapes:
            self.add_tape(''.join(tape))
        self.tapes_panel.Layout()

        #...and load the new program's table
        self.program_table.DeleteAllItems()
        for action in self.program.actions:
            self.add_action(action)
            
        self.run_pause_button.Enable(True)
    
    
    def run_pause(self, event):
        #if we already have a machine running, just pause or resume it
        if hasattr(self, 'tm') and self.tm.running:
            if self.tm.should_continue.is_set():  #if the TuringMachine isn't paused
                self.tm.should_continue.clear()  #pause its thread
                
                self.speed_input.Enable(True)
                self.run_pause_button.SetLabel("Resume")
            else:
                self.tm.speed = self.speed_input.GetValue()
                self.tm.should_continue.set()  #resume the machine's thread
                
                self.speed_input.Enable(False)
                self.run_pause_button.SetLabel("Pause")

                #focus on the table in order to better highlight the current action
                self.program_table.SetFocus()

        #otherwise start a new simulation
        else:
            self.program_chooser.Enable(False)
            self.speed_input.Enable(False)
            self.reset_button.Enable(True)
            self.tapes_panel.Enable(False)
            self.run_pause_button.SetLabel("Pause")
            self.program_table.SetFocus()

            #load the current UI values into the program's tapes
            for tape_nr, tape in enumerate(self.program.tapes):
                self.program.tapes[tape_nr] = list(self.tape_panels[tape_nr].GetValue())
                
            self.tm = tm.TuringMachine(self.program, self.speed_input.GetValue(), self.tm_listener)
            self.tm.start()


    """
    This method is called whenever the machine needs to be reset,
    not only by pressing the reset button, but also when the program ends or encounters an error.
    """
    def reset(self, event=None):
        if hasattr(self, 'tm'):
            self.tm.running = False

        self.program_chooser.Enable(True)
        self.speed_input.Enable(True)
        self.reset_button.Enable(False)
        self.tapes_panel.Enable(True)
        self.run_pause_button.SetLabel("Run")
        self.select_action(-1)
        
        for tape_nr, tape in enumerate(self.tm.program.tapes):
            self.update_tape(tape_nr, ''.join(tape), -1)


    """
    Wrapper, for calling the listener indirectly.
    We need to use wx.CallAfter when updating the GUI from another thread, else crashes might occur.
    """
    def tm_listener(self, tm, state):
        wx.CallAfter(self.window_updater, tm, state)


    """
    The actual listener, updates the tape values, positions and current program action,
    after each simulation step.
    """
    def window_updater(self, tm, state):
        if hasattr(tm, 'error'):
            wx.MessageBox(str(tm.error), 'Error', wx.OK|wx.ICON_ERROR)
            self.reset()
        else:
            if tm.running:
                for tape_nr, tape in enumerate(tm.program.tapes):
                    self.update_tape(tape_nr, ''.join(tape), tm.tapes_pos[tape_nr])
                
                if tm.current_action != None:
                    self.select_action(tm.current_action['id'])
            else:
                self.reset()



if __name__ == '__main__':
    app = wx.App()
    window = MainWindow()
    window.Centre()
    window.Show()
    app.MainLoop()
