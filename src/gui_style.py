"""
Canking_Ran 橙色调扁平样式表
"""
import tkinter as tk
from tkinter import ttk

# ==================== 调色板 ====================

# 主色 - 橙色系
BLUE       = "#FF6B00"    # 主色 (橙)
BLUE_LIGHT = "#FF8F33"    # 主色浅色 (浅橙)
GREEN      = "#27AE60"    # 成功/运行
GREEN_LIGHT = "#2ECC71"
ORANGE     = "#E67E22"    # 警告
RED        = "#E74C3C"    # 错误/停止
RED_LIGHT  = "#EC7063"

# 背景 (浅色)
BG_BASE    = "#F0F2F5"    # 最底层背景
BG_CARD    = "#FAFAFA"    # 卡片/面板背景
BG_INPUT   = "#FFFFFF"    # 输入框背景
BG_HOVER   = "#FEE9D1"    # 悬停 (浅橙)
BG_ACTIVE  = "#FDD2A0"    # 按下 (深一点的浅橙)

# 文字
TEXT_PRIMARY   = "#2C3E50"
TEXT_SECONDARY = "#95A5A6"
TEXT_DISABLED  = "#BDC3C7"

# 边框
BORDER       = "#E0E0E0"
BORDER_LIGHT = "#ECECEC"

# 滚动条
SCROLL_TROUGH  = "#F5F5F5"
SCROLL_SLIDER  = "#C0C0C0"
SCROLL_HOVER   = "#A0A0A0"

# 表格表头
HEADER_BG = "#FFF3E0"

# ==================== 字体 ====================

FONT_MONO    = ("Consolas", 10)
FONT_BODY    = ("Microsoft YaHei", 9)
FONT_SMALL   = ("Microsoft YaHei", 8)
FONT_HEADING = ("Microsoft YaHei", 11, "bold")
FONT_TREEVIEW = ("Consolas", 10)
FONT_SECTION = ("Microsoft YaHei", 10, "bold")

PAD_X = 8
PAD_Y = 6
TREE_ROW_HEIGHT = 26

# ==================== 主题应用 ====================

