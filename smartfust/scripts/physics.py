def mouse_in_box(mouse_pos, box_corners):
    x1, x2, y1, y2 = box_corners
    return x1 < mouse_pos[0] < x2 and y1 < mouse_pos[1] < y2

def mouse_in_rect(mouse_pos, rect):
    x, y, w, h = rect
    box = (x, x+w, y, y+h)
    return mouse_in_box(mouse_pos, box)
