import streamlit as st
import numpy as np
from math import log10, radians, sin, cos, atan2, degrees
import folium
from streamlit_folium import st_folium

def calculate_distance_from_signal(freq_mhz, signal_dBuV_m, h_rx):
    """
    Tính khoảng cách (km) từ anten thu đến nguồn phát
    theo FSPL ngược:
    FSPL = 32.45 + 20*log10(d) + 20*log10(f)
    signal_dBm = signal_dBuV_m - 120
    signal_dBm = -30 - FSPL + 10*log10(h_rx+1)
    """
    signal_dBm = signal_dBuV_m - 120
    fspl = -30 + 10 * log10(h_rx + 1) - signal_dBm
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

# Streamlit UI
st.title("🔎 Tính toán vị trí nguồn phát từ tín hiệu thu")

with st.form("input_form"):
    lat_rx = st.number_input("Vĩ độ anten thu", value=21.0285, format="%.6f")
    lon_rx = st.number_input("Kinh độ anten thu", value=105.8542, format="%.6f")
    freq = st.number_input("Tần số thu (MHz)", min_value=1.0, value=422.0)
    signal = st.number_input("Mức tín hiệu thu (dBμV/m)", value=85.0)
    h_rx = st.number_input("Chiều cao anten thu (m)", min_value=1.0, value=80.0)
    azimuth = st.number_input("Góc phương vị (độ)", min_value=0.0, max_value=360.0, value=45.0)
    submitted = st.form_submit_button("Tính toán vị trí nguồn phát")

if submitted:
    try:
        dist = calculate_distance_from_signal(freq, signal, h_rx)
        lat_src, lon_src = calculate_destination(lat_rx, lon_rx, azimuth, dist)

        st.success(f"Khoảng cách đến nguồn phát: {dist:.4f} km")
        st.success(f"Tọa độ nguồn phát (lat, lon): ({lat_src:.6f}, {lon_src:.6f})")

        # Tạo bản đồ
        m = folium.Map(location=[lat_rx, lon_rx], zoom_start=13)
        folium.Marker([lat_rx, lon_rx], tooltip="Anten thu", icon=folium.Icon(color='blue')).add_to(m)
        folium.Marker([lat_src, lon_src], tooltip="Nguồn phát", icon=folium.Icon(color='red')).add_to(m)
        folium.PolyLine(
            locations=[[lat_rx, lon_rx], [lat_src, lon_src]],
            color='blue',
            weight=4,
            opacity=0.7
        ).add_to(m)

        st_folium(m, width=700, height=500)
    except Exception as e:
        st.error(f"Lỗi trong tính toán: {e}")
