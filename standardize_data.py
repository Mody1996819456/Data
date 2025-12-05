import pandas as pd
import re

def standardize_pest(pest):
    if pd.isna(pest) or pest == "":
        return "غير محدد"
    pest = str(pest).strip().lower()
    if "اكروس" in pest or "اكاروس" in pest or "acaros" in pest:
        return "أكاروس"
    elif "سوسة" in pest and ("نخيل" in pest or "حمراء" in pest):
        return "سوسة النخيل الحمراء"
    elif "دوباس" in pest:
        return "دوباس"
    elif "ديدان" in pest or "دود" in pest:
        return "ديدان"
    elif "لفحة" in pest or "قلب ناشف" in pest:
        return "مرض اللفحة السوداء"
    elif "بقع" in pest and ("بنيه" in pest or "غائره" in pest):
        return "بقع بنية غائرة"
    elif "خياس" in pest:
        return "خياس الطلع"
    elif "لسعة شمس" in pest:
        return "لسعة شمس على الثمار"
    else:
        return str(pest).title()

def extract_severity(note):
    if pd.isna(note):
        return "غير محدد"
    note = str(note).lower()
    if "شديدة" in note or "كثيف" in note:
        return "شديدة"
    elif "متوسط" in note:
        return "متوسطة"
    elif "خفيف" in note:
        return "خفيفة"
    else:
        return "غير محدد"

def clean_data(df):
    df = df.copy()
    df['وصف الافة'] = df['وصف الافة'].apply(standardize_pest)
    df['شدة الإصابة'] = df['ملاحظات'].apply(extract_severity)
    for col in ['المبيد 1', 'المبيد 2', 'المبيد 3', 'المبيد 4', 'المبيد 5']:
        df[col] = df[col].fillna("لا يوجد").astype(str)
        df[col] = df[col].str.replace(r'لايوجد|لا يوجد|لايوج', 'لا يوجد', case=False, regex=True)
    df['تاريخ الفحص'] = pd.to_datetime(df['تاريخ الفحص'], errors='coerce')
    df['السنة'] = df['تاريخ الفحص'].dt.year
    df['الشهر'] = df['تاريخ الفحص'].dt.month
    df['الأسبوع'] = df['تاريخ الفحص'].dt.isocalendar().week
    return df

# تنفيذ التنظيف (اختياري عند التشغيل مباشرة)
if __name__ == "__main__":
    df = pd.read_excel("data.xlsx", sheet_name="فحص حقلي")
    df_clean = clean_data(df)
    df_clean.to_excel("data_clean.xlsx", index=False)
    print("✅ تم تنظيف البيانات وحفظها كـ data_clean.xlsx")