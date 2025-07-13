import os
import numpy as np
import pandas as pd
import folium
import json
import re
import time
import math
import heapq


# -------------------- A* Algoritması --------------------

def heuristic(a, b):
    # Euclidean distance
    return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)

def astar(start, goal, grid):
    rows, cols = grid.shape
    open_set = []
    heapq.heappush(open_set, (0 + heuristic(start, goal), 0, start, [start]))
    visited = set()

    def neighbors(node):
        r, c = node
        directions = [
            (1, 0), (-1, 0), (0, 1), (0, -1),
            (-1, -1), (-1, 1), (1, -1), (1, 1)  # 8 yönlü hareket
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

# -------------------- Grid - GPS dönüşüm --------------------

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

# -------------------- CSV'den GPS Koordinatları --------------------

def load_gps_coordinates_from_csv(csv_path):
    df = pd.read_csv(csv_path)
    coords = []
    for raw in df['data']:
        try:
            decoded = raw.encode('utf-8').decode('unicode_escape')
            match = re.search(r'Latitude: ([\d\.]+) N, Longitude: ([\d\.]+) E', decoded)
            if match:
                lat = float(match.group(1))
                lon = float(match.group(2))
                coords.append((lat, lon))
        except:
            continue
    return coords

# -------------------- Animasyonlu rota çizimi --------------------

def animasyonlu_harita(path_latlon, bounds, grid_size, engeller, start_pos, goal_pos, save_path):
    m = folium.Map(location=start_pos, zoom_start=17)

    # Engelleri işaretle
    for e in engeller:
        folium.CircleMarker(
            location=[e['lat'], e['lon']],
            radius=5,
            color='red',
            fill=True,
            fill_opacity=0.7,
            popup='Engel'
        ).add_to(m)

    # Başlangıç ve hedef işaretle
    folium.Marker(location=start_pos, popup="Başlangıç", icon=folium.Icon(color='green')).add_to(m)
    folium.Marker(location=goal_pos, popup="Hedef", icon=folium.Icon(color='red')).add_to(m)

    # Rota çizimi için PolyLine
    folium.PolyLine(path_latlon, color='blue', weight=5, opacity=0.7).add_to(m)

    # Araç marker (Animasyon için)
    vehicle_marker = folium.Marker(location=path_latlon[0], icon=folium.Icon(icon="arrow-up", prefix='fa', color='blue'))
    vehicle_marker.add_to(m)

    # Basit animasyon (her nokta için marker'ı güncelleyen JS kodu)
    move_js = f"""
        var latlngs = {path_latlon};
        var marker = {vehicle_marker.get_name()};
        var index = 0;
        function moveMarker() {{
            marker.setLatLng(latlngs[index]);
            index++;
            if (index < latlngs.length) {{
                setTimeout(moveMarker, 500);
            }}
        }}
        moveMarker();
    """

    m.get_root().html.add_child(folium.Element(f'<script>{move_js}</script>'))
    m.save(save_path)
    print(f"Harita kaydedildi: {save_path}")

# -------------------- Ana Fonksiyon --------------------

def main():
    csv_path = r"D:\MAVARSYS\01_Calismalar\01_Rota_Planlama\paketler\rota_planlama_py\koordinatlar.csv"
    hedef_json = "hedef_koordinat.json"
    engel_json = "engeller.json"

    coords = load_gps_coordinates_from_csv(csv_path)
    if not coords:
        print("CSV'den koordinat yüklenemedi!")
        return

    # Bounds hesapla (küçük bir margin ile)
    latitudes = [lat for lat, lon in coords]
    longitudes = [lon for lat, lon in coords]
    margin = 0.0005
    lat_min = min(latitudes) - margin
    lat_max = max(latitudes) + margin
    lon_min = min(longitudes) - margin
    lon_max = max(longitudes) + margin
    bounds = [lat_min, lon_min, lat_max, lon_max]

    grid_size = (60, 60)
    grid = np.zeros(grid_size)

    # Engelleri oku ve gridde işaretle
    if os.path.exists(engel_json):
        with open(engel_json, 'r', encoding='utf-8') as f:
            engeller = json.load(f)
        for e in engeller:
            r, c = latlon_to_grid(e['lat'], e['lon'], bounds, grid_size)
            grid[r, c] = 1
    else:
        engeller = []

    # Başlangıç ve hedef noktaları
    start_latlon = coords[0]
    if not os.path.exists(hedef_json):
        print(f"{hedef_json} bulunamadı!")
        return

    with open(hedef_json, 'r', encoding='utf-8') as f:
        hedef_data = json.load(f)
    goal_latlon = (hedef_data['lat'], hedef_data['lon'])

    start = latlon_to_grid(*start_latlon, bounds, grid_size)
    goal = latlon_to_grid(*goal_latlon, bounds, grid_size)

    # Başlangıç ya da hedef engelin üstünde ise hata
    if grid[start[0], start[1]] == 1 or grid[goal[0], goal[1]] == 1:
        print("Başlangıç veya hedef engel üzerinde!")
        return

    # A* ile rota hesapla
    path = astar(start, goal, grid)
    if path is None:
        print("Yol bulunamadı!")
        return

    # Rota koordinatlarını lat/lon’a çevir
    path_latlon = [grid_to_latlon(r, c, bounds, grid_size) for r, c in path]

    # Animasyonlu harita oluştur
    animasyonlu_harita(path_latlon, bounds, grid_size, engeller, start_latlon, goal_latlon, "rota_animasyon.html")

if __name__ == "__main__":
    main()