def apply_style(root: tk.Tk):
    style = ttk.Style(root)

    if "clam" in style.theme_names():
        style.theme_use("clam")

    # --- 框架 ---
    style.configure("TFrame", background=BG_CARD)

    # --- Labelframe: 扁平卡片 ---
    style.configure("Card.TLabelframe",
                    background=BG_CARD,
                    bordercolor=BG_CARD,
                    relief="flat",
                    borderwidth=0)
    style.configure("Card.TLabelframe.Label",
                    background=BG_CARD,
                    foreground=BLUE,
                    font=FONT_SECTION)

    # --- 按钮 ---
    style.configure("TButton",
                    background=BG_CARD,
                    foreground=TEXT_PRIMARY,
                    borderwidth=1,
                    bordercolor=BLUE,
                    focusthickness=0,
                    padding=(14, 6),
                    font=FONT_BODY,
                    relief="flat")
    style.map("TButton",
              background=[("active", BG_HOVER),
                          ("pressed", BG_ACTIVE),
                          ("disabled", BG_CARD)],
              foreground=[("disabled", TEXT_DISABLED)],
              bordercolor=[("active", BLUE_LIGHT),
                           ("disabled", TEXT_DISABLED)])

    # 主色按钮 (橙色)
    style.configure("Primary.TButton",
                    background=BLUE,
                    foreground="#FFFFFF",
                    borderwidth=1,
                    bordercolor=BLUE,
                    focusthickness=0,
                    padding=(14, 6),
                    font=FONT_BODY,
                    relief="flat")
    style.map("Primary.TButton",
              background=[("active", BLUE_LIGHT),
                          ("pressed", "#E06000"),
                          ("disabled", BORDER)],
              foreground=[("disabled", TEXT_DISABLED)],
              bordercolor=[("active", BLUE_LIGHT),
                           ("disabled", BORDER)])

    # 淡橙色按钮
    style.configure("LightOrange.TButton",
                    background="#DBD3FF",
                    foreground=TEXT_PRIMARY,
                    borderwidth=1,
                    bordercolor=BLUE,
                    focusthickness=0,
                    padding=(14, 6),
                    font=FONT_BODY,
                    relief="flat")
    style.map("LightOrange.TButton",
              background=[("active", BG_HOVER),
                          ("pressed", BG_ACTIVE),
                          ("disabled", BG_CARD)],
              foreground=[("disabled", TEXT_DISABLED)])

    # 危险按钮
    style.configure("Danger.TButton",
                    background="#FDEDEC",
                    foreground=RED,
                    borderwidth=1,
                    bordercolor=RED,
                    focusthickness=0,
                    padding=(14, 6),
                    font=FONT_BODY,
                    relief="flat")
    style.map("Danger.TButton",
              background=[("active", "#FDEDEC"),
                          ("disabled", BG_CARD)],
              foreground=[("disabled", TEXT_DISABLED)],
              bordercolor=[("active", RED_LIGHT),
                           ("disabled", BORDER)])

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
                    font=FONT_HEADING)

    style.configure("Status.TLabel",
                    background=BG_BASE,
                    foreground=TEXT_SECONDARY,
                    font=FONT_SMALL,
                    padding=(8, 5))

    # --- 输入框 ---
    style.configure("TEntry",
                    fieldbackground=BG_INPUT,
                    foreground=TEXT_PRIMARY,
                    insertcolor=TEXT_PRIMARY,
                    borderwidth=1,
                    bordercolor=BORDER,
                    padding=6,
                    font=FONT_BODY,
                    relief="solid")
    style.map("TEntry",
              bordercolor=[("focus", BLUE), ("!focus", BORDER)])

    # --- 下拉框 ---
    style.configure("TCombobox",
                    fieldbackground=BG_INPUT,
                    foreground=TEXT_PRIMARY,
                    arrowcolor=TEXT_PRIMARY,
                    borderwidth=1,
                    bordercolor=BORDER,
                    padding=5,
                    font=FONT_BODY,
                    relief="solid")
    style.map("TCombobox",
              fieldbackground=[("readonly", BG_INPUT)],
              bordercolor=[("focus", BLUE), ("!focus", BORDER)])
    style.configure("Disabled.TCombobox",
                    fieldbackground=BG_CARD,
                    foreground=TEXT_DISABLED,
                    arrowcolor=TEXT_DISABLED,
                    bordercolor=BORDER)

    # --- Notebook (Tab栏) ---
    style.configure("TNotebook",
                    background=BG_CARD,
                    borderwidth=0,
                    tabmargins=[0, 0, 0, 0])
    style.configure("TNotebook.Tab",
                    background=BG_CARD,
                    foreground=TEXT_SECONDARY,
                    borderwidth=0,
                    padding=(16, 6),
                    font=FONT_BODY)
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
                    foreground=TEXT_PRIMARY,
                    font=FONT_BODY,
                    borderwidth=0,
                    relief="flat",
                    padding=(8, 5))
    style.map("Treeview.Heading",
              background=[("active", BG_HOVER)])
    style.map("Treeview",
              background=[("selected", BLUE)],
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
                    width=10,
                    borderwidth=0,
                    relief="flat")
    style.configure("Horizontal.TScrollbar",
                    background=SCROLL_TROUGH,
                    troughcolor=SCROLL_TROUGH,
                    arrowcolor=TEXT_SECONDARY,
                    height=10,
                    borderwidth=0,
                    relief="flat")
    style.map("Vertical.TScrollbar",
              background=[("pressed", SCROLL_HOVER),
                          ("active", SCROLL_SLIDER),
                          ("!disabled", SCROLL_SLIDER)],
              arrowsize=[("!disabled", 7)])
    style.map("Horizontal.TScrollbar",
              background=[("pressed", SCROLL_HOVER),
                          ("active", SCROLL_SLIDER),
                          ("!disabled", SCROLL_SLIDER)],
              arrowsize=[("!disabled", 7)])


# ==================== Treeview 标签 ====================

def configure_tree_tags(tree: ttk.Treeview):
    tree.tag_configure("signal",
                       foreground=GREEN,
                       font=FONT_TREEVIEW)
    tree.tag_configure("no_signal",
                       foreground=TEXT_DISABLED,
                       font=FONT_TREEVIEW)


# ==================== 工具函数 ====================

def section_label(parent, text, **kwargs):
    """创建分区标题标签"""
    return ttk.Label(parent, text=text, font=FONT_SECTION,
                     foreground=BLUE, background=BG_CARD, **kwargs)

def divider(parent, orient="horizontal"):
    """放置分隔线"""
    s = ttk.Separator(parent, orient=orient)
    s.pack(fill=tk.X if orient == "horizontal" else tk.Y, pady=4)
    return s
