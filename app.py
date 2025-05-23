import streamlit as st
import numpy as np
from math import log10, radians, sin, cos, atan2, degrees
import folium
from streamlit_folium import st_folium

def watt_to_dBm(P_watt):
    if P_watt <= 0:
        raise ValueError("Công suất nguồn phát phải > 0 W")
    return 10 * np.log10(P_watt * 1000)

def calculate_distance_with_power(freq_mhz, signal_dBuV_m, h_rx, power_tx_watt):
    """
    Tính khoảng cách (km) theo FSPL có xét công suất nguồn phát (dBm),
    tín hiệu thu (dBm), tần số (MHz), chiều cao anten thu (m)
    Giả định anten phát và thu có độ lợi 0 dBi (có thể bổ sung nếu có)
    """
    signal_dBm = signal_dBuV_m - 120
    p_tx_dBm = watt_to_dBm(power_tx_watt)

    # Tính FSPL tương ứng
    fspl = p_tx_dBm - signal_dBm

    # Tính khoảng cách d (km)
    val = fspl - 32.45 - 20 * log10(freq_mhz)
    dist_log = val / 20
    distance_km = 10 ** dist_log

    return distance_km

def calculate_destination(lat1, lon1, azimuth_deg, distance_km):
    R = 6371.0  # km
    brng = radians(azimuth_deg)
    lat1_rad = radians(lat1)
    lon1_rad = radians(lon1)

    lat2 = np.arcsin(sin(lat1_rad)*cos(distance_km/R) + cos(lat1_rad)*sin(distance_km/R)*cos(brng))
    lon2 = lon1_rad + atan2(sin(brng)*sin(distance_km/R)*cos(lat1_rad), cos(distance_km/R) - sin(lat1_rad)*sin(lat2))

    return degrees(lat2), degrees(lon2)

st.title("🔎 Tính toán vị trí nguồn phát với công suất và chiều cao anten phát")

with st.form("input_form"):
    lat_rx = st.number_input("Vĩ độ anten thu", value=21.0285, format="%.6f")
    lon_rx = st.number_input("Kinh độ anten thu", value=105.8542, format="%.6f")
    freq = st.number_input("Tần số thu (MHz)", min_value=1.0, value=422.0)
    signal = st.number_input("Mức tín hiệu thu (dBμV/m)", value=85.0)
    h_rx = st.number_input("Chiều cao anten thu (m)", min_value=1.0, value=80.0)
    power_tx = st.number_input("Công suất nguồn phát (W)", min_value=0.01, value=100.0, format="%.3f")
    azimuth = st.number_input("Góc phương vị (độ)", min_value=0.0, max_value=360.0, value=45.0)
    submitted = st.form_submit_button("Tính toán vị trí nguồn phát")

if submitted:
    try:
        dist = calculate_distance_with_power(freq, signal, h_rx, power_tx)
        lat_src, lon_src = calculate_destination(lat_rx, lon_rx, azimuth, dist)

        st.success(f"Khoảng cách đến nguồn phát: {dist:.4f} km")
        st.success(f"Tọa độ nguồn phát (lat, lon): ({lat_src:.6f}, {lon_src:.6f})")

        # Tạo bản đồ folium với key để tránh nháy
        m = folium.Map(location=[lat_rx, lon_rx], zoom_start=13)
        folium.Marker([lat_rx, lon_rx], tooltip="Anten thu", icon=folium.Icon(color='blue')).add_to(m)
        folium.Marker([lat_src, lon_src], tooltip="Nguồn phát", icon=folium.Icon(color='red')).add_to(m)
        folium.PolyLine(
            locations=[[lat_rx, lon_rx], [lat_src, lon_src]],
            color='blue',
            weight=4,
            opacity=0.7
        ).add_to(m)

        st_folium(m, width=700, height=500, key="map_no_flicker")
    except Exception as e:
        st.error(f"Lỗi trong tính toán: {e}")
