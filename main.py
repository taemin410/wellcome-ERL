from dotenv import load_dotenv
load_dotenv()

import os
import json
import streamlit as st
import pandas as pd
import datetime
from langchain_openai import ChatOpenAI
import numpy as np
import time
import streamlit.components.v1 as components
import requests
from datetime import datetime, timedelta

from langchain_community.callbacks import get_openai_callback


# 현재 날짜 기준으로 50년 전과 50년 후의 날짜 계산
years_ago = datetime.now() - timedelta(days=365*30)
years_later = datetime.now() + timedelta(days=365*30)

# 세션 상태 초기화 및 페이지 설정
if 'current_page' not in st.session_state:
    st.session_state.current_page = 0
    st.session_state.required_msg = False

required_msg = False
test_mode = 1
hr_site_url = "https://well-come.info"

# 페이지 제목
page_titles = [
    "취업 확인",
    "취업 기업 정보 입력",
    "개인정보 입력",
    "초안 검토 및 수정",
    "최종 중보 제거 및 정리",
    "추가 서비스 제안 및 결제"
]

required_fields = {
    # 1: ["company_name", "registration_number"],
    1: ["company_name"],
    # 2: ["full_name", "age", "gender", "phone_number", "nationality", "passport_number", "passport_issue_date", "passport_expiry_date", "kor_address", "foreign_address", "email", "education", "career", "language_score", "certificate"],
    2: ["full_name", "age", "gender", "nationality", "education", "career", "language_score", "certificate", "self_introduction"],
}

