

instructions = {
    "newmap": 1,
    "setwallpos": 2,
    'setwalldir': 1,
    "addwalldir": 1,
    "setwallsdir": 1,
    "rmwallpos": 1,
    "rmwalldir": 0,
    "rmwallsdir": 0,
    "clear": 0,
    "exit": 0,
    "get": 1,
    "set": 2,
    "help": 1,
    "show": 0,
}

aliases = {
    "cls": "clear",
    "q": "exit"
}

help_list = {
    "newmap": {
        "description": "Creates a new map of specified nature",
        "param": ["[nature] (str) : 'empty'/'maze'"],
        "exemple": ["'newmap maze'", "'newmap empty'"]
    },
    "setwallpos": {
        "description": "Creates or change a wall of color (r,g,b) at the designated (x,y) coordinates",
        "param": [
            "[x] (int) : idx of the line",
            "[y] (int) : idx of the column",
            "[r] (int) : red value",
            "[g] (int) : green value",
            "[b] (int) : blue value"
            ],
        "exemple": ["'setwallpos 3,5 255,255,255'    # create a white wall at line 3, column 5"]
    },
    "setwalldir": {
        "description": "Change the first wall in the player direction to color (r,g,b)",
        "param": [
            "[r] (int) : red value",
            "[g] (int) : green value",
            "[b] (int) : blue value"
            ],
        "exemple": ["'setwall dir 255,0,0'      # Change the first wall in direction to red"]
    },
    "addwalldir": {
        "description": "Add a wall of color (r,g,b) at the furthest empty cell in player direction",
        "param": [
            "[r] (int) : red value",
            "[g] (int) : green value",
            "[b] (int) : blue value"
            ],
        "exemple": ["'addwalldir 0,255,0'        # Add a green wall in direction "]
    },
    "rmwallpos": {
        "description": "Remove a wall at the designated (x,y) coordinates",
        "param": [
            "[x] (int) : idx of the line",
            "[y] (int) : idx of the column",
            ],
        "exemple": ["'rmwallpos 10,4'     # Remove the wall at line 10, column 4"]
    },
    "rmwalldir": {
        "description": "Remove the first wall in player direction",
        "param": ["No parameters"],
        "exemple": ["'rmwalldir'     # Will remove the first wall in direction"]
    },
    "rmwallsdir": {
        "description": "Remove all the walls in player direction",
        "param": ["No parameters"],
        "exemple": ["'rmwallsdir'     # Will remove every wall in direction"]
    },
    "clear": {
        "description": "Clear the command prompt",
        "param": ["[No Parameters]"],
        "exemple": ["'clear'    # Will remove all the text in the cmd"]
    },
    "show": {
        "description": "Show the list of all the available commands",
        "param": ["[No Parameters]"],
        "exemple": ["'show'    # Will show the list of all the available commands"]
    },
    "help": {
        "description": "Display help/instructions for the given command",
        "param": [
            "[instruction] (str) : [any command name]",
            ],
        "exemple": ["'help setfov'    # Display the help for the 'setfov' command"]
    },
    "exit": {
        "description": "Exit command mode",
        "param": ["[No Parameters]"],
        "exemple": ["'exit'    # Exit command mode"]
    },
    "get": {
        "description": "Get the current value of for the requested variable",
        "param": [
            "[var_name] (str) : name of the variable",
            "The supported names are in the following list :",
            "\"fps\"",
            "\"fov\"",
            "\"pos\"",
            "\"speed\"",
            "\"screendims\"",
            "\"solve\"",
            "\"map_nature\"",
            "\"wallheight\"",
            "\"cmdcolor\"",
            "\"cmdfont\"",
            ],
        "exemple": ["'getvar fps'    # Will return the current fps value (default : 30)"]
    },
    "set": {
        "description": "Set the value for a variable",
        "param": [
            "[var_name] (str) : name of the variable",
            "The supported names are in the following list :",
            "\"fps\"",
            "\"fov\"",
            "\"pos\"",
            "\"speed\"",
            "\"screendims\"",
            "\"solve\"",
            "\"wallheight\"",
            "\"cmdcolor\"",
            "\"cmdfont\"",
            ],
        "exemple": ["'qsetvar cmdfont Arial'    # Set the font in the cmd to arial"]
    },

}




"""
Liste des commandes :

# Map
newmap -> Nouvelle map et nouvelle position du joueur
setwallpos x,y r,g,b -> Ajoute un mur aux coordonnées
setwalldir -> Change un mur dans la direction
addwalldir r,g,b -> Ajoute un mur dans la direction du joueur
setwallsdir r,g,b -> Remplace toutes les cellules dans la direction du joueur par des murs
rmwallpos x,y -> Supprime un mur aux coordonnées
rmwalldir -> Enlève le premier mur dans la direction
rmwallsdir -> Enlève tous les murs dans la direction

# Player
setpos x,y -> Met à jour la position absolue du joueur
setgridpos x,y -> Met à jour la position dans la grille du joueur
setfov n -> Met à jour la fov du joueur
setspeed n -> Met à jour la vitesse du joueur
setsolve n -> Met à jour la manière de résoudre le labyrinthe

# Renderer
setfps -> Met à jour les FPS
setwallheight -> Met à jour la const wall height
setscreendims width,height -> Met à jour les dimensions de l'écran

"""
