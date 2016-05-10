"""
File: tm.py
The main turing module/library.
It defines 2 classes TuringProgram and the TuringMachine itself.
"""

"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""

import threading
import time


#used for the TuringMachine's listener, in order to specify the current step in the simulation
STEP_READ = 0
STEP_WRITE = 1
STEP_MOVE = 2
STEP_STATE = 3


"""
This class is used to help define a Turing Machine program
and its associated data (like alphabet, special states and symbols)
Examples of turing programs can be viewed in programs.py
"""
class TuringProgram:
    
    """
    The constructor method
    [name] = the name of the program, used for the GUI
    """
    def __init__(self, name):
        self.name = name

        #Default values
        self.input_values = "01"     #a string, where each character represents a value. This is 
                                     #currently only used for the GUI's tape value generator.
        self.symbol_blank = '_'      #a single character/symbol. Used when extending the tapes.
        self.dir_left = '<'          #symbol for moving the pointer left
        self.dir_right = '>'         #symbol for moving the pointer right
        self.dir_none = '-'          #symbol for not chaning the position
        self.state_initial = 'init'  #the state set when the machine starts
        self.state_final = 'halt'    #the state in which the machine stops running

        self.tapes = list()          #The list of tapes used by this program.
                                     #Each tape is a list of characters (not a string)
        self.actions = list()        #The program itself, as a list of actions (see the
                                     #add_action method for the structure of an action)


    """
    The alphabet of a turing machine, in other words the list of tape valeus it accepts.
    Note: Our code does not currently enforce values to be part of the alphabet.
    """
    def set_alphabet(self, input_values, blank):
        self.input_values = input_values
        self.symbol_blank = blank


    """
    Set the symbols used for the move instructions.
    """
    def set_directions(self, left, right, none):
        self.dir_left = left
        self.dir_right = right
        self.dir_none = none


    """
    Shortcut function to set both initial and final states
    """
    def set_limit_states(self, initial, final):
        self.state_initial = initial
        self.state_final = final


    """
    Shortcut function for adding tapes.
    """
    def set_tapes(self, *arg):
        self.tapes = list(arg)


    """
    Add a single action to the program.
    If the machine's current state is the one specified by [state], and the value it read from 
    each tape its corresponding value from [read_values], it will replace those values with
    the ones from [write_values], then move the tapes according to the [directions]
    and finally change the machine's state to [next_state]
    """
    def add_action(self, state, read_values, write_values, directions, next_state):
        self.actions.append(dict(id=len(self.actions),
                                 state=state,
                                 read_values=read_values,
                                 write_values=write_values,
                                 directions=directions,
                                 next_state=next_state))


    """
    A shortcut to set all actions at once, using a string table.
    (See programs.py for examples)
    """
    def set_actions(self, table):
        self.actions = list()
        for line in table.split('\n'):
            columns = line.split()
            
            state = columns[0]
            
            #if we have multiple tapes, these columns will have multiple values, separated by commas
            read_values = columns[1].split(',')
            write_values = columns[2].split(',')
            directions = columns[3].split(',')
            
            next_state = columns[4]
            
            self.add_action(state, read_values, write_values, directions, next_state)


    """
    Used by the TuringMachine, to search for an action in the list,
    based on its current [state] and [read_values]
    """
    def get_action(self, state, read_values):
        for action_id, action in enumerate(self.actions):
            if action['state'] == state and action['read_values'] == read_values:
                return action
        return None



