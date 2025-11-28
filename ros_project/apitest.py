from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn
import time


class LoadCellReading(BaseModel):
    """로드셀을 통해 측정된 현재 무게 센싱 데이터"""
    weight_grams: float
    """현재 측정된 무게 (그램 단위)"""
    timestamp: str
    """데이터가 측정된 시간 (ISO 8601 형식)"""
    unit: str = "g"
    """무게의 단위 (기본값: g)"""

class SensingResponse(BaseModel):
    """센싱 요청에 대한 표준 응답 구조"""
    status: str = "success"
    """요청 처리 결과 (success 또는 error)"""
    data: LoadCellReading
    """측정된 무게 데이터"""

app = FastAPI(
    title="로드셀 센싱 테스트 API",
    description="2.1 섹션의 로드셀 센싱 기능을 테스트합니다."
)

@app.get(
    "/sensor/loadcell/{device_id}",
    response_model=SensingResponse,  # 응답 모델 지정
    summary="로드셀 무게 측정값 조회 (테스트)",
    description="특정 로드셀 장치의 가상 무게 데이터를 반환합니다."
)
def read_loadcell_data(
    device_id: str
):
   
    
    # **가상 테스트 로직**
    if device_id == "tray_station_01":
        # 성공적인 응답을 위한 데이터 생성
        current_reading = LoadCellReading(
            weight_grams=350.5, # 가상 무게 값
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%S+09:00")
        )
        return SensingResponse(data=current_reading)
    
    elif device_id == "error_test":
        # 에러 응답 테스트를 위한 HTTPException 발생
        raise HTTPException(
            status_code=404, 
            detail="요청하신 장치 ID를 찾을 수 없습니다. (에러 테스트)"
        )
        
    else:
        # 일반적인 실패 응답
        raise HTTPException(
            status_code=400, 
            detail="유효하지 않은 장치 ID입니다."
        )



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)