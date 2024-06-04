import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Wedge

# 读取CSV数据
data = pd.read_csv("filtered2.csv")
# data['startDate'] = pd.to_datetime(data['startDate'], format='%d-%b-%y', errors='coerce')
print(data['startDate'])
data['startDate'] = pd.to_datetime(data['startDate'], format="%d-%b-%y", errors='coerce')
# "%B %d, %Y"
data = data.dropna(subset=['startDate'])

# 计算年份跨度
min_date = data['startDate'].min()
max_date = data['startDate'].max()
year_span = int(max_date.year - min_date.year + 1)

# 全局变量定义
total_points = year_span * 366
patches = []
highlighted_patch = None

# 自定义函数绘制带多种颜色的点
def draw_multicolor_circle(ax, x, y, colors, radius=0.03, data=None):
    radius = 0.01 + 0.005 * len(colors)
    wedges = [Wedge((x, y), radius, 360 * i / len(colors), 360 * (i + 1) / len(colors), facecolor=color) for i, color in enumerate(colors)]
    for wedge in wedges:
        ax.add_patch(wedge)
        wedge.data = data  # 将相关数据存储在每个 wedge 对象中
    return wedges

def highlight_wedges(patch, hover):
    if hover:
        patch.set_edgecolor('red')
        patch.set_linewidth(1)
    else:
        patch.set_edgecolor('white')
        patch.set_linewidth(1)

def draw_months_and_seasons(ax, radius_start, radius_end):
    # Draw 12-segment lines for months
    for i in range(12):
        angle = 2 * np.pi * i / 12
        x = [0, radius_end * np.cos(angle)]
        y = [0, radius_end * np.sin(angle)]
        ax.plot(x, y, color='grey', alpha=0.3)

    # Draw 4-segment lines for seasons
    for i in range(4):
        angle = 2 * np.pi * i / 4
        x = [0, radius_end * np.cos(angle)]
        y = [0, radius_end * np.sin(angle)]
        ax.plot(x, y, color='grey', alpha=0.7)

# 定义绘制螺旋线的函数
def plot_spiral(start_angle):
    radius_start = 0.30
    radius_end = 2
    global patches

    theta = np.linspace(start_angle, -year_span * 2 * np.pi + start_angle, total_points)
    r = np.linspace(radius_start, radius_end, total_points)
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    
    ax.clear()
    ax.plot(x, y, alpha=0.5)

    for year in range(year_span):
        year_angle = start_angle - year * 2 * np.pi
        year_radius = radius_start + (radius_end - radius_start) * year / year_span
        year_x = year_radius * np.cos(year_angle)
        year_y = year_radius * np.sin(year_angle)
        ax.text(year_x, year_y +0.02, f'{min_date.year + year}', fontsize=10, ha='center', va='top')

    families = data['family'].unique()
    colors_map = plt.cm.jet(np.linspace(0, 1, len(families)))
    family_colors = {family: color for family, color in zip(families, colors_map)}
    
    points_dict = {}

    total_days = year_span * 365.25
    for _, row in data.iterrows():
        date = row['startDate']
        year = date.year - min_date.year
        day_of_year = (date - pd.Timestamp(year=date.year, month=1, day=1)).days
        days_span = day_of_year + year * 365.25
        percentage = days_span / total_days

        angle = theta[int((total_points - 1) * percentage)]
        radius = r[int((total_points - 1) * percentage)]
        x_pos = radius * np.cos(angle)
        y_pos = radius * np.sin(angle)
        if (x_pos, y_pos) not in points_dict:
            points_dict[(x_pos, y_pos)] = []
        points_dict[(x_pos, y_pos)].append((family_colors[row['family']], row))

    patches.clear()
    for point, details in points_dict.items():
        colors = [detail[0] for detail in details]
        row_data = [detail[1] for detail in details]
        wedges = draw_multicolor_circle(ax, point[0], point[1], colors, data=row_data)
        patches.extend(wedges)

    for patch in patches:
        highlight_wedges(patch, False)

    handles = [plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=color, markersize=10, label=family) for family, color in family_colors.items()]
    ax.legend(handles=handles, loc='upper right')

    ax.axis('equal')
    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines[['top', 'right', 'bottom', 'left']].set_visible(False)

    draw_months_and_seasons(ax, radius_start, radius_end)
    canvas.draw()

def on_hover(event):
    global highlighted_patch
    # current_family = ""
    # for patch in patches:
    #     if patch.contains_point([event.x, event.y]):
    #         current_family = patch.data[0]['family']
    # for patch in patches:
    #     for row in patch.data.iterrows():
    #         if row['family'] == current_family:
    #             highlight_wedges(patch, True)
                
    for patch in patches:
        if patch.contains_point([event.x, event.y]):
            if highlighted_patch is not None and highlighted_patch != patch:
                highlight_wedges(highlighted_patch, False)
            highlight_wedges(patch, True)
            highlighted_patch = patch
            # 从 patch 对象中获取存储的数据
            data_info = highlighted_patch.data
            tooltip_text = data_info[0]['startDate'].strftime("%Y-%m-%d\n") + "\n".join([f"{row['family']} - {row['model']}" for row in data_info])
            show_tooltip(event, tooltip_text)
            break
        else:
            if highlighted_patch is not None:
                highlight_wedges(highlighted_patch, False)
            highlighted_patch = None
            hide_tooltip(event)
    canvas.draw_idle()

# 创建主窗口
root = tk.Tk()
root.title("螺旋线调整器")

# 创建工具提示窗口
tooltip = tk.Toplevel(root)
tooltip.withdraw()  # 隐藏工具提示窗口
tooltip.overrideredirect(True)
tooltip_label = tk.Label(tooltip, text="", background="white", relief="solid", borderwidth=1, font=("Calibri", 20))
tooltip_label.pack()

def show_tooltip(event, text):
    tooltip_label.config(text=text)
    tooltip.geometry(f"+{event.guiEvent.x_root+20}+{event.guiEvent.y_root-20}")
    tooltip.deiconify()

def hide_tooltip(event):
    tooltip.withdraw()

fig, ax = plt.subplots(figsize=(36, 27))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack()

plot_spiral(-0.5 * np.pi)

# 绑定鼠标悬停事件
fig.canvas.mpl_connect('motion_notify_event', on_hover)

root.mainloop()