"""
The Turing machine simulator class
It's threaded, so it can be displayed in a GUI and multiple simulations can be run at the same time
All methods are for internal use, to use the machine you just need to specify the required values
in its constructor, and then call start()
"""
class TuringMachine(threading.Thread):

    """
    The constructor method
    [program] = the TuringProgram that will be used for this machine
    [speed] = the simulation's speed (in number of steps per second)/ 
              If it's -1, the simulation will be run in realtime
    [listener] = a function that will be called after every step, used to show the progress
                 of the simulation. It will receive the following arguments:
                 [tm] = the turing machine that called the function
                 [step] = a number which specifies the last step type performed by the machine 
                 (STEP_READ, STEP_WRITE, STEP_MOVE, or STEP_STATE for state changes)
    """
    def __init__(self, program=None, speed=4, listener=None):
        threading.Thread.__init__(self)
        
        self.program = program
        self.speed = speed
        self.listener = listener
        
        self.should_continue = threading.Event()  #allows us to pause the simulation.
                                                  #clear() to pause and set() to resume


    """
    The main method of the machine, that handles the whole simulation
    """
    def run(self):
        if self.program == None: raise RuntimeError("No program specified")

        #prepare a list to store the current positions for each tape,
        #and then fill it with the starting position, 0
        self.tapes_pos = list()                   
        for i in range(len(self.program.tapes)):
            self.tapes_pos.append(0)

        #make sure all tapes have at least one value, to prevent issues when reading/writing
        for tape in self.program.tapes:
            if len(tape) == 0:
                tape.append(self.program.symbol_blank)

        self.current_state = self.program.state_initial
        self.current_action = None
        self.running = True
        self.should_continue.set()  #start in running (non-paused) state


        #The main loop. It runs a standard Turing cycle (read, write, move, change state),
        #until it encounters the final/halt state of the program
        while self.running:
            self.should_continue.wait()  #if the machine is paused (by should_continue.clear()),
                                         #this will block until it resumes (should_continue.set())
            self.read_step()
            self.post_step(STEP_READ)

            self.should_continue.wait()
            self.write_step()
            self.post_step(STEP_WRITE)

            self.should_continue.wait()
            self.move_step()
            self.post_step(STEP_MOVE)

            self.should_continue.wait()
            self.state_change_step()
            self.post_step(STEP_STATE)


    """
    Run after each simulation step.
    It calls the listener to notify it of the changes,
    raises an error, if one was encountered in the last step,
    and then sleeps a bit, so the user can follow the simulation
    """
    def post_step(self, step_type):
        if self.listener != None:
            self.listener(self, step_type)
        
        #we set errors using self.error instead of raising them directly when we enconter them,
        #in order to allow the listener to handle the error itself
        #because otherwise it couldn't know about an error raised in another thread)
        if hasattr(self, 'error'):
            raise RuntimeError(self.error)
    
        if self.speed != -1:
            time.sleep(1/float(self.speed))


    """
    In the read step, the machine reads the current value from each tape,
    and then uses these values and the machine's current state to search for
    a corresponding action in the program's list
    """
    def read_step(self):
        read_values = []
        for tape_nr, tape in enumerate(self.program.tapes): 
            read_values.append(tape[self.tapes_pos[tape_nr]]) 
            
        self.current_action = self.program.get_action(self.current_state, read_values)
        if self.current_action == None:
            self.error = "No action defined for state '%(state)s' and values (%(read)s)" \
                         % dict(state=self.current_state, read=','.join(read_values))
            self.running = False

    
    """
    Writes new values on each tape, as dictated by the program's current action
    """
    def write_step(self):
        for tape_nr, tape in enumerate(self.program.tapes):
              tape[self.tapes_pos[tape_nr]] = self.current_action['write_values'][tape_nr]


    """
    Moves each tape according to the program's current action
    """
    def move_step(self):
        for tape_nr, tape in enumerate(self.program.tapes):
            direction = self.current_action['directions'][tape_nr]
            if direction == self.program.dir_left:
                if self.tapes_pos[tape_nr] <= 0:
                    #if we reached the left edge, insert a new blank value...
                    tape.insert(0, self.program.symbol_blank)
                    #...and make sure the position is at the new 0 edge
                    self.tapes_pos[tape_nr] = 0                
                else: 
                    self.tapes_pos[tape_nr] -= 1
            elif direction == self.program.dir_right: 
                self.tapes_pos[tape_nr] += 1
                if self.tapes_pos[tape_nr] >= len(tape):
                    #if we reached the right edge, insert a new value
                    tape.append(self.program.symbol_blank)
            #else: the direction is assumed to be [dir_none]

    
    """
    Changes the machine's state to the one specified by the current action's [next_state]
    """
    def state_change_step(self):
        self.current_state = self.current_action['next_state']
        if self.current_state == self.program.state_final:
            self.running = False



#Test Code
if __name__ == "__main__":
    tape = "0100101"
    print("Initial value: "+tape)
    
    inversion = TuringProgram("Inversion")
    inversion.set_tapes(list(tape))
    inversion.set_actions("""init 0 1 > init
                             init 1 0 > init
                             init _ _ - halt""")

    def print_tapes(tm, step_type):
        if step_type == STEP_READ:
            tcopy = list(tm.program.tapes[0])
            pos = tm.tapes_pos[0]
            tcopy.insert(pos, '[')
            tcopy.insert(pos+2, ']')
            print(''.join(tcopy))
        elif step_type == STEP_STATE and not tm.running:
            print("Final value (trimmed): " + (''.join(tm.program.tapes[0])).strip('_'))
            
    machine = TuringMachine(inversion, listener=print_tapes)
    machine.start()
    machine.join()
