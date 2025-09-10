import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_plotly_events import plotly_events
import io

# Streamlit 페이지 설정
st.set_page_config(
    page_title="구매 발주 진행 현황",
    layout="wide",
)

# 앱의 메인 제목
st.title('구매 발주 진행 현황')

# --- 파일 업로드 섹션 ---
st.sidebar.header('파일 업로드')
uploaded_file = st.sidebar.file_uploader("엑셀 파일을 업로드하세요", type=['xlsx', 'xls'])

# 엑셀 파일이 업로드되었는지 확인
if uploaded_file is not None:
    try:
        # 엑셀 파일을 데이터프레임으로 읽기
        df = pd.read_excel(uploaded_file)
        
        # 불필요한 컬럼 리스트
        columns_to_drop = [
            'No', '순번', '납품', '발주유형', '구매그룹', '예산단위', '예산계정', '라인유형', '계정범주', '품목', '품목그룹',
            '품목규격', '통화', '환율', '단가', '금액', '세무구분', '부가세', '전자결재상태', '발주상태', '가입고수량',
            '입고수량', '송장수량', '저장위치', '공장', '담당자', '요청결재문서번호', '요청번호', '요청순번', '요청일',
            '귀속부서', '요청자', '요청자부서'
        ]

        # 불필요한 컬럼 삭제 (오류 발생 시 무시)
        df_cleaned = df.drop(columns=columns_to_drop, errors='ignore')
        
        # --- 사이드바에 전체 정제 데이터 다운로드 버튼 추가 ---
        st.sidebar.info("데이터 정제가 완료되었습니다. 정제 데이터를 다운로드할 수 있습니다.")
        
        # 전체 정제 데이터를 엑셀 파일로 생성하여 다운로드 버튼에 연결
        output_cleaned = io.BytesIO()
        with pd.ExcelWriter(output_cleaned, engine='xlsxwriter') as writer:
            df_cleaned.to_excel(writer, index=False, sheet_name='Sheet1')
        xlsx_data_cleaned = output_cleaned.getvalue()

        st.sidebar.download_button(
            label="전체 정제 데이터 다운로드 (XLSX)",
            data=xlsx_data_cleaned,
            file_name='구매_발주_정제_데이터.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        
        # --- 메인 화면에 필터링된 데이터프레임 표시 ---
        if '품목계정그룹' in df_cleaned.columns and '장부단가' in df_cleaned.columns:
            # 첫 번째 필터링: 고정자산
            filtered_groups_1 = ['자산공통', '고정자산-건설중인자산(캐니스터)']
            df_filtered_1 = df_cleaned[df_cleaned['품목계정그룹'].isin(filtered_groups_1)]
            
            st.subheader("고정자산 구매 발주 진행 현황")
            st.info(f"'{', '.join(filtered_groups_1)}' 그룹에 해당하는 데이터만 표시됩니다.")
            st.dataframe(df_filtered_1, hide_index=True)

            # 고정자산 필터링 데이터 다운로드 버튼
            output_1 = io.BytesIO()
            with pd.ExcelWriter(output_1, engine='xlsxwriter') as writer:
                df_filtered_1.to_excel(writer, index=False, sheet_name='고정자산')
            xlsx_data_1 = output_1.getvalue()
            st.download_button(
                label="고정자산 데이터 다운로드 (XLSX)",
                data=xlsx_data_1,
                file_name='고정자산_필터링_데이터.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            )
            
            # 두 번째 필터링: 소모품 + 장부단가 100만원 이상
            filtered_groups_2 = [
                '제조-소모품', '경상개발비-연구소모품'
            ]
            
            df_filtered_2 = df_cleaned[
                (df_cleaned['품목계정그룹'].isin(filtered_groups_2)) & 
                (df_cleaned['장부단가'] >= 1000000)
            ]
            
            # 요청에 따라 '발주일', '납기예정일' 컬럼 삭제
            df_filtered_2 = df_filtered_2.drop(columns=['발주일', '납기예정일'], errors='ignore')

            st.subheader("100만원 이상 소모품 구매 현황")
            st.info(f"'{', '.join(filtered_groups_2)}' 그룹 중 장부단가가 100만원 이상인 데이터만 표시됩니다.")
            st.dataframe(df_filtered_2, hide_index=True)
            
            # 100만원 이상 소모품 필터링 데이터 다운로드 버튼
            output_2 = io.BytesIO()
            with pd.ExcelWriter(output_2, engine='xlsxwriter') as writer:
                df_filtered_2.to_excel(writer, index=False, sheet_name='고액_소모품_수선비')
            xlsx_data_2 = output_2.getvalue()
            st.download_button(
                label="100만원 이상 소모품 데이터 다운로드 (XLSX)",
                data=xlsx_data_2,
                file_name='100만원_이상_소모품_데이터.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            )

            # 세 번째 필터링: 수선비 + 장부단가 600만원 이상
            filtered_groups_3 = [
                '제조-수선비', '제조-검교정수수료(생산)', '경상개발비-수선비'
            ]
            
            df_filtered_3 = df_cleaned[
                (df_cleaned['품목계정그룹'].isin(filtered_groups_3)) &
                (df_cleaned['장부단가'] >= 6000000)
            ]

            # 요청에 따라 '발주일', '납기예정일' 컬럼 삭제
            df_filtered_3 = df_filtered_3.drop(columns=['발주일', '납기예정일'], errors='ignore')

            st.subheader("600만원 이상 수선비 현황")
            st.info(f"'{', '.join(filtered_groups_3)}' 그룹 중 장부단가가 600만원 이상인 데이터만 표시됩니다.")
            st.dataframe(df_filtered_3, hide_index=True)

            # 600만원 이상 수선비 필터링 데이터 다운로드 버튼
            output_3 = io.BytesIO()
            with pd.ExcelWriter(output_3, engine='xlsxwriter') as writer:
                df_filtered_3.to_excel(writer, index=False, sheet_name='고액_수선비')
            xlsx_data_3 = output_3.getvalue()
            st.download_button(
                label="600만원 이상 수선비 데이터 다운로드 (XLSX)",
                data=xlsx_data_3,
                file_name='600만원_이상_수선비_데이터.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            )
        else:
            st.warning("데이터에 '품목계정그룹' 또는 '장부단가' 컬럼이 없어 필터링을 적용할 수 없습니다.")
            st.subheader("정제 데이터프레임")
            st.dataframe(df_cleaned)

    except Exception as e:
        st.error(f"파일을 읽거나 처리하는 중 오류가 발생했습니다: {e}")
        st.stop()

# 파일이 업로드되지 않았을 때만 메시지 표시
else:
    st.markdown("""
    ### 사용방법 안내
    
    안녕하세요! 이 페이지는 사용자가 업로드한 구매발주진행현황 파일을 토대로  
    **고정자산/소모품/수선비**를 검토하는 데 도움을 주기 위한 목적으로 개발되었습니다.  
    
    1. ERP>구매발주진행현황 메뉴에서 원하는 기간의 자료를 조회합니다.
    2. 조회 화면에 우측 클릭한 뒤 엑셀 내보내기>엑셀 내보내기(화면,숨김 컬럼 포함)를 클릭합니다.
    3. 다운받은 엑셀 파일을 왼쪽 사이드바에 업로드합니다.
    
    이제 파일을 업로드하여 데이터를 확인해 보세요!  
    """)

    st.info("시작하려면 왼쪽 사이드바에 엑셀 파일을 업로드하세요.")
# ---
