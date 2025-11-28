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
# 블루투스 마이크를 쓰면 arecord -l 로 확인한 index를 여기 넣으면 됩니다.
MIC_INDEX   = None      # 예: 1

SAMPLE_RATE = 16000

# ============================
# 2. 세션 ID (웹 UI와 공유)
# ============================
# 웹 브라우저 Network 탭 → chat-... 요청의 session_id 값
SESSION_ID = "chat-1763816316954"   



# ============================
# 3. 종료 키워드 (음성 인식 결과에 포함되면 대화 종료 처리)
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
# 4. 유틸 함수들
# ============================
def record_audio(seconds: int = 7) -> str:
    """마이크에서 음성을 녹음해서 임시 wav 파일 경로 반환"""
    print(f"\n🎤 {seconds}초 동안 녹음합니다. 말씀해 주세요...")

    if MIC_INDEX is not None:
        # 입력 디바이스만 MIC_INDEX 로 설정, 출력은 기존 기본값 유지
        try:
            in_dev, out_dev = sd.default.device
        except Exception:
            out_dev = None
        sd.default.device = (MIC_INDEX, out_dev)

    audio = sd.rec(
        int(seconds * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1
    )
    sd.wait()

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    sf.write(tmp.name, audio, SAMPLE_RATE)
    print(f"[녹음 완료] 파일: {tmp.name}")
    return tmp.name


def call_stt(audio_path: str) -> str:
    """음성 파일을 /api/stt 에 보내 텍스트로 변환"""
    try:
        with open(audio_path, "rb") as f:
            resp = requests.post(STT_URL, files={"audio": f}, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print("❌ STT 호출 오류:", e)
        return ""

    # 응답 예시: {"success": true, "text": "인식된 텍스트", "language": "ko"}
    text = data.get("text", "") or ""
    print(f"🧑 (음성→텍스트): {text}")
    return text


def call_chat(text: str) -> str:
    """텍스트를 /api/chat 으로 보내서 AI 답변 텍스트만 반환"""
    payload = {
        "message": text,
        "model": "gpt-4o-mini",
        "session_id": SESSION_ID,
    }

    try:
        resp = requests.post(CHAT_URL, json=payload, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print("❌ Chat 호출 오류:", e)
        # 최소한 대화는 이어가도록 fallback 메시지
        return "죄송해요, 잠깐 말을 잘 못 알아들었어요. 한 번만 더 말씀해 주실 수 있을까요?"

    # 응답 예시:
    # {
    #   "success": true,
    #   "response": "AI 답변",
    #   "session_id": "chat-...",
    #   "model": "gpt-4o-mini"
    # }
    if isinstance(data, dict) and "response" in data:
        reply = data["response"]
    elif isinstance(data, str):
        reply = data
    else:
        reply = str(data)

    print(f"🤖 (AI): {reply}")
    return reply


def call_tts(text: str) -> str | None:
    """텍스트를 /api/tts 로 보내 wav 파일 생성 후, 파일 경로 반환"""
    payload = {
        "model": "tts-1",
        "text": text,
        "voice": "nova",   # alloy / nova / shimmer / onyx 등 변경 가능
    }

    try:
        resp = requests.post(TTS_URL, json=payload, timeout=10)
    except Exception as e:
        print("❌ TTS 호출 오류:", e)
        return None

    if resp.status_code != 200:
        print("❌ TTS 오류:", resp.text)
        return None

    # ※ 서버가 WAV 바이너리를 돌려준다는 가정
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    with open(tmp.name, "wb") as f:
        f.write(resp.content)

    print(f"[TTS 생성 파일]: {tmp.name}")
    return tmp.name


def play_audio(path: str) -> None:
    """주어진 오디오 파일 재생"""
    try:
        data, sr = sf.read(path)
        sd.play(data, sr)
        sd.wait()
    finally:
        # 재생 후 임시 파일 삭제 (에러 나더라도 시도)
        try:
            os.remove(path)
        except OSError:
            pass


# ============================
# 5. 시작 인사 (한 번만)
# ============================
def play_greeting():
    """
    스크립트 시작 시 한 번만 실행되는 인사.
    웹 UI와 같은 캐릭터로 인사하게 하기 위해 /api/chat 을 한번 호출하고,
    그 답변을 /api/tts 로 읽어준다.
    """
    print("\n[초기 인사] AI가 먼저 인사합니다...")

    # 알프레드에게 "첫 인사 멘트"를 만들어 달라고 요청
    greeting_prompt = (
        "지금부터 너는 요양원에서 일하는 말동무 AI '알프레드'야. "
        "어르신과 처음 대화를 시작하는 상황이라고 생각하고, "
        "한 번만 인사해 줘. "
        "예를 들어, \"안녕하세요, 저는 어르신과 이야기 나누는 말동무 알프레드예요. "
        "어르신 성함을 알려주실 수 있을까요?\" 와 비슷한 느낌으로 말해 줘."
    )

    ai_text = call_chat(greeting_prompt)

    tts_path = call_tts(ai_text)
    if tts_path:
        play_audio(tts_path)


# ============================
# 6. 메인 음성 대화 루프
# ============================
def voice_chat_loop():
    print("\n====== 🎤 음성 대화 시작 ======")
    print(f"세션 ID: {SESSION_ID}")
    time.sleep(0.5)

    while True:
        # 1) 음성 녹음
        audio_path = record_audio(seconds=7)

        # 2) STT
        user_text = call_stt(audio_path)

        # STT용 임시 파일 삭제
        try:
            os.remove(audio_path)
        except OSError:
            pass

        if not user_text.strip():
            print("⚠️ 인식된 텍스트가 없습니다. 다시 시도합니다.")
            continue

        # 2-1) 종료 키워드가 포함되어 있는지 검사
        quit_detected = any(k in user_text for k in QUIT_KEYWORDS)

        # 3) Chat → 알프레드 답변
        ai_text = call_chat(user_text)

        # 4) TTS + 재생 (마무리 인사도 여기서 읽어 줌)
        tts_path = call_tts(ai_text)
        if tts_path:
            play_audio(tts_path)

        # 5) 종료 키워드가 나온 경우: 감정 평가 JSON 추가 요청 후 종료
        if quit_detected:
            print("\n[감정 평가] 이번 대화를 JSON으로 평가합니다...\n")
            eval_prompt = "이번 대화 감정 평가 JSON으로 정리해줘"
            eval_json = call_chat(eval_prompt)  # 프롬프트 규칙상 JSON만 반환하도록 설정해둔 상태
            print("=== 감정 평가 JSON ===")
            print(eval_json)
            break

        # (선택) 키보드로도 종료하고 싶으면 이 부분 사용
        cmd = input("\n계속하려면 Enter, 종료하려면 q 입력: ").strip().lower()
        if cmd == "q":
            eval_prompt = "이번 대화 감정 평가 JSON으로 정리해줘"
            eval_json = call_chat(eval_prompt)
            print("=== 감정 평가 JSON ===")
            print(eval_json)
            break


# ============================
# 7. 실행
# ============================
if __name__ == "__main__":
    # 1) 먼저 인사 한 번 음성으로 재생
    play_greeting()
    # 2) 그 다음부터 음성 대화 루프
    voice_chat_loop()
