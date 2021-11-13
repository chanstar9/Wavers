# 텔레그렘 추가
1. telegram.py 추가
 - telegram_greeks 함수 추가: 함수 내부에 telegram_token, telegram_chat_id 변수는 개인별로 변경 요망.
 해당함수는 loc_image 변수에 저장된 주소의 이미지 파일을 텔레그램으로 전송하는 함수임.
 (https://vincinotes.com/%ED%8C%8C%EC%9D%B4%EC%8D%AC-%ED%85%94%EB%A0%88%EA%B7%B8%EB%9E%A8-%EB%B4%87-%EC%B1%97%EB%B4%87/ 참조)
 - inner_loop_telegram 함수 추가: Greek별 이미지 파일을 Storage_folder('Image_greeks')에 저장함
 - loop_infinite 함수 추가: 그냥 통화별 step을 추가하는 While 루프. 추후에 에러 발생시 무시하고 재귀함수로 설정할 예정.

2. Deribit.py에 신규함수 추가
- get_index_price_resp 및 get_index_price 함수 추가: 'btc_usd' 또는 'eth_usd' 등의 문자열 입력시 현물 가격 산출해줌.
- add_columns 함수 추가: 기존에 find_data_MongoDB 함수 중에서 NAME에 MAT, STRIKE, CP 등의 정보를 분리하는 코드를 함수화함.
