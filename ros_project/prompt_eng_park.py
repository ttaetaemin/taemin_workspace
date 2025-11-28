#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
박점례 어르신 대화 기반 정서 분석 시스템
- 여성 TTS (pyttsx3)
- STT 대답 대기시간 7초 (phrase_time_limit 10초)
- 총 5개의 질문만 진행
- OpenAI gpt-4o-mini 분석
"""

from openai import OpenAI
import pyttsx3
import speech_recognition as sr
import json
import time
from datetime import datetime


# ==========================================
# 0. OpenAI 클라이언트 설정
# ==========================================
# client = OpenAI(api_key="")  # ★ 여기에 본인 키 넣기


# ==========================================
# 1. 프로필 + 대화 계획
# ==========================================
PROFILE_AND_PLAN = {
    "profile": {
        "name": "서보리",
        "age": 73,
        "gender": "여성",
        "facility_type": "요양원",
        "entrance_day": "2025-11-19",
        "diagnosis": ["치매 초기", "무릎 관절염"],
        "mobility": "보행기 사용, 짧은 거리 보행 가능",
        "cognitive_level": "간단한 대화는 가능하나, 최근 기억은 잘 잊어버림",
        "recent_interests": ["옛날 드라마 이야기", "손주 이야기", "꽃 키우기"],
        "recent_state": "최근에 무릎 통증이 심해져서 외출을 잘 못 하고, 조금 우울해 보임",
        "family_info": "아들, 며느리, 손주 2명. 한 달에 2번 정도 면회.",
        "avoid_topics": ["최근 사망한 가족 이야기", "정치 이야기"]
    },
    "conversation_plan": {
        "topics": [
            {
                "topic_title": "요양원 생활과 적응",
                "questions": [
                    "점례님, 여기 오신 지 얼마 안 되셨는데 요즘 생활은 좀 어떠세요?"
                ]
            },
            {
                "topic_title": "하루 일과와 몸 상태",
                "questions": [
                    "요즘은 아침부터 저녁까지 어떤 순서로 시간을 보내고 계세요?"
                ]
            },
            {
                "topic_title": "옛날 드라마와 추억 이야기",
                "questions": [
                    "예전에 즐겨보시던 드라마나 배우가 있으셨나요?"
                ]
            },
            {
                "topic_title": "가족과 손주 이야기",
                "questions": [
                    "손주분들과 함께 했던 일 중에 기억에 남는 즐거운 일이 있으세요?"
                ]
            },
            {
                "topic_title": "꽃 키우기와 자연",
                "questions": [
                    "꽃을 키우실 때 어떤 점이 가장 즐거우셨나요?"
                ]
            }
        ]
    }
}


# ==========================================
# 2. TTS 설정 (여성 목소리 선택 지원)
# ==========================================
engine = pyttsx3.init()

# ★ 여성 목소리를 강제로 지정하고 싶으면 여기에 숫자를 넣으세요.
#    실행 후 콘솔에 "TTS 사용 가능한 목소리 목록"이 출력됨 → 거기서 인덱스 고르기
FEMALE_VOICE_INDEX = None   # 예: 1, 2, 3 ...  (처음엔 None으로 테스트)

def select_female_voice():
    voices = engine.getProperty('voices')

    print("\n[TTS] 사용 가능한 목소리 목록:")
    for i, v in enumerate(voices):
        print(f"  {i}: name='{v.name}', id='{v.id}'")

    # 1) 사용자가 직접 인덱스 설정한 경우
    if FEMALE_VOICE_INDEX is not None:
        if 0 <= FEMALE_VOICE_INDEX < len(voices):
            engine.setProperty('voice', voices[FEMALE_VOICE_INDEX].id)
            print(f"[TTS] 수동 선택된 목소리: {voices[FEMALE_VOICE_INDEX].name}")
            return
        else:
            print("[TTS] FEMALE_VOICE_INDEX 범위 오류 → 자동 탐색으로 이동")

    # 2) 자동 탐색: female, woman, korean 포함된 음성 찾기
    for v in voices:
        name = v.name.lower()
        if "female" in name or "woman" in name or "korean" in name:
            engine.setProperty('voice', v.id)
            print(f"[TTS] 자동으로 여성/한국어 음성 선택됨: {v.name}")
            return

    # 3) 실패 시 두 번째 음성으로라도 사용
    if len(voices) > 1:
        engine.setProperty('voice', voices[1].id)
        print(f"[TTS] 여성 음성을 찾지 못해 1번 인덱스로 설정: {voices[1].name}")
    else:
        print("[TTS] 목소리가 1개뿐이라 기본 음성 사용")

select_female_voice()


def speak(text: str):
    print(f"\n[TTS] 질문: {text}")
    engine.say(text)
    engine.runAndWait()


# ==========================================
# 3. STT 설정
# ==========================================
recognizer = sr.Recognizer()
BT_MIC_INDEX = None   # 필요하면 블루투스 마이크 index 지정

def listen() -> str:
    """마이크에서 음성 듣고 텍스트로 변환"""
    source_mic = sr.Microphone(device_index=BT_MIC_INDEX) if BT_MIC_INDEX else sr.Microphone()

    with source_mic as source:
        print("\n🎤 어르신의 답변을 기다리는 중... 천천히 말씀하셔도 됩니다.")
        recognizer.adjust_for_ambient_noise(source, duration=0.3)

        try:
            # ▼ 7초 동안 말 시작을 기다림
            # ▼ 최대 10초 발화 허용
            audio = recognizer.listen(source, timeout=7, phrase_time_limit=10)
        except Exception as e:
            print(f"[STT 오류 - 듣기 실패] {e}")
            return ""

    try:
        text = recognizer.recognize_google(audio, language="ko-KR")
        print(f"[STT] 인식된 답변: {text}")
        return text
    except Exception as e:
        print(f"[STT 오류 - 인식 실패] {e}")
        return ""


# ==========================================
# 4. LLM 정서 분석
# ==========================================
def analyze_answer(profile, topic_title, question, answer):
    profile_json = json.dumps(profile, ensure_ascii=False)

    prompt = f"""
