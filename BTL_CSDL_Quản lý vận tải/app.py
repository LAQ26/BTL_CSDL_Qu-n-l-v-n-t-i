import streamlit as st
import mysql.connector
import pandas as pd
from datetime import date

st.set_page_config(page_title="Hệ Thống Quản Lý Vận Tải", page_icon="🚌", layout="wide")

# --- CUSTOM CSS LÀM ĐẸP GIAO DIỆN ---
st.markdown("""
<style>
    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        padding: 15px 20px;
        border-radius: 12px;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
    }
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s;
    }
    .main-banner {
        background: linear-gradient(90deg, #1E3A8A 0%, #2563EB 100%);
        padding: 20px 25px;
        border-radius: 12px;
        color: white;
        margin-bottom: 20px;
    }
    .main-banner h2 {
        margin: 0;
        font-size: 24px;
        color: white;
    }
    .main-banner p {
        margin: 5px 0 0 0;
        opacity: 0.9;
        font-size: 14px;
    }
</style>
""", unsafe_allow_html=True)

# --- KẾT NỐI CSDL ---
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="QuanLyVanTai"
    )

def run_query(query, params=None):
    conn = get_connection()
    df = pd.read_sql(query, conn, params=params)
    conn.close()
    return df

def execute_sql(query, params=None):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        conn.commit()
        return True, "Thao tác thành công!"
    except mysql.connector.Error as err:
        return False, f"Lỗi CSDL: {err.msg}"
    finally:
        cursor.close()
        conn.close()

# =====================================================================
# VỊ TRÍ 1: ẢNH MINH HỌA Ở MÀN HÌNH ĐĂNG NHẬP
# =====================================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    col_l, col_c, col_r = st.columns([1, 1.3, 1])
    with col_c:
        st.markdown("<br>", unsafe_allow_html=True)
        with st.container(border=True):
            # <--- ẢNH BÌA XE KHÁCH Ở ĐÂY (Có thể thay bằng "banner_xe.jpg" nếu lưu trong máy)
            st.image("baner.jpg", use_container_width=True)
            st.markdown("### 🚌 HỆ THỐNG QUẢN LÝ VẬN TẢI")
            st.caption("Vui lòng đăng nhập để truy cập hệ thống điều hành")
            user = st.text_input("Tên đăng nhập", placeholder="Nhập admin...")
            pwd = st.text_input("Mật khẩu", type="password", placeholder="Nhập 123456...")
            if st.button("Đăng nhập hệ thống", type="primary", use_container_width=True):
                if user == "admin" and pwd == "123456":
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("❌ Sai tài khoản hoặc mật khẩu!")
    st.stop()

