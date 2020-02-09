import json
import operator
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import bezier
import math
from matplotlib.transforms import TransformedBbox, Bbox

plt.figure(figsize=(14,10))
fig = plt.gcf()
rend = fig.canvas.get_renderer()
ax1 = plt.subplot(1, 2, 1)
ax1.set_aspect(1)

ax2 = plt.subplot(1, 2, 2)

ax1.set_xlim(-2.25,2.25)
ax1.set_ylim(-2.25,2.25)
ax2.set_xlim(-0.2, 4.2)
ax2.set_ylim(-1, 50.5)
ax2.axis('off')
ax1.axis('off')

yardstick = ax1.transData.transform([1, 0])[0] - ax1.transData.transform([0, 0])[0]
max_width = ax2.transData.transform([1, 0])[0] - ax2.transData.transform([0, 0])[0]
overs = []
orig = ax2.annotate("", xy=(0,0), xytext=(0,0), textcoords="offset points",
                    bbox=dict(boxstyle="round", fc="w"))
orig.set_visible(False)
clipped = []
tobe_recovered = 0

colors = ['blue', 'red', 'green', 'brown', 'orange', 'purple', 'lime', 'cyan']
colors_num = 0

r1 = 0.7
r2 = 2.0
rr = (r1 + r2*4) / 5.0

def initalize():
    mpl.rcParams['lines.linewidth'] = 1
    plt.rcParams.update({'font.size': 6})
    theta = np.linspace(0, 2*np.pi, 150)
    x1 = r1*np.cos(theta)
    x2 = r1*np.sin(theta)
    ax1.plot(x1, x2)

    x1 = r2*np.cos(theta)
    x2 = r2*np.sin(theta)
    ax1.plot(x1, x2)
    
    x = np.linspace(0, 3, 100)
    for i in range(51):
        y = np.repeat(i, 100)
        ax2.plot(x, y, color='black')
    y = np.linspace(0, 50, 100)
    for i in range(4):
        x = np.repeat(i, 100)
        ax2.plot(x, y, color='black')
    x = np.linspace(3, 4, 10)
    y = np.repeat(49, 10)
    ax2.plot(x, y, color='black')
    y = np.repeat(50, 10)
    ax2.plot(x, y, color='black')
    x = np.repeat(4, 10)
    y = np.linspace(49, 50, 10)
    ax2.plot(x, y, color='black')
    mpl.rcParams['lines.linewidth'] = 0.5

    for i, m in enumerate(sorted_meals):
        x = i // 50 + 0.01
        y = 49 - i % 50 + 0.1
        x2 = x + 1
        y2 = y + 1
        box = TransformedBbox(Bbox([[x, y], [x2, y2]]), ax2.transData)
        t = ax2.annotate(m, xy=(x, y), clip_box=box)
        bb = t.get_window_extent(renderer=rend)
        if bb.width > max_width:
            overs.append(i)     
        clipped.append(t)


def onclick(event):
    global colors_num
    if event.inaxes != ax2:
        return
    if event.xdata != None and event.ydata !=None:
        i = math.floor(event.xdata)
        j = math.floor(event.ydata)
        x = [i, i, i+1, i+1]
        y = [j, j+1, j+1, j]
        ax2.fill(x, y, color=colors[colors_num])
        ind = i*50 + (50-j) - 1
        connect(ind)
        colors_num = (colors_num + 1) % 8
        plt.draw()


def connect(start):
    start_rad = start*2*np.pi/count_meal
    xi = r1 * np.cos(start_rad)  # inner cicrle
    yi = r1 * np.sin(start_rad)
    for i in dishes [sorted_meals[start]]:
        o_rad = 2*np.pi/count_ind * sorted_ind.index(i)
        xo = r2 * np.cos(o_rad)    # outer circle
        yo = r2 * np.sin(o_rad)
        if o_rad - start_rad < 0 and o_rad - start_rad + 2*np.pi < np.pi:
            r_rad = (2*start_rad + o_rad + 2*np.pi) / 3
        elif o_rad - start_rad < np.pi:
            r_rad = (2*start_rad + o_rad) / 3
        else:   # anticlockwise
            x = 2*np.pi - start_rad
            y = 2*np.pi - o_rad
            if y - x < 0:
                r_rad = (2*x + y + 2*np.pi) /3
            else:
                r_rad = (2*x + y) /3
            r_rad = 2*np.pi - r_rad
        xr = rr * np.cos(r_rad)
        yr = rr * np.sin(r_rad)
        nodes = np.asfortranarray([[xi, xr, xo], [yi, yr, yo]])
        curve =  bezier.Curve(nodes, degree=2)
        _ = curve.plot(num_pts=256, ax=ax1, color=colors[colors_num])

        ang = o_rad /(2*np.pi) * 360
        ind = sorted_ind.index(i)
        if ind  == 0:
            prev_ind = count_ind - 1
        else:
            prev_ind = ind - 1
        if ind == count_ind -1:
            next_ind = 0
        else:
            next_ind = ind + 1 
        if gap[prev_ind] > gap[next_ind]:
            margin = gap[prev_ind]
        else:
            margin = gap[next_ind]
        xo_gap = (r2 + margin) * np.cos(o_rad)
        yo_gap = (r2 + margin) * np.sin(o_rad)
        if ang > 90 and ang < 270:
            ang = ang - 180
            t = ax1.text(xo_gap, yo_gap, i, color=colors[colors_num], fontsize=6, horizontalalignment='right', rotation=ang, rotation_mode='anchor')
        else:
            t = ax1.text(xo_gap, yo_gap, i, color=colors[colors_num], fontsize=6, rotation=ang, rotation_mode='anchor')
        gap[sorted_ind.index(i)] = t.get_window_extent(renderer=rend).width / yardstick 
        
        
def update_orig(ind):
    x = ind // 50 + 0.01
    y = 49 - ind % 50 + 0.1
    orig.xy = (x, y)
    text = sorted_meals[ind]
    orig.set_text(text)
    orig.get_bbox_patch().set_facecolor('yellow')
    orig.get_bbox_patch().set_alpha(1.0)


def hover(event):
    global tobe_recovered
    vis = orig.get_visible()
    if event.inaxes != ax2:
        return
    if event.xdata != None and event.ydata !=None:
        i = math.floor(event.xdata)
        j = math.floor(event.ydata)
        ind = i*50 + (50-j) - 1
        if ind in overs:
            update_orig(ind)
            orig.set_visible(True)
            clipped[ind].set_visible(False)
            if ind+50 < count_meal:
                clipped[ind+50].set_visible(False)
            tobe_recovered = ind
            fig.canvas.draw_idle()
        else:
            if vis:
                orig.set_visible(False)
                clipped[tobe_recovered].set_visible(True)
                if tobe_recovered+50 < count_meal:
                    clipped[tobe_recovered+50].set_visible(True)
                fig.canvas.draw_idle()

# main 
dishes = {}
meals = []
ingredients = []
count_meal = 0
with open('meals.json') as json_file:
    data = json.load(json_file)
    for p in data:
        material = []
        count_meal += 1
        for i in data[p]['ingredients']:
            material.append(i)
            if not i in ingredients:
                ingredients.append(i)
        dishes[p] = material
        meals.append(p)
        
sorted_meals = sorted(meals)
sorted_ind = sorted(ingredients)
count_ind = len(sorted_ind)
gap = [0.01 for i in range(count_ind)]

initalize()

cid = fig.canvas.mpl_connect('button_press_event', onclick)
fig.canvas.mpl_connect("motion_notify_event", hover)

plt.show()


