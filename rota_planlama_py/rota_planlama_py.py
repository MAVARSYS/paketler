import numpy as np
import matplotlib.pyplot as plt
from queue import PriorityQueue
import cv2
from matplotlib.backends.backend_agg import FigureCanvasAgg

# ------------------------------
# A* algoritması (visited biriktirme)
# ------------------------------

def astar_with_visited(grid, start, goal):
    rows, cols = grid.shape
    open_set = PriorityQueue()
    open_set.put((0, start))
    came_from = {}
    g_score = {start: 0}
    visited = np.zeros_like(grid)

    def heuristic(a, b):
       return ((a[0]-b[0])**2 + (a[1]-b[1])**2)**0.5


    while not open_set.empty():
        _, current = open_set.get()
        visited[current[0], current[1]] += 1  # ✅ biriktir!

        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            return path[::-1], visited

        neighbors = [
    (current[0]+1, current[1]),
    (current[0]-1, current[1]),
    (current[0], current[1]+1),
    (current[0], current[1]-1),
    (current[0]+1, current[1]+1),
    (current[0]+1, current[1]-1),
    (current[0]-1, current[1]+1),
    (current[0]-1, current[1]-1)
        ]

        for neighbor in neighbors:
            r, c = neighbor
            if 0 <= r < rows and 0 <= c < cols:
                if grid[r, c] == 1:
                    continue
                tentative_g = g_score[current] + 1
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    g_score[neighbor] = tentative_g
                    f_score = tentative_g + heuristic(neighbor, goal)
                    open_set.put((f_score, neighbor))
                    came_from[neighbor] = current

    return None, visited


# ---------------------------
# Grid ve parametreler
rows, cols = 50, 50
grid = np.zeros((rows, cols))
grid[10:15, 5:45] = 1
grid[30:35, 5:45] = 1

start = (5, 5)
goal = (45, 45)

# Global Path (statik engeller)
global_path, _ = astar_with_visited(grid, start, goal)

# Dinamik engeller
dynamic_obstacles = [
    [25, 25],  # Engel 1
    [20, 20]   # Engel 2
]

vehicle_pos = list(start)
key_pressed = []

VEHICLE_STEP_INTERVAL = 5
step_counter = 0

# --- 1) Interaktif pencere (TkAgg)
fig, ax = plt.subplots(figsize=(8, 8))

# --- 2) Video için arka planda Agg canvas
# fig2, ax2 = plt.subplots(figsize=(8, 8))
# canvas2 = FigureCanvasAgg(fig2)

frames = []

# Klavye dinleme
def on_key(event):
    global key_pressed
    key_pressed.append(event.key)
    print(f"Tuş basıldı: {event.key}")

fig.canvas.mpl_connect('key_press_event', on_key)

# ---------------------------
# Simülasyon döngüsü
# ---------------------------
for t in range(500):
    for key in key_pressed:
        if key == 'up':
            dynamic_obstacles[0][0] = max(0, dynamic_obstacles[0][0] - 1)
        elif key == 'down':
            dynamic_obstacles[0][0] = min(rows-1, dynamic_obstacles[0][0] + 1)
        elif key == 'left':
            dynamic_obstacles[0][1] = max(0, dynamic_obstacles[0][1] - 1)
        elif key == 'right':
            dynamic_obstacles[0][1] = min(cols-1, dynamic_obstacles[0][1] + 1)
        elif key == 'w':
            dynamic_obstacles[1][0] = max(0, dynamic_obstacles[1][0] - 1)
        elif key == 's':
            dynamic_obstacles[1][0] = min(rows-1, dynamic_obstacles[1][0] + 1)
        elif key == 'a':
            dynamic_obstacles[1][1] = max(0, dynamic_obstacles[1][1] - 1)
        elif key == 'd':
            dynamic_obstacles[1][1] = min(cols-1, dynamic_obstacles[1][1] + 1)
    key_pressed = []

    local_grid = np.copy(grid)
    for obs in dynamic_obstacles:
        y, x = obs
        local_grid[y, x] = 1

    local_path, visited = astar_with_visited(local_grid, tuple(vehicle_pos), goal)
    if local_path is None:
        print(f"[T={t}] Engel nedeniyle yol bulunamadı!")
        break

    if step_counter % VEHICLE_STEP_INTERVAL == 0:
        if len(local_path) > 1:
            next_pos = local_path[1]
            vehicle_pos = list(next_pos)
    step_counter += 1

    # --- 1) Interaktif pencere
    ax.clear()
    ax.imshow(local_grid, cmap='gray_r', alpha=0.5)
    ax.imshow(visited, cmap='hot', alpha=0.5)  # ✅ visited biriktikçe renkli ısı haritası
    if global_path:
        gp = np.array(global_path)
        ax.plot(gp[:, 1], gp[:, 0], 'b--', label='Global Path')
    lp = np.array(local_path)
    ax.plot(lp[:, 1], lp[:, 0], 'g-', label='Local Path')
    for i, obs in enumerate(dynamic_obstacles):
        y, x = obs
        ax.plot(x, y, 'rs', label=f'Dynamic Obstacle {i+1}')
    ax.plot(vehicle_pos[1], vehicle_pos[0], 'yo', label='Vehicle')
    ax.plot(goal[1], goal[0], 'm*', label='Goal')
    ax.legend(loc='upper right')
    ax.set_title(f"Timestep {t} | Local A* Renkli Isı Haritası")

    # --- 2) Video için Agg
    # ax2.clear()
    # ax2.imshow(local_grid, cmap='gray_r', alpha=0.5)
    # ax2.imshow(visited, cmap='hot', alpha=0.5)
    # if global_path:
    #     ax2.plot(gp[:, 1], gp[:, 0], 'b--', label='Global Path')
    # ax2.plot(lp[:, 1], lp[:, 0], 'g-', label='Local Path')
    # for i, obs in enumerate(dynamic_obstacles):
    #     y, x = obs
    #     ax2.plot(x, y, 'rs')
    # ax2.plot(vehicle_pos[1], vehicle_pos[0], 'yo')
    # ax2.plot(goal[1], goal[0], 'm*')
    # ax2.set_title(f"Timestep {t} | Video Frame")
    # ax2.legend(loc='upper right')
    # canvas2.draw()

    # w, h = fig2.canvas.get_width_height()
    # argb = np.frombuffer(canvas2.tostring_argb(), dtype='uint8').reshape(h, w, 4)
    # rgb = np.empty((h, w, 3), dtype='uint8')
    # rgb[..., 0] = argb[..., 1]
    # rgb[..., 1] = argb[..., 2]
    # rgb[..., 2] = argb[..., 3]
    # frames.append(rgb)

    plt.pause(0.01) # Oynatma hizini ayarlar

plt.ioff()
plt.show()

# ---------------------------
# Video dosyası yaz
# ---------------------------
# print("Videoyu kaydediyor...")

# h, w, _ = frames[0].shape
# out = cv2.VideoWriter('astar_simulation.mp4', cv2.VideoWriter_fourcc(*'mp4v'), 10, (w, h))
# for f in frames:
#     out.write(cv2.cvtColor(f, cv2.COLOR_RGB2BGR))
# out.release()

# print("Video kaydedildi: astar_simulation.mp4")

exit()