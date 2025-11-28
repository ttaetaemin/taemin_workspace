#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
로컬 STT + Chat + TTS 음성 인터페이스 (웹 UI 세션 공유 버전)

- /api/stt  : Whisper 음성인식
- /api/chat : ChatGPT 대화 (웹 test_chat_interface.html 과 동일 세션 사용)
- /api/tts  : TTS 음성 출력

웹 UI의 Network 탭에서 확인한 session_id를 그대로 사용합니다.
"""

import os
import time
import tempfile

import requests
import sounddevice as sd
import soundfile as sf

# ============================
# 0. 서버 주소 & 엔드포인트
# ============================
API_BASE = "http://192.168.0.218:8001"

STT_URL  = f"{API_BASE}/api/stt"
CHAT_URL = f"{API_BASE}/api/chat"
TTS_URL  = f"{API_BASE}/api/tts"

# ============================
# 1. 오디오 설정
# ============================
MIC_INDEX   = None
SAMPLE_RATE = 16000

# ============================
# 2. 세션 ID (웹 UI와 공유)
# ============================
SESSION_ID = "chat-1763816316954"

# ============================
# 3. 종료 키워드
# ============================
QUIT_KEYWORDS = [
    "오늘은 여기까지",
    "이제 그만",
    "대화 끝",
    "그만 이야기할래",
    "쉬고 싶어요",
    "알프레드, 고마워 이제 괜찮아",
]

# ============================
# 4. 알프레드 SYSTEM PROMPT
# ============================
ALFRED_SYSTEM_PROMPT = """
당신은 요양원에서 오래 근무한 베테랑 직원이자 말동무 AI “알프레드”입니다.
반드시 아래 규칙을 따릅니다.

[알프레드 기본 성향]
- 어떤 이야기도 진심으로 잘 들어주고, 어르신의 감정에 세심하게 공감합니다.
- 말투는 따뜻하고 부드럽고, 존댓말 사용.
- 해결책은 간결하고 부담 없는 방식으로 제시.

[대화 규칙]
1) 첫 인사 시 스스로를 “말동무 알프레드”라고 소개.
2) 반드시 상대 이름 또는 호칭(“어르신”)을 물어보고 기억해 사용.
3) 대화 초반 3~5턴 안에 다음 2가지를 질문:
   - “어제 생활 중에 좋았던 점 있으셨어요?”
   - “어제 생활 중에 힘들거나 불편했던 점 있으셨어요?”
4) 스몰토크 + 감정 케어 중심.

[감정 평가 규칙]
사용자가 “이번 대화 감정 평가 JSON으로 정리해줘”라고 하면,
**JSON만 출력**, 다른 문장 금지.

JSON 예시:
{
  "mood_valence": "positive | neutral | negative",
  "happiness_score": 0~1,
  "energy_level": 0~1,
  "loneliness_level": 0~1,
  "pain_level": 0~1,
  "summary": "한 문장 요약"
}
"""

# ============================
# 5. 유틸 함수들
# ============================

def record_audio(seconds: int = 7) -> str:
    print(f"\n🎤 {seconds}초 동안 녹음합니다. 말씀해 주세요...")

    if MIC_INDEX is not None:
        try:
            in_dev, out_dev = sd.default.device
        except Exception:
            out_dev = None
        sd.default.device = (MIC_INDEX, out_dev)

    audio = sd.rec(int(seconds * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1)
    sd.wait()

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    sf.write(tmp.name, audio, SAMPLE_RATE)
    print(f"[녹음 완료] 파일: {tmp.name}")
    return tmp.name


def call_stt(audio_path: str) -> str:
    try:
        with open(audio_path, "rb") as f:
            resp = requests.post(STT_URL, files={"audio": f}, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        print("❌ STT 오류:", e)
        return ""

    data = resp.json()
    text = data.get("text", "") or ""
    print(f"🧑 (음성→텍스트): {text}")
    return text


def call_chat(text: str) -> str:
    """system_prompt 추가 버전"""
    payload = {
        "message": text,
        "model": "gpt-4o-mini",
        "session_id": SESSION_ID,
        "system_prompt": ALFRED_SYSTEM_PROMPT,   # ← 핵심 추가!
    }

    try:
        resp = requests.post(CHAT_URL, json=payload, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print("❌ Chat 오류:", e)
        return "죄송해요, 제가 잠깐 잘 못 알아들었어요."

    if isinstance(data, dict) and "response" in data:
        reply = data["response"]
    else:
        reply = str(data)

    print(f"🤖 (AI): {reply}")
    return reply


def call_tts(text: str) -> str | None:
    payload = {
        "model": "tts-1",
        "text": text,
        "voice": "nova",
    }

    try:
        resp = requests.post(TTS_URL, json=payload, timeout=10)
    except Exception as e:
        print("❌ TTS 오류:", e)
        return None

    if resp.status_code != 200:
        print("❌ TTS 오류:", resp.text)
        return None

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    with open(tmp.name, "wb") as f:
        f.write(resp.content)

    print(f"[TTS 생성 파일]: {tmp.name}")
    return tmp.name


def play_audio(path: str):
    try:
        data, sr = sf.read(path)
        sd.play(data, sr)
        sd.wait()
    finally:
        try:
            os.remove(path)
        except:
            pass


# ============================
# 6. 시작 인사
# ============================
def play_greeting():
    print("\n[초기 인사] AI가 먼저 인사합니다...")

    greeting_prompt = (
        "어르신과 처음 만났어. 알프레드답게 따뜻하게 인사하고, "
        "성함을 확인하는 첫 멘트만 한 번 출력해줘."
    )

    ai_text = call_chat(greeting_prompt)
    tts_path = call_tts(ai_text)
    if tts_path:
        play_audio(tts_path)


# ============================
# 7. 메인 음성 대화 루프
# ============================
def voice_chat_loop():
    print("\n====== 🎤 음성 대화 시작 ======")
    print(f"세션 ID: {SESSION_ID}\n")
    time.sleep(0.5)

    while True:
        audio_path = record_audio(seconds=7)
        user_text = call_stt(audio_path)

        try: os.remove(audio_path)
        except: pass

        if not user_text.strip():
            print("⚠️ 인식 실패, 다시 시도.")
            continue

        quit_detected = any(k in user_text for k in QUIT_KEYWORDS)

        ai_text = call_chat(user_text)

        tts_path = call_tts(ai_text)
        if tts_path:
            play_audio(tts_path)

        if quit_detected:
            print("\n[감정 평가] JSON 생성중...\n")
            eval_json = call_chat("이번 대화 감정 평가 JSON으로 정리해줘")
            print("=== 감정 평가 JSON ===")
            # print(eval_json)
            break

        cmd = input("\nEnter=계속 / q=종료 : ").strip().lower()
        if cmd == "q":
            eval_json = call_chat("이번 대화 감정 평가 JSON으로 정리해줘")
            print("=== 감정 평가 JSON ===")
            # print(eval_json)
            break


# ============================
# 8. 실행
# ============================

if __name__ == "__main__":
    play_greeting()
    voice_chat_loop()