# =====================================================================
# VỊ TRÍ 2: LOGO HÃNG XE TRÊN THANH MENU BÊN TRÁI (SIDEBAR)
# =====================================================================
with st.sidebar:
    # <--- LOGO XE Ở ĐÂY (Có thể thay bằng "logo.png" nếu lưu trong máy)
    st.image("https://cdn-icons-png.flaticon.com/512/3448/3448339.png", width=90)
    st.markdown("## VẬN TẢI ĐƯỜNG DÀI")
    st.caption("Hệ thống điều hành & Quản lý CSDL")
    st.divider()
    menu = st.radio(
        "DANH MỤC CHỨC NĂNG",
        [
            "💰 Bảng Lương Tài Xế",
            "📊 Thống Kê Doanh Thu",
            "🛠️ Lịch Bảo Dưỡng Xe",
            "🛣️ Điều Phối Chuyến Xe",
            "🗂️ Quản Lý Danh Mục"
        ]
    )
    st.divider()
    st.info("👤 Đang đăng nhập: **Admin**")
    if st.button("🚪 Đăng xuất", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

# ==========================================
# MỤC 1: LƯƠNG TÀI XẾ
# ==========================================
if menu == "💰 Bảng Lương Tài Xế":
    st.markdown("""
        <div class="main-banner">
            <h2>💰 BẢNG LƯƠNG TÀI XẾ THÁNG HIỆN TẠI</h2>
            <p>Tính tự động dựa trên số chuyến, vai trò (Lái chính x2 Phụ xe) và hệ số độ phức tạp tuyến đường</p>
        </div>
    """, unsafe_allow_html=True)

    q1 = """
    SELECT tx.ma_bang_lai AS 'Mã Bằng Lái', tx.ho_ten AS 'Họ Tên',
        COUNT(cx.ma_chuyen) AS 'Số Chuyến',
        COALESCE(SUM(
            CASE 
                WHEN cx.ma_lai_xe = tx.ma_bang_lai THEN 1000000 * (CASE t.do_phuc_tap WHEN 1 THEN 1.0 WHEN 2 THEN 1.2 WHEN 3 THEN 1.5 END)
                WHEN cx.ma_phu_xe = tx.ma_bang_lai THEN 500000 * (CASE t.do_phuc_tap WHEN 1 THEN 1.0 WHEN 2 THEN 1.2 WHEN 3 THEN 1.5 END)
                ELSE 0
            END
        ), 0) AS 'Lương Tháng (VNĐ)'
    FROM TaiXe tx
    LEFT JOIN ChuyenXe cx ON (tx.ma_bang_lai = cx.ma_lai_xe OR tx.ma_bang_lai = cx.ma_phu_xe)
        AND MONTH(cx.ngay_chay) = MONTH(CURDATE()) AND YEAR(cx.ngay_chay) = YEAR(CURDATE()) AND cx.ngay_chay <= CURDATE()
    LEFT JOIN TuyenXe t ON cx.ma_tuyen = t.ma_tuyen
    GROUP BY tx.ma_bang_lai, tx.ho_ten ORDER BY 4 DESC;
    """
    df_luong = run_query(q1)

    c1, c2, c3 = st.columns(3)
    c1.metric("Tổng số tài xế", f"{len(df_luong)} người")
    c2.metric("Tổng quỹ lương tháng", f"{df_luong['Lương Tháng (VNĐ)'].sum():,.0f} đ")
    top_tx = df_luong.iloc[0]['Họ Tên'] if not df_luong.empty else "N/A"
    c3.metric("Tài xế lương cao nhất", top_tx)

    st.markdown("<br>", unsafe_allow_html=True)
    col_left, col_right = st.columns([1.4, 1])

    with col_left:
        st.subheader("📋 Chi tiết bảng lương")
        st.dataframe(
            df_luong,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Lương Tháng (VNĐ)": st.column_config.NumberColumn(format="%d đ")
            }
        )
        st.download_button(
            "📥 Tải Bảng Lương (CSV)",
            df_luong.to_csv(index=False).encode('utf-8-sig'),
            "bang_luong.csv",
            "text/csv",
            type="primary"
        )

    with col_right:
        st.subheader("🔍 Lịch sử chạy xe cá nhân")
        ds_tx = run_query("SELECT ma_bang_lai, ho_ten FROM TaiXe")
        chon_tx = st.selectbox("Chọn tài xế cần xem:", ds_tx['ma_bang_lai'] + " - " + ds_tx['ho_ten'])
        ma_tx = chon_tx.split(" - ")[0]
        df_lich_su = run_query("""
            SELECT cx.ma_chuyen AS 'Mã Chuyến', cx.ngay_chay AS 'Ngày Chạy', 
                   CONCAT(t.diem_dau, ' → ', t.diem_cuoi) AS 'Tuyến Đường',
                   IF(cx.ma_lai_xe = %s, 'Lái chính', 'Phụ xe') AS 'Vai Trò'
            FROM ChuyenXe cx JOIN TuyenXe t ON cx.ma_tuyen = t.ma_tuyen
            WHERE cx.ma_lai_xe = %s OR cx.ma_phu_xe = %s
        """, (ma_tx, ma_tx, ma_tx))
        st.dataframe(df_lich_su, use_container_width=True, hide_index=True)

