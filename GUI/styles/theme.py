from tkinter import ttk

from GUI.styles.colors import (
    CONTENT,
    PANEL,
    PANEL_HOVER,
    TEXT_DARK,
    TABLE_HEADING,
    TABLE_SELECTED,
)

FONT_FAMILY = "Arial"

FONT_TITLE = (FONT_FAMILY, 22, "bold")
FONT_PAGE_TITLE = (FONT_FAMILY, 20, "bold")
FONT_SECTION = (FONT_FAMILY, 18, "bold")
FONT_STAT_LABEL = (FONT_FAMILY, 10, "bold")
FONT_STAT_VALUE = (FONT_FAMILY, 23, "bold")
FONT_BODY = (FONT_FAMILY, 12)
FONT_BODY_BOLD = (FONT_FAMILY, 12, "bold")
FONT_NAV = (FONT_FAMILY, 13, "bold")
FONT_SMALL = (FONT_FAMILY, 10)
FONT_SMALL_BOLD = (FONT_FAMILY, 10, "bold")
FONT_TABLE = (FONT_FAMILY, 10)
FONT_TABLE_HEADING = (FONT_FAMILY, 10, "bold")
FONT_FORM_LABEL = (FONT_FAMILY, 11, "bold")
FONT_FORM_INPUT = (FONT_FAMILY, 12)

SIDEBAR_WIDTH = 185
HEADER_HEIGHT = 78
CONTENT_PAD_X = 32
CONTENT_PAD_Y = 20
PANEL_RADIUS = 10
BUTTON_RADIUS = 9

BUTTON_HEIGHT = 58
BUTTON_PAD_X = 5
BUTTON_PAD_Y = 4
INPUT_RADIUS = 8

SIDEBAR_BRAND_PAD_X = 22
SIDEBAR_BRAND_PAD_Y = 28
SIDEBAR_BRAND_BOTTOM = 34
SIDEBAR_BUTTON_HEIGHT = 42
SIDEBAR_BUTTON_PAD_X = 13
SIDEBAR_BUTTON_PAD_Y = 3
SIDEBAR_BOTTOM_PAD_X = 20
SIDEBAR_BOTTOM_PAD_Y = 20

HEADER_PAD_X = 28
HEADER_PAD_Y = 20

TABLE_ROW_HEIGHT = 34
TABLE_CELL_PAD_X = 10
TABLE_OUTER_PAD_X = 18
TABLE_OUTER_PAD_Y = 18

FORM_WIDTH = 560
FORM_HEIGHT = 680
FORM_PAD_X = 28
FORM_PAD_Y = 24
FORM_FIELD_GAP = 14
FORM_BUTTON_HEIGHT = 40


def configure_treeview_style():
    style = ttk.Style()
    style.theme_use("clam")
    style.configure(
        "Budget.Treeview",
        background=CONTENT,
        fieldbackground=CONTENT,
        foreground=TEXT_DARK,
        rowheight=TABLE_ROW_HEIGHT,
        borderwidth=0,
        relief="flat",
        font=FONT_TABLE,
    )
    style.configure(
        "Budget.Treeview.Heading",
        background=TABLE_HEADING,
        foreground=TEXT_DARK,
        font=FONT_TABLE_HEADING,
        relief="flat",
        borderwidth=0,
    )
    style.map(
        "Budget.Treeview",
        background=[("selected", TABLE_SELECTED)],
        foreground=[("selected", TEXT_DARK)],
    )
    style.map(
        "Budget.Treeview.Heading",
        background=[("active", TABLE_HEADING)],
    )
    return style
