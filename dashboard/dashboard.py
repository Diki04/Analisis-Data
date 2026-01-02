import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import datetime
import os

# --- 1. CONFIG & SETUP ---
st.set_page_config(
    page_title="Bike Sharing Analytics By Rizkillah",
    page_icon="🚲",
    layout="wide"
)

# --- 2. STYLE & THEME ---
# Mengatur tema plot agar background putih bersih
sns.set_theme(style="white", rc={
    "axes.grid": True,
    "grid.color": "#E9ECEF",
    "figure.facecolor": "#FFFFFF",
    "axes.facecolor": "#FFFFFF",
    "axes.labelcolor": "black",
    "text.color": "black",
    "xtick.color": "black",
    "ytick.color": "black",
    "axes.spines.left": False,
    "axes.spines.right": False,
    "axes.spines.top": False,
    "axes.spines.bottom": True,
    "font.family": "sans-serif"
})

# Custom CSS untuk Insight Box (Sesuai request sebelumnya)
# SAYA MENAMBAHKAN STYLE .recommendation-box AGAR BEDA WARNA SEDIKIT (HIJAU) UNTUK PEMBEDA
st.markdown("""
<style>
.main-title {
    font-size: 3rem;
    font-weight: 800;
    text-align: center;
    margin-bottom: 1rem;
}
.insight-box {
    background-color: #262730; /* Warna latar gelap */
    color: #FFFFFF;            /* Teks putih agar terbaca */
    border-left: 5px solid #007BFF; /* Biru untuk Insight */
    padding: 15px;
    margin-top: 15px;
    border-radius: 5px;
    font-size: 16px;
}
.recommendation-box {
    background-color: #262730; 
    color: #FFFFFF;            
    border-left: 5px solid #28a745; /* Hijau untuk Rekomendasi */
    padding: 15px;
    margin-top: 10px; /* Jarak sedikit dari insight */
    border-radius: 5px;
    font-size: 16px;
}
</style>
""", unsafe_allow_html=True)

# --- 3. DATA LOADING ---
@st.cache_data
def load_data():
    # Pastikan file day_clean.csv dan hour_clean.csv ada di folder yang sama dengan script
    try:
        base_dir = os.path.dirname(__file__)
        days_path = os.path.join(base_dir, "day_clean.csv")
        hours_path = os.path.join(base_dir, "hour_clean.csv")

        days_df = pd.read_csv(days_path)
        hours_df = pd.read_csv(hours_path)
    except FileNotFoundError:
        # Fallback jika dijalankan langsung tanpa struktur folder
        days_df = pd.read_csv("day_clean.csv")
        hours_df = pd.read_csv("hour_clean.csv")

    days_df["dteday"] = pd.to_datetime(days_df["dteday"])
    hours_df["dteday"] = pd.to_datetime(hours_df["dteday"])

    return days_df, hours_df

