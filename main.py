import pygame as pg
from commands.command_prompt import CommandPrompt
from user_input.input_handler import InputHandler
from maze.solver import Solver
from physics_engine.physics import Physics
from level.level_master import LevelMaster
from settings import SCREEN_DIMS
from state_master import StateMaster
from player import Player
from renderer import Renderer
from level.raycaster import Raycaster
import smartfust as sf
from audio import Audio
from random import randbytes

bg_texture = sf.load_texture("rsc/raycaster.png", size=SCREEN_DIMS)

MENU_WIDGET = {
    "bg": sf.TextureWidget((0, 0), SCREEN_DIMS, bg_texture),
    0: sf.Label((220, 50), (350, 80), "Main Menu", sf.WHITE, text_height=50,
                colors=[sf.WHITE, (200, 200, 255), (150, 150, 255), (100, 100, 255)], borders=[3, 3, 3]),
    1: sf.Button((280, 400), (230, 60), text="Play", return_value="quit", textfg=sf.WHITE,text_height=20,
                 colors=[(200, 200, 200), (170, 170, 170), (130, 130, 130), (100, 100, 100)], borders=[3, 3, 3],
                 animation={"color": -6, "size": (3, 2)}),
    2: sf.Label((260, 170), (150, 30), "Maze width :", sf.WHITE, text_height=25, colors=[sf.TRANSPARENT]),
    3: sf.Slider((410, 175), (120, 30), range=(5, 50), default_value=20, colors=[(70, 70, 70), sf.LIGHTBLUE],
                 bar_text_fg=sf.WHITE),
    4: sf.Label((235, 230), (200, 30), "Maze height :", sf.WHITE, text_height=25, colors=[sf.TRANSPARENT]),
    5: sf.Slider((415, 235), (120, 30), range=(5, 50), default_value=20, colors=[(70, 70, 70), sf.LIGHTBLUE],
                 bar_text_fg=sf.WHITE),
    6: sf.Label((270, 330), (200, 30), "Spawn at furthest :", sf.WHITE, text_height=20, colors=[sf.TRANSPARENT]),
    7: sf.Checkbox((460, 330), (30, 30)),
    8: sf.Label((265, 280), (100, 30), "Solver :", sf.WHITE, text_height=25, colors=[sf.TRANSPARENT]),
    9: sf.List((375, 280), (150, 30), text_height=18, values=["Dead end fill", "RH-Follower", "LH-Follower"],
               colors=[(50, 50, 50), sf.LIGHTBLUE]),

}


#from profilehooks import profile
#@profile(stdout=False, filename='basic.prof')  # <== Profiling


def main():

    pg.init()
    display = sf.Display(dims=SCREEN_DIMS, title="Raycaster menu")
    display.add_widgets(MENU_WIDGET)
    display.mainloop()
    output = display.get_output()
    if output == sf.GLOBAL_QUIT:
        return
    MAZE_DIMENSIONS = (output[3], output[5])
    SOLVER = output[9]
    pg.mouse.set_visible(False)

    audio = Audio()
    state_master = StateMaster()
    global_physics = Physics()

    level_master = LevelMaster(MAZE_DIMENSIONS, SOLVER)
    renderer = Renderer(level_master, audio, state_master)
    player = Player(level_master=level_master, far_spawn=output[7])
    raycaster = Raycaster(player=player, level_master=level_master, renderer=renderer)
    input_handler = InputHandler(level_master=level_master)
    command_prompt = CommandPrompt(level_master=level_master, raycaster=raycaster, player=player, renderer=renderer)
    

    game_running = True
    solving = False
    command_mode = False

    while game_running:

        # Update player x and y angle using mouse position since last frame
        player.reset_vars()
        if not state_master.mouse_visible:
            delta_mousex, delta_mousey = input_handler.get_mouse_movement_since_last_frame()
        player.update_x_angle(delta_mousex)
        player.update_y_angle(delta_mousey)

        # Get if game is exited
        mouse_event = input_handler.get_mouse_event()
        if mouse_event == "quit_game":
            game_running = False

        # Key press handling
        pressed_keys = input_handler.get_keyboard_events()

        if "haut" in pressed_keys and not solving:
            player.move(global_physics.forward)
        if "bas" in pressed_keys and not solving:
            player.move(global_physics.backward)
        if "gauche" in pressed_keys and not solving:
            player.move(global_physics.left)
        if "droite" in pressed_keys and not solving:
            player.move(global_physics.right)
        
        if player.hit_nature == 3: # Glass:
            if not state_master.knocked_glass:
                audio.play_rdm(glass=True)
                state_master.knocked_glass = True
        else:
            state_master.knocked_glass = False
                
        if mouse_event == "rightclick":
            command_prompt.addwalldir(randbytes(3))
        if mouse_event == "leftclick":
            command_prompt.rmwalldir()
        if "r" in pressed_keys and state_master.check_solving_update_possible():
            solving = not solving
            if solving:
                solver = Solver(player=player, level_master=level_master)

        if solving:
            solver.update()
            if not solver.is_solving:
                solving = False

        if "map" in pressed_keys:
            state_master.check_map_update_possible()
        if "cmd" in pressed_keys:
            command_mode = True
        if "esc" in pressed_keys:
            state_master.check_mouse_update_possible()
            pg.mouse.set_visible(state_master.mouse_visible)

        if command_mode:
            pg.mouse.set_visible(True)
            command_prompt.mainloop()
            game_running = command_prompt.game_running
            command_mode = False
            pg.mouse.set_visible(False)
            continue


        # Raycast
        raycaster.raycast(map_shown=state_master.map_shown)

        # Check if player reached the exit
        if level_master.check_player_reached_exit(player.pos):
            command_prompt.set_new_map("maze")

        # Rendering
        if state_master.map_shown:
            renderer.render_minimap_on_screen(player, raycaster)
        else:
            renderer.render_3D_foreground(raycaster.rays_data, player.pos, player.x_angle)
            renderer.render_3D_foreground_on_screen(
                player.is_moving,
                player.y_angle
            )

        # Screen refresh / Update
        renderer.update()
        state_master.update()


    pg.quit()


if __name__ == "__main__":
    main()
