import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from standardize_data import clean_data

st.set_page_config(page_title="منصة ذكية لفحص النخيل", layout="wide")
st.title("🌴 منصة تحليل وتنبؤ آفات النخيل")

@st.cache_data
def load_data():
    df = pd.read_excel("data.xlsx", sheet_name="فحص حقلي")
    return clean_data(df)

df = load_data()
df_original = df.copy()

# الفلاتر
st.sidebar.header("🛠️ الفلاتر")
min_date = df['تاريخ الفحص'].min().date()
max_date = df['تاريخ الفحص'].max().date()
start_date = st.sidebar.date_input("من تاريخ", min_date)
end_date = st.sidebar.date_input("إلى تاريخ", max_date)
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date) + pd.Timedelta(days=1)

sectors = ["الكل"] + sorted(df['القطاع'].dropna().unique().astype(str).tolist())
selected_sector = st.sidebar.selectbox("القطاع", sectors)
if selected_sector != "الكل":
    df = df[df['القطاع'].astype(str) == selected_sector]

pests = ["الكل"] + sorted(df['وصف الافة'].dropna().unique().astype(str).tolist())
selected_pest = st.sidebar.selectbox("نوع الآفة", pests)
if selected_pest != "الكل":
    df = df[df['وصف الافة'].astype(str) == selected_pest]

# تطبيق التاريخ
df = df[(df['تاريخ الفحص'] >= start_date) & (df['تاريخ الفحص'] <= end_date)]

# الملخص
st.subheader("📈 ملخص عام")
col1, col2, col3 = st.columns(3)
col1.metric("السجلات", f"{len(df):,}")
col2.metric("الآفات", df['وصف الافة'].nunique())
col3.metric("القطاعات", df['القطاع'].nunique())

# الرسوم
st.subheader("📊 تحليلات متقدمة")

# 1. أكثر الآفات
st.write("#### أكثر الآفات انتشارًا")
top = df['وصف الافة'].value_counts().head(10)
fig1 = px.bar(top, orientation='h')
fig1.update_layout(yaxis={'categoryorder':'total ascending'})
st.plotly_chart(fig1, use_container_width=True)

# 2. Heatmap: القطاع × الآفة
st.write("#### توزيع الآفات حسب القطاع (Heatmap)")
heatmap_data = df.groupby(['القطاع', 'وصف الافة']).size().reset_index(name='العدد')
if not heatmap_data.empty:
    fig2 = px.density_heatmap(heatmap_data, x='وصف الافة', y='القطاع', z='العدد', color_continuous_scale='Blues')
    st.plotly_chart(fig2, use_container_width=True)

# 3. تطور الحالات مع الوقت
st.write("#### تطور الحالات مع الوقت")
df_time = df.groupby(df['تاريخ الفحص'].dt.to_period('W')).size().reset_index(name='العدد')
df_time['الأسبوع'] = df_time['تاريخ الفحص'].astype(str)
fig3 = px.line(df_time, x='الأسبوع', y='العدد')
st.plotly_chart(fig3, use_container_width=True)

# 4. المبيدات
st.write("#### المبيدات المستخدمة")
pest_cols = ['المبيد 1','المبيد 2','المبيد 3','المبيد 4','المبيد 5']
all_pesticides = pd.concat([df[col].dropna() for col in pest_cols])
top_pesticides = all_pesticides[all_pesticides != "لا يوجد"].value_counts().head(10)
if not top_pesticides.empty:
    fig4 = px.bar(top_pesticides, orientation='h')
    fig4.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig4, use_container_width=True)

# عرض الجدول
st.subheader("📋 البيانات")
st.dataframe(df.fillna("—"), height=500)

# تنزيل
csv = df.to_csv(index=False, encoding='utf-8-sig')
st.download_button("📥 تنزيل البيانات المفلترة", csv, "filtered.csv", "text/csv")