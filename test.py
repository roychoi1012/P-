import streamlit as st
from openai import OpenAI
import json
import time
from PIL import Image

# OpenAI 클라이언트 생성
client = OpenAI(api_key="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")

# Streamlit 앱 타이틀 설정
st.title("사회 트렌드와 관련 직업 추천 시스템")

# 사용자 입력: 분야 선택
q = st.text_input("분야를 입력하세요:")

# 파일 업로드: 데이터 파일과 뉴스 파일을 업로드
uploaded_trend = st.file_uploader("사회 트렌드 데이터 업로드", type=["txt"])
uploaded_news = st.file_uploader("뉴스 파일 업로드", type=["txt"])

# 로딩 gif 표시
def show_loading():
    gif = Image.open("loading.gif")
    st.image(gif, use_column_width=True, caption="로딩 중... 잠시만 기다려 주세요.")

# 결과 저장용 리스트
answers = []

# 파일이 업로드되었을 경우 처리
if uploaded_trend and uploaded_news:
    # 로딩 gif 시작
    show_loading()

    # 파일 내용 읽기
    trend = uploaded_trend.read().decode("utf-8")
    News = uploaded_news.read().decode("utf-8")

    # 5회 반복 실행 (Self-Consistency)
    for i in range(3):
        # 첫 번째 요청: 사회 트렌드와 분야의 연관성을 분석
        response1 = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={ "type": "json_object" },
            messages=[
                {"role": "system", "content": "You are a helpful assistant designed to output JSON. Please write in Korean."},
                {"role": "user", "content": f"사회 트렌드 분석 결과는 다음과 같습니다: {trend}. 이를 기반으로 '{q}'와 연관된 사회 트렌드를 분석하고, 중간 결과를 나타내시오."}
            ]
        )
        result1 = response1.choices[0].message.content

        # 두 번째 요청: 중간 결과를 활용하여 직업을 추천
        response2 = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={ "type": "json_object" },
            messages=[
                {"role": "system", "content": "You are a helpful assistant designed to output JSON. Please write in Korean."},
                {"role": "user", "content": f"이전 분석 결과는 다음과 같습니다: {result1}. 이를 기반으로 '{News}'의 내용을 참고하여 추천할 만한 관련 직업 3개를 명시하세요. 출력값은 다음과 같은 형식을 따르세요. {{'직업':[의사,회계사,작곡가]}}."}
            ]
        )
        result2 = response2.choices[0].message.content
        
        result2 = json.loads(result2)
        answers.append(result2["직업"])

    # 최종 결과: 가장 많이 나온 직업과 필요한 역량 분석
    response_final = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={ "type": "json_object" },
        messages=[
            {"role": "system", "content": "You are a helpful assistant designed to output JSON. Please write in Korean."},
            {"role": "user", "content": f"{answers}의 내용에서 가장 많이 나온 직업 3개와 각 직업에 대한 필요 역량을 답변하세요. 출력값은 다음과 같은 형식을 따르세요. {{'직업':[의사,회계사,작곡가], '필요역량':[의사자격증,수학지식,음악감각]}}. 직업[0]에 대한 필요역량은 필요역량[0]에 해당하는 방식이다."}
        ]   
    )

    result_final = response_final.choices[0].message.content

    # 로딩 화면이 끝난 후 결과 출력
    st.subheader("최종 추천 직업과 필요 역량")
    result = json.loads(result_final)

    # 직업과 필요 역량을 예쁘게 출력
    st.write("**추천 직업**")
    st.write(f"1. {result['직업'][0]}")
    st.write(f"2. {result['직업'][1]}")
    st.write(f"3. {result['직업'][2]}")

    st.write("**필요 역량**")
    st.write(f"1. {result['필요역량'][0]}")
    st.write(f"2. {result['필요역량'][1]}")
    st.write(f"3. {result['필요역량'][2]}")

else:
    st.warning("사회 트렌드 파일과 뉴스 파일을 업로드해 주세요.")