 t = (0:0.1:10)';  % zaman vektörü (10 saniye, 0.1 sn aralýk)
 
 lat_ref    = 40.0 * ones(length(t),1); % sabit 40.0 deðeri
 lon_ref    = 29.0 * ones(length(t),1); % sabit 40.0 deðeri
 lat_target = 40.0005 * ones(length(t),1); % sabit 40.0 deðeri
 lon_target = 29.0007 * ones(length(t),1); % sabit 40.0 deðeri
 R          = 6371000 * ones(length(t),1); % sabit 40.0 deðeri

lat_ref    = [t lat_ref]; % zaman ve veri sütunlarýný birleþtir
lon_ref    = [t lon_ref]; % zaman ve veri sütunlarýný birleþtir
lat_target = [t lat_target]; % zaman ve veri sütunlarýný birleþtir
lon_target = [t lon_target]; % zaman ve veri sütunlarýný birleþtir
R          = [t R]; % zaman ve veri sütunlarýný birleþtir