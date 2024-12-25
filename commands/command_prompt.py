from cell import Cell
from utils import * 
from math import pi
from commands.text import *
from user_input.input_handler import InputHandler


class GameCommand:
    def __init__(self, command):
        self.name, raw_args = self.get_command_components(command)
        self.args = self.get_args_components(raw_args)
        self.nb_args = len(self.args)
    
    @staticmethod
    def get_command_components(command: str):
        command_list = command.split(" ")
        return command_list[0], command_list[1:]

    @staticmethod
    def get_args_components(args: list[str]):
        return [arg.split(",") if "," in arg else arg for arg in args]
    


class CommandPrompt:
    def __init__(self, level_master, raycaster, player, renderer):
        self.level_master = level_master
        self.raycaster = raycaster
        self.player = player
        self.renderer = renderer
        self.command = None
        self.execution_sucess = None
        self.exit = False

        self.output_lines = []
        self.input_line = ""
        self.game_running = True

    
    @staticmethod
    def get_instructions() -> str:
        text = f"{titlelize('Available Commands')} \n"
        for ligne in instructions.keys():
            text += f" - \"{ligne}\"\n"
        text += "\nType 'help [command name]' to show the help for a command"
        return text
    
    def show_instructions(self):
        self.add_line()
        for line in self.get_instructions().split("\n"):
            self.add_line(line)
        self.add_line()
    
    def input_command(self, command):
        self.command = GameCommand(command)
    
    def add_line(self, line: str=""):
        self.output_lines.append(line)
    
    def valid(self, command: GameCommand) -> bool:
        if not (command.name in instructions.keys()):
            self.add_line(f"Command \"{command.name}\" not recognised")
            return False
        if not (command.nb_args == instructions[command.name]):
            self.add_line(f"Wrong number of arguments (expected : {instructions[command.name]}, received : {command.nb_args})")
            return False
        return True
    
    def execute_command(self):
        self.exit = False
        self.execution_sucess = True
        if not self.valid(self.command):
            self.execution_sucess = False
            return 
        
        if self.command.name == "newmap":
            nature = self.command.args[0]
            self.set_new_map(nature)
        if self.command.name == "setwallpos":
            pos = self.string_array_to_int_array(self.command.args[0])
            rgb = self.string_array_to_int_array(self.command.args[1])
            self.setwallpos(pos, rgb)
        if self.command.name == "setwalldir":
            rgb = self.string_array_to_int_array(self.command.args[0])
            self.setwalldir(rgb)
        if self.command.name == "setwallsdir":
            rgb = self.string_array_to_int_array(self.command.args[0])
            self.setwallsdir(rgb)
        if self.command.name == "rmwallpos":
            pos = self.string_array_to_int_array(self.command.args[0])
            self.rmwallpos(pos)
        if self.command.name == "rmwalldir":
            self.rmwallsdir()
        if self.command.name == "rmwallsdir":
            self.rmwallsdir()
        if self.command.name == "setpos":
            pos = self.string_array_to_int_array(self.command.args[0])
            self.setpos(pos)
        if self.command.name == "setgridpos":
            grid_pos = self.string_array_to_int_array(self.command.args[0])
            self.setgridpos(grid_pos)
        if self.command.name == "setfov":
            fov = self.array_to_int(self.command.args[0])
            self.setfov(fov)
        if self.command.name == "setspeed":
            speed = self.get_int(self.command.args[0])
            self.setspeed(speed)
        if self.command.name == "setsolve":
            solve_method = self.command.args[0]
            self.setsolve(solve_method)
        if self.command.name == "setfps":
            fps = self.get_int(self.command.args[0])
            self.setfps(fps)
        if self.command.name == "setwallheight":
            wall_height = self.get_int(self.command.args[0])
            self.setwallheight(wall_height)
        if self.command.name == "setscreendims":
            screen_dims = self.string_array_to_int_array(self.command.args[0])
            self.setscreendims(screen_dims)
        if self.command.name == "clear":
            self.output_lines = []
            self.pretext()
        if self.command.name == "show":
            self.show_instructions()
        if self.command.name == "help":
            help_command = self.command.args[0]
            self.displayhelp(help_command)
        if self.command.name == "exit":
            self.exit = True
        if self.command.name == "setcmdcolor":
            rgb = self.string_array_to_int_array(self.command.args[0])
            self.setcmdcolor(rgb)
        if self.command.name == "setcmdfont":
            font = self.command.args[0]
            self.setcmdfont(font)
        if self.command.name == "getvar":
            var_name = self.command.args[0]
            self.getvar(var_name)
    
    
    @staticmethod
    def string_array_to_int_array(array):
        return [int(element) for element in array]
    
    def array_to_int(self, array):
        new_array = self.string_array_to_int_array(array)
        return new_array[0]
    
    def get_int(self, string: str):
        try:
            return int(string)
        except:
            self.add_line("Parameter is not numeric")
            


    def set_new_map(self, nature):
        self.level_master.gen_map(nature)
        self.player.set_grid_pos(self.level_master.player_starting_pos)
        self.renderer.render_minimap()

    def setwalldir(self, rgb):
        wall_grid_pos = self.raycaster.first_wall_dir()
        if wall_grid_pos == None:
            return
        self.level_master.map_data[wall_grid_pos[1]][wall_grid_pos[0]] = Cell(nature=1, color=rgb)
        self.renderer.render_minimap()

    def setwallpos(self, pos, rgb):
        self.level_master.map_data[pos[1]][pos[0]] = Cell(nature=1, color=rgb)
        self.renderer.render_minimap()

    def rmwallpos(self, pos):
        self.level_master.map_data[pos[1]][pos[0]] = Cell(nature=0)
        self.renderer.render_minimap()

    def addwalldir(self, rgb):
        grid_pos = self.raycaster.last_space_before_wall_front_player_coord()
        if grid_pos == None:
            return
        self.level_master.map_data[grid_pos[1]][grid_pos[0]] = Cell(nature=1, color=rgb)
        self.renderer.render_minimap()

    def setwallsdir(self, rgb):
        cell_pos = self.raycaster.every_cell_in_dir()
        for cell in cell_pos:
            self.level_master.map_data[cell[1]][cell[0]] = Cell(nature=1, color=rgb)
        self.renderer.render_minimap()

    def rmwalldir(self):
        wall_pos = self.raycaster.first_wall_dir()
        if wall_pos == None:
            return
        self.level_master.map_data[wall_pos[1]][wall_pos[0]] = Cell(nature=0)
        self.renderer.render_minimap()

    def rmwallsdir(self):
        cell_pos = self.raycaster.every_cell_in_dir()
        for cell in cell_pos:
            self.level_master.map_data[cell[1]][cell[0]] = Cell(nature=0)
        self.renderer.render_minimap()

    def setpos(self, pos):
        self.player.set_pos(pos)

    def setgridpos(self, grid_pos):
        self.player.set_grid_pos(grid_pos)

    def setfov(self, fov):
        self.player.fov = fov * (pi / 180)

    def setspeed(self, speed):
        self.player.speed = speed

    def setsolve(self, method: str):
        self.level_master.solver_name = method

    def setfps(self, fps):
        print(fps)
        self.renderer.fps = fps

    def setwallheight(self, height):
        self.level_master.normalised_wall_height = height

    def setscreendims(self, dims):
        player_grid = self.player.get_grid_pos()
        self.level_master.update_screen_dims(dims)
        self.player.set_grid_pos(player_grid)
        self.renderer.set_dims(dims)
        self.renderer.render_3D_background()
        self.renderer.render_minimap()
    
    def displayhelp(self, help_command: list):
        # Get the command data
        command_name = help_command
        if command_name not in help_list.keys():
            self.add_line(f"Command \"{command_name}\" not recognised")
            self.execution_sucess = False
            return
        command_data = help_list[command_name]
        description = command_data["description"]
        params = command_data["param"]
        exemples = command_data["exemple"]
        
        self.add_line()
        for line in titlelize('Help').split("\n"):
            self.add_line(line)
        self.add_line()
        self.add_line(f"Command name : '{command_name}'")
        self.add_line()
        self.add_line(f"Description : {description}")
        self.add_line()
        self.add_line(f"Parameters :")
        for param in params:
            self.add_line(f" - {param}")
        self.add_line()
        self.add_line("Exemples :")
        for exemple in exemples:
            self.add_line(f" - {exemple}")
        self.add_line()
    
    def setcmdcolor(self, color):
        self.renderer.cmdcolor = color
    
    def setcmdfont(self, font):
        self.renderer.setcmdfont(font)
    
    def getvar(self, var_name):
        # Créer un dictionnaire des variables qui nous intéressent
        supported_vars = {
            "fps": self.renderer.fps,
            "fov": self.player.fov,
            "pos": {"x": self.player.posx, "y": self.player.posy},
            "speed": self.player.speed,
            "screendims": self.level_master.screen_dims,
            "solve": self.level_master.solve_method,
            "map_nature": self.level_master.map_nature,
            "wallheight": self.level_master.normalised_wall_height,
            "cmdcolor": self.renderer.cmdcolor,
            "cmdfont": self.renderer.cmdfontname
        }

        if var_name not in supported_vars.keys():
            self.add_line(f"Variable \"{var_name}\" not found")
            return
        
        var_value = supported_vars[var_name]
        if isinstance(var_value, dict):
            for key, value in var_value.items():
                self.add_line(f"Value of \"{key}\" : {value} (type : {type(value).__name__})")
            return
        self.add_line(f"Value of \"{var_name}\" : {var_value} (type : {type(var_value).__name__})")
        

    def pretext(self):
        self.add_line()
        self.add_line("Raycaster Terminal")
        self.add_line()
        self.add_line(" 'up' and 'down' arrows to navigate")
        self.add_line(" Type 'show' to show the available commands")
        self.add_line()

    def mainloop(self):
        self.exit = False
        self.output_lines = []
        self.input_line = ""
        ask_command = False
        scroll_up = 1
        last_key = ""

        self.pretext()
        while not self.exit:

            # Get user input
            input = InputHandler.get_cmd_event(last_key)
            if input == "exit":
                self.exit = True
                self.game_running = False
            elif input == "return":
                ask_command = True
            elif input == "backspace":
                self.input_line = self.input_line[:-1]
                scroll_up = -1
            elif input == "up":
                scroll_up = min(scroll_up + 1, abs((len(self.output_lines) - self.renderer.MAX_LINES)))
            elif input == "down":
                scroll_up = max(scroll_up - 1, -1)
            elif input == "":
                pass
            else:
                self.input_line += input
                scroll_up = -1
            
            if ask_command:
                self.input_command(self.input_line)
                self.output_lines.append(f" > {self.input_line}")
                self.execute_command()
                ask_command = False
                self.input_line = ""


            self.renderer.draw_terminal(self.output_lines, self.input_line, scroll_up)
            self.renderer.update()



            