# ==========================================
# MỤC 2: DOANH THU XE KHÁCH
# ==========================================
elif menu == "📊 Thống Kê Doanh Thu":
    st.markdown("""
        <div class="main-banner">
            <h2>📊 THỐNG KÊ DOANH THU THEO XE KHÁCH</h2>
            <p>Báo cáo tổng hợp sản lượng vận chuyển và doanh thu bán vé theo khoảng thời gian tùy chọn</p>
        </div>
    """, unsafe_allow_html=True)

    with st.container(border=True):
        col1, col2 = st.columns(2)
        tu_ngay = col1.date_input("📅 Từ ngày:", date(2026, 11, 1))
        den_ngay = col2.date_input("📅 Đến ngày:", date.today())

    q2 = """
    SELECT xk.bien_so AS 'Biển Số', xk.hang_san_xuat AS 'Hãng Xe', xk.model AS 'Model',
        COUNT(cx.ma_chuyen) AS 'Số Chuyến',
        COALESCE(SUM(cx.so_khach * cx.gia_ve), 0) AS 'Doanh Thu (VNĐ)'
    FROM XeKhach xk
    LEFT JOIN ChuyenXe cx ON xk.bien_so = cx.bien_so AND cx.ngay_chay BETWEEN %s AND %s
    GROUP BY xk.bien_so, xk.hang_san_xuat, xk.model ORDER BY 5 DESC;
    """
    df_dt = run_query(q2, (tu_ngay, den_ngay))

    c1, c2, c3 = st.columns(3)
    c1.metric("Tổng doanh thu kỳ này", f"{df_dt['Doanh Thu (VNĐ)'].sum():,.0f} đ")
    c2.metric("Tổng số chuyến đã chạy", f"{df_dt['Số Chuyến'].sum()} chuyến")
    top_xe = df_dt.iloc[0]['Biển Số'] if not df_dt.empty else "N/A"
    c3.metric("Xe đạt doanh thu cao nhất", top_xe)

    st.markdown("<br>", unsafe_allow_html=True)
    col_t, col_c = st.columns([1.2, 1])
    with col_t:
        st.subheader("📋 Bảng số liệu chi tiết")
        st.dataframe(
            df_dt,
            use_container_width=True,
            hide_index=True,
            column_config={"Doanh Thu (VNĐ)": st.column_config.NumberColumn(format="%d đ")}
        )
        st.download_button("📥 Xuất Báo Cáo (CSV)", df_dt.to_csv(index=False).encode('utf-8-sig'), "doanh_thu.csv", "text/csv", type="primary")
    with col_c:
        st.subheader("📈 Biểu đồ so sánh")
        st.bar_chart(df_dt.set_index('Biển Số')['Doanh Thu (VNĐ)'], color="#2563EB")

