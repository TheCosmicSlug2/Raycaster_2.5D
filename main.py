import pygame as pg
from commands.command_prompt import CommandPrompt
from smartfust.scripts.display import GLOBAL_QUIT
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
from entitites import EntityManager
from settings import FPS

bg_texture = sf.load_texture("rsc/raycaster.png", size=SCREEN_DIMS)

MENU_WIDGET = {
    "bg": sf.TextureWidget((0, 0), SCREEN_DIMS, bg_texture),
    0: sf.Label((220, 50), (350, 80), "Main Menu", sf.WHITE, text_height=50,
                colors=[sf.WHITE, (200, 200, 255), (150, 150, 255), (100, 100, 255)], borders=[3, 3, 3]),
    1: sf.Button((280, 460), (230, 60), text="Play", return_value="quit", textfg=sf.WHITE,text_height=20,
                 colors=[(200, 200, 200), (170, 170, 170), (130, 130, 130), (100, 100, 100)], borders=[3, 3, 3],
                 animation={"color": -6, "size": (3, 2)}),
    2: sf.Label((260, 170), (150, 30), "Maze width :", sf.WHITE, text_height=25, colors=[sf.TRANSPARENT]),
    3: sf.Slider((410, 175), (120, 30), _range=(5, 50), default_value=20, colors=[(70, 70, 70), sf.LIGHTBLUE],
                 bar_text_fg=sf.WHITE),
    4: sf.Label((235, 230), (200, 30), "Maze height :", sf.WHITE, text_height=25, colors=[sf.TRANSPARENT]),
    5: sf.Slider((415, 235), (120, 30), _range=(5, 50), default_value=20, colors=[(70, 70, 70), sf.LIGHTBLUE],
                 bar_text_fg=sf.WHITE),
    6: sf.Label((270, 330), (200, 30), "Spawn at furthest :", sf.WHITE, text_height=20, colors=[sf.TRANSPARENT]),
    7: sf.Checkbox((460, 330), (30, 30)),
    8: sf.Checkbox((460, 370), (30, 30)),
    9: sf.Label((270, 370), (200, 30), "çyka blyat mode :", sf.WHITE, text_height=20, colors=[sf.TRANSPARENT]),
    10: sf.Label((265, 280), (100, 30), "Solver :", sf.WHITE, text_height=25, colors=[sf.TRANSPARENT]),
    11: sf.List((375, 280), (150, 30), text_height=18, values=["Dead end fill", "RH-Follower", "LH-Follower"],
               colors=[(50, 50, 50), sf.LIGHTBLUE]),
    12: sf.Checkbox((460, 410), (30, 30)),
    13: sf.Label((270, 410), (200, 30), "pacman mode :", sf.WHITE, text_height=20, colors=[sf.TRANSPARENT])

}

game_widgets = {
    0: sf.Label((SCREEN_DIMS[0] - 100, 0), (100, 30), f"0 / 100", sf.LIGHTBLUE, colors=[sf.LIGHTBLUE, sf.BLACK], borders=[3, 3]),
    1: sf.Label((0, SCREEN_DIMS[1] - 50), (200, 50), "Solving", text_height=30, colors=[sf.BLACK, sf.LIGHTBLUE], borders=[3,3])
}



