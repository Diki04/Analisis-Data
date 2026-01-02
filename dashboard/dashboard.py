import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import datetime
import os

st.set_page_config(
    page_title="Bike Sharing Analytics By Rizkillah",
    page_icon="🚲",
    layout="wide"
)


COLOR_PRIMARY = "#007BFF"   
COLOR_ACCENT = "#FF5733"    

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

st.markdown("""
<style>
    /* Judul Utama */
    .main-title {
        font-size: 3rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 1rem;
        /* Warna akan otomatis mengikuti tema (Putih di Dark Mode) */
    }
    
    /* Insight Box (Kotak Penjelasan) */
    /* Kita beri warna sedikit terang agar teks hitam terbaca, atau biarkan default */
    .insight-box {
        background-color: #262730; /* Warna gelap sedikit beda dari background */
        border-left: 5px solid #007BFF;
        padding: 15px;
        margin-top: 15px;
        border-radius: 5px;
        /* Text otomatis putih */
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    try:
        base_dir = os.path.dirname(__file__)
        days_path = os.path.join(base_dir, "day_clean.csv")
        hours_path = os.path.join(base_dir, "hour_clean.csv")

        days_df = pd.read_csv(days_path)
        hours_df = pd.read_csv(hours_path)

        return days_df, hours_df

    except FileNotFoundError as e:
        st.error(f"File CSV tidak ditemukan: {e}")
        st.stop()

    datetime_columns = ["dteday"]
    for column in datetime_columns:
        days_df[column] = pd.to_datetime(days_df[column])
        hours_df[column] = pd.to_datetime(hours_df[column])
        
    return days_df, hours_df

def create_advanced_features(df):
    season_map = {1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'}
    if df['season'].dtype in ['int64', 'int32']:
        df['season'] = df['season'].map(season_map)
        
    if 'humidity_category' not in df.columns:
        df['humidity_category'] = pd.cut(df['humidity'], bins=[0, 0.45, 0.75, 1.0], labels=['Kering', 'Ideal', 'Lembab'])
    if 'wind_category' not in df.columns:
        df['wind_category'] = pd.cut(df['wind_speed'], bins=[0, 0.2, 0.4, 1.0], labels=['Low', 'Medium', 'High'])
        
    return df

days_df_raw, hours_df_raw = load_data()
days_df = create_advanced_features(days_df_raw)
hours_df = create_advanced_features(hours_df_raw)

min_date = days_df["dteday"].min()
max_date = days_df["dteday"].max()

with st.sidebar:
    st.header("Filter Dashboard")
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )
    st.caption(f"Data tersedia dari {min_date.date()} hingga {max_date.date()}")

main_df_days = days_df[(days_df["dteday"] >= str(start_date)) & (days_df["dteday"] <= str(end_date))]
main_df_hour = hours_df[(hours_df["dteday"] >= str(start_date)) & (hours_df["dteday"] <= str(end_date))]

if main_df_days.empty:
    st.warning("⚠️ Tidak ada data untuk rentang tanggal yang dipilih.")
    st.stop()

st.markdown('<h1 class="main-title">🚲 Bike Sharing Analytics By Rizkillah</h1>', unsafe_allow_html=True)
st.markdown("Selamat datang. Dashboard ini menyajikan **insight** mendalam tentang performa operasional bisnis.")
st.markdown("---")

st.subheader("Ringkasan Performa Kunci")
col1, col2, col3 = st.columns(3)

total_orders = main_df_days['count_cr'].sum()
total_reg = main_df_days['registered'].sum()
total_cas = main_df_days['casual'].sum()

with col1:
    st.metric("Total Penyewaan (All Time)", value=f"{total_orders:,.0f}".replace(",", "."), delta_color="off")
with col2:
    perc_reg = (total_reg / total_orders * 100) if total_orders > 0 else 0
    st.metric("Total Member (Registered)", value=f"{total_reg:,.0f}".replace(",", "."), help=f"{perc_reg:.1f}% dari total")
with col3:
    perc_cas = (total_cas / total_orders * 100) if total_orders > 0 else 0
    st.metric("Total Pengguna Kasual", value=f"{total_cas:,.0f}".replace(",", "."), help=f"{perc_cas:.1f}% dari total")

st.markdown("---")

with st.container():
    st.subheader("1. Analisis Tren & Distribusi Harian")
    
    main_df_days['rolling_mean'] = main_df_days['count_cr'].rolling(window=30).mean()
    mean_val = main_df_days['count_cr'].mean()
    
    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(20, 6))

    sns.lineplot(x='dteday', y='count_cr', data=main_df_days, ax=ax[0], 
                 color='grey', alpha=0.4, linewidth=1.5, label='Harian (Raw)')
    sns.lineplot(x='dteday', y='rolling_mean', data=main_df_days, ax=ax[0], 
                 color=COLOR_PRIMARY, linewidth=3, label='Tren Bulanan (30-day MA)')
    ax[0].set_title('Pertumbuhan & Tren Jangka Panjang', fontsize=14, fontweight='bold', color='black')
    ax[0].set_xlabel('')
    ax[0].set_ylabel('Jumlah Penyewaan')
    ax[0].legend(frameon=False)

    sns.histplot(main_df_days['count_cr'], kde=True, color=COLOR_PRIMARY, alpha=0.6, edgecolor=None, ax=ax[1])
    ax[1].axvline(mean_val, color=COLOR_ACCENT, linestyle='--', linewidth=2, label=f'Rata-rata: {int(mean_val)}')
    ax[1].set_title('Distribusi Frekuensi Harian', fontsize=14, fontweight='bold', color='black')
    ax[1].set_xlabel('Jumlah Penyewaan per Hari')
    ax[1].set_ylabel('Frekuensi')
    ax[1].legend(frameon=False)

    st.pyplot(fig)
    
    st.markdown("""
    <div class="insight-box">
    💡 <b>Key Insight:</b> Grafik kiri menunjukkan tren pertumbuhan. Grafik kanan menunjukkan distribusi frekuensi.
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

with st.container():
    st.subheader("2. Pola Aktivitas Per Jam")
    hourly_counts = main_df_hour.groupby('hours')['count_cr'].mean().reset_index()

    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(20, 6))

    sns.lineplot(x='hours', y='count_cr', data=hourly_counts, marker='o', markersize=8,
                 color=COLOR_PRIMARY, linewidth=3, ax=ax[0])
    ax[0].set_title('Pola Komuter', fontsize=14, fontweight='bold', color='black')
    ax[0].set_xlabel('Jam (0-23)')
    ax[0].set_ylabel('Rata-rata Penyewaan')
    ax[0].set_xticks(range(0, 24, 2))
    ax[0].grid(True, linestyle='--', alpha=0.7)

    sns.barplot(x='hours', y='count_cr', data=hourly_counts, color='#AEC6CF', ax=ax[1])
    top_3_hours = hourly_counts.nlargest(3, 'count_cr')['hours'].values
    for i, patch in enumerate(ax[1].patches):
        if hourly_counts.loc[i, 'hours'] in top_3_hours:
            patch.set_color(COLOR_ACCENT)
            
    ax[1].set_title('Ranking Volume per Jam', fontsize=14, fontweight='bold', color='black')
    ax[1].set_xlabel('Jam (0-23)')
    ax[1].set_ylabel('')
    ax[1].set_xticks([8, 17, 18]) 
    ax[1].set_xticklabels(['08:00', '17:00', '18:00'])

    st.pyplot(fig)

    st.markdown("""
    <div class="insight-box">
    💡 <b>Key Insight:</b> Pola dua puncak (08:00 & 17:00) terlihat jelas.
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

with st.container():
    col_season, col_holiday = st.columns(2)

    with col_season:
        st.subheader("3. Analisis Musiman")
        season_order = ['Spring', 'Summer', 'Fall', 'Winter']
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.barplot(x='season', y='count_cr', data=main_df_days, estimator=sum, order=season_order, palette='viridis', errorbar=None, ax=ax)
        ax.set_title('Total Volume per Musim', fontsize=12, fontweight='bold', color='black')
        ax.set_ylabel('Total (Juta)', color='black')
        ax.set_xlabel('')
        for p in ax.patches:
            ax.annotate(f'{p.get_height()/1e6:.2f}M', (p.get_x() + p.get_width() / 2., p.get_height()), 
                        ha='center', va='bottom', fontsize=10, weight='bold', color='black')
        st.pyplot(fig)

    with col_holiday:
        st.subheader("4. Analisis Hari Libur")
        temp_df = main_df_days.copy()
        temp_df['holiday_label'] = temp_df['holiday'].map({0: 'Hari Kerja', 1: 'Hari Libur'})
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.barplot(x='holiday_label', y='count_cr', data=temp_df, estimator='mean', errorbar=None, palette=[COLOR_PRIMARY, 'grey'], ax=ax)
        ax.set_title('Rata-rata Harian', fontsize=12, fontweight='bold', color='black')
        ax.set_ylabel('Rata-rata', color='black')
        ax.set_xlabel('')
        for p in ax.patches:
             ax.annotate(f'{int(p.get_height()):,}', (p.get_x() + p.get_width() / 2., p.get_height()), 
                        ha='center', va='bottom', fontsize=11, weight='bold', color='black')
        st.pyplot(fig)

    st.markdown("""
    <div class="insight-box">
    💡 <b>Key Insight:</b> Musim Gugur paling tinggi. Rata-rata hari kerja lebih tinggi dari libur.
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

with st.container():
    st.subheader("5. Profil Pengguna & Cuaca")
    col_user, col_weather = st.columns([1, 2])

    with col_user:
        st.markdown("##### Komposisi User")
        fig, ax = plt.subplots(figsize=(5, 5))
        wedges, texts, autotexts = ax.pie([total_cas, total_reg], labels=['Casual', 'Registered'], 
            autopct='%1.1f%%', colors=['grey', COLOR_PRIMARY], startangle=90, pctdistance=0.85, explode=(0.05, 0))
        centre_circle = plt.Circle((0,0),0.70,fc='white')
        fig.gca().add_artist(centre_circle)
        
        for text in texts: text.set_color('black')
        for autotext in autotexts: autotext.set_color('white')
        
        st.pyplot(fig)

    with col_weather:
        st.markdown("##### Dampak Cuaca")
        avg_hum = main_df_days.groupby('humidity_category')['count_cr'].mean().reset_index()
        avg_wind = main_df_days.groupby('wind_category')['count_cr'].mean().reset_index()
        
        fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(12, 5))
        sns.barplot(x='humidity_category', y='count_cr', data=avg_hum, palette='Blues_d', ax=ax[0])
        ax[0].set_title('Kelembaban', fontsize=11, fontweight='bold', color='black')
        ax[0].set_ylabel('Rata-rata', color='black')
        ax[0].set_xlabel('')
        
        sns.barplot(x='wind_category', y='count_cr', data=avg_wind, palette='coolwarm', ax=ax[1])
        ax[1].set_title('Angin', fontsize=11, fontweight='bold', color='black')
        ax[1].set_ylabel('')
        ax[1].set_xlabel('')
        st.pyplot(fig)

    st.markdown("""
    <div class="insight-box">
    💡 <b>Key Insight:</b> Dominasi Registered User sangat kuat.
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.caption(f'© {datetime.datetime.now().year} Bike Sharing Analytics By Rizkillah.')