# ==========================================
# MỤC 3: BẢO DƯỠNG XE
# ==========================================
elif menu == "🛠️ Lịch Bảo Dưỡng Xe":
    st.markdown("""
        <div class="main-banner">
            <h2>🛠️ THEO DÕI CHU KỲ & CẢNH BÁO BẢO DƯỠNG</h2>
            <p>Chu kỳ tiêu chuẩn 360 ngày (giảm 1 ngày mỗi 100km quy đổi theo hệ số đường khó)</p>
        </div>
    """, unsafe_allow_html=True)

    q3 = """
    WITH BaoDuongCTE AS (
        SELECT xk.bien_so, xk.model, xk.ngay_bao_duong_cuoi,
            COALESCE(SUM(t.do_dai * (CASE t.do_phuc_tap WHEN 1 THEN 1.0 WHEN 2 THEN 1.2 WHEN 3 THEN 1.5 END)), 0) AS km_quy_doi
        FROM XeKhach xk
        LEFT JOIN ChuyenXe cx ON xk.bien_so = cx.bien_so AND cx.ngay_chay > xk.ngay_bao_duong_cuoi
        LEFT JOIN TuyenXe t ON cx.ma_tuyen = t.ma_tuyen
        GROUP BY xk.bien_so, xk.model, xk.ngay_bao_duong_cuoi
    )
    SELECT bien_so AS 'Biển Số', model AS 'Model', ngay_bao_duong_cuoi AS 'Bảo Dưỡng Cuối',
        ROUND(km_quy_doi, 1) AS 'Km Quy Đổi',
        DATE_ADD(ngay_bao_duong_cuoi, INTERVAL (360 - FLOOR(km_quy_doi / 100)) DAY) AS 'Hạn Bảo Dưỡng Tiếp Theo',
        IF(DATE_ADD(ngay_bao_duong_cuoi, INTERVAL (360 - FLOOR(km_quy_doi / 100)) DAY) < CURDATE(), 'QUÁ HẠN', 'Bình thường') AS 'Trạng Thái'
    FROM BaoDuongCTE;
    """
    df_bd = run_query(q3)
    df_quahan = df_bd[df_bd['Trạng Thái'] == 'QUÁ HẠN']

    c1, c2, c3 = st.columns(3)
    c1.metric("Tổng đội xe", f"{len(df_bd)} xe")
    c2.metric("Xe đang hoạt động tốt", f"{len(df_bd) - len(df_quahan)} xe")
    c3.metric("Xe QUÁ HẠN bảo dưỡng", f"{len(df_quahan)} xe", delta=f"-{len(df_quahan)} cần xử lý" if len(df_quahan)>0 else "An toàn", delta_color="inverse")

    st.subheader("🚨 Danh Sách Xe Quá Hạn Bảo Dưỡng (Cần xử lý ngay)")
    if df_quahan.empty:
        st.success("✅ Tuyệt vời! Hiện không có xe nào quá hạn bảo dưỡng.")
    else:
        st.dataframe(df_quahan, use_container_width=True, hide_index=True)

    st.subheader("📋 Tình Trạng Toàn Bộ Đội Xe")
    st.dataframe(df_bd, use_container_width=True, hide_index=True)

    with st.container(border=True):
        st.write("**✅ Cập nhật trạng thái sau khi bảo dưỡng xong**")
        c_sel, c_btn = st.columns([2, 1])
        xe_bd = c_sel.selectbox("Chọn biển số xe vừa hoàn thành bảo dưỡng:", df_bd['Biển Số'], label_visibility="collapsed")
        if c_btn.button("Xác nhận bảo dưỡng hôm nay", type="primary", use_container_width=True):
            ok, msg = execute_sql("UPDATE XeKhach SET ngay_bao_duong_cuoi = CURDATE() WHERE bien_so = %s", (xe_bd,))
            if ok:
                st.success(msg)
                st.rerun()

