maxNumCompThreads('automatic')

% Shapefile oku (ayný klasörde olduðundan dosya adý yeterli)
S = shaperead('D:\MAVARSYS\01_Calismalar\01_Rota_Planlama\paketler\rota_planlama_matlab\gshhg-shp-2.3.7\GSHHS_shp\h\GSHHS_h_L1');
%%  Türkiye sýnýr kutusu
latlim = [35 43.5];     % Güney Akdeniz’den Karadeniz kuzeyine kadar
lonlim = [25 46];       % Yunan sýnýrýndan Hakkâri doðusuna kadar

% Türkiye civarýndaki poligonlarý seç
S_filtered = S(arrayfun(@(s) ...
    any(s.Y > latlim(1) & s.Y < latlim(2) & ...
        s.X > lonlim(1) & s.X < lonlim(2)), S));
%% Harita penceresi
figure;
axesm('mercator', 'MapLatLimit', latlim, 'MapLonLimit', lonlim);
framem on; gridm on; mlabel on; plabel on;
axis off;

% Arka plan rengi (deniz rengi)
setm(gca, 'FFaceColor', [0.6 0.8 1]);  % açýk mavi deniz

% Örnek: bir dikdörtgen engel (lat/lon köþeleri)
engel_lat = [40.75 40.76 40.69 40.69];
engel_lon = [28.05 28.15 28.15 28.05];

% Haritada kýrmýzý dolu poligon olarak çiz
geoshow(engel_lat, engel_lon, ...
    'DisplayType', 'polygon', ...
    'FaceColor', [1 0 0], ...
    'EdgeColor', 'k', ...               % siyah sýnýr
    'FaceAlpha', 1);                    % opak

% Çizim
for k = 1:length(S_filtered)
    lat = S_filtered(k).Y;
    lon = S_filtered(k).X;
    validIdx = ~isnan(lat) & ~isnan(lon);

    geoshow(lat(validIdx), lon(validIdx), ...
        'DisplayType', 'polygon', ...
        'FaceColor', [0.7 0.7 0.7], ...     % gri kara
        'EdgeColor', 'k', ...               % siyah sýnýr
        'FaceAlpha', 1);                    % opak
end


title('Türkiye ve Yakýn Çevresi');

%% 
% Shapefile oku
S = shaperead('ne_10m_admin_0_countries.shp');

% Türkiye'yi filtrele
turkey = S(strcmp({S.NAME}, 'Turkey'));

% Türkiye polygonunu düz plot komutuyla çiz
figure;
for k = 1:length(turkey)
    plot(turkey(k).X, turkey(k).Y, 'b-')
    hold on;
end
axis equal
title('Türkiye Haritasý (Projeksiyonsuz)');

