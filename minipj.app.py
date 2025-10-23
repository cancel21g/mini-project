import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 페이지 설정
st.set_page_config(
    page_title="사업자 현황 분석",
    page_icon="📊",
    layout="wide"
)

# 제목
st.title("📊 사업자 현황 분석 대시보드")
st.markdown("### 2025년 04월 100대 생활업종")

# 엑셀 파일 경로
BASE_DIR = Path(__file__).parent
file_path = BASE_DIR / "data" / "사업자 현황(2025년 04월 100대생활업종).xlsx"

# 데이터 로드 함수 (캐싱)
@st.cache_data
def load_data():
    df = pd.read_excel(file_path)
    return df

# 데이터 로드
try:
    df = load_data()
    
    # 사이드바 - 지역 선택
    st.sidebar.header("🔍 지역 선택")
    
    # 지역 목록 추출 (실제 컬럼명에 맞게 조정 필요)
    if '지역명' in df.columns:
        regions = sorted(df['지역명'].unique())
        selected_region = st.sidebar.selectbox("지역을 선택하세요:", regions)
    else:
        st.error("'지역명' 컬럼을 찾을 수 없습니다. 데이터 구조를 확인해주세요.")
        st.write("현재 컬럼:", df.columns.tolist())
        st.stop()
    
    # 상위 N개 선택
    top_n = st.sidebar.slider("상위 몇 개를 표시할까요?", 5, 20, 10)
    
    # 지역 데이터 필터링
    region_data = df[df['지역명'] == selected_region].copy()
    
    if region_data.empty:
        st.warning(f"'{selected_region}' 지역의 데이터가 없습니다.")
        st.stop()
    
    # 메인 컨텐츠
    st.markdown(f"## 📍 {selected_region} 지역 분석")
    
    # 전체 통계
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("전체 업종 수", f"{len(region_data)}개")
    with col2:
        st.metric("총 점포 수", f"{region_data['점포수'].sum():,}개")
    with col3:
        avg_growth = region_data['증감율'].mean()
        st.metric("평균 증감율", f"{avg_growth:.2f}%")
    with col4:
        high_growth_count = len(region_data[region_data['증감율'] >= 100])
        st.metric("증감율 100% 이상", f"{high_growth_count}개")
    
    st.markdown("---")
    
    # 탭으로 구분
    tab1, tab2, tab3 = st.tabs(["📈 증감율 분석", "🏪 점포수 분석", "📋 전체 데이터"])
    
    # 탭 1: 증감율 100 이상 상위 업종
    with tab1:
        st.subheader(f"🚀 증감율 100% 이상 상위 {top_n}개 업종")
        
        # 증감율 100 이상 필터링
        high_growth = region_data[region_data['증감율'] >= 100].copy()
        
        if high_growth.empty:
            st.info(f"'{selected_region}' 지역에 증감율이 100% 이상인 업종이 없습니다.")
        else:
            # 증감율 기준 정렬
            high_growth_sorted = high_growth.sort_values(by='증감율', ascending=False).head(top_n)
            
            # 테이블 표시
            display_df = high_growth_sorted[['업종명', '증감율', '점포수']].reset_index(drop=True)
            display_df.index = display_df.index + 1
            display_df.columns = ['업종명', '증감율 (%)', '점포수 (개)']
            
            st.dataframe(
                display_df.style.format({'증감율 (%)': '{:.2f}', '점포수 (개)': '{:,}'}),
                use_container_width=True
            )
            
            # 차트
            col1, col2 = st.columns(2)
            
            with col1:
                # 막대 차트
                fig1 = px.bar(
                    high_growth_sorted.head(top_n),
                    x='증감율',
                    y='업종명',
                    orientation='h',
                    title=f'증감율 상위 {top_n}개 업종',
                    labels={'증감율': '증감율 (%)', '업종명': ''},
                    color='증감율',
                    color_continuous_scale='Reds'
                )
                fig1.update_layout(yaxis={'categoryorder': 'total ascending'})
                st.plotly_chart(fig1, use_container_width=True)
            
            with col2:
                # 점포수와 증감율 관계
                fig2 = px.scatter(
                    high_growth_sorted.head(top_n),
                    x='점포수',
                    y='증감율',
                    text='업종명',
                    title='점포수 vs 증감율',
                    labels={'점포수': '점포수 (개)', '증감율': '증감율 (%)'},
                    color='증감율',
                    color_continuous_scale='Viridis',
                    size='점포수'
                )
                fig2.update_traces(textposition='top center')
                st.plotly_chart(fig2, use_container_width=True)
    
    # 탭 2: 점포수 상위 업종
    with tab2:
        st.subheader(f"🏪 당월 점포수 상위 {top_n}개 업종")
        
        # 점포수 기준 정렬
        top_stores = region_data.sort_values(by='점포수', ascending=False).head(top_n)
        
        # 테이블 표시
        display_df2 = top_stores[['업종명', '점포수', '증감율']].reset_index(drop=True)
        display_df2.index = display_df2.index + 1
        display_df2.columns = ['업종명', '점포수 (개)', '증감율 (%)']
        
        st.dataframe(
            display_df2.style.format({'점포수 (개)': '{:,}', '증감율 (%)': '{:.2f}'}),
            use_container_width=True
        )
        
        # 차트
        col1, col2 = st.columns(2)
        
        with col1:
            # 막대 차트
            fig3 = px.bar(
                top_stores.head(top_n),
                x='점포수',
                y='업종명',
                orientation='h',
                title=f'점포수 상위 {top_n}개 업종',
                labels={'점포수': '점포수 (개)', '업종명': ''},
                color='점포수',
                color_continuous_scale='Blues'
            )
            fig3.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig3, use_container_width=True)
        
        with col2:
            # 파이 차트
            fig4 = px.pie(
                top_stores.head(top_n),
                values='점포수',
                names='업종명',
                title=f'점포수 비율 (상위 {top_n}개)',
                hole=0.4
            )
            st.plotly_chart(fig4, use_container_width=True)
    
    # 탭 3: 전체 데이터
    with tab3:
        st.subheader(f"📋 {selected_region} 지역 전체 업종 데이터")
        
        # 필터링 옵션
        col1, col2 = st.columns(2)
        with col1:
            min_growth = st.number_input("최소 증감율 (%)", value=-100.0, step=10.0)
        with col2:
            min_stores = st.number_input("최소 점포수", value=0, step=10)
        
        # 필터링 적용
        filtered_data = region_data[
            (region_data['증감율'] >= min_growth) & 
            (region_data['점포수'] >= min_stores)
        ].sort_values(by='점포수', ascending=False)
        
        st.write(f"필터링된 업종 수: {len(filtered_data)}개")
        st.dataframe(filtered_data, use_container_width=True)
        
        # CSV 다운로드
        csv = filtered_data.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 CSV 다운로드",
            data=csv,
            file_name=f"{selected_region}_사업자현황.csv",
            mime="text/csv"
        )

except FileNotFoundError:
    st.error(f"❌ 파일을 찾을 수 없습니다: {file_path}")
    st.info("파일 경로를 확인해주세요.")
except Exception as e:
    st.error(f"❌ 오류가 발생했습니다: {str(e)}")
    st.exception(e)
