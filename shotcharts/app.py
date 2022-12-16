import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, Arc
import seaborn as sns

ax = None
lw = 1
color = 'gray'
outer_lines = True

plt.figure(figsize=(12,11))

if ax is None:
    ax = plt.gca()

# Basketball Hoop
hoop = Circle((0, 0), radius=7.5, linewidth=lw, color=color, fill=False)

# Create Backboard
backboard = Rectangle((-30, -12.5), 60, 0, linewidth=lw, color=color)

# The Paint
# Outer box of paint
outer_box = Rectangle((-80, -47.5), 160, 190, linewidth=lw, color=color, fill=False)

# Inner box
inner_box = Rectangle((-60, -47.5), 120, 190, linewidth=lw, color=color, fill=False)

# Free throw top arc
top_free_throw = Arc((0, 142.5), 120, 120, theta1=0, theta2=180, linewidth=lw, color=color, fill=False)

# Free throw bottom arc
bottom_free_throw = Arc((0, 142.5), 120, 120, theta1=180, theta2=0, linewidth=lw, color=color, linestyle='dashed')

# Restricted Zone
restricted = Arc((0,0), 80, 80, theta1=0, theta2=180, linewidth=lw, color=color)

# Three point line
corner_three_a = Rectangle((-220, -47.5), 0, 140, linewidth=lw, color=color)
corner_three_b = Rectangle((220, -47.5), 0, 140, linewidth=lw, color=color)
three_arc = Arc((0,0,), 475, 475, theta1=22, theta2=158, linewidth=lw, color=color)

# Center court
center_outer_arc = Arc((0, 422.5), 120, 120, theta1=180, theta2=0, linewidth=lw, color=color)
center_inner_arc = Arc((0, 422.5), 40, 40, theta1=180, theta2=0, linewidth=lw, color=color)

court_elements = [hoop, backboard, outer_box, inner_box, top_free_throw, bottom_free_throw, restricted, corner_three_a, corner_three_b, three_arc,
                  center_inner_arc, center_outer_arc]

if outer_lines:
    outer_lines = Rectangle((-250, -47.5), 500, 470, linewidth=lw, color=color, fill=False)
    court_elements.append(outer_lines)

for element in court_elements:
    ax.add_patch(element)

plt.xlim(-300,300)
plt.ylim(-100,500)
plt.show()