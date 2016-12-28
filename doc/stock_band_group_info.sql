CREATE TABLE stock_band_group_info(
oid INT NOT NULL AUTO_INCREMENT UNIQUE,
s_code VARCHAR(30) NOT NULL,
start_date DATE NOT NULL,
end_date DATE NOT NULL,
group_num INT,
group_type VARCHAR(10) NOT NULL,
threshold FLOAT(5,4) NOT NULL,
hold_type VARCHAR(20),
max_hold_duration INT,
create_date DATETIME,
refresh_date DATETIME
);