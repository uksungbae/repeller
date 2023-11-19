# 퇴치메소드
PIR 탐지 퇴치 메소드 통합

1. PIR센서에게 물체가 감지되는지 확인
2. 물체 감지 시 
	2-1. 메소드별 랭킹을 매길수 없는 경우(보상값이 계산이 안된경우, 첫탐지)
	 -랜덤 메소드 재생
		2-1-1. 현재 재생 중인 메소드로 퇴치됨.
		-보상값 계산 
		2-1-2. 현재 재생 중인 메소드로 퇴치가 안됨.
 		-즉시 다른 퇴치 메소드로 변경 후 물체감지로 넘어감
	2-2. 메소드별 랭킹이 나타난 경우(보상값이 계산이 된 경우)
	-최적의 퇴치 메소드 재생
		2-1-1. 현재 재생 중인 메소드로 퇴치됨.
		-보상값 계산 
		2-1-2. 현재 재생 중인 메소드로 퇴치가 안됨.
		-즉시 다른 퇴치 메소드로 변경 후 물체감지로 넘어감
3. 보상값 계산 
  	3-1. 탐지 후 재생한 퇴치 메소드로 바로 퇴치 된 경우
	- 해당 퇴치 메소드에  (+)로 보상값 계산 
	3-2 탐지 후 여러 퇴치 메소드 변경 후 퇴치 된 경우
	- 퇴치된 퇴치 메소드에 (+)로 보상값 계산, 적응을 한 퇴치 메소드에는 (-)로 보상값 계산