def create_advanced_features(df):
    season_map = {1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'}
    if df['season'].dtype in ['int64', 'int32', 'float64']:
        df['season'] = df['season'].map(season_map)
    
    if 'humidity_category' not in df.columns:
        df['humidity_category'] = pd.cut(
            df['humidity'],
            bins=[0, 0.45, 0.75, 1.0],
            labels=['Terlalu kering', 'Ideal', 'Terlalu Lembab']
        )
    return df

days_df_raw, hours_df_raw = load_data()
days_df = create_advanced_features(days_df_raw)
hours_df = create_advanced_features(hours_df_raw)

# --- 4. SIDEBAR FILTER ---
min_date = days_df["dteday"].min().date()
max_date = days_df["dteday"].max().date()

with st.sidebar:
    st.header("Filter Dashboard")
    start_date, end_date = st.date_input(
        "Rentang Waktu",
        min_value=min_date,
        max_value=max_date,
        value=(min_date, max_date)
    )
    st.caption(f"Data tersedia dari {min_date} hingga {max_date}")

# Filter Dataframes
main_df_days = days_df[
    (days_df["dteday"].dt.date >= start_date) &
    (days_df["dteday"].dt.date <= end_date)
].copy()

main_df_hour = hours_df[
    (hours_df["dteday"].dt.date >= start_date) &
    (hours_df["dteday"].dt.date <= end_date)
].copy()

if main_df_days.empty:
    st.warning("⚠️ Tidak ada data untuk rentang tanggal yang dipilih.")
    st.stop()

# --- 5. TITLE & METRICS ---
st.markdown('<h1 class="main-title">🚲 Bike Sharing Analytics By Rizkillah</h1>', unsafe_allow_html=True)
st.markdown(
    """
    Dashboard ini dirancang untuk menyajikan **insight** yang komprehensif
    terkait pola penggunaan sepeda, tren permintaan, serta faktor-faktor
    yang memengaruhi performa operasional layanan bike sharing.
    """
)


st.markdown("---")

col1, col2, col3 = st.columns(3)
total_orders = main_df_days['count_cr'].sum()
total_reg = main_df_days['registered'].sum()
total_cas = main_df_days['casual'].sum()

with col1:
    st.metric("Total Penyewaan", value=f"{total_orders:,.0f}".replace(",", "."))
with col2:
    st.metric("Registered Users", value=f"{total_reg:,.0f}".replace(",", "."))
with col3:
    st.metric("Casual Users", value=f"{total_cas:,.0f}".replace(",", "."))

st.markdown("---")

# ==============================================================================
# VISUALISASI DENGAN INSIGHT BOX STYLE
# ==============================================================================

# --- VISUALISASI 1: Tren Pertumbuhan ---
with st.container():
    st.subheader("1. Tren Pertumbuhan & Distribusi Data")
    
    day_df_vis1 = main_df_days.copy()
    day_df_vis1['rolling_mean'] = day_df_vis1['count_cr'].rolling(window=30).mean()

    mean_val = day_df_vis1['count_cr'].mean()
    min_val = day_df_vis1['count_cr'].min()
    max_val = day_df_vis1['count_cr'].max()

    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(20, 6))

    sns.lineplot(x='dteday', y='count_cr', data=day_df_vis1, ax=ax[0], 
                 color='#BDC3C7', alpha=0.5, label='Data Harian (Raw)')
    sns.lineplot(x='dteday', y='rolling_mean', data=day_df_vis1, ax=ax[0], 
                 color='#2980B9', linewidth=3, label='Tren Bulanan (30-day MA)')

    if not day_df_vis1.empty:
        min_date_val = day_df_vis1.loc[day_df_vis1['count_cr'].idxmin(), 'dteday']
        max_date_val = day_df_vis1.loc[day_df_vis1['count_cr'].idxmax(), 'dteday']
        ax[0].scatter(min_date_val, min_val, color='#C0392B', s=100, zorder=5)
        ax[0].scatter(max_date_val, max_val, color='#27AE60', s=100, zorder=5) 
        ax[0].text(max_date_val, max_val + 200, f'Max: {max_val}', ha='center', color='#27AE60', fontweight='bold')
        ax[0].text(min_date_val, min_val - 500, f'Min: {min_val}', ha='center', color='#C0392B', fontweight='bold')

    ax[0].set_title('Tren Pertumbuhan Penyewaan', fontsize=16)
    ax[0].set_ylabel('Jumlah Penyewaan', fontsize=12)
    ax[0].set_xlabel('Tanggal', fontsize=12)
    ax[0].legend(loc='upper left')
    ax[0].grid(True, linestyle='--', alpha=0.5)

    sns.histplot(day_df_vis1['count_cr'], kde=True, color='#90CAF9', edgecolor='white', ax=ax[1])
    ax[1].axvline(mean_val, color='#2980B9', linestyle='--', linewidth=2, label=f'Rata-rata ({int(mean_val)})')
    
    ax[1].set_title('Distribusi Frekuensi', fontsize=16)
    ax[1].set_ylabel('Frekuensi', fontsize=12)
    ax[1].set_xlabel('Jumlah Penyewaan', fontsize=12)
    ax[1].legend()

    plt.tight_layout()
    st.pyplot(fig)
    
    # Custom Insight Box
    st.markdown(f"""
    <div class="insight-box">
    💡 <b>Key Insight:</b><br>
    Rata-rata penyewaan harian berada di angka <b>{int(mean_val):,.0f}</b>. 
    Grafik menunjukkan adanya fluktuasi, namun garis tren (Moving Average) membantu melihat pola pertumbuhan jangka panjang yang lebih jelas.
    </div>
    """, unsafe_allow_html=True)

    # ADDED RECOMMENDATION
    st.markdown("""
    <div class="recommendation-box">
    🎯 <b>Actionable Recommendation:</b><br>
    Pastikan stok sepeda selalu tersedia minimal di angka rata-rata harian. 
    Lakukan <i>maintenance</i> atau perbaikan unit besar-besaran saat tren sedang menyentuh titik terendah (Min) untuk menghindari kekurangan armada saat permintaan puncak.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

# --- VISUALISASI 2: Cuaca ---
with st.container():
    st.subheader("2. Analisis Dampak Cuaca")
    
    day_df_vis2 = main_df_days.copy()
    try:
        day_df_vis2['wind_category'] = pd.qcut(day_df_vis2['wind_speed'], q=3, labels=['Low', 'Medium', 'High'])
    except ValueError:
        day_df_vis2['wind_category'] = pd.cut(day_df_vis2['wind_speed'], bins=3, labels=['Low', 'Medium', 'High'])

    wind_order = ['Low', 'Medium', 'High']
    hum_order = ['Terlalu kering', 'Ideal', 'Terlalu Lembab'] 

    avg_wind = day_df_vis2.groupby('wind_category', observed=False)['count_cr'].mean().reset_index()
    avg_hum = day_df_vis2.groupby('humidity_category', observed=False)['count_cr'].mean().reset_index()

    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(18, 7))

    sns.barplot(x='humidity_category', y='count_cr', data=avg_hum, order=hum_order, palette='Blues', ax=ax[0])
    ax[0].set_title('Kelembaban vs Rata-rata Penyewaan', fontsize=15)
    ax[0].bar_label(ax[0].containers[1], fmt='%.0f') 

    sns.barplot(x='wind_category', y='count_cr', data=avg_wind, order=wind_order, palette='coolwarm', ax=ax[1])
    ax[1].set_title('Kecepatan Angin vs Rata-rata Penyewaan', fontsize=15)
    ax[1].bar_label(ax[1].containers[0], fmt='%.0f') 

    st.pyplot(fig)
    
    # Custom Insight Box
    st.markdown("""
    <div class="insight-box">
    💡 <b>Key Insight:</b><br>
    Kondisi lingkungan sangat berpengaruh. Pengguna cenderung menghindari cuaca yang terlalu lembab dan angin kencang (High Wind).
    Kondisi <b>Ideal Humidity</b> dan <b>Low Wind</b> menghasilkan rata-rata penyewaan tertinggi.
    </div>
    """, unsafe_allow_html=True)

    # ADDED RECOMMENDATION
    st.markdown("""
    <div class="recommendation-box">
    🎯 <b>Actionable Recommendation:</b><br>
    Integrasikan data cuaca <b>real-time</b> ke aplikasi. 
    Berikan notifikasi promosi saat cuaca diprediksi "Ideal" untuk meningkatkan penjualan, dan berikan peringatan keselamatan kepada pengguna saat cuaca "High Wind".
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

# --- VISUALISASI 3: Hari Libur ---
with st.container():
    st.subheader("3. Analisis Hari Libur vs Hari Kerja")

    temp_df = main_df_days.copy()
    temp_df['holiday_label'] = temp_df['holiday'].map({0: 'Bukan Libur', 1: 'Libur'})

    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(18, 6))

    sns.barplot(x='holiday_label', y='count_cr', data=temp_df, estimator=sum, errorbar=None, palette=["#90CAF9", "#D3D3D3"], ax=ax[0])
    ax[0].set_title('Total Volume', fontsize=16)
    
    sns.barplot(x='holiday_label', y='count_cr', data=temp_df, estimator='mean', errorbar=None, palette=["#90CAF9", "#D3D3D3"], ax=ax[1])
    ax[1].set_title('Rata-rata Harian', fontsize=16)
    
    for p in ax[1].patches:
        ax[1].annotate(f'{int(p.get_height())}', (p.get_x() + p.get_width() / 2., p.get_height()), 
                       ha = 'center', va = 'bottom', fontsize=12, weight='bold')

    plt.tight_layout()
    st.pyplot(fig)

    # Custom Insight Box
    st.markdown("""
    <div class="insight-box">
    💡 <b>Key Insight:</b><br>
    Meskipun total volume di 'Bukan Libur' jauh lebih tinggi (karena jumlah harinya lebih banyak), 
    rata-rata penyewaan harian juga menunjukkan bahwa hari kerja/biasa lebih sibuk dibandingkan hari libur nasional.
    </div>
    """, unsafe_allow_html=True)

    # ADDED RECOMMENDATION
    st.markdown("""
    <div class="recommendation-box">
    🎯 <b>Actionable Recommendation:</b><br>
    Pada <b>Hari Kerja</b>, fokuskan distribusi sepeda di area perkantoran dan stasiun transit. 
    Pada <b>Hari Libur</b>, buat paket promo "Akhir Pekan" atau "Family Bundling" untuk menarik segmen pengguna rekreasi yang lebih santai.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

# --- VISUALISASI 4: Musim ---
with st.container():
    st.subheader("4. Analisis Musiman")

    season_order = ['Spring', 'Summer', 'Fall', 'Winter']
    day_df_vis4 = main_df_days.copy()

    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(20, 6))

    sns.barplot(x='season', y='count_cr', data=day_df_vis4, estimator=sum, order=season_order, palette='coolwarm', errorbar=None, ax=ax[0])
    ax[0].set_title('Total Volume per Musim', fontsize=16)
    
    sns.boxplot(x='season', y='count_cr', data=day_df_vis4, order=season_order, palette='coolwarm', ax=ax[1])
    ax[1].set_title('Distribusi Penyewaan Harian', fontsize=16)

    plt.tight_layout()
    st.pyplot(fig)

    # Dynamic Insight Text
    best_season = "Unknown"
    if not day_df_vis4.empty:
        best_season = day_df_vis4.groupby('season', observed=False)['count_cr'].sum().idxmax()

    st.markdown(f"""
    <div class="insight-box">
    💡 <b>Key Insight:</b><br>
    Musim <b>{best_season}</b> mendominasi jumlah penyewaan sepeda. 
    Hal ini menunjukkan preferensi pengguna yang kuat terhadap kondisi cuaca pada musim tersebut dibandingkan musim lainnya.
    </div>
    """, unsafe_allow_html=True)

    # ADDED RECOMMENDATION
    st.markdown("""
    <div class="recommendation-box">
    🎯 <b>Actionable Recommendation:</b><br>
    Alokasikan anggaran pemasaran terbesar pada awal musim puncak (Fall/Summer) untuk memaksimalkan pendapatan. 
    Pada <b>Low Season</b> (Spring), terapkan strategi efisiensi biaya operasional atau tawarkan diskon <b>Early Bird</b>.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

# --- VISUALISASI 5: Hourly Trend ---
with st.container():
    st.subheader("5. Pola Aktivitas Per Jam")
    
    hourly_counts = main_df_hour.groupby('hours')['count_cr'].mean().reset_index()

    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(20, 6))

    sns.lineplot(x='hours', y='count_cr', data=hourly_counts, marker='o', color='#4A90E2', linewidth=3, ax=ax[0])
    ax[0].set_title('Tren Aktivitas Harian', fontsize=16)
    ax[0].set_xticks(range(0, 24))
    ax[0].grid(True, linestyle='--', alpha=0.5)

    sns.barplot(x='hours', y='count_cr', data=hourly_counts, color='#90CAF9', ax=ax[1])
    if not hourly_counts.empty:
        max_val_hour = hourly_counts['count_cr'].max()
        for patch in ax[1].patches:
            if patch.get_height() == max_val_hour:
                patch.set_color('#E74C3C') 
    ax[1].set_title('Ranking Volume per Jam', fontsize=16)

    plt.tight_layout()
    st.pyplot(fig)

    # Dynamic Insight Text
    peak_hour_str = "-"
    if not hourly_counts.empty:
        max_hour_row = hourly_counts.loc[hourly_counts['count_cr'].idxmax()]
        peak_hour_str = f"{int(max_hour_row['hours'])}:00"

    st.markdown(f"""
    <div class="insight-box">
    💡 <b>Key Insight:</b><br>
    Aktivitas memuncak pada jam <b>{peak_hour_str}</b> (biasanya jam pulang kerja) dan juga tinggi di pagi hari (jam berangkat kerja).
    Pola ini mengindikasikan penggunaan sepeda yang kuat untuk keperluan komuter (berangkat/pulang kerja).
    </div>
    """, unsafe_allow_html=True)

    # ADDED RECOMMENDATION
    st.markdown("""
    <div class="recommendation-box">
    🎯 <b>Actionable Recommendation:</b><br>
    Terapkan <b>Dynamic Rebalancing</b>:
    Pastikan stok sepeda penuh di area pemukiman sebelum jam 08:00 pagi, dan pindahkan stok ke area perkantoran sebelum jam 17:00 sore untuk mengakomodasi arus komuter.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

# --- VISUALISASI 6: User & Monthly ---
with st.container():
    st.subheader("6. Komposisi User & Tren Bulanan")

    day_df_vis6 = main_df_days.copy()
    monthly_counts = day_df_vis6.resample('M', on='dteday')['count_cr'].sum().reset_index()

    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(20, 8))

    ax[0].pie([day_df_vis6['casual'].sum(), day_df_vis6['registered'].sum()], 
              labels=['Casual', 'Registered'], autopct='%1.1f%%', colors=["#D3D3D3", "#90CAF9"], 
              explode=(0, 0.1), shadow=True, startangle=90, textprops={'fontsize': 14})
    ax[0].set_title("Perbandingan Tipe User", fontsize=16)

    if not monthly_counts.empty:
        ax[1].plot(monthly_counts['dteday'], monthly_counts['count_cr'], marker='o', linewidth=2, color='#4A90E2')
        ax[1].set_title("Tren Penyewaan Bulanan", fontsize=16)
        ax[1].grid(color='lightgrey', linestyle='--', alpha=0.5)

    plt.tight_layout()
    st.pyplot(fig)

    st.markdown("""
    <div class="insight-box">
    💡 <b>Key Insight:</b><br>
    Mayoritas pengguna adalah <b>Registered User</b>. 
    Hal ini penting untuk strategi bisnis: fokus pada retensi pengguna terdaftar sambil mencoba mengonversi pengguna kasual menjadi member.
    </div>
    """, unsafe_allow_html=True)

    # ADDED RECOMMENDATION
    st.markdown("""
    <div class="recommendation-box">
    🎯 <b>Actionable Recommendation:</b><br>
    Buat program <b>Loyalty Rewards</b> untuk mempertahankan pengguna <b>Registered</b> (seperti poin per km). 
    Untuk pengguna <b>Casual</b>, tawarkan promo "Diskon Pendaftaran Member" setelah mereka menyelesaikan perjalanan pertama.
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.caption(f'© {datetime.datetime.now().year} Bike Sharing Analytics By Rizkillah.')