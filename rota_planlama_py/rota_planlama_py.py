import numpy as np
import pandas as pd
import folium
from folium.plugins import TimestampedGeoJson
import re
import heapq
from datetime import datetime, timedelta

# ------------------------
# A* Algoritması
# ------------------------
def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])  # Manhattan mesafesi

def astar(start, goal, grid):
    rows, cols = grid.shape
    open_set = []
    heapq.heappush(open_set, (0 + heuristic(start, goal), 0, start, [start]))  # (f, g, node, path)
    visited = set()

    def neighbors(node):
        r, c = node
        for nr, nc in [(r+1,c), (r-1,c), (r,c+1), (r,c-1)]:
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
                new_g = g + 1
                new_f = new_g + heuristic(n, goal)
                heapq.heappush(open_set, (new_f, new_g, n, path + [n]))

    return None  # Yol bulunamadı

# ------------------------
# GPS <-> Grid dönüşüm fonksiyonları
# ------------------------
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

# ------------------------
# CSV'den GPS verisi alma
# ------------------------
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

# ------------------------
# Ana program
# ------------------------

def main():
    # Parametreler
    grid_size = (50, 50)
    bounds = [41.052, 28.592, 41.0423, 28.6052]

    # Grid oluştur, statik engel ekle
    grid = np.zeros(grid_size)
    grid[20:25, 10:40] = 1  # Engel bölgesi

    # CSV dosya yolu
    csv_path = r"D:\MAVARSYS\01_Calismalar\01_Rota_Planlama\paketler\rota_planlama_py\koordinatlar.csv"
    coords = load_gps_coordinates_from_csv(csv_path)


    if not coords:
        print("Koordinat bulunamadı.")
        return
    # Otomatik bounds belirle
    latitudes = [lat for lat, lon in coords]
    longitudes = [lon for lat, lon in coords]
    margin = 0.0005
    lat_min = min(latitudes) - margin
    lat_max = max(latitudes) + margin
    lon_min = min(longitudes) - margin
    lon_max = max(longitudes) + margin
    bounds = [lat_min, lon_min, lat_max, lon_max] 

    # Grid oluştur
    grid_size = (50, 50)
    grid = np.zeros(grid_size)
    grid[20:25, 10:40] = 1  # Statik engel  

    # Start / goal dönüşümü
    goal_latlon = (41.0786, 28.6252)  # haritada tıkladığın nokta

    start = latlon_to_grid(*coords[0], bounds, grid_size)
    goal = latlon_to_grid(*goal_latlon, bounds, grid_size)

    # A* ile yol bul
    path = astar(start, goal, grid)

    print(f"Start grid koordinatı: {start}, değeri: {grid[start[0], start[1]]}")
    print(f"Goal grid koordinatı: {goal}, değeri: {grid[goal[0], goal[1]]}")


    if path is None:
        print("Yol bulunamadı.")
        return

    print(f"Yol bulundu, uzunluk: {len(path)}")

    # Harita oluştur
    center_lat, center_lon = coords[0]
    m = folium.Map(location=[center_lat, center_lon], zoom_start=15)

    # Zaman başlangıcı
    start_time = datetime.now()

    # Yol noktalarını GeoJSON formatına dönüştür
    features = []
    for i, (r, c) in enumerate(path):
        lat, lon = grid_to_latlon(r, c, bounds, grid_size)
        time = (start_time + timedelta(seconds=i)).isoformat()
        features.append({
            'type': 'Feature',
            'geometry': {'type': 'Point', 'coordinates': [lon, lat]},
            'properties': {
                'time': time,
                'style': {'color': 'red'},
                'icon': 'circle',
                'iconstyle': {
                    'fillColor': 'red',
                    'fillOpacity': 0.8,
                    'stroke': 'true',
                    'radius': 6
                },
                'popup': f"Path point {i+1}: {lat:.6f}, {lon:.6f}"
            }
        })

    # Statik engelleri yeşil renkte göster
    for r in range(grid_size[0]):
        for c in range(grid_size[1]):
            if grid[r, c] == 1:
                lat, lon = grid_to_latlon(r, c, bounds, grid_size)
                folium.CircleMarker(location=[lat, lon], radius=3, color='green', fill=True, fill_opacity=0.5).add_to(m)

    # Animasyon ekle
    timestamped_geojson = {
        'type': 'FeatureCollection',
        'features': features,
    }

    TimestampedGeoJson(
        timestamped_geojson,
        period='PT1S',
        add_last_point=True,
        auto_play=True,
        loop=False,
        max_speed=1,
        loop_button=True,
        date_options='YYYY/MM/DD HH:mm:ss',
        time_slider_drag_update=True
    ).add_to(m)

    # Haritayı kaydet
    output_file = 'astar_path_animation.html'
    m.save(output_file)
    print(f"Animasyon haritası '{output_file}' olarak kaydedildi.")

if __name__ == "__main__":
    main()
