from typing import List, Optional
import tkinter as tk
from tkinter import ttk, simpledialog
import math
import numpy as np

from game import run_experiment, ExperimentResults


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


def _plot_stats_window_tk(results: ExperimentResults) -> None:
    running_avg = results.running_avg
    scores = results.scores
    count_reached7 = results.count_reached7
    count_already_true = results.count_already_true
    cards_at_scoring = results.cards_at_scoring

    if not running_avg or not scores:
        return

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
        # Use logarithmic scale for x-axis to create uneven spacing
        log_min = math.log10(x_min)
        log_max = math.log10(x_max)
        log_val = math.log10(max(1, x_val))
        return pad_left + (log_val - log_min) / (log_max - log_min) * (
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
        "Games (log scale)",
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
    # X ticks with logarithmic spacing
    log_min = math.log10(x_min)
    log_max = math.log10(x_max)
    for i in range(tick_count + 1):
        log_val = log_min + i * (log_max - log_min) / tick_count
        x_val = 10**log_val
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
            hx0 - 8, y_px, text=f"{int(round(y_val))}", anchor="e", font=("Segoe UI", 9)
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

    # --- Box plot tab (scores) ---
    box_frame = ttk.Frame(nb)
    nb.add(box_frame, text="Box Plot")
    box_canvas = tk.Canvas(box_frame, width=width, height=height, bg="white")
    box_canvas.pack()
    if scores:
        data = np.array(scores)
        q1 = np.percentile(data, 25)
        median = np.percentile(data, 50)
        q3 = np.percentile(data, 75)
        min_val = np.min(data)
        max_val = np.max(data)
        iqr = q3 - q1
        lower_whisker = np.min(data[data >= q1 - 1.5 * iqr])
        upper_whisker = np.max(data[data <= q3 + 1.5 * iqr])
        outliers = data[(data < lower_whisker) | (data > upper_whisker)]

        # Box plot coordinates
        plot_left = pad_left + 100
        plot_right = width - pad_right - 100
        plot_center = (plot_left + plot_right) / 2
        plot_top = pad_top + 60
        plot_bottom = height - pad_bottom - 60

        def y_to_px_box(val):
            return plot_bottom - (val - min_val) / (max_val - min_val) * (
                plot_bottom - plot_top
            )

        # Draw vertical axis
        box_canvas.create_line(plot_center, plot_top, plot_center, plot_bottom, width=2)
        # Draw box
        box_canvas.create_rectangle(
            plot_center - 40,
            y_to_px_box(q3),
            plot_center + 40,
            y_to_px_box(q1),
            fill="#c6dbef",
            outline="#2171b5",
            width=2,
        )
        # Draw median
        box_canvas.create_line(
            plot_center - 40,
            y_to_px_box(median),
            plot_center + 40,
            y_to_px_box(median),
            fill="#d62728",
            width=2,
        )
        # Draw whiskers
        box_canvas.create_line(
            plot_center,
            y_to_px_box(lower_whisker),
            plot_center,
            y_to_px_box(q1),
            width=2,
        )
        box_canvas.create_line(
            plot_center,
            y_to_px_box(q3),
            plot_center,
            y_to_px_box(upper_whisker),
            width=2,
        )
        # Whisker caps
        box_canvas.create_line(
            plot_center - 20,
            y_to_px_box(lower_whisker),
            plot_center + 20,
            y_to_px_box(lower_whisker),
            width=2,
        )
        box_canvas.create_line(
            plot_center - 20,
            y_to_px_box(upper_whisker),
            plot_center + 20,
            y_to_px_box(upper_whisker),
            width=2,
        )
        # Outliers
        for out in outliers:
            box_canvas.create_oval(
                plot_center - 5,
                y_to_px_box(out) - 5,
                plot_center + 5,
                y_to_px_box(out) + 5,
                fill="#ff7f0e",
                outline="",
            )
        # Labels
        box_canvas.create_text(
            plot_center,
            pad_top + 20,
            text="Box Plot of Scores",
            font=("Segoe UI", 12, "bold"),
        )
        for val, label in [
            (min_val, "Min"),
            (q1, "Q1"),
            (median, "Median"),
            (q3, "Q3"),
            (max_val, "Max"),
        ]:
            box_canvas.create_text(
                plot_center + 60,
                y_to_px_box(val),
                text=f"{label}: {val:.1f}",
                anchor="w",
                font=("Segoe UI", 10),
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
        text="Reasons for scoring",
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
            min((width - pad_left - pad_right), (height - pad_top - pad_bottom)) * 0.35
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
            text=f"Reached 7 cards: {count_reached7} ({pct(count_reached7):.1f}%)",
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
            text=f"2 Duplicate cards: {count_already_true} ({pct(count_already_true):.1f}%)",
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
            cx0 - 8, y_px, text=f"{int(round(y_val))}", anchor="e", font=("Segoe UI", 9)
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
            min((width - pad_left - pad_right), (height - pad_top - pad_bottom)) * 0.35
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


def get_number_of_runs() -> Optional[int]:
    """Show a dialog to get the number of runs from the user."""
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    runs = simpledialog.askinteger(
        "Flip-7 Statistics",
        "Enter the number of games to simulate:",
        initialvalue=100000,
        minvalue=100,
        maxvalue=10000000,
    )

    root.destroy()
    return runs


def main():
    # Get number of runs from user
    num_runs = get_number_of_runs()

    if num_runs is None:
        print("No input provided. Exiting.")
        return

    print(f"Running {num_runs:,} simulations...")
    results = run_experiment(hands=num_runs)
    _plot_stats_window_tk(results)
    final_avg = results.running_avg[-1] if results.running_avg else 0.0
    print(f"Final average: {final_avg:.2f}")


if __name__ == "__main__":
    main()
