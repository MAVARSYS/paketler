import numpy as np
import folium
import pandas as pd
import heapq
import json
import re

# -------------------- A* için yardımcı fonksiyonlar --------------------

def heuristic(a, b):
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5  # Euclidean

def astar(start, goal, grid):
    rows, cols = grid.shape
    open_set = []
    heapq.heappush(open_set, (0 + heuristic(start, goal), 0, start, [start]))
    visited = set()

    def neighbors(node):
        r, c = node
        directions = [
            (1, 0), (-1, 0), (0, 1), (0, -1),     # N, S, E, W
            (-1, -1), (-1, 1), (1, -1), (1, 1)    # NW, NE, SW, SE
        ]
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 0:
                yield (nr, nc)

    while open_set:
        f, g, current, path = heapq.heappop(open_set)
        if current == goal:
            return path
        if current in visited:
            continue
        visited.add(current)
        for n in neighbors(current):
            if n not in visited:
                new_g = g + heuristic(current, n)
                new_f = new_g + heuristic(n, goal)
                heapq.heappush(open_set, (new_f, new_g, n, path + [n]))
    return None

# -------------------- Grid ↔ GPS Dönüşümü --------------------

def latlon_to_grid(lat, lon, bounds, grid_size):
    lat_min, lon_min, lat_max, lon_max = bounds
    rows, cols = grid_size
    row = int((lat_max - lat) / (lat_max - lat_min) * (rows - 1))
    col = int((lon - lon_min) / (lon_max - lon_min) * (cols - 1))
    return row, col

def grid_to_latlon(row, col, bounds, grid_size):
    lat_min, lon_min, lat_max, lon_max = bounds
    rows, cols = grid_size
    lat = lat_max - (row / (rows - 1)) * (lat_max - lat_min)
    lon = lon_min + (col / (cols - 1)) * (lon_max - lon_min)
    return lat, lon

# -------------------- GPS CSV'den yükle --------------------

def load_gps_coordinates_from_csv(csv_path):
    df = pd.read_csv(csv_path)
    gps_coords = []
    for raw in df['data']:
        try:
            decoded = raw.encode('utf-8').decode('unicode_escape')
            match = re.search(r'Latitude: ([\d\.]+) N, Longitude: ([\d\.]+) E', decoded)
            if match:
                lat = float(match.group(1))
                lon = float(match.group(2))
                gps_coords.append((lat, lon))
        except:
            continue
    return gps_coords

# -------------------- Ana Program --------------------

def main():
    # Dosya yolları
    csv_path = r"D:\MAVARSYS\01_Calismalar\01_Rota_Planlama\paketler\rota_planlama_py\koordinatlar.csv"
    hedef_json_path = "hedef_koordinat.json"

    coords = load_gps_coordinates_from_csv(csv_path)
    if not coords:
        print("Koordinat bulunamadı.")
        return

    # Bounds'ı veriden otomatik al
    latitudes = [lat for lat, lon in coords]
    longitudes = [lon for lat, lon in coords]
    margin = 0.0005
    lat_min = min(latitudes) - margin
    lat_max = max(latitudes) + margin
    lon_min = min(longitudes) - margin
    lon_max = max(longitudes) + margin
    bounds = [lat_min, lon_min, lat_max, lon_max]

    # Grid boyutu ve engel
    grid_size = (60, 60)
    grid = np.zeros(grid_size)
    grid[25:30, 15:45] = 1  # Statik engel

    # Başlangıç noktası
    start = latlon_to_grid(*coords[0], bounds, grid_size)

    # Haritada seçilmiş hedef koordinatını oku
    with open(hedef_json_path) as f:
        hedef_data = json.load(f)
    goal_latlon = (hedef_data['lat'], hedef_data['lon'])
    goal = latlon_to_grid(*goal_latlon, bounds, grid_size)

    print(f"Start grid: {start}, Goal grid: {goal}")

    if grid[start[0], start[1]] == 1 or grid[goal[0], goal[1]] == 1:
        print("Start veya Goal engel üstünde!")
        return

    # A* rotasını bul
    path = astar(start, goal, grid)
    if path is None:
        print("Yol bulunamadı.")
        return

    print(f"Yol uzunluğu: {len(path)}")

    # Harita görselleştirme
    center_lat, center_lon = coords[0]
    m = folium.Map(location=[center_lat, center_lon], zoom_start=17)

    # Başlangıç ve hedef
    folium.Marker(location=coords[0], popup="Start", icon=folium.Icon(color='green')).add_to(m)
    folium.Marker(location=goal_latlon, popup="Goal", icon=folium.Icon(color='red')).add_to(m)

    # Statik engelleri çiz
    for r in range(grid_size[0]):
        for c in range(grid_size[1]):
            if grid[r, c] == 1:
                lat, lon = grid_to_latlon(r, c, bounds, grid_size)
                folium.CircleMarker(location=[lat, lon], radius=2, color='black', fill=True).add_to(m)

    # A* yolunu çiz
    path_latlon = [grid_to_latlon(r, c, bounds, grid_size) for r, c in path]
    folium.PolyLine(path_latlon, color="blue", weight=4, opacity=0.7, tooltip="A* Rota").add_to(m)

    # Kaydet ve göster
    m.save("astar_8_yon_harita.html")
    print("Harita kaydedildi: astar_8_yon_harita.html")

if __name__ == "__main__":
    main()
