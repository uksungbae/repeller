# 퇴치메소드(rankingTest.py)(단순 if-else로직)
전체적인 시스템 구조
https://lucid.app/users/registerOrLogin/free?showLogin=false&invitationId=inv_8b551305-d3a8-4fd4-bf30-5bd6d67ad620&productOpt=chart&invitationType=documentAcceptance&returnUrlOverride=%2Flucidchart%2F3aa756b9-d3dd-4827-9936-aa33cff07374%2Fedit%3Fviewport_loc%3D-3774%252C-3777%252C4501%252C2536%252C0_0%26invitationId%3Dinv_8b551305-d3a8-4fd4-bf30-5bd6d67ad620


## 1. PIR센서에게 물체가 감지되는지 확인
## 2. 물체 감지 시 
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
## 3. 보상값 계산 
  	3-1. 탐지 후 재생한 퇴치 메소드로 바로 퇴치 된 경우
	- 해당 퇴치 메소드에  (+)로 보상값 계산 
	3-2 탐지 후 여러 퇴치 메소드 변경 후 퇴치 된 경우
	- 퇴치된 퇴치 메소드에 (+)로 보상값 계산, 적응을 한 퇴치 메소드에는 (-)로 보상값 계산

# DQN_Agent.py
keras 모델을 통한 딥러닝
## 1. 개요
이 프로젝트는 강화 학습 에이전트를 사용하여 소리 기반의 퇴치 시스템을 제어하는 DQN을 구현합니다. 에이전트는 모션이 감지될 때 특정 소리를 재생하도록 훈련되며, 소리가 감지된 모션을 퇴치하는 효과에 따라 보상을 최대화하는 것을 목표로 합니다. 이 시스템은 Pygame(퇴치용 소리 출력), Keras(신경망 모델 구축용)를 사용합니다.


## 2. 주요 구성 요소
###Agent 클래스
Agent 클래스는 DQN을 캡슐화하여 신경망, 메모리 및 행동을 처리합니다. 주요 메서드는 다음과 같습니다.

_build_model(self): 신경망 모델을 구축.
save_model(self): 모델 가중치를 저장.
act(self, state): 현재 상태를 기반으로 행동을 선택.
remember(self, state, action, reward, next_state, done): 환경의 Action에 따른 학습을 메모리에 저장.
replay(self, sample_batch_size): 메모리를 통해 학습.

###Repeller 클래스
Repeller 클래스는 환경과 에이전트와의 상호작용을 관리합니다. 주요 메서드는 다음과 같습니다.

getResult(self, action, returnTimeAction): 수행한 행동과 경과 시간을 기반으로 보상을 계산.
run(self): 에이전트를 실행하는 메인 루프를 처리하며, 모션 감지, 소리 재생 및 에이전트 학습을 담당.


## 3. 참고 사항
시스템은 JSON 객체를 통해 stdin에서 모션 감지 입력과 응답을 읽어야 합니다.
모델 가중치는 /home/pi/Projects/WARS/wars_weight.h5에 저장되고 로드됩니다.
에이전트는 초기에는 높은 Exploration으로 시작하며, 학습하면서 점차 감소합니다.



# 추후 보완사항
1. 
2.