def game():
    pg.mouse.set_visible(True)
    display = sf.Display(dims=SCREEN_DIMS, title="Raycaster menu")
    display.add_widgets(MENU_WIDGET)
    display.mainloop()
    if display.output_code == GLOBAL_QUIT:
        return 0
    output = display.widget_values()
    del display
    blyat_mode = output[8]
    pacman_mode = output[12]
    MAZE_DIMENSIONS = (21, 21) if pacman_mode else (output[3], output[5])

    SOLVER = output[11]
    color = sf.BLACK if pacman_mode else None
    pg.mouse.set_visible(False)

    audio = Audio(blyat_mode)
    state_master = StateMaster()
    global_physics = Physics()

    level_master = LevelMaster(MAZE_DIMENSIONS, SOLVER)
    level_master.gen_map(nature="maze", pacman_mode=pacman_mode, color=color)
    renderer = Renderer(level_master, audio, state_master, pacman_mode)
    sfdisplay = sf.Display(renderer.SCREEN, widgets=game_widgets)


    sfdisplay.hide_all_widgets()
    if pacman_mode:
        sfdisplay.show_widget(0)

    player = Player(level_master=level_master, far_spawn=output[7], pacman_mode=pacman_mode)
    raycaster = Raycaster(player=player, level_master=level_master, renderer=renderer)
    raycaster.set_mode(pacman_mode)
    input_handler = InputHandler(level_master=level_master)
    command_prompt = CommandPrompt(level_master=level_master, raycaster=raycaster, player=player, renderer=renderer, audio=audio)
    entity_manager = EntityManager(player, level_master, blyat_mode, pacman_mode)

    goms_ate = 0
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
            return 0

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
        if "e" in pressed_keys:
            return 1
        if "r" in pressed_keys and state_master.check_solving_update_possible() and not pacman_mode:
            solving = not solving
            if solving:
                sfdisplay.show_widget(1)
                solver = Solver(player=player, level_master=level_master)
            else:
                sfdisplay.hide_widget(1)

        if solving:
            solver.update()
            nb_dots = (2 * renderer.tick // FPS) % 4
            sfdisplay.change_widget(1, f"Solving{"."*nb_dots}")
            if not solver.is_solving:
                solving = False
                sfdisplay.hide_widget(1)

        if "map" in pressed_keys:
            state_master.check_map_update_possible()
        if "cmd" in pressed_keys:
            command_mode = True
        if "esc" in pressed_keys:
            state_master.check_mouse_update_possible()
            pg.mouse.set_visible(state_master.mouse_visible)

        if command_mode:
            pg.mouse.set_visible(True)
            sfdisplay.hide_widget(0)
            command_prompt.mainloop()
            game_running = command_prompt.game_running
            command_mode = False
            pg.mouse.set_visible(False)
            if pacman_mode:
                sfdisplay.show_widget(0)
            continue

        entity_manager.update()
        if entity_manager.ate_gom:
            entity_manager.ate_gom = False
            goms_ate += 1
            sfdisplay.change_widget(0, f"{goms_ate} / {entity_manager.nb_goms}")
        
        if pacman_mode:
            if goms_ate == entity_manager.nb_goms:
                return 1


        if blyat_mode:
            level_master.change_walls_blyat_mode()

        # Raycast
        raycaster.raycast(map_shown=state_master.map_shown)

        # Check if player reached the exit
        if not pacman_mode:
            if level_master.check_player_reached_exit(player.pos):
                command_prompt.set_new_map("maze")

        # Rendering
        if state_master.map_shown:
            renderer.render_minimap_on_screen(player, raycaster, entity_manager.ennemies)
        else:
            dic = {}
            for idx, ray in enumerate(raycaster.rays_data):
                dic[idx] = raycaster.rays_data[(idx + 1) % len(raycaster.rays_data)]
            
            
            raycast_data = raycaster.rays_data + entity_manager.get_ennemies()
            # on attache les indices originaux
            indexed = list(enumerate(raycast_data))

            # tri
            indexed_sorted = sorted(indexed, key=lambda t: t[1][1][0][1], reverse=True)

            # reconstruction de la liste triée
            raycast_data_sorted = [x for _, x in indexed_sorted]

            # (optionnel) mapping inverse
            new_to_old = {new_idx: old_idx for new_idx, (old_idx, _) in enumerate(indexed_sorted)}

            renderer.render_3D_foreground(raycast_data_sorted, dic, new_to_old, player.pos, player.x_angle, len(entity_manager.ennemies))
            renderer.render_3D_foreground_on_screen(
                player.is_moving,
                player.y_angle
            )

        sfdisplay.update([])

        # Screen refresh / Update
        renderer.update()
        state_master.update()


    pg.quit()


def main():
    pg.init()
    global_running = True
    while global_running:
        global_running = game()
    pg.quit()

if __name__ == "__main__":
    main()
