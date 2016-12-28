CREATE TABLE stock_band_group_data(
s_code VARCHAR(30) NOT NULL,
group_info_oid INT NOT NULL,
band_group_id INT NOT NULL,
band_num INT NOT NULL,
price_ratio FLOAT(5,2) NOT NULL,
max_reverse_ratio FLOAT(5,2) NOT NULL,
group_duration_trade INT NOT NULL,
group_duration_date INT NOT NULL,
seqnum INT,
start_date DATE NOT NULL,
end_date DATE NOT NULL,
price_start FLOAT(6,2) NOT NULL,
price_end FLOAT(6,2) NOT NULL
);