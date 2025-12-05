from prophet import Prophet
import pandas as pd

def forecast_pest(df, pest_name, sector=None, periods=7):
    # فلترة البيانات
    df_pest = df[df['وصف الافة'] == pest_name]
    if sector:
        df_pest = df_pest[df_pest['القطاع'] == sector]
    
    if df_pest.empty:
        return None
    
    # تحضير السلاسل الزمنية
    df_ts = df_pest.groupby('تاريخ الفحص').size().reset_index(name='count')
    df_ts.columns = ['ds', 'y']
    
    # تدريب النموذج
    model = Prophet()
    model.fit(df_ts)
    
    # التنبؤ
    future = model.make_future_dataframe(periods=periods)
    forecast = model.predict(future)
    
    return forecast[['ds', 'yhat']].tail(periods)

# مثال على الاستخدام
if __name__ == "__main__":
    df = pd.read_excel("data.xlsx", sheet_name="فحص حقلي")
    from standardize_data import clean_data
    df = clean_data(df)
    
    pred = forecast_pest(df, "أكاروس", sector=28, periods=7)
    print("التنبؤ بعدد حالات أكاروس في القطاع 28 خلال 7 أيام:")
    print(pred)