# ==========================================
# MỤC 4: QUẢN LÝ CHUYẾN XE & RÀNG BUỘC
# ==========================================
elif menu == "🛣️ Điều Phối Chuyến Xe":
    st.markdown("""
        <div class="main-banner">
            <h2>🛣️ ĐIỀU PHỐI CHUYẾN XE & KIỂM SOÁT RÀNG BUỘC</h2>
            <p>Tự động kiểm tra giới hạn hành khách (Số ghế - 2) và phân tách Lái chính / Phụ xe</p>
        </div>
    """, unsafe_allow_html=True)

    tab_ds, tab_them, tab_xoa = st.tabs(["📋 Danh Sách Chuyến Xe", "➕ Thêm Chuyến Mới", "🗑️ Xóa Chuyến Xe"])

    with tab_ds:
        tu_khoa = st.text_input("🔍 Tìm kiếm nhanh theo mã chuyến hoặc biển số xe:", placeholder="Ví dụ: CX01 hoặc 29B-111.11...")
        df_cx = run_query("""
            SELECT cx.ma_chuyen AS 'Mã Chuyến', cx.bien_so AS 'Biển Số', xk.so_ghe AS 'Tổng Ghế',
                   CONCAT(t.diem_dau, ' → ', t.diem_cuoi) AS 'Tuyến Đường',
                   tx1.ho_ten AS 'Lái Chính', tx2.ho_ten AS 'Phụ Xe',
                   cx.ngay_chay AS 'Ngày Chạy', cx.so_khach AS 'Số Khách', cx.gia_ve AS 'Giá Vé'
            FROM ChuyenXe cx
            JOIN XeKhach xk ON cx.bien_so = xk.bien_so
            JOIN TuyenXe t ON cx.ma_tuyen = t.ma_tuyen
            JOIN TaiXe tx1 ON cx.ma_lai_xe = tx1.ma_bang_lai
            JOIN TaiXe tx2 ON cx.ma_phu_xe = tx2.ma_bang_lai
            ORDER BY cx.ngay_chay DESC
        """)
        if tu_khoa:
            df_cx = df_cx[df_cx['Mã Chuyến'].str.contains(tu_khoa, case=False) | df_cx['Biển Số'].str.contains(tu_khoa, case=False)]
        st.dataframe(df_cx, use_container_width=True, hide_index=True, column_config={"Giá Vé": st.column_config.NumberColumn(format="%d đ")})

    with tab_them:
        with st.form("form_them_chuyen"):
            c1, c2, c3 = st.columns(3)
            ma_chuyen = c1.text_input("Mã chuyến xe (VD: CX07)")
            ds_xe = run_query("SELECT bien_so, so_ghe FROM XeKhach")
            xe_chon = c2.selectbox("Chọn xe:", ds_xe['bien_so'] + " (" + ds_xe['so_ghe'].astype(str) + " ghế)")
            bien_so = xe_chon.split(" ")[0]
            so_ghe_xe = int(ds_xe[ds_xe['bien_so'] == bien_so]['so_ghe'].values[0])

            ds_tuyen = run_query("SELECT ma_tuyen, diem_dau, diem_cuoi FROM TuyenXe")
            tuyen_chon = c3.selectbox("Chọn tuyến:", ds_tuyen['ma_tuyen'] + " (" + ds_tuyen['diem_dau'] + " - " + ds_tuyen['diem_cuoi'] + ")")
            ma_tuyen = tuyen_chon.split(" ")[0]

            c4, c5, c6 = st.columns(3)
            ds_tx = run_query("SELECT ma_bang_lai, ho_ten FROM TaiXe")
            tx_opts = ds_tx['ma_bang_lai'] + " - " + ds_tx['ho_ten']
            lai_xe = c4.selectbox("Lái chính:", tx_opts).split(" - ")[0]
            phu_xe = c5.selectbox("Phụ xe:", tx_opts).split(" - ")[0]
            ngay_chay = c6.date_input("Ngày chạy:", date.today())

            c7, c8 = st.columns(2)
            so_khach = c7.number_input(f"Số hành khách (Tối đa {so_ghe_xe - 2} khách):", min_value=0, step=1)
            gia_ve = c8.number_input("Giá vé (VNĐ):", min_value=0, value=200000, step=10000)

            if st.form_submit_button("💾 Lưu Chuyến Xe", type="primary"):
                if not ma_chuyen:
                    st.warning("⚠️ Vui lòng nhập Mã chuyến xe!")
                elif lai_xe == phu_xe:
                    st.error("❌ Lỗi ràng buộc: Lái chính và Phụ xe không được là cùng một người!")
                elif so_khach > (so_ghe_xe - 2):
                    st.error(f"❌ Lỗi ràng buộc: Số khách ({so_khach}) vượt quá số ghế quy định ({so_ghe_xe} - 2 = {so_ghe_xe - 2})!")
                else:
                    ok, msg = execute_sql(
                        "INSERT INTO ChuyenXe VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                        (ma_chuyen, bien_so, ma_tuyen, lai_xe, phu_xe, ngay_chay, so_khach, gia_ve)
                    )
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

    with tab_xoa:
        ds_ma_cx = run_query("SELECT ma_chuyen FROM ChuyenXe")['ma_chuyen'].tolist()
        if ds_ma_cx:
            cx_del = st.selectbox("Chọn mã chuyến cần xóa:", ds_ma_cx)
            if st.button("🗑️ Xóa chuyến xe này", type="primary"):
                ok, msg = execute_sql("DELETE FROM ChuyenXe WHERE ma_chuyen = %s", (cx_del,))
                st.success(msg) if ok else st.error(msg)
                if ok: st.rerun()