def load_file_content(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def merge_contents(text1, text2, text3):
    return f"[company information]\n{text1}\n\n[foreigner information]\n{text2}\n\n[requested term]\n{text3}\n"

def corrections_text(merged_text, result_text, corrections):
    return f"{merged_text}\n\n[result_text]\n{result_text}\n\n[corrections]\n{corrections}"

# 국가 목록을 불러오는 함수
def get_country_list():
    if 'country_list' not in st.session_state:
        url = "https://restcountries.com/v3.1/all"
        try:
            response = requests.get(url)
            response.raise_for_status()
            countries = response.json()
            country_names = [country['name']['common'] for country in countries]
            st.session_state.country_list = country_names
        except requests.RequestException as e:
            st.error("국가 정보를 불러오는데 실패했습니다.")
            st.session_state.country_list = []

# 필수 입력 항목 검사 함수
def check_required_fields(page):
    missing_fields = []
    if page in required_fields:
        for field in required_fields[page]:
            if not st.session_state.get(field):
                missing_fields.append(field)
    if missing_fields:
        st.session_state.required_msg = True
        return False
    st.session_state.required_msg = False
    return True


def input_with_required(label, key, widget_type, options=None, placeholder=None, height=None):
    # 필수 입력을 확인하는 로직
    required = "*" if key in required_fields.get(st.session_state.current_page, []) else ""
    required_html = f"<span style='color: red;'>{required}</span>"
    
    # 공통 레이블 생성
    label_html = f"<label for='input_{key}' style='line-height: 1.5;'>{label} {required_html}</label>"
    st.markdown(label_html, unsafe_allow_html=True)
    
    # 위젯 유형에 따라 다른 입력 메서드 호출
    if widget_type == 'text_input':
        value = st.text_input(label, key=key, placeholder=placeholder if placeholder else label, label_visibility="collapsed")
    elif widget_type == 'radio':
        value = st.radio(label, options=options, key=key, label_visibility="collapsed")
    elif widget_type == 'selectbox':
        value = st.selectbox(label, options=options, key=key, label_visibility="collapsed")
    elif widget_type == 'text_area':
        value = st.text_area(label, key=key, placeholder=placeholder if placeholder else label, height=height, label_visibility="collapsed")
    else:
        raise ValueError("Unsupported widget type")
    
    st.empty()
    return value


def process_response(response):
    content = response.content if hasattr(response, 'content') else ""
    clean_content = content.replace("content='", "").rstrip("'")
    return clean_content

# def regenerate_response(prompt):
#     response = llm.invoke(prompt)
#     clean_response = process_response(response)
#     st.write(clean_response)
#     corrections = st.text_area("초안을 수정하거나 추가로 입력할 내용을 입력하세요.")
#     st.write(corrections)
#     if st.button("수정 요청"):        
#         corrections_prompt = corrections_text(prompt, clean_response, corrections)
#         return regenerate_response(corrections_prompt)
    
#     if st.button("수정 완료"):
#         return clean_response

def regenerate_response(prompt, attempt=0):
    response = llm.invoke(prompt)
    clean_response = process_response(response)
    st.write(clean_response)

    # 고유한 키를 생성하기 위해 `attempt`를 사용합니다.
    corrections_key = f"corrections_{attempt}"
    corrections = st.text_area("초안을 수정하거나 추가로 입력할 내용을 입력하세요.", key=corrections_key)
    st.write(corrections)

    if st.button("수정 요청", key=f"request_modification_{attempt}"):
        corrections_prompt = corrections_text(prompt, clean_response, corrections)
        # 재귀 호출 시 `attempt` 값을 증가시켜 고유한 키를 유지합니다.
        return regenerate_response(corrections_prompt, attempt + 1)
    
    if st.button("수정 완료", key=f"modification_complete_{attempt}"):
        return clean_response

def update_value(key, value):
    st.session_state[key] = value

def handle_modification_request(initial_response_key, prompt_key, corrections_key, unique_key):
    if st.button("수정요청", key=unique_key):
        prompt = st.session_state[prompt_key]
        corrections = st.session_state[corrections_key]
        corrections_prompt = corrections_text(prompt, st.session_state[initial_response_key], corrections)
        modified_response = process_response(llm.invoke(corrections_prompt))
        st.session_state[initial_response_key] = modified_response
        # st.experimental_rerun()
        st.rerun()


# 페이지 함수
def show_page(page):
    get_country_list()
    if page == 0:
        # 취업 확인 페이지
        col1, col2 = st.columns(2)
        with col1:
            st.link_button("아직 일자리를 찾고 있어요", hr_site_url)
        with col2:
            st.button("일자리를 찾았어요", on_click=next_page)

    elif page == 1:
        # 취업 기업 정보 입력 페이지
        input_with_required("기업 이름", "company_name", "text_input")
        # input_with_required("사업자등록번호", "registration_number", "text_input")
        st.session_state.register_certificate = st.file_uploader("사업자등기부등본", type="pdf")
        if test_mode:
            # st.session_state.company_location = st.text_input("기업 위치")
            # st.session_state.annual_revenue = st.text_input("연매출(예: 100억원)")
            # st.session_state.number_of_employees = st.text_input("재직인원(예: 50명)")
            st.session_state.business_type = st.text_input("사업 형태")
            st.session_state.business_introduction = st.text_area("사업 소개")
        else:
            st.session_state.company_introduction = st.file_uploader("기업 소개서", type="pdf")

        
    elif page == 2:
        check_fields_1 = True
        # 개인정보 입력 페이지
        col1, col2 = st.columns([1, 1])
        with col1:
            input_with_required("이름", "full_name", "text_input")
        with col2:
            input_with_required("나이", "age", "text_input")

        col1, col2 = st.columns([1, 1])
        with col1:
            input_with_required("성별", "gender", "radio", ['남성', '여성'])
        with col2:
            input_with_required("전화번호", "phone_number", "text_input")

        col1, col2 = st.columns([1, 1])
        with col1:
            country_list = st.session_state.country_list
            input_with_required('국적을 선택하세요', 'nationality', "selectbox", country_list)
        if test_mode:
            with col2:
                st.write("테스트모드에서는 여권번호, 여권 발급일, 여권 만료일을 입력하지 않습니다. 실제 서비스에서는 필수 입력사항입니다.")
        else:
            with col2:
                input_with_required("여권번호", "passport_number", "text_input")
            col1, col2 = st.columns([1, 1])
            with col1:
                st.session_state.passport_issue_date = st.date_input(
                    "여권 발급일",
                    min_value=years_ago.date(),
                    max_value=years_later.date(),
                    value=datetime.now().date()  # 기본값을 오늘 날짜로 설정
                )
            with col2:
                st.session_state.passport_expiry_date = st.date_input(
                    "여권 만료일",
                    min_value=years_ago.date(),
                    max_value=years_later.date(),
                    value=datetime.now().date()  # 기본값을 오늘 날짜로 설정
                )
            input_with_required("국내 주소지", "kor_address", "text_input")
            input_with_required("본국 주소지", "foreign_address", "text_input")
            input_with_required("이메일 주소", "email", "text_input")

        input_with_required("학력사항", "education", "text_area", "", "학교명/학위/전공/졸업상태,\n학교명/학위/전공/졸업상태,")
        input_with_required("경력사항", "career", "text_area", "","회사명/직무/근무기간,\n회사명/직무/근무기간,")
        input_with_required("언어점수", "language_score", "text_area", "","자격이름/점수 및 등급/취득일/만료일,\n자격이름/점수 및 등급/취득일/만료일,")
        input_with_required("자격증", "certificate", "text_area", "","자격이름/점수 및 등급/취득일/만료일,\n자격이름/점수 및 등급/취득일/만료일,")
        input_with_required("자기소개서", "self_introduction", "text_area", "","자기소개서 내용을 입력하세요.")
        

    elif page == 3:
        # 기업 정보 정리
        company_info_text = f"""
            기업 이름: {st.session_state.get('company_name', '')},
            연매출: {st.session_state.get('annual_revenue', '')},
            재직인원: {st.session_state.get('number_of_employees', '')},
            사업 형태: {st.session_state.get('business_type', '')},
            사업 소개: {st.session_state.get('business_introduction', '')}
        """

        # 개인 정보 정리
        personal_info_text = f"""
            이름: {st.session_state.get('full_name', '')},
            나이: {st.session_state.get('age', '')},
            국적: {st.session_state.get('nationality', '')},
            학력: {st.session_state.get('education', '')},
            경력: {st.session_state.get('career', '')},
            언어점수: {st.session_state.get('language_score', '')},
            자격증: {st.session_state.get('certificate', '')}
            자기소개서: {st.session_state.get('self_introduction', '')}
        """

        # 텍스트(프롬프트) 파일 열기
        company_introduction_prompt_path = os.path.join('prompt', 'Company-Introduction.txt')
        expertise_workers_path = os.path.join('prompt', 'Expertise-Of-The-Foreign-Workers.txt')
        reasons_cannot_Korean_path = os.path.join('prompt', 'Reasons-Cannot-Replace-With-Korean-Workers.txt')
        reaseos_foreign_path = os.path.join('prompt', 'Reasons-For-Needing-Foreign-Workers.txt')
        
        # 텍스트(프롬프트) 파일 내용 불러오기
        company_introduction_prompt_text = load_file_content(company_introduction_prompt_path)
        expertise_workers_text = load_file_content(expertise_workers_path)
        reasons_cannot_Korean_text = load_file_content(reasons_cannot_Korean_path)
        reaseos_foreign_text = load_file_content(reaseos_foreign_path)

        # 텍스트(프롬프트) 파일 내용을 합치기
        st.session_state.prompt1 = merge_contents(company_info_text, personal_info_text, company_introduction_prompt_text)
        st.session_state.prompt2 = merge_contents(company_info_text, personal_info_text, expertise_workers_text)
        st.session_state.prompt3 = merge_contents(company_info_text, personal_info_text, reasons_cannot_Korean_text)
        st.session_state.prompt4 = merge_contents(company_info_text, personal_info_text, reaseos_foreign_text)


        # 초기 응답을 생성하고 저장
        if 'initial_response_1' not in st.session_state:
            st.session_state.initial_response_1 = process_response(llm.invoke(st.session_state.prompt1))
        if 'initial_response_2' not in st.session_state:
            st.session_state.initial_response_2 = process_response(llm.invoke(st.session_state.prompt2))
        if 'initial_response_3' not in st.session_state:
            st.session_state.initial_response_3 = process_response(llm.invoke(st.session_state.prompt3))
        if 'initial_response_4' not in st.session_state:
            st.session_state.initial_response_4 = process_response(llm.invoke(st.session_state.prompt4))

        if 'corrent_1' not in st.session_state:
            st.session_state.corrent_1 = "초기 텍스트 또는 특정 조건에 따른 수정"
        if 'corrent_2' not in st.session_state:
            st.session_state.corrent_2 = "초기 텍스트 또는 특정 조건에 따른 수정"
        if 'corrent_3' not in st.session_state:
            st.session_state.corrent_3 = "초기 텍스트 또는 특정 조건에 따른 수정"
        if 'corrent_4' not in st.session_state:
            st.session_state.corrent_4 = "초기 텍스트 또는 특정 조건에 따른 수정"

        # 수정 요청 처리
        st.write(st.session_state.initial_response_1)
        st.text_area("초안을 수정하거나 추가로 입력할 내용을 입력하세요.", key="corrections_1")
        handle_modification_request("initial_response_1", "prompt1", "corrections_1", "unique_key_1")
        st.write(st.session_state.initial_response_2)
        st.text_area("초안을 수정하거나 추가로 입력할 내용을 입력하세요.", key="corrections_2")
        handle_modification_request("initial_response_2", "prompt2", "corrections_2", "unique_key_2")
        st.write(st.session_state.initial_response_3)
        st.text_area("초안을 수정하거나 추가로 입력할 내용을 입력하세요.", key="corrections_3")
        handle_modification_request("initial_response_3", "prompt3", "corrections_3", "unique_key_3")
        st.write(st.session_state.initial_response_4)
        st.text_area("초안을 수정하거나 추가로 입력할 내용을 입력하세요.", key="corrections_4")
        handle_modification_request("initial_response_4", "prompt4", "corrections_4", "unique_key_4")

    elif page == 4:
        final_review_order = os.path.join('prompt', 'Content-Final-Review-Order.txt')
        st.session_state.order_text = load_file_content(final_review_order)

        st.subheader("결과 리뷰")
        # st.session_state.total_response = f"""
        #     **1.기업소개\n {st.session_state.initial_response_1}\n\n
        #     2.외국인력 도입 업무와 관련한 전문인력부족 현황\n{st.session_state.initial_response_2}\n\n
        #     3.국내인력 채용노력 및 인력을 충원하지 못한 사유\n{st.session_state.initial_response_3}\n\n
        #     4.전문외국인력의 기술과 담당할 업무의 연관성\n{st.session_state.initial_response_4}\n\n
        #     """
        st.session_state.total_response = """
            **#1. 기업 소개**  
            {introduction}    
            **#2. 외국인력 도입 업무와 관련한 전문 인력 부족 현황**  
            {expertise_shortage}    
            **#3. 국내 인력 채용 노력 및 인력을 충원하지 못한 사유**  
            {recruitment_efforts}       
            **#4. 전문 외국인력의 기술과 담당할 업무의 연관성**  
            {expertise_relevance}    
            """.format(
                introduction=st.session_state.initial_response_1,
                expertise_shortage=st.session_state.initial_response_2,
                recruitment_efforts=st.session_state.initial_response_3,
                expertise_relevance=st.session_state.initial_response_4,
            )
        st.markdown(st.session_state.total_response)
        # st.text_area("최종본 수정 사항", key="corrections_last")
        # handle_modification_request("total_response", "order_text", "corrections_last", "unique_key_5")


    elif page == 5:
        st.subheader("추가 서비스 제안 및 결제")
        st.write("추가 서비스 제안 및 결제 페이지입니다.")
        if st.button("결제 완료"):
            st.write("결제가 완료되었습니다.")
            st.session_state.current_page += 1

# 페이지 이동 함수
def next_page():
    if check_required_fields(st.session_state.current_page):
        if st.session_state.current_page < len(page_titles) - 1:
            st.session_state.current_page += 1
            st.session_state.required_msg = False
    else:
        st.session_state.required_msg = True

def previous_page():
    if st.session_state.current_page > 0:
        st.session_state.current_page -= 1

# 현재 페이지 표시
llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.6)

st.title(page_titles[st.session_state.current_page])
show_page(st.session_state.current_page)

if st.session_state.required_msg:
    st.error("모든 필수 항목을 입력해주세요.")

if 'check_fields' in st.session_state and st.session_state.check_fields:
    if not check_required_fields(st.session_state.current_page):
        st.error("모든 필수 항목을 입력해주세요.", anchor="top")
    # 검사 후에는 다시 False로 설정하여 메시지가 반복해서 표시되지 않도록 함
    st.session_state.check_fields = False

col1, col2, col3 = st.columns([0.1, 0.8, 0.1])
with col1:
    if st.session_state.current_page > 0:
        st.button("이전", on_click=previous_page)
with col3:
    if st.session_state.current_page < len(page_titles) - 1 and st.session_state.current_page != 0:
        st.button("다음", on_click=next_page)

