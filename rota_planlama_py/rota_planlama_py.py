# ------------------------------
# O zaman sana Global Path + Local Cost Map + Gerçek Zamanlı Engel Kaçınma mantığını bir Python prototipinde örnekle göstereyim.
# Bu örnek:
# ✅ Basit bir grid harita (statik engeller)
# ✅ Gerçek zamanlı dinamik engeller (simüle edilmiş)
# ✅ Bir A* fonksiyonu
# ✅ Bir örnek simülasyon döngüsü içerir.
# ✅ matplotlib ile görsel animasyon oluşturur.
# ------------------------------


import numpy as np
import matplotlib.pyplot as plt
from queue import PriorityQueue

# ------------------------------
# Basit A* Pathfinding Fonksiyonu
# ------------------------------

def astar(grid, start, goal):
    rows, cols = grid.shape
    open_set = PriorityQueue()
    open_set.put((0, start))
    came_from = {}
    g_score = {start: 0}

    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])  # Manhattan

    while not open_set.empty():
        _, current = open_set.get()

        if current == goal:
            # Yol oluştur
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            return path[::-1]  # Ters çevir

        neighbors = [
            (current[0]+1, current[1]),
            (current[0]-1, current[1]),
            (current[0], current[1]+1),
            (current[0], current[1]-1)
        ]

        for neighbor in neighbors:
            r, c = neighbor
            if 0 <= r < rows and 0 <= c < cols:
                if grid[r, c] == 1:  # Engel
                    continue
                tentative_g = g_score[current] + 1
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    g_score[neighbor] = tentative_g
                    f_score = tentative_g + heuristic(neighbor, goal)
                    open_set.put((f_score, neighbor))
                    came_from[neighbor] = current

    return None  # Yol bulunamadı


# ----------------------------------
# Statik Grid + Dinamik Engel Simüle
# ----------------------------------

# Grid boyutları
rows, cols = 50, 50
grid = np.zeros((rows, cols))

# Statik engeller (kara)
grid[10:15, 5:45] = 1
grid[30:35, 5:45] = 1

# Başlangıç ve hedef
start = (5, 5)
goal = (45, 45)

# Başlangıçta Global Path planla
global_path = astar(grid, start, goal)

# -------------------------------
# Simülasyon: Dinamik Engel + Local Planlama
# -------------------------------

# Dinamik engel (örneğin bir diğer gemi)
dynamic_obstacle_pos = [25, 25]

# Araç pozisyonu (ilk başta start)
vehicle_pos = list(start)

# Animasyon ayarları
plt.ion()
fig, ax = plt.subplots(figsize=(8, 8))

for t in range(100):
    # 1) Dinamik engel pozisyonunu değiştir (örneğin ileri geri)
    dynamic_obstacle_pos[0] += (-1)**t  # basit hareket

    # 2) Dinamik engeli grid'e yerleştir
    local_grid = np.copy(grid)
    dy, dx = dynamic_obstacle_pos
    local_grid[dy, dx] = 1

    # 3) Araç konumundan hedefe local A* planla
    local_path = astar(local_grid, tuple(vehicle_pos), goal)

    if local_path is None:
        print(f"[T={t}] Engel nedeniyle yol bulunamadı!")
        break

    # 4) Bir adım ilerle
    if len(local_path) > 1:
        next_pos = local_path[1]
        vehicle_pos = list(next_pos)

    # 5) Görselleştir
    ax.clear()
    ax.imshow(local_grid, cmap='gray_r')
    # Global path (mavi)
    if global_path:
        gp = np.array(global_path)
        ax.plot(gp[:, 1], gp[:, 0], 'b--', label='Global Path')
    # Local path (yeşil)
    lp = np.array(local_path)
    ax.plot(lp[:, 1], lp[:, 0], 'g-', label='Local Path')
    # Dinamik engel (kırmızı)
    ax.plot(dx, dy, 'rs', label='Dynamic Obstacle')
    # Araç pozisyonu (sarı)
    ax.plot(vehicle_pos[1], vehicle_pos[0], 'yo', label='Vehicle')
    # Hedef (mor)
    ax.plot(goal[1], goal[0], 'm*', label='Goal')

    ax.legend()
    ax.set_title(f"Timestep {t}")
    plt.pause(0.2)

plt.ioff()
plt.show()
