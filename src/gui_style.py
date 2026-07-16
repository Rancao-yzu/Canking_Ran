"""
Canking_Ran 现代圆角橙色调样式表
"""
import tkinter as tk
from tkinter import ttk

# ==================== 调色板 ====================

# 主色 - 橙色系 (更现代、更柔和)
BLUE       = "#FF7A1A"    # 主色 (活力橙)
BLUE_LIGHT = "#FF9F4D"    # 主色浅色 (明亮橙)
BLUE_DARK  = "#E06000"    # 主色深色 (按压橙)
GREEN      = "#27AE60"    # 成功/运行
GREEN_LIGHT = "#2ECC71"
ORANGE     = "#F39C12"    # 警告
RED        = "#E74C3C"    # 错误/停止
RED_LIGHT  = "#EC7063"

# 背景 (浅色)
BG_BASE    = "#EEF1F5"    # 最底层背景
BG_CARD    = "#FFFFFF"    # 卡片/面板背景 (纯白更干净)
BG_INPUT   = "#FFFFFF"    # 输入框背景
BG_HOVER   = "#FFF0E0"    # 悬停 (暖浅橙)
BG_ACTIVE  = "#FFE3C0"    # 按下 (暖中橙)
BG_SECONDARY = "#F7F8FA"  # 次级背景 (微灰)

# 文字
TEXT_PRIMARY   = "#1A1A2E"
TEXT_SECONDARY = "#8E8E9A"
TEXT_DISABLED  = "#C4C4CC"
TEXT_HINT      = "#B0B0BB"

# 边框
BORDER       = "#DDDEE1"
BORDER_LIGHT = "#EBECEE"
BORDER_FOCUS = "#FF7A1A"

# 滚动条
SCROLL_TROUGH  = "#F2F3F5"
SCROLL_SLIDER  = "#C8C9CD"
SCROLL_HOVER   = "#A8A9AD"

# 表格表头
HEADER_BG   = "#FFF5EC"
HEADER_TEXT = "#FF7A1A"

# 按钮颜色细化
BTN_PRIMARY_BG      = "#FF7A1A"
BTN_PRIMARY_HOVER   = "#FF8C36"
BTN_PRIMARY_ACTIVE  = "#E06800"
BTN_PRIMARY_TEXT    = "#FFFFFF"

BTN_SECONDARY_BG    = "#FFF0E0"
BTN_SECONDARY_HOVER = "#FFE3C0"
BTN_SECONDARY_ACTIVE = "#FFD6A8"
BTN_SECONDARY_TEXT  = "#FF7A1A"
BTN_SECONDARY_BORDER = "#FFD6A8"

BTN_DANGER_BG       = "#FFF0F0"
BTN_DANGER_HOVER    = "#FFE0E0"
BTN_DANGER_ACTIVE   = "#FFD0D0"
BTN_DANGER_TEXT     = "#E74C3C"
BTN_DANGER_BORDER   = "#FFC8C8"

BTN_DEFAULT_BG      = "#FFFFFF"
BTN_DEFAULT_HOVER   = "#F7F8FA"
BTN_DEFAULT_ACTIVE  = "#EEF0F4"
BTN_DEFAULT_TEXT    = "#1A1A2E"
BTN_DEFAULT_BORDER  = "#DDDEE1"

BTN_SUCCESS_BG      = "#E6F9F0"
BTN_SUCCESS_HOVER   = "#D0F4E0"
BTN_SUCCESS_ACTIVE  = "#B8EFD0"
BTN_SUCCESS_TEXT    = "#27AE60"
BTN_SUCCESS_BORDER  = "#B8EFD0"

# ==================== 圆角配置 ====================
# Tkinter ttk 不支持原生圆角，通过 padding/border/reliief 模拟
# 对原生 tk widget (Canvas/Listbox/Text) 用 highlightthickness=0 平滑边缘
BORDER_RADIUS_SM  = 4    # 小圆角 (输入框/标签)
BORDER_RADIUS_MD  = 6    # 中圆角 (按钮/卡片)
BORDER_RADIUS_LG  = 10   # 大圆角 (面板)

# ==================== 字体 ====================

