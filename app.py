import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# 페이지 설정
st.set_page_config(
    page_title="판매 대시보드",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 스타일 설정
st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #FF6B6B;
    }
    </style>
""", unsafe_allow_html=True)

# 데이터 로드
@st.cache_data
def load_data():
    customer_df = pd.read_csv('customer_data_csv.csv')
    sales_df = pd.read_csv('sales_data_csv_file.csv')

    # 날짜 형식 변환
    sales_df['date'] = pd.to_datetime(sales_df['date'])
    customer_df['join_date'] = pd.to_datetime(customer_df['join_date'])
    customer_df['last_purchase_date'] = pd.to_datetime(customer_df['last_purchase_date'])

    return customer_df, sales_df

customer_df, sales_df = load_data()

# 제목
st.title("📊 판매 & 고객 대시보드")
st.markdown("---")

# 사이드바 필터
st.sidebar.title("🔍 필터")

# 날짜 범위 선택
date_range = st.sidebar.date_input(
    "날짜 범위 선택",
    value=(sales_df['date'].min().date(), sales_df['date'].max().date()),
    min_value=sales_df['date'].min().date(),
    max_value=sales_df['date'].max().date()
)

# 지역 선택
regions = st.sidebar.multiselect(
    "지역 선택",
    options=sales_df['region'].unique(),
    default=sales_df['region'].unique()
)

# 카테고리 선택
categories = st.sidebar.multiselect(
    "상품 카테고리 선택",
    options=sales_df['category'].unique(),
    default=sales_df['category'].unique()
)

# 필터 적용
filtered_sales = sales_df[
    (sales_df['date'].dt.date >= date_range[0]) &
    (sales_df['date'].dt.date <= date_range[1]) &
    (sales_df['region'].isin(regions)) &
    (sales_df['category'].isin(categories))
]

# KPI 메트릭
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_sales = filtered_sales['total'].sum()
    st.metric("📈 총 판매액", f"₩{total_sales:,.0f}", delta=None)

with col2:
    transaction_count = len(filtered_sales)
    st.metric("🛍️ 거래건수", f"{transaction_count:,}", delta=None)

with col3:
    avg_transaction = filtered_sales['total'].mean() if transaction_count > 0 else 0
    st.metric("💰 평균 거래액", f"₩{avg_transaction:,.0f}", delta=None)

with col4:
    unique_customers = filtered_sales['customer_id'].nunique()
    st.metric("👥 고객 수", f"{unique_customers:,}", delta=None)

st.markdown("---")

# 탭 생성
tab1, tab2, tab3, tab4 = st.tabs(["📊 판매 현황", "👥 고객 분석", "🏆 Top 분석", "📈 트렌드"])

# 탭 1: 판매 현황
with tab1:
    col1, col2 = st.columns(2)

    with col1:
        # 지역별 판매액
        region_sales = filtered_sales.groupby('region')['total'].sum().sort_values(ascending=False)
        fig_region = px.bar(
            x=region_sales.index,
            y=region_sales.values,
            labels={'x': '지역', 'y': '판매액'},
            title="🗺️ 지역별 판매액",
            color=region_sales.values,
            color_continuous_scale='Blues'
        )
        fig_region.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_region, use_container_width=True)

    with col2:
        # 카테고리별 판매액
        category_sales = filtered_sales.groupby('category')['total'].sum().sort_values(ascending=False)
        fig_category = px.pie(
            values=category_sales.values,
            names=category_sales.index,
            title="🏷️ 카테고리별 판매액",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_category.update_layout(height=400)
        st.plotly_chart(fig_category, use_container_width=True)

    # 결제 수단별 통계
    col1, col2 = st.columns(2)
    with col1:
        payment_method = filtered_sales.groupby('payment')['total'].sum().sort_values(ascending=False)
        fig_payment = px.bar(
            x=payment_method.index,
            y=payment_method.values,
            labels={'x': '결제 수단', 'y': '판매액'},
            title="💳 결제 수단별 판매액",
            color=payment_method.values,
            color_continuous_scale='Greens'
        )
        fig_payment.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_payment, use_container_width=True)

    with col2:
        # 등급별 판매액
        grade_sales = filtered_sales.groupby('grade')['total'].sum().sort_values(ascending=False)
        fig_grade = px.bar(
            y=grade_sales.index,
            x=grade_sales.values,
            orientation='h',
            labels={'x': '판매액', 'y': '고객등급'},
            title="⭐ 고객등급별 판매액",
            color=grade_sales.values,
            color_continuous_scale='Oranges'
        )
        fig_grade.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_grade, use_container_width=True)

# 탭 2: 고객 분석
with tab2:
    col1, col2 = st.columns(2)

    with col1:
        # 나이대별 고객
        customer_df['age_group'] = pd.cut(customer_df['age'], bins=[0, 20, 30, 40, 50, 60, 100],
                                          labels=['10대', '20대', '30대', '40대', '50대', '60대+'])
        age_dist = customer_df['age_group'].value_counts().sort_index()
        fig_age = px.bar(
            x=age_dist.index,
            y=age_dist.values,
            labels={'x': '나이대', 'y': '고객수'},
            title="👤 나이대별 고객분포",
            color=age_dist.values,
            color_continuous_scale='Viridis'
        )
        fig_age.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_age, use_container_width=True)

    with col2:
        # 성별 분포
        gender_dist = customer_df['gender'].value_counts()
        fig_gender = px.pie(
            values=gender_dist.values,
            names=gender_dist.index,
            title="🧑‍🤝‍🧑 성별 분포",
            color_discrete_sequence=['#FF9999', '#66B2FF']
        )
        fig_gender.update_layout(height=400)
        st.plotly_chart(fig_gender, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        # 지역별 고객수
        region_customers = customer_df['region'].value_counts().sort_values(ascending=False)
        fig_region_cust = px.bar(
            x=region_customers.index,
            y=region_customers.values,
            labels={'x': '지역', 'y': '고객수'},
            title="🗺️ 지역별 고객수",
            color=region_customers.values,
            color_continuous_scale='Purples'
        )
        fig_region_cust.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_region_cust, use_container_width=True)

    with col2:
        # 고객 세그먼트
        segment_dist = customer_df['segment'].value_counts()
        fig_segment = px.bar(
            x=segment_dist.index,
            y=segment_dist.values,
            labels={'x': '고객세그먼트', 'y': '고객수'},
            title="🎯 고객 세그먼트 분포",
            color=segment_dist.values,
            color_continuous_scale='RdYlGn'
        )
        fig_segment.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_segment, use_container_width=True)

# 탭 3: Top 분석
with tab3:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🏆 Top 10 상품")
        top_products = filtered_sales.groupby('product_name')['total'].sum().sort_values(ascending=False).head(10)
        fig_top_products = px.barh(
            x=top_products.values,
            y=top_products.index,
            labels={'x': '판매액', 'y': '상품명'},
            color=top_products.values,
            color_continuous_scale='Reds'
        )
        fig_top_products.update_layout(height=500, showlegend=False)
        st.plotly_chart(fig_top_products, use_container_width=True)

    with col2:
        st.subheader("🌟 Top 10 고객")
        top_customers = filtered_sales.groupby('name')['total'].sum().sort_values(ascending=False).head(10)
        fig_top_customers = px.barh(
            x=top_customers.values,
            y=top_customers.index,
            labels={'x': '구매액', 'y': '고객명'},
            color=top_customers.values,
            color_continuous_scale='Blues'
        )
        fig_top_customers.update_layout(height=500, showlegend=False)
        st.plotly_chart(fig_top_customers, use_container_width=True)

# 탭 4: 트렌드
with tab4:
    # 일별 판매 추이
    daily_sales = filtered_sales.groupby('date')['total'].sum().reset_index()
    fig_trend = px.line(
        daily_sales,
        x='date',
        y='total',
        title="📈 일별 판매액 추이",
        labels={'date': '날짜', 'total': '판매액'},
        markers=True,
        color_discrete_sequence=['#FF6B6B']
    )
    fig_trend.update_layout(height=400, hovermode='x unified')
    st.plotly_chart(fig_trend, use_container_width=True)

    # 누적 판매액
    daily_sales['cumulative'] = daily_sales['total'].cumsum()
    fig_cumulative = px.line(
        daily_sales,
        x='date',
        y='cumulative',
        title="📊 누적 판매액",
        labels={'date': '날짜', 'cumulative': '누적 판매액'},
        markers=True,
        color_discrete_sequence=['#4ECDC4']
    )
    fig_cumulative.update_layout(height=400, hovermode='x unified')
    st.plotly_chart(fig_cumulative, use_container_width=True)

# 데이터 테이블
st.markdown("---")
st.subheader("📋 상세 거래 데이터")
display_sales = filtered_sales[['date', 'name', 'product_name', 'category', 'price', 'quantity', 'total', 'payment', 'region']].copy()
display_sales['date'] = display_sales['date'].dt.strftime('%Y-%m-%d')
st.dataframe(display_sales, use_container_width=True, height=400)

# 하단 정보
st.markdown("---")
st.markdown(f"""
    <div style="text-align: center; color: #666;">
    <p>📊 마지막 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    <p>데이터 범위: {sales_df['date'].min().date()} ~ {sales_df['date'].max().date()}</p>
    </div>
""", unsafe_allow_html=True)
