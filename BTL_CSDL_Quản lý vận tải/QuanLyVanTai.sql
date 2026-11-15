-- Active: 1794755643008@@127.0.0.1@3306@mysql
DROP DATABASE IF EXISTS QuanLyVanTai;
CREATE DATABASE QuanLyVanTai CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE QuanLyVanTai;

-- 1. TẠO BẢNG
CREATE TABLE XeKhach (
    bien_so VARCHAR(15) PRIMARY KEY,
    mau_xe VARCHAR(30) NOT NULL,
    hang_san_xuat VARCHAR(50) NOT NULL,
    doi_xe INT NOT NULL,
    model VARCHAR(50) NOT NULL,
    so_ghe INT NOT NULL CHECK (so_ghe > 2),
    so_nam_su_dung INT NOT NULL CHECK (so_nam_su_dung >= 0),
    ngay_bao_duong_cuoi DATE NOT NULL
);

CREATE TABLE TaiXe (
    ma_bang_lai VARCHAR(20) PRIMARY KEY,
    cmt VARCHAR(20) UNIQUE NOT NULL,
    ho_ten VARCHAR(100) NOT NULL,
    loai_bang_lai VARCHAR(10) NOT NULL,
    dia_chi VARCHAR(200),
    ngay_sinh DATE NOT NULL,
    tham_nien INT DEFAULT 0 CHECK (tham_nien >= 0)
);

CREATE TABLE TuyenXe (
    ma_tuyen VARCHAR(10) PRIMARY KEY,
    diem_dau VARCHAR(100) NOT NULL,
    diem_cuoi VARCHAR(100) NOT NULL,
    do_dai FLOAT NOT NULL CHECK (do_dai > 0),
    do_phuc_tap INT NOT NULL CHECK (do_phuc_tap IN (1, 2, 3))
);

CREATE TABLE ChuyenXe (
    ma_chuyen VARCHAR(15) PRIMARY KEY,
    bien_so VARCHAR(15) NOT NULL,
    ma_tuyen VARCHAR(10) NOT NULL,
    ma_lai_xe VARCHAR(20) NOT NULL,
    ma_phu_xe VARCHAR(20) NOT NULL,
    ngay_chay DATE NOT NULL,
    so_khach INT NOT NULL CHECK (so_khach >= 0),
    gia_ve DECIMAL(12, 2) NOT NULL CHECK (gia_ve >= 0),
    FOREIGN KEY (bien_so) REFERENCES XeKhach(bien_so) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (ma_tuyen) REFERENCES TuyenXe(ma_tuyen) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (ma_lai_xe) REFERENCES TaiXe(ma_bang_lai) ON UPDATE CASCADE,
    FOREIGN KEY (ma_phu_xe) REFERENCES TaiXe(ma_bang_lai) ON UPDATE CASCADE
);

-- 2. TRIGGER KIỂM TRA SỐ KHÁCH TỐI ĐA (so_ghe - 2) KHI THÊM & SỬA
CREATE TRIGGER trg_check_so_khach_ins BEFORE INSERT ON ChuyenXe
FOR EACH ROW
BEGIN
    DECLARE max_ghe INT;
    IF NEW.ma_lai_xe = NEW.ma_phu_xe THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Lai xe va phu xe khong duoc trung nhau!';
    END IF;
    SELECT so_ghe INTO max_ghe FROM XeKhach WHERE bien_so = NEW.bien_so;
    IF NEW.so_khach > (max_ghe - 2) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'So khach vuot qua (so_ghe - 2)!';
    END IF;
END;

CREATE TRIGGER trg_check_so_khach_upd BEFORE UPDATE ON ChuyenXe
FOR EACH ROW
BEGIN
    DECLARE max_ghe INT;
    IF NEW.ma_lai_xe = NEW.ma_phu_xe THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Lai xe va phu xe khong duoc trung nhau!';
    END IF;
    SELECT so_ghe INTO max_ghe FROM XeKhach WHERE bien_so = NEW.bien_so;
    IF NEW.so_khach > (max_ghe - 2) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'So khach vuot qua (so_ghe - 2)!';
    END IF;
END;

-- 3. NHẬP DỮ LIỆU MẪU
INSERT INTO XeKhach VALUES
('29B-111.11', 'Trắng', 'Hyundai', 2022, 'Universe', 45, 4, '2026-08-01'),
('29B-222.22', 'Đỏ', 'Thaco', 2021, 'Mobihome', 34, 5, '2025-11-01'), -- Xe này sẽ quá hạn bảo dưỡng
('30F-333.33', 'Xanh', 'Ford', 2023, 'Transit', 16, 3, '2026-10-15'),
('29B-444.44', 'Bạc', 'Hyundai', 2020, 'County', 29, 6, '2025-12-20'); -- Xe này chạy nhiều đèo núi -> quá hạn