당신은 요양원 어르신의 정서 상태를 분석하는 보조 도우미입니다.

[프로필]
{profile_json}

[주제] {topic_title}
[질문] {question}
[답변] {answer}

아래 항목을 기반으로 JSON만 출력하십시오.
- mood_valence: -2 ~ +2
- happiness_score: 0 ~ 100
- energy_level: 0 ~ 100
- pain_level: 0 ~ 10
- loneliness_level: 0 ~ 10
- comment: 2~3문장 요약 평가
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "당신은 노인 대화 정서 분석 전문가입니다."},
            {"role": "user", "content": prompt}
        ]
    )

    content = response.choices[0].message.content

    try:
        return json.loads(content)
    except:
        print("[경고] JSON 파싱 실패:")
        print(content)
        return {"comment": content}


# ==========================================
# 5. 메인: 총 5개 질문만 진행
# ==========================================
def run_conversation_session():
    profile = PROFILE_AND_PLAN["profile"]
    topics = PROFILE_AND_PLAN["conversation_plan"]["topics"]

    session = {
        "profile": profile,
        "session_started_at": datetime.now().isoformat(),
        "exchanges": []
    }

    QUESTION_LIMIT = 5
    MAX_STT_RETRY = 3
    count = 0

    for topic in topics:
        for question in topic["questions"]:

            if count >= QUESTION_LIMIT:
                print("\n[안내] 5개의 질문을 모두 완료했습니다.\n")
                session["session_ended_at"] = datetime.now().isoformat()
                return session

            count += 1
            answer = ""

            # 음성 인식 3번까지 재시도
            for attempt in range(MAX_STT_RETRY):
                speak(question)
                answer = listen()

                if answer.strip():
                    break
                print(f"[주의] 인식 실패 (시도 {attempt+1}/{MAX_STT_RETRY})")

            if not answer.strip():
                print("[건너뜀] 답변을 받지 못했습니다.\n")
                continue

            analysis = analyze_answer(profile, topic["topic_title"], question, answer)

            session["exchanges"].append({
                "topic": topic["topic_title"],
                "question": question,
                "answer": answer,
                "analysis": analysis,
                "timestamp": datetime.now().isoformat()
            })

    session["session_ended_at"] = datetime.now().isoformat()
    return session


# ==========================================
# 6. 실행
# ==========================================
if __name__ == "__main__":
    result = run_conversation_session()

    print("\n================ 세션 전체 결과(JSON) ================\n")
    print(json.dumps(result, indent=2, ensure_ascii=False))
