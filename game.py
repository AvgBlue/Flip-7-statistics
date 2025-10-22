from typing import List
import random
from player import Player
import tkinter as tk
from tkinter import ttk


def _plot_running_average_tk(running_avg: List[float]) -> None:
    """Show a window with a graph of running average (y) vs games (x)."""
    if not running_avg:
        return

    width, height = 900, 550
    pad_left, pad_right, pad_top, pad_bottom = 70, 20, 20, 70

    y_min = min(running_avg)
    y_max = max(running_avg)
    if y_min == y_max:
        # Avoid zero span
        y_min -= 1
        y_max += 1
    x_min, x_max = 1, len(running_avg)

    def x_to_px(x_val: float) -> float:
        return pad_left + (x_val - x_min) / (x_max - x_min) * (
            width - pad_left - pad_right
        )

    def y_to_px(y_val: float) -> float:
        # Invert y so higher values are higher on the canvas
        return pad_top + (y_max - y_val) / (y_max - y_min) * (
            height - pad_top - pad_bottom
        )

    root = tk.Tk()
    root.title("Average score vs number of games")
    canvas = tk.Canvas(root, width=width, height=height, bg="white")
    canvas.pack()

    # Axes
    x0, y0 = pad_left, height - pad_bottom
    x1, y1 = width - pad_right, pad_top
    canvas.create_line(x0, y0, x1, y0, width=2)  # X axis
    canvas.create_line(x0, y0, x0, y1, width=2)  # Y axis

    # Axis labels
    canvas.create_text(
        (x0 + x1) / 2, height - pad_bottom / 2, text="Games", font=("Segoe UI", 11)
    )
    canvas.create_text(
        pad_left / 2, (y0 + y1) / 2, text="Average", angle=90, font=("Segoe UI", 11)
    )
    canvas.create_text(
        (x0 + x1) / 2,
        pad_top / 2,
        text="Average score vs number of games",
        font=("Segoe UI", 12, "bold"),
    )

    # Grid and ticks
    tick_count = 5
    # Y ticks
    for i in range(tick_count + 1):
        y_val = y_min + i * (y_max - y_min) / tick_count
        y_px = y_to_px(y_val)
        canvas.create_line(x0, y_px, x1, y_px, fill="#eee")
        canvas.create_text(
            x0 - 8, y_px, text=f"{y_val:.1f}", anchor="e", font=("Segoe UI", 9)
        )
    # X ticks
    for i in range(tick_count + 1):
        x_val = x_min + i * (x_max - x_min) / tick_count
        x_px = x_to_px(x_val)
        canvas.create_line(x_px, y0, x_px, y1, fill="#f7f7f7")
        canvas.create_text(
            x_px, y0 + 14, text=f"{int(round(x_val))}", anchor="n", font=("Segoe UI", 9)
        )

    # Polyline for running average
    pts: List[float] = []
    for i, y in enumerate(running_avg, start=1):
        pts.extend([x_to_px(i), y_to_px(y)])
    if len(pts) >= 4:
        canvas.create_line(*pts, fill="#1f77b4", width=2)

    # Optional: small circles at sparse intervals to aid readability
    step = max(1, len(running_avg) // 50)
    for i in range(1, len(running_avg) + 1, step):
        canvas.create_oval(
            x_to_px(i) - 2,
            y_to_px(running_avg[i - 1]) - 2,
            x_to_px(i) + 2,
            y_to_px(running_avg[i - 1]) + 2,
            fill="#1f77b4",
            outline="",
        )


def _draw_axes(
    canvas: tk.Canvas,
    width: int,
    height: int,
    pad_left: int,
    pad_right: int,
    pad_top: int,
    pad_bottom: int,
    x_label: str,
    y_label: str,
    title: str,
):
    """Draw axes and labels; return (x0, y0, x1, y1) axis bounds."""
    x0, y0 = pad_left, height - pad_bottom
    x1, y1 = width - pad_right, pad_top
    canvas.create_line(x0, y0, x1, y0, width=2)  # X axis
    canvas.create_line(x0, y0, x0, y1, width=2)  # Y axis
    canvas.create_text(
        (x0 + x1) / 2, height - pad_bottom / 2, text=x_label, font=("Segoe UI", 11)
    )
    canvas.create_text(
        pad_left / 2, (y0 + y1) / 2, text=y_label, angle=90, font=("Segoe UI", 11)
    )
    canvas.create_text(
        (x0 + x1) / 2, pad_top / 2, text=title, font=("Segoe UI", 12, "bold")
    )
    return x0, y0, x1, y1


def _plot_stats_window_tk(
    running_avg: List[float],
    scores: List[int],
    count_reached7: int,
    count_already_true: int,
    cards_at_scoring: List[int],
) -> None:
    """Show a window with multiple tabs: running average, histogram of scores, pie of error reasons, and cards-at-scoring histogram."""
    try:
        if not running_avg or not scores:
            return

        import math

        width, height = 900, 550
        pad_left, pad_right, pad_top, pad_bottom = 70, 20, 20, 70

        root = tk.Tk()
        root.title("Flip-7 statistics")
        root.lift()
        root.attributes("-topmost", True)
        root.after_idle(root.attributes, "-topmost", False)
        nb = ttk.Notebook(root)
        nb.pack(fill="both", expand=True)

        # --- Running average tab ---
        avg_frame = ttk.Frame(nb)
        nb.add(avg_frame, text="Running average")
        avg_canvas = tk.Canvas(avg_frame, width=width, height=height, bg="white")
        avg_canvas.pack()

        y_min = min(running_avg)
        y_max = max(running_avg)
        if y_min == y_max:
            y_min -= 1
            y_max += 1
        x_min, x_max = 1, len(running_avg)

        def x_to_px_avg(x_val: float) -> float:
            return pad_left + (x_val - x_min) / (x_max - x_min) * (
                width - pad_left - pad_right
            )

        def y_to_px_avg(y_val: float) -> float:
            return pad_top + (y_max - y_val) / (y_max - y_min) * (
                height - pad_top - pad_bottom
            )

        ax0, ay0, ax1, ay1 = _draw_axes(
            avg_canvas,
            width,
            height,
            pad_left,
            pad_right,
            pad_top,
            pad_bottom,
            "Games",
            "Average",
            "Average score vs number of games",
        )
        tick_count = 5
        for i in range(tick_count + 1):
            y_val = y_min + i * (y_max - y_min) / tick_count
            y_px = y_to_px_avg(y_val)
            avg_canvas.create_line(ax0, y_px, ax1, y_px, fill="#eee")
            avg_canvas.create_text(
                ax0 - 8, y_px, text=f"{y_val:.1f}", anchor="e", font=("Segoe UI", 9)
            )
        for i in range(tick_count + 1):
            x_val = x_min + i * (x_max - x_min) / tick_count
            x_px = x_to_px_avg(x_val)
            avg_canvas.create_line(x_px, ay0, x_px, ay1, fill="#f7f7f7")
            avg_canvas.create_text(
                x_px,
                ay0 + 14,
                text=f"{int(round(x_val))}",
                anchor="n",
                font=("Segoe UI", 9),
            )
        pts: List[float] = []
        for i, y in enumerate(running_avg, start=1):
            pts.extend([x_to_px_avg(i), y_to_px_avg(y)])
        if len(pts) >= 4:
            avg_canvas.create_line(*pts, fill="#1f77b4", width=2)
        step = max(1, len(running_avg) // 50)
        for i in range(1, len(running_avg) + 1, step):
            avg_canvas.create_oval(
                x_to_px_avg(i) - 2,
                y_to_px_avg(running_avg[i - 1]) - 2,
                x_to_px_avg(i) + 2,
                y_to_px_avg(running_avg[i - 1]) + 2,
                fill="#1f77b4",
                outline="",
            )

        # --- Histogram tab (scores) ---
        hist_frame = ttk.Frame(nb)
        nb.add(hist_frame, text="Histogram")
        hist_canvas = tk.Canvas(hist_frame, width=width, height=height, bg="white")
        hist_canvas.pack()
        n = len(scores)
        k = max(10, int(math.ceil(math.log2(n) + 1)))
        s_min, s_max = min(scores), max(scores)
        if s_min == s_max:
            s_min -= 1
            s_max += 1
        span = s_max - s_min
        bin_width = span / k if k > 0 else 1
        if bin_width <= 0:
            bin_width = 1
        edges = [s_min + i * bin_width for i in range(k + 1)]
        counts = [0] * k
        for v in scores:
            if v == edges[-1]:
                counts[-1] += 1
            else:
                idx = int((v - s_min) / bin_width)
                idx = max(0, min(k - 1, idx))
                counts[idx] += 1
        c_min, c_max = 0, max(counts) if counts else 1

        def x_to_px_hist(x_val: float) -> float:
            return pad_left + (x_val - s_min) / (s_max - s_min) * (
                width - pad_left - pad_right
            )

        def y_to_px_hist(y_val: float) -> float:
            denom = (c_max - c_min) if c_max > c_min else 1
            return pad_top + (c_max - y_val) / denom * (height - pad_top - pad_bottom)

        hx0, hy0, hx1, hy1 = _draw_axes(
            hist_canvas,
            width,
            height,
            pad_left,
            pad_right,
            pad_top,
            pad_bottom,
            "Score",
            "Count",
            "Histogram of scores",
        )
        for i in range(6):
            y_val = c_min + i * (c_max - c_min) / 5
            y_px = y_to_px_hist(y_val)
            hist_canvas.create_line(hx0, y_px, hx1, y_px, fill="#eee")
            hist_canvas.create_text(
                hx0 - 8,
                y_px,
                text=f"{int(round(y_val))}",
                anchor="e",
                font=("Segoe UI", 9),
            )
        step_edges = max(1, k // 10)
        for i in range(0, len(edges), step_edges):
            x_val = edges[i]
            x_px = x_to_px_hist(x_val)
            hist_canvas.create_line(x_px, hy0, x_px, hy1, fill="#f7f7f7")
            hist_canvas.create_text(
                x_px,
                hy0 + 14,
                text=f"{int(round(x_val))}",
                anchor="n",
                font=("Segoe UI", 9),
            )
        for i, count in enumerate(counts):
            left = x_to_px_hist(edges[i])
            right = x_to_px_hist(edges[i + 1])
            top = y_to_px_hist(count)
            bottom = hy0
            hist_canvas.create_rectangle(
                left + 1, top, right - 1, bottom, fill="#ff7f0e", outline="#cc6a0c"
            )
            center_x = (left + right) / 2
            label_y = max(pad_top + 10, top - 6)
            hist_canvas.create_text(
                center_x,
                label_y,
                text=str(int(count)),
                anchor="s",
                font=("Segoe UI", 9),
                fill="#222",
            )

        # --- Pie chart tab (IndexError reasons) ---
        pie_frame = ttk.Frame(nb)
        nb.add(pie_frame, text="Reasons (pie)")
        pie_canvas = tk.Canvas(pie_frame, width=width, height=height, bg="white")
        pie_canvas.pack()
        total = count_reached7 + count_already_true
        pie_canvas.create_text(
            width / 2,
            pad_top / 2,
            text="IndexError reasons",
            font=("Segoe UI", 12, "bold"),
        )
        if total <= 0:
            pie_canvas.create_text(
                width / 2,
                height / 2,
                text="No IndexError events recorded",
                font=("Segoe UI", 11),
            )
        else:
            radius = (
                min((width - pad_left - pad_right), (height - pad_top - pad_bottom))
                * 0.35
            )
            cx = pad_left + radius + 40
            cy = pad_top + (height - pad_top - pad_bottom) / 2
            bbox = (cx - radius, cy - radius, cx + radius, cy + radius)

            def pct(x: int) -> float:
                return x / total * 100.0 if total > 0 else 0.0

            angle_reached7 = 360.0 * (count_reached7 / total)
            angle_already = 360.0 - angle_reached7
            color_reached7 = "#2ca02c"
            color_already = "#d62728"
            start = 0
            pie_canvas.create_arc(
                *bbox,
                start=start,
                extent=angle_reached7,
                fill=color_reached7,
                outline="white",
            )
            start += angle_reached7
            pie_canvas.create_arc(
                *bbox,
                start=start,
                extent=angle_already,
                fill=color_already,
                outline="white",
            )
            legend_x = cx + radius + 60
            legend_y = cy - 30
            box_size = 14
            spacing = 22
            pie_canvas.create_rectangle(
                legend_x,
                legend_y,
                legend_x + box_size,
                legend_y + box_size,
                fill=color_reached7,
                outline="black",
            )
            pie_canvas.create_text(
                legend_x + box_size + 8,
                legend_y + box_size / 2,
                text=f"Reached 7 True positions: {count_reached7} ({pct(count_reached7):.1f}%)",
                anchor="w",
                font=("Segoe UI", 10),
            )
            legend_y += spacing
            pie_canvas.create_rectangle(
                legend_x,
                legend_y,
                legend_x + box_size,
                legend_y + box_size,
                fill=color_already,
                outline="black",
            )
            pie_canvas.create_text(
                legend_x + box_size + 8,
                legend_y + box_size / 2,
                text=f"position already True: {count_already_true} ({pct(count_already_true):.1f}%)",
                anchor="w",
                font=("Segoe UI", 10),
            )

        # --- Cards at scoring histogram tab ---
        cas_frame = ttk.Frame(nb)
        nb.add(cas_frame, text="Cards at scoring")
        cas_canvas = tk.Canvas(cas_frame, width=width, height=height, bg="white")
        cas_canvas.pack()
        if cards_at_scoring:
            cmin, cmax = min(cards_at_scoring), max(cards_at_scoring)
        else:
            cmin, cmax = 0, 1
        int_edges = [cmin - 0.5 + i for i in range((cmax - cmin + 1) + 1)]
        int_counts = [0] * (len(int_edges) - 1)
        for v in cards_at_scoring:
            idx = int(v - cmin)
            if 0 <= idx < len(int_counts):
                int_counts[idx] += 1
        ic_min, ic_max = 0, max(int_counts) if int_counts else 1

        def x_to_px_cas(x_val: float) -> float:
            xmin_edge = int_edges[0]
            xmax_edge = int_edges[-1]
            return pad_left + (x_val - xmin_edge) / (xmax_edge - xmin_edge) * (
                width - pad_left - pad_right
            )

        def y_to_px_cas(y_val: float) -> float:
            denom = (ic_max - ic_min) if ic_max > ic_min else 1
            return pad_top + (ic_max - y_val) / denom * (height - pad_top - pad_bottom)

        cx0, cy0, cx1, cy1 = _draw_axes(
            cas_canvas,
            width,
            height,
            pad_left,
            pad_right,
            pad_top,
            pad_bottom,
            "Cards in hand",
            "Count",
            "Histogram: cards in hand at scoring",
        )
        for i in range(6):
            y_val = ic_min + i * (ic_max - ic_min) / 5
            y_px = y_to_px_cas(y_val)
            cas_canvas.create_line(cx0, y_px, cx1, y_px, fill="#eee")
            cas_canvas.create_text(
                cx0 - 8,
                y_px,
                text=f"{int(round(y_val))}",
                anchor="e",
                font=("Segoe UI", 9),
            )
        for i in range(len(int_edges)):
            if i < len(int_edges) - 1:
                center = (int_edges[i] + int_edges[i + 1]) / 2
                x_px = x_to_px_cas(int_edges[i])
                cas_canvas.create_line(x_px, cy0, x_px, cy1, fill="#f7f7f7")
                cas_canvas.create_text(
                    x_to_px_cas(center),
                    cy0 + 14,
                    text=f"{int(round(center))}",
                    anchor="n",
                    font=("Segoe UI", 9),
                )
        for i, count in enumerate(int_counts):
            left = x_to_px_cas(int_edges[i])
            right = x_to_px_cas(int_edges[i + 1])
            top = y_to_px_cas(count)
            bottom = cy0
            cas_canvas.create_rectangle(
                left + 1, top, right - 1, bottom, fill="#9467bd", outline="#7b56a0"
            )
            center_x = (left + right) / 2
            label_y = max(pad_top + 10, top - 6)
            cas_canvas.create_text(
                center_x,
                label_y,
                text=str(int(count)),
                anchor="s",
                font=("Segoe UI", 9),
                fill="#222",
            )

        # --- Cards at scoring pie chart tab ---
        pie2_frame = ttk.Frame(nb)
        nb.add(pie2_frame, text="Cards at scoring (pie)")
        pie2_canvas = tk.Canvas(pie2_frame, width=width, height=height, bg="white")
        pie2_canvas.pack()
        total_cas = len(cards_at_scoring)
        pie2_canvas.create_text(
            width / 2,
            pad_top / 2,
            text="Cards in hand at scoring (pie)",
            font=("Segoe UI", 12, "bold"),
        )
        if total_cas == 0:
            pie2_canvas.create_text(
                width / 2,
                height / 2,
                text="No scoring events recorded",
                font=("Segoe UI", 11),
            )
        else:
            from collections import Counter

            cas_counts = Counter(cards_at_scoring)
            sorted_keys = sorted(cas_counts.keys())
            colors = [
                "#1f77b4",
                "#ff7f0e",
                "#2ca02c",
                "#d62728",
                "#9467bd",
                "#8c564b",
                "#e377c2",
                "#7f7f7f",
                "#bcbd22",
                "#17becf",
            ]
            radius = (
                min((width - pad_left - pad_right), (height - pad_top - pad_bottom))
                * 0.35
            )
            cx = pad_left + radius + 40
            cy = pad_top + (height - pad_top - pad_bottom) / 2
            bbox = (cx - radius, cy - radius, cx + radius, cy + radius)
            start = 0
            for idx, k in enumerate(sorted_keys):
                count = cas_counts[k]
                extent = 360.0 * (count / total_cas)
                color = colors[idx % len(colors)]
                pie2_canvas.create_arc(
                    *bbox, start=start, extent=extent, fill=color, outline="white"
                )
                start += extent
            legend_x = cx + radius + 60
            legend_y = cy - 30
            box_size = 14
            spacing = 22
            for idx, k in enumerate(sorted_keys):
                count = cas_counts[k]
                color = colors[idx % len(colors)]
                pie2_canvas.create_rectangle(
                    legend_x,
                    legend_y,
                    legend_x + box_size,
                    legend_y + box_size,
                    fill=color,
                    outline="black",
                )
                pct = 100.0 * count / total_cas
                pie2_canvas.create_text(
                    legend_x + box_size + 8,
                    legend_y + box_size / 2,
                    text=f"{k} cards: {count} ({pct:.1f}%)",
                    anchor="w",
                    font=("Segoe UI", 10),
                )
                legend_y += spacing

        root.mainloop()
    except Exception as e:
        import traceback

        print("Exception in _plot_stats_window_tk:")
        traceback.print_exc()


def main() -> int:
    deck: List[int] = [0]
    for i in range(1, 13):
        deck += [i] * i
    deck += [f"+{i}" for i in range(2, 10, 2)] + ["*2"] + ["Second Chance"] * 3
    random.shuffle(deck)
    player = Player()
    len_deck = len(deck)
    games = 10_000_000  # number of completed games to simulate
    index = 0
    scores: List[int] = []
    cards_at_scoring: List[int] = []
    running_avg: List[float] = []
    cumulative_sum = 0
    card_flips = 0
    # Counters for IndexError reasons
    count_reached7 = 0
    count_already_true = 0
    while games > 0:
        if index == len_deck:
            index = 0
            random.shuffle(deck)
        try:
            player.add_card(deck[index])
        except IndexError as e:
            # Count specific IndexError reasons
            msg = str(e)
            if msg == "Reached 7 True positions":
                count_reached7 += 1
            elif msg.startswith("position ") and msg.endswith(" is already True"):
                count_already_true += 1

            # capture cards in hand at scoring moment (positions only, no modifiers)
            cards_in_hand_now = sum(1 for v in player.hand if v)

            score = player.Score()
            scores.append(score)
            cards_at_scoring.append(cards_in_hand_now)
            cumulative_sum += score
            running_avg.append(cumulative_sum / len(scores))
            player.reset_hand()
            games -= 1
        except Exception as e:
            print(e)
        index += 1
        card_flips += 1
    # Show graphs; then print final average after the window is closed
    if scores:
        _plot_stats_window_tk(
            running_avg, scores, count_reached7, count_already_true, cards_at_scoring
        )
        final_avg = running_avg[-1]
        print(f"Final average: {final_avg:.2f}")


if __name__ == "__main__":
    main()
