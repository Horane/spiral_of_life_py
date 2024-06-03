import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Wedge

# 读取CSV数据
data = pd.read_csv("filtered.csv")
data['startDate'] = pd.to_datetime(data['startDate'], format='%d-%b-%y', errors='coerce')
data = data.dropna(subset=['startDate'])

# 计算年份跨度
min_date = data['startDate'].min()
max_date = data['startDate'].max()
year_span = int(max_date.year - min_date.year + 1)

# 全局变量定义
total_points = 1000
patches = []
highlighted_patch = None

# 自定义函数绘制带多种颜色的点
def draw_multicolor_circle(ax, x, y, colors, radius=0.03):
    radius = 0.01 * len(colors)
    wedges = [Wedge((x, y), radius, 360 * i / len(colors), 360 * (i + 1) / len(colors), facecolor=color) for i, color in enumerate(colors)]
    for wedge in wedges:
        ax.add_patch(wedge)
    return wedges

def highlight_wedges(patch, hover):
    if(hover):
        patch.set_edgecolor('red')
        patch.set_linewidth(1)
    else:
        patch.set_edgecolor('white')
        patch.set_linewidth(1)

# 定义绘制螺旋线的函数
def plot_spiral(start_angle):
    radius_start = 0.30
    radius_end = 1
    global patches

    theta = np.linspace(start_angle, -year_span * 2 * np.pi + start_angle, total_points)
    r = np.linspace(radius_start, radius_end, total_points)
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    
    ax.clear()
    ax.plot(x, y, alpha=0.5)

    for year in range(year_span):
        year_angle = start_angle - year * 2 * np.pi
        year_radius = radius_start + (radius_end + 0.02 - radius_start) * year / year_span
        year_x = year_radius * np.cos(year_angle)
        year_y = year_radius * np.sin(year_angle)
        ax.text(year_x, year_y + 0.02, f'{min_date.year + year}', fontsize=10, ha='center', va='top')

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
        points_dict[(x_pos, y_pos)].append((family_colors[row['family']], row['model']))

    patches.clear()
    for point, details in points_dict.items():
        colors = [detail[0] for detail in details]
        wedges = draw_multicolor_circle(ax, point[0], point[1], colors)
        patches.extend(wedges)

    for patch in patches:
        highlight_wedges(patch, False)

    handles = [plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=color, markersize=10, label=family) for family, color in family_colors.items()]
    ax.legend(handles=handles, loc='upper right')

    ax.axis('equal')
    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines[['top', 'right', 'bottom', 'left']].set_visible(False)

    canvas.draw()

def on_hover(event):
    global highlighted_patch
    for patch in patches:
        if patch.contains_point([event.x, event.y]):
            if highlighted_patch is not None and highlighted_patch != patch:
                highlight_wedges(highlighted_patch, False)
            highlight_wedges(patch, True)
            highlighted_patch = patch
            break
    else:
        if highlighted_patch is not None:
            highlight_wedges(highlighted_patch, False)
        highlighted_patch = None
    canvas.draw_idle()

# 创建主窗口
root = tk.Tk()
root.title("螺旋线调整器")

fig, ax = plt.subplots(figsize=(16, 16))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack()

plot_spiral(-0.5 * np.pi)

# 绑定鼠标悬停事件
fig.canvas.mpl_connect('motion_notify_event', on_hover)

root.mainloop()