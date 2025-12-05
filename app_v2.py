# app.py - نسخة محدثة تعمل مع ملف "data.xlsx"
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(
    page_title="تحليل فحص آفات النخيل",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🌴 نظام تحليل فحص آفات النخيل")
st.markdown("تم تصميم هذا النظام لتحليل بيانات فحوصات آفات النخيل وعرض الرؤى بصريًا.")

# تحميل البيانات
@st.cache_data
def load_data():
    try:
        df = pd.read_excel("data.xlsx", sheet_name="فحص حقلي")  # اسم الورقة مهم!
    except FileNotFoundError:
        st.error("❌ الملف 'data.xlsx' غير موجود. تأكد من رفعه في نفس المجلد.")
        st.stop()
    except Exception as e:
        st.error(f"❌ خطأ في قراءة الملف: {e}")
        st.stop()

    # تنظيف البيانات
    df['تاريخ الفحص'] = pd.to_datetime(df['تاريخ الفحص'], errors='coerce')
    df['تاريخ المعاملة'] = pd.to_datetime(df['تاريخ المعاملة'], errors='coerce')

    # إزالة الأعمدة غير المستخدمة (اختياري)
    columns_to_drop = ['م', 'كود النخلة', 'كود دورة الفحص', 'الفاحص', 'مهندس المكافحة', 'مشرف عام', 'مشرف أساسي', 'مشرف مساعد', 'القائم بالتسجيل']
    df = df.drop(columns=[col for col in columns_to_drop if col in df.columns], errors='ignore')

    return df

df = load_data()
df_original = df.copy()

# الفلاتر
st.sidebar.header("🛠️ الفلاتر")

# نطاق التاريخ
if df['تاريخ الفحص'].notna().any():
    min_date = df['تاريخ الفحص'].min().date()
    max_date = df['تاريخ الفحص'].max().date()
else:
    min_date = max_date = datetime.today().date()

start_date = st.sidebar.date_input("من تاريخ", value=min_date, min_value=min_date, max_value=max_date)
end_date = st.sidebar.date_input("إلى تاريخ", value=max_date, min_value=min_date, max_value=max_date)

start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)

# فلتر القطاع
sectors = ["الكل"] + sorted(df['القطاع'].dropna().astype(str).unique().tolist())
selected_sector = st.sidebar.selectbox("القطاع", sectors)
if selected_sector != "الكل":
    df = df[df['القطاع'].astype(str) == selected_sector]

# فلتر الآفة
pests = ["الكل"] + sorted(df['وصف الافة'].dropna().astype(str).unique().tolist())
selected_pest = st.sidebar.selectbox("نوع الآفة", pests)
if selected_pest != "الكل":
    df = df[df['وصف الافة'].astype(str) == selected_pest]

# تطبيق فلتر التاريخ
df = df[(df['تاريخ الفحص'] >= start_date) & (df['تاريخ الفحص'] <= end_date)]

# الملخص العام
st.subheader("📈 ملخص عام")
col1, col2, col3 = st.columns(3)
col1.metric("إجمالي السجلات", f"{len(df):,}")
col2.metric("الآفات الفريدة", df['وصف الافة'].nunique())
col3.metric("القطاعات", df['القطاع'].nunique())

# الرسوم البيانية
st.subheader("📊 الرسوم البيانية")

# 1. أكثر الآفات انتشارًا
st.write("#### أكثر الآفات انتشارًا")
top_pests = df['وصف الافة'].value_counts().head(10)
fig1 = px.bar(top_pests, orientation='h', labels={'value': 'العدد', 'index': 'نوع الآفة'})
fig1.update_layout(yaxis={'categoryorder': 'total ascending'}, height=400)
st.plotly_chart(fig1, use_container_width=True)

# 2. التوزيع حسب تصنيف الآفة
st.write("#### التوزيع حسب تصنيف الآفة")
class_counts = df['تصنيف الافة'].value_counts()
if not class_counts.empty:
    fig2 = px.pie(values=class_counts.values, names=class_counts.index, hole=0.4)
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("لا توجد بيانات لتصنيف الآفات.")

# 3. المبيدات الأكثر استخدامًا
st.write("#### المبيدات الأكثر استخدامًا")
pesticide_cols = ['المبيد 1','المبيد 2','المبيد 3','المبيد 4','المبيد 5']
all_pesticides = pd.concat([df[col].dropna() for col in pesticide_cols], ignore_index=True)
all_pesticides = all_pesticides[all_pesticides != "لا يوجد"]
top_pesticides = all_pesticides.value_counts().head(10)

if not top_pesticides.empty:
    fig3 = px.bar(top_pesticides, x=top_pesticides.values, y=top_pesticides.index, orientation='h')
    fig3.update_layout(yaxis={'categoryorder': 'total ascending'}, height=400, xaxis_title="العدد", yaxis_title="المبيد")
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.info("لا توجد بيانات عن المبيدات.")

# 4. تطور الحالات بمرور الوقت
st.write("#### تطور عدد الفحوصات بمرور الوقت")
df_time = df.copy()
df_time = df_time.dropna(subset=['تاريخ الفحص'])
df_time['الأسبوع'] = df_time['تاريخ الفحص'].dt.to_period('W').dt.start_time
time_series = df_time.groupby('الأسبوع').size().reset_index(name='العدد')
fig4 = px.line(time_series, x='الأسبوع', y='العدد')
st.plotly_chart(fig4, use_container_width=True)

# عرض الجدول
st.subheader("📋 البيانات المفلترة")
st.dataframe(df.fillna("—"), height=500)

# تنزيل البيانات
csv = df.to_csv(index=False, encoding='utf-8-sig')
st.download_button("📥 تنزيل البيانات كـ CSV", csv, "البيانات_المفلترة.csv", "text/csv")