INSERT INTO TaiXe VALUES
('BL001', '001090000111', 'Nguyễn Văn An', 'E', 'Hà Nội', '1990-05-12', 10),
('BL002', '001092000222', 'Trần Bình Trọng', 'E', 'Hà Nam', '1992-08-20', 8),
('BL003', '001095000333', 'Lê Hoàng Cường', 'D', 'Nam Định', '1995-02-10', 5),
('BL004', '001098000444', 'Phạm Minh Dũng', 'D', 'Thái Bình', '1998-11-25', 3);

INSERT INTO TuyenXe VALUES
('T01', 'Hà Nội', 'Hải Phòng', 120, 1),   -- Hệ số 1.0
('T02', 'Hà Nội', 'Vinh', 300, 2),        -- Hệ số 1.2
('T03', 'Hà Nội', 'Hà Giang', 320, 3),    -- Hệ số 1.5
('T04', 'Hà Nội', 'Sa Pa', 315, 3);       -- Hệ số 1.5

INSERT INTO ChuyenXe VALUES
('CX01', '29B-111.11', 'T01', 'BL001', 'BL003', '2026-11-02', 40, 150000),
('CX02', '29B-111.11', 'T02', 'BL002', 'BL004', '2026-11-05', 38, 250000),
('CX03', '30F-333.33', 'T01', 'BL003', 'BL004', '2026-11-08', 14, 150000),
('CX04', '29B-444.44', 'T03', 'BL001', 'BL002', '2026-06-15', 25, 350000),
('CX05', '29B-444.44', 'T04', 'BL001', 'BL004', '2026-11-10', 26, 350000),
('CX06', '29B-222.22', 'T03', 'BL002', 'BL003', '2026-11-12', 30, 350000);

-- 4. CÁC CÂU TRUY VẤN THEO ĐỀ BÀI
-- Truy vấn 1: Lương tháng tính đến ngày hiện tại
SELECT 
    tx.ma_bang_lai, tx.ho_ten,
    COALESCE(SUM(
        CASE 
            WHEN cx.ma_lai_xe = tx.ma_bang_lai THEN 1000000 * (CASE t.do_phuc_tap WHEN 1 THEN 1.0 WHEN 2 THEN 1.2 WHEN 3 THEN 1.5 END)
            WHEN cx.ma_phu_xe = tx.ma_bang_lai THEN 500000 * (CASE t.do_phuc_tap WHEN 1 THEN 1.0 WHEN 2 THEN 1.2 WHEN 3 THEN 1.5 END)
            ELSE 0
        END
    ), 0) AS luong_thang_hien_tai
FROM TaiXe tx
LEFT JOIN ChuyenXe cx ON (tx.ma_bang_lai = cx.ma_lai_xe OR tx.ma_bang_lai = cx.ma_phu_xe)
    AND MONTH(cx.ngay_chay) = MONTH(CURDATE())
    AND YEAR(cx.ngay_chay) = YEAR(CURDATE())
    AND cx.ngay_chay <= CURDATE()
LEFT JOIN TuyenXe t ON cx.ma_tuyen = t.ma_tuyen
GROUP BY tx.ma_bang_lai, tx.ho_ten;

-- Truy vấn 2: Doanh thu từng xe trong khoảng thời gian
SELECT 
    xk.bien_so, xk.model,
    COUNT(cx.ma_chuyen) AS so_chuyen,
    COALESCE(SUM(cx.so_khach * cx.gia_ve), 0) AS doanh_thu
FROM XeKhach xk
LEFT JOIN ChuyenXe cx ON xk.bien_so = cx.bien_so 
    AND cx.ngay_chay BETWEEN '2026-11-01' AND '2026-11-30'
GROUP BY xk.bien_so, xk.model;

-- Truy vấn 3: Ngày bảo dưỡng tiếp theo & Danh sách xe quá hạn
WITH BaoDuongCTE AS (
    SELECT 
        xk.bien_so, xk.model, xk.ngay_bao_duong_cuoi,
        COALESCE(SUM(t.do_dai * (CASE t.do_phuc_tap WHEN 1 THEN 1.0 WHEN 2 THEN 1.2 WHEN 3 THEN 1.5 END)), 0) AS km_quy_doi
    FROM XeKhach xk
    LEFT JOIN ChuyenXe cx ON xk.bien_so = cx.bien_so AND cx.ngay_chay > xk.ngay_bao_duong_cuoi
    LEFT JOIN TuyenXe t ON cx.ma_tuyen = t.ma_tuyen
    GROUP BY xk.bien_so, xk.model, xk.ngay_bao_duong_cuoi
)
SELECT 
    bien_so, model, ngay_bao_duong_cuoi,
    ROUND(km_quy_doi, 1) AS km_lam_viec,
    DATE_ADD(ngay_bao_duong_cuoi, INTERVAL (360 - FLOOR(km_quy_doi / 100)) DAY) AS ngay_bao_duong_tiep_theo,
    IF(DATE_ADD(ngay_bao_duong_cuoi, INTERVAL (360 - FLOOR(km_quy_doi / 100)) DAY) < CURDATE(), 'QUÁ HẠN', 'Bình thường') AS trang_thai
FROM BaoDuongCTE;