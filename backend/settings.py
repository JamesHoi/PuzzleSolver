
class Settings():
    # 拼图数据变量
    src_img = None
    bg_img = None
    bg_img_cv2 = None
    edit_img = None
    pic_width = None
    pic_height = None
    pic_rows = None
    pic_columns = None
    piece_size = None
    pieces = None
    pieces_num = None
    pieces_index_list = []
    pieces_rect_list = []
    pieces_index_list_not_placed = []

    # 拼图视窗变量
    zoom_scale = 1
    init_scale = 0.6
    scale = init_scale
    opacity = 100
    bg_img_dir = None
    start_view_position = None
    view_position = (0,0)
    view_move_speed = 1.2
    grid_color = [0,255,0]

    # 操作动作变量
    is_open = False
    scale_changed = False
    read_dir = None
    save_dir = None
    refresh_puzzle_list = False
    is_shuffle = False

    # 算法变量
    gaps_solution = None
    brute_used = None
    is_brute = False

    # 快捷键变量
    is_pressing_middle = False


settings = Settings()