FONT_MONO    = ("Consolas", 10)
FONT_BODY    = ("Microsoft YaHei", 9)
FONT_SMALL   = ("Microsoft YaHei", 9)
FONT_HEADING = ("Microsoft YaHei", 13, "bold")
FONT_TREEVIEW = ("Consolas", 10)
FONT_SECTION = ("Microsoft YaHei", 10, "bold")

PAD_X = 8
PAD_Y = 6
TREE_ROW_HEIGHT = 28

# ==================== 主题应用 ====================

def apply_style(root: tk.Tk):
    style = ttk.Style(root)

    if "clam" in style.theme_names():
        style.theme_use("clam")

    # --- 框架 ---
    style.configure("TFrame", background=BG_CARD)

    # --- Labelframe: 精致卡片 ---
    style.configure("Card.TLabelframe",
                    background=BG_CARD,
                    bordercolor=BORDER_LIGHT,
                    relief="solid",
                    borderwidth=1)
    style.configure("Card.TLabelframe.Label",
                    background=BG_CARD,
                    foreground=BLUE,
                    font=("Microsoft YaHei", 10, "bold"),
                    padding=(10, 6))

    # --- 基础按钮 (TButton) ---
    style.configure("TButton",
                    background=BTN_DEFAULT_BG,
                    foreground=BTN_DEFAULT_TEXT,
                    borderwidth=1,
                    bordercolor=BTN_DEFAULT_BORDER,
                    focusthickness=0,
                    padding=(16, 7),
                    font=FONT_BODY,
                    relief="flat")
    style.map("TButton",
              background=[("active", BTN_DEFAULT_HOVER),
                          ("pressed", BTN_DEFAULT_ACTIVE),
                          ("disabled", BTN_DEFAULT_BG)],
              foreground=[("disabled", TEXT_DISABLED)],
              bordercolor=[("active", BTN_PRIMARY_BG),
                           ("pressed", BTN_PRIMARY_BG),
                           ("disabled", BORDER_LIGHT)])

    # 主色按钮 (橙色 - 实心填充)
    style.configure("Primary.TButton",
                    background=BTN_PRIMARY_BG,
                    foreground=BTN_PRIMARY_TEXT,
                    borderwidth=0,
                    bordercolor=BTN_PRIMARY_BG,
                    focusthickness=0,
                    padding=(18, 8),
                    font=("Microsoft YaHei", 9, "bold"),
                    relief="flat")
    style.map("Primary.TButton",
              background=[("active", BTN_PRIMARY_HOVER),
                          ("pressed", BTN_PRIMARY_ACTIVE),
                          ("disabled", BORDER_LIGHT)],
              foreground=[("disabled", TEXT_DISABLED)],
              bordercolor=[("disabled", BORDER_LIGHT)])

    # 次要按钮 (浅橙描边)
    style.configure("Secondary.TButton",
                    background=BTN_SECONDARY_BG,
                    foreground=BTN_SECONDARY_TEXT,
                    borderwidth=1,
                    bordercolor=BTN_SECONDARY_BORDER,
                    focusthickness=0,
                    padding=(16, 7),
                    font=FONT_BODY,
                    relief="flat")
    style.map("Secondary.TButton",
              background=[("active", BTN_SECONDARY_HOVER),
                          ("pressed", BTN_SECONDARY_ACTIVE),
                          ("disabled", BG_CARD)],
              foreground=[("disabled", TEXT_DISABLED)],
              bordercolor=[("active", BTN_PRIMARY_BG),
                           ("disabled", BORDER_LIGHT)])

    # 淡橙色按钮 (保持兼容别名)
    style.configure("LightOrange.TButton",
                    background=BTN_SECONDARY_BG,
                    foreground=BTN_SECONDARY_TEXT,
                    borderwidth=1,
                    bordercolor=BTN_SECONDARY_BORDER,
                    focusthickness=0,
                    padding=(16, 7),
                    font=FONT_BODY,
                    relief="flat")
    style.map("LightOrange.TButton",
              background=[("active", BTN_SECONDARY_HOVER),
                          ("pressed", BTN_SECONDARY_ACTIVE),
                          ("disabled", BG_CARD)],
              foreground=[("disabled", TEXT_DISABLED)],
              bordercolor=[("active", BTN_PRIMARY_BG),
                           ("disabled", BORDER_LIGHT)])

    # 危险按钮 (红色描边)
    style.configure("Danger.TButton",
                    background=BTN_DANGER_BG,
                    foreground=BTN_DANGER_TEXT,
                    borderwidth=1,
                    bordercolor=BTN_DANGER_BORDER,
                    focusthickness=0,
                    padding=(16, 7),
                    font=FONT_BODY,
                    relief="flat")
    style.map("Danger.TButton",
              background=[("active", BTN_DANGER_HOVER),
                          ("pressed", BTN_DANGER_ACTIVE),
                          ("disabled", BG_CARD)],
              foreground=[("disabled", TEXT_DISABLED)],
              bordercolor=[("active", RED),
                           ("pressed", RED),
                           ("disabled", BORDER_LIGHT)])

    # 成功按钮 (绿色描边)
    style.configure("Success.TButton",
                    background=BTN_SUCCESS_BG,
                    foreground=BTN_SUCCESS_TEXT,
                    borderwidth=1,
                    bordercolor=BTN_SUCCESS_BORDER,
                    focusthickness=0,
                    padding=(16, 7),
                    font=FONT_BODY,
                    relief="flat")
    style.map("Success.TButton",
              background=[("active", BTN_SUCCESS_HOVER),
                          ("pressed", BTN_SUCCESS_ACTIVE),
                          ("disabled", BG_CARD)],
              foreground=[("disabled", TEXT_DISABLED)],
              bordercolor=[("active", GREEN),
                           ("pressed", GREEN),
                           ("disabled", BORDER_LIGHT)])

    # --- 标签 ---
    style.configure("TLabel",
                    background=BG_CARD,
                    foreground=TEXT_PRIMARY,
                    font=FONT_BODY)

    style.configure("Secondary.TLabel",
                    background=BG_CARD,
                    foreground=TEXT_SECONDARY,
                    font=FONT_SMALL)

    style.configure("Heading.TLabel",
                    background=BG_BASE,
                    foreground=BLUE,
                    font=("Microsoft YaHei", 12, "bold"))

    style.configure("Status.TLabel",
                    background=BG_BASE,
                    foreground=TEXT_SECONDARY,
                    font=FONT_SMALL,
                    padding=(10, 6))

    # --- 输入框 ---
    style.configure("TEntry",
                    fieldbackground=BG_INPUT,
                    foreground=TEXT_PRIMARY,
                    insertcolor=TEXT_PRIMARY,
                    borderwidth=1,
                    bordercolor=BORDER,
                    padding=8,
                    font=FONT_BODY,
                    relief="solid")
    style.map("TEntry",
              bordercolor=[("focus", BORDER_FOCUS),
                           ("!focus", BORDER)])

    # --- 下拉框 ---
    style.configure("TCombobox",
                    fieldbackground=BG_INPUT,
                    foreground=TEXT_PRIMARY,
                    arrowcolor=TEXT_PRIMARY,
                    borderwidth=1,
                    bordercolor=BORDER,
                    padding=7,
                    font=FONT_BODY,
                    relief="solid")
    style.map("TCombobox",
              fieldbackground=[("readonly", BG_INPUT)],
              bordercolor=[("focus", BORDER_FOCUS),
                           ("!focus", BORDER)])
    style.configure("Disabled.TCombobox",
                    fieldbackground=BG_CARD,
                    foreground=TEXT_DISABLED,
                    arrowcolor=TEXT_DISABLED,
                    bordercolor=BORDER_LIGHT)

    # --- Notebook (Tab栏) ---
    style.configure("TNotebook",
                    background=BG_BASE,
                    borderwidth=0,
                    tabmargins=[0, 0, 0, 0])
    style.configure("TNotebook.Tab",
                    background=BG_CARD,
                    foreground=TEXT_SECONDARY,
                    borderwidth=0,
                    padding=(20, 8),
                    font=("Microsoft YaHei", 9, "bold"))
    style.map("TNotebook.Tab",
              background=[("selected", BG_CARD),
                          ("active", BG_HOVER)],
              foreground=[("selected", BLUE)],
              expand=[("selected", [0, 0, 0, 0])])

    # --- PanedWindow ---
    style.configure("TPanedwindow",
                    background=BG_BASE)

    # --- Treeview ---
    style.configure("Treeview",
                    background=BG_INPUT,
                    foreground=TEXT_PRIMARY,
                    fieldbackground=BG_INPUT,
                    borderwidth=0,
                    font=FONT_TREEVIEW,
                    rowheight=TREE_ROW_HEIGHT,
                    relief="flat")
    style.configure("Treeview.Heading",
                    background=HEADER_BG,
                    foreground=HEADER_TEXT,
                    font=("Microsoft YaHei", 9, "bold"),
                    borderwidth=0,
                    relief="flat",
                    padding=(10, 6))
    style.map("Treeview.Heading",
              background=[("active", BG_HOVER)])
    style.map("Treeview",
              background=[("selected", BTN_PRIMARY_BG)],
              foreground=[("selected", "#FFFFFF")])

    # --- 滚动条 ---
    _scrollbar_styles(style)

    # --- 分隔线 ---
    style.configure("TSeparator", background=BORDER_LIGHT)

    # --- 勾选框 ---
    style.configure("TCheckbutton",
                    background=BG_CARD,
                    foreground=TEXT_PRIMARY,
                    font=FONT_BODY)
    style.map("TCheckbutton",
              background=[("active", BG_CARD)])