# ==========================================
# MỤC 5: QUẢN LÝ DANH MỤC
# ==========================================
elif menu == "🗂️ Quản Lý Danh Mục":
    st.markdown("""
        <div class="main-banner">
            <h2>🗂️ QUẢN LÝ DANH MỤC HỆ THỐNG</h2>
            <p>Cập nhật dữ liệu gốc cho Đội xe khách, Hồ sơ tài xế và Tuyến đường khai thác</p>
        </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["🚌 Xe Khách", "👨‍✈️ Tài Xế", "🗺️ Tuyến Xe"])
    
    # =====================================================================
    # VỊ TRÍ 3: THƯ VIỆN ẢNH CÁC DÒNG XE CHỦ LỰC TRONG TAB XE KHÁCH
    # =====================================================================
    with tab1:
        st.subheader("📸 Đội Xe Chủ Lực Của Hãng")
        col_img1, col_img2, col_img3 = st.columns(3)
        col_img1.image("Hyundai Universe.jpg", caption="Hyundai Universe (45 ghế - Đường dài)", use_container_width=True)
        col_img2.image("Thaco Mobihome.jpg", caption="Thaco Mobihome (34 ghế - Giường nằm)", use_container_width=True)
        col_img3.image("Ford Transit.jpg", caption="Ford Transit (16 ghế - Tuyến ngắn)", use_container_width=True)
        
        st.divider()
        st.dataframe(run_query("SELECT * FROM XeKhach"), use_container_width=True, hide_index=True)
        with st.form("add_xe"):
            st.write("**➕ Thêm Xe Khách Mới**")
            col1, col2, col3, col4 = st.columns(4)
            bs = col1.text_input("Biển số")
            mau = col2.text_input("Màu xe")
            hang = col3.text_input("Hãng SX")
            doi = col4.number_input("Đời xe", 2000, 2026, 2024)
            col5, col6, col7, col8 = st.columns(4)
            mod = col5.text_input("Model")
            ghe = col6.number_input("Số ghế", 4, 60, 29)
            nam = col7.number_input("Số năm sử dụng", 0, 30, 2)
            nbd = col8.date_input("Ngày bảo dưỡng cuối", date.today())
            if st.form_submit_button("Thêm Xe", type="primary"):
                ok, msg = execute_sql("INSERT INTO XeKhach VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", (bs, mau, hang, doi, mod, ghe, nam, nbd))
                st.success(msg) if ok else st.error(msg)
                if ok: st.rerun()

    with tab2:
        st.dataframe(run_query("SELECT * FROM TaiXe"), use_container_width=True, hide_index=True)
        with st.form("add_tx"):
            st.write("**➕ Thêm Tài Xế Mới**")
            c1, c2, c3, c4 = st.columns(4)
            mbl = c1.text_input("Mã bằng lái")
            cmt = c2.text_input("Số CMT/CCCD")
            ten = c3.text_input("Họ tên")
            hang_bl = c4.selectbox("Hạng bằng", ["D", "E", "FC"])
            c5, c6, c7 = st.columns(3)
            dc = c5.text_input("Địa chỉ")
            ns = c6.date_input("Ngày sinh", date(1995, 1, 1))
            tn = c7.number_input("Thâm niên (năm)", 0, 40, 3)
            if st.form_submit_button("Thêm Tài Xế", type="primary"):
                ok, msg = execute_sql("INSERT INTO TaiXe VALUES (%s,%s,%s,%s,%s,%s,%s)", (mbl, cmt, ten, hang_bl, dc, ns, tn))
                st.success(msg) if ok else st.error(msg)
                if ok: st.rerun()

    with tab3:
        st.dataframe(run_query("SELECT * FROM TuyenXe"), use_container_width=True, hide_index=True)
        with st.form("add_tuyen"):
            st.write("**➕ Thêm Tuyến Xe Mới**")
            c1, c2, c3, c4, c5 = st.columns(5)
            mt = c1.text_input("Mã tuyến")
            dd = c2.text_input("Điểm đầu")
            dc = c3.text_input("Điểm cuối")
            km = c4.number_input("Độ dài (km)", 1.0, 2000.0, 100.0)
            pt = c5.selectbox("Độ phức tạp", [1, 2, 3])
            if st.form_submit_button("Thêm Tuyến", type="primary"):
                ok, msg = execute_sql("INSERT INTO TuyenXe VALUES (%s,%s,%s,%s,%s)", (mt, dd, dc, km, pt))
                st.success(msg) if ok else st.error(msg)
                if ok: st.rerun()