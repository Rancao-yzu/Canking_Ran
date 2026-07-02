# Canking_Ran — Agent Guide

## Run

```sh
python src/main.py
```

## Distribute

```sh
pyinstaller Canking_Ran.spec
# output: dist/Canking_Ran (single-file GUI binary)
```

## Dependencies

- `python-can` (with kvaser backend) — CAN bus interface
- `cantools` — DBC parsing and signal encoding
- `tkinter` — stdlib, GUI framework

No `requirements.txt` or `pyproject.toml`. Install manually: `pip install python-can cantools`.

## Project Structure

```
src/
├── main.py                  # Entrypoint: tk.Tk → MainWindow → root.mainloop()
├── gui_style.py             # ttk theme (orange/"clam"), color palette, font defs
├── core/
│   ├── can_bus.py           # KvaserBusManager — singleton wrapping can.Bus
│   └── dbc_loader.py        # DbcLoader — wraps cantools.database
├── filter/
│   └── can_filter.py        # CanFilter — set-based software filter, no hardware filter
├── receiver/
│   └── message_receiver.py  # MessageReceiver — background thread, queue for UI
├── sender/
│   └── message_sender.py    # MessageSender + SendWorker thread — single/cyclic/random
└── ui/
    ├── main_window.py       # MainWindow — orchestrator, binds all callbacks
    ├── config_panel.py      # DBC path, channel, bitrate, FD mode
    ├── filter_panel.py      # CAN ID filter add/remove/clear
    ├── send_panel.py        # Raw hex + DBC signal send; raw/DBC toggle
    └── receive_panel.py     # Treeview display, lazy DBC decode on expand
```

## Key Patterns

- **CAN ID input is always hex.** Even without `0x` prefix, `int("10", 16)` → 16. Label says "CAN ID (Hex)".
- **DBC decoding is lazy.** Receive panel decodes signals only when user expands a row, not on receipt.
- **Filtering is software-only.** `CanFilter.match(id)` checked in `_poll_queue()`. Hardware `can_filters` sent only at connect time.
- **`KvaserBusManager` is a singleton** via `__new__`. Single `can.Bus` instance.
- **Receiver runs in a daemon thread.** UI polls via `root.after(50, _poll_queue)`.
- **Send cycles run in `SendWorker` thread.** `stop_cyclic()` joins with 2s timeout.
- **ASC recording** is handled transparently inside `KvaserBusManager.send/recv`.
- **No tests, no CI, no lint/typecheck.** No conftest, no pytest config.

## CAN ID Parsing (Important)

All three CAN ID input points parse with `int(raw, 16)` unconditionally:
- `send_panel.py` `get_raw_can_id()`
- `filter_panel.py` `get_all_ids()`
- `main_window.py` `_on_add_filter_id()`

No need to prefix `0x`. Input `10` → decimal 16.

## UI Style

- Theme: `clam`, orange primary (`#FF7A1A`), light background
- Button styles: `Primary.TButton` (solid orange), `Danger.TButton` (red outline), `LightOrange.TButton` (orange outline)
- Widget style helper: `gui_style.style_native_widget()` for Listbox/Text/Canvas
- Fonts: `Consolas` for mono, `Microsoft YaHei` for UI text

## Non-obvious

- `CanFilter.to_can_filters()` generates both standard and extended mask entries per ID — hardware filter always matches both.
- `MainWindow._rebuild_filter()` clears and re-adds all IDs (used after remove/toggle).
- `DBC get_message_by_frame_id()` is used by name `get_message_by_id()` in `dbc_loader.py`, not `get_message_by_frame_id()` in `cantools`.
- Sender defaults `bitrate_switch=is_fd` — always on for FD frames.