def _scrollbar_styles(style: ttk.Style):
    style.configure("Vertical.TScrollbar",
                    background=SCROLL_TROUGH,
                    troughcolor=SCROLL_TROUGH,
                    arrowcolor=TEXT_SECONDARY,
                    width=8,
                    borderwidth=0,
                    relief="flat")
    style.configure("Horizontal.TScrollbar",
                    background=SCROLL_TROUGH,
                    troughcolor=SCROLL_TROUGH,
                    arrowcolor=TEXT_SECONDARY,
                    height=8,
                    borderwidth=0,
                    relief="flat")
    style.map("Vertical.TScrollbar",
              background=[("pressed", SCROLL_HOVER),
                          ("active", SCROLL_SLIDER),
                          ("!disabled", SCROLL_SLIDER)],
              arrowsize=[("!disabled", 8)])
    style.map("Horizontal.TScrollbar",
              background=[("pressed", SCROLL_HOVER),
                          ("active", SCROLL_SLIDER),
                          ("!disabled", SCROLL_SLIDER)],
              arrowsize=[("!disabled", 8)])


# ==================== Treeview 标签 ====================

def configure_tree_tags(tree: ttk.Treeview):
    tree.tag_configure("signal",
                       foreground=GREEN,
                       font=FONT_TREEVIEW)
    tree.tag_configure("no_signal",
                       foreground=TEXT_HINT,
                       font=FONT_TREEVIEW)
    tree.tag_configure("placeholder",
                       foreground=TEXT_HINT,
                       font=("Consolas", 9))


# ==================== 工具函数 ====================

def section_label(parent, text, **kwargs):
    """创建分区标题标签"""
    return ttk.Label(parent, text=text, font=FONT_SECTION,
                     foreground=BLUE, background=BG_CARD, **kwargs)


def divider(parent, orient="horizontal"):
    """放置分隔线"""
    s = ttk.Separator(parent, orient=orient)
    s.pack(fill=tk.X if orient == "horizontal" else tk.Y, pady=6)
    return s


# ==================== 原生 Widget 样式辅助 ====================

def style_native_widget(widget, bg=None, fg=None, select_bg=None, select_fg=None):
    """统一为原生 tk widget (Listbox/Text/Canvas) 应用圆角风格"""
    if bg is None:
        bg = BG_INPUT
    if fg is None:
        fg = TEXT_PRIMARY
    if select_bg is None:
        select_bg = BTN_PRIMARY_BG
    if select_fg is None:
        select_fg = "#FFFFFF"

    widget.configure(
        bg=bg,
        fg=fg,
        selectbackground=select_bg,
        selectforeground=select_fg,
        borderwidth=0,
        highlightthickness=0,
        relief="flat"
    )
