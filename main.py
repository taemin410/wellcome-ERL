from dotenv import load_dotenv
load_dotenv()

import os
from langchain import verbose
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
    "추가 연계 서비스 선택"
]

required_fields = {
    1: ["company_name", "registration_number"],
    2: ["full_name", "age", "gender", "phone_number", "nationality", "passport_number", "passport_issue_date", "passport_expiry_date", "kor_address", "foreign_address", "email", "education", "career", "language_score", "certificate"],
}

def load_file_content(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def merge_contents(text1, text2, text3):
    return f"[Company Information]\n{text1}\n\n[Foreigner Information]\n{text2}\n\n[Requested term]\n{text3}"

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


def text_input_with_required(label, key):
    # 필수 항목 표시를 위한 HTML 생성
    required = "*" if key in required_fields.get(st.session_state.current_page, []) else ""
    required_html = f"<span style='color: red;'>{required}</span>"
    st.markdown(f"<label for='input_{key}' style='line-height: 1.5;'>{label} {required_html}</label>", unsafe_allow_html=True)
    value = st.text_input(label, key=key, placeholder=label, label_visibility="collapsed")
    st.empty()
    return value

def radio_with_required(label, key, options):
    required = "*" if key in required_fields.get(st.session_state.current_page, []) else ""
    required_html = f"<span style='color: red;'>{required}</span>"
    st.markdown(f"<label for='input_{key}'>{label} {required_html}</label>", unsafe_allow_html=True)
    # 라벨 값을 ' '에서 실제 라벨 값으로 변경하고, label_visibility="collapsed" 추가
    return st.radio(label, options=options, key=key, label_visibility="collapsed")


def selectbox_with_required(label, key, options):
    required = "*" if key in required_fields.get(st.session_state.current_page, []) else ""
    required_html = f"<span style='color: red;'>{required}</span>"
    st.markdown(f"<label for='input_{key}'>{label} {required_html}</label>", unsafe_allow_html=True)
    return st.selectbox(label, options=options, key=key, label_visibility="collapsed")

def text_area_with_required(label, key, placeholder=None, height=None):
    # Determine if the field is required based on the current page and required fields
    required = "*" if key in required_fields.get(st.session_state.current_page, []) else ""
    required_html = f"<span style='color: red;'>{required}</span>"
    # Display the label with the required indicator
    st.markdown(f"<label for='textarea_{key}' style='line-height: 1.5;'>{label} {required_html}</label>", unsafe_allow_html=True)
    # Create the text area widget
    value = st.text_area(label, key=key, placeholder=placeholder if placeholder else label, height=height, label_visibility="collapsed")
    st.empty()  # You might not need this empty space unless you have a specific layout in mind
    return value

def process_response(response):
    # Directly access the content attribute of the AIMessage object
    # This is based on the assumption that the response object has a 'content' attribute.
    # If the actual attribute/method name differs, you will need to adjust this accordingly.
    content = response.content if hasattr(response, 'content') else ""

    # Assuming 'content' contains the string you're interested in,
    # you can further process it as needed
    clean_content = content.replace("content='", "").rstrip("'")
    return clean_content

# def get_enhanced_response(initial_prompt, initial_response):
#     # 사용자로부터의 추가 입력을 받기 위한 text_area 생성
#     user_input = st.text_area("추가 정보를 입력하세요 (만족할 때까지 반복됩니다):", key="user_input")

#     # 새로운 프롬프트 생성
#     # 여기서는 예시로, 초기 프롬프트, 초기 응답, 그리고 사용자의 추가 입력을 결합
#     new_prompt = f"{initial_prompt}\n\nInitial Response: {initial_response}\n\nAdditional User Input: {user_input}"
    
#     # 새로운 프롬프트를 사용하여 OpenAI 모델에 요청
#     # 여기서는 예시로 process_response 함수를 다시 호출
#     new_response = process_response(llm.invoke(new_prompt))
    
#     return new_response

def handle_revision(page_num, user_input_key, response_key, initial_prompt_key):
    user_input = st.session_state[user_input_key]
    initial_prompt = st.session_state[initial_prompt_key]
    initial_response = st.session_state[response_key]
    
    # 새로운 프롬프트 생성
    new_prompt = f"{initial_prompt}\n\nInitial Response: {initial_response}\n\nUser Input: {user_input}"
    # 새로운 응답 가져오기 (여기서는 예시로 초기 응답을 사용합니다. 실제로는 OpenAI API를 호출해야 합니다.)
    new_response = process_response(new_prompt)  # 이 함수는 적절한 OpenAI 호출로 대체해야 합니다.
    
    # 새로운 응답 저장
    st.session_state[response_key] = new_response


# 페이지 함수
def show_page(page):
    get_country_list()
    if page == 0:
        # 취업 확인 페이지
        # st.session_state.employment_status = st.radio("현재 취업 상태를 선택하세요.", ('취업', '미취업'))
        col1, col2 = st.columns(2)
        with col1:
            st.link_button("아직 일자리를 찾고 있어요", hr_site_url)
        with col2:
            st.button("일자리를 찾았어요", on_click=next_page)

    elif page == 1:
        # 취업 기업 정보 입력 페이지
        text_input_with_required("기업 이름", "company_name")
        text_input_with_required("사업자등록번호", "registration_number")
        # st.session_state.company_name = st.text_input("기업 이름")
        # st.session_state.registration_number = st.text_input("사업자등록번호")
        st.session_state.register_certificate = st.file_uploader("사업자등기부등본", type="pdf")
        if test_mode:
            st.session_state.company_location = st.text_input("기업 위치")
            st.session_state.annual_revenue = st.text_input("연매출(예: 100억원)")
            st.session_state.number_of_employees = st.text_input("재직인원(예: 50명)")
            st.session_state.business_type = st.text_input("사업 형태")
            st.session_state.business_introduction = st.text_area("사업 소개")
        else:
            st.session_state.company_introduction = st.file_uploader("기업 소개서", type="pdf")

        
    elif page == 2:
        # 개인정보 입력 페이지
        col1, col2 = st.columns([1, 1])
        with col1:
            text_input_with_required("이름", "full_name")
        with col2:
            text_input_with_required("나이", "age")
        col1, col2 = st.columns([1, 1])
        with col1:
            radio_with_required("성별", "gender", ['남성', '여성'])
        with col2:
            text_input_with_required("전화번호", "phone_number")

        col1, col2 = st.columns([1, 1])
        with col1:
            country_list = st.session_state.country_list
            selectbox_with_required('국적을 선택하세요', 'nationality', country_list)
        with col2:
            text_input_with_required("여권번호", "passport_number")

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
        text_input_with_required("국내 주소지", "kor_address")
        text_input_with_required("본국 주소지", "foreign_address")
        text_input_with_required("이메일 주소", "email")

        text_area_with_required("학력사항", "education","학교명/학위/전공/졸업상태,\n학교명/학위/전공/졸업상태,")
        text_area_with_required("경력사항", "career","회사명/직무/근무기간,\n회사명/직무/근무기간,")
        text_area_with_required("언어점수", "language_score","자격이름/점수 및 등급/취득일/만료일,\n자격이름/점수 및 등급/취득일/만료일,")
        text_area_with_required("자격증", "certificate","자격이름/점수 및 등급/취득일/만료일,\n자격이름/점수 및 등급/취득일/만료일,")
        text_area_with_required("자기소개서", "self_introduction","자기소개서 내용을 입력하세요.")
        

    elif page == 3:
        # 개인 정보를 텍스트로 모음
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

        # 기업 정보를 텍스트로 모음
        company_info_text = f"""
            기업 이름: {st.session_state.get('company_name', '')},
            연매출: {st.session_state.get('annual_revenue', '')},
            재직인원: {st.session_state.get('number_of_employees', '')},
            사업 형태: {st.session_state.get('business_type', '')},
            사업 소개: {st.session_state.get('business_introduction', '')}
        """

        # 텍스트 출력
        # st.text("개인 정보:")
        # st.text(personal_info_text)

        # st.text("기업 정보:")
        # st.text(company_info_text)

        company_introduction_prompt_path = os.path.join('prompt', 'Company-Introduction.txt')
        expertise_workers_path = os.path.join('prompt', 'Expertise-Of-The-Foreign-Workers.txt')
        reasons_cannot_Korean_path = os.path.join('prompt', 'Reasons-Cannot-Replace-With-Korean-Workers.txt')
        reaseos_foreign_path = os.path.join('prompt', 'Reasons-For-Needing-Foreign-Workers.txt')
        
        company_introduction_prompt_text = load_file_content(company_introduction_prompt_path)
        expertise_workers_text = load_file_content(expertise_workers_path)
        reasons_cannot_Korean_text = load_file_content(reasons_cannot_Korean_path)
        reaseos_foreign_text = load_file_content(reaseos_foreign_path)

        prompt1 = merge_contents(company_info_text, personal_info_text, company_introduction_prompt_text)
        prompt2 = merge_contents(company_info_text, personal_info_text, expertise_workers_text)
        prompt3 = merge_contents(company_info_text, personal_info_text, reasons_cannot_Korean_text) 
        prompt4 = merge_contents(company_info_text, personal_info_text, reaseos_foreign_text)

        with get_openai_callback() as cb:
            initial_response1 = llm.invoke(prompt1)
            initial_response2 = llm.invoke(prompt2)
            initial_response3 = llm.invoke(prompt3)
            initial_response4 = llm.invoke(prompt4)

            clean_response1 = process_response(initial_response1)
            clean_response2 = process_response(initial_response2)
            clean_response3 = process_response(initial_response3)
            clean_response4 = process_response(initial_response4)

            # 추출한 정보 출력
            st.write(clean_response1)
            st.write(clean_response2)
            st.write(clean_response3)
            st.write(clean_response4)
        

        # st.write("추가로 이용할 수 있는 서비스를 선택하세요.")

    elif page == 4:
        # 추가 연계 서비스 선택 페이지
        st.write("추가로 이용할 수 있는 서비스를 선택하세요.")

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
llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.5)
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
# 페이지 이동 버튼
    if st.session_state.current_page > 0:
        st.button("이전", on_click=previous_page)
with col3:
    if st.session_state.current_page < len(page_titles) - 1 and st.session_state.current_page != 0:
        st.button("다음", on_click=next_page)

