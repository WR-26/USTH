Cau 1 :

1. Cấu hình Hostname, Enable Password và IP Interface
   
Trên Router R1:

<img width="950" height="1011" alt="image" src="https://github.com/user-attachments/assets/be376cd9-58f1-414d-9dee-c6c7eec7f80d" />

Trên Sw_Core (Switch 3560):

<img width="961" height="1008" alt="image" src="https://github.com/user-attachments/assets/e0af90ef-aa06-4a95-8481-2ae67ec04042" />

Trên SW_01:

<img width="955" height="993" alt="image" src="https://github.com/user-attachments/assets/53d31415-12e4-4564-8c3b-e3fda933ffa1" />

Trên SW_02:

<img width="938" height="1000" alt="image" src="https://github.com/user-attachments/assets/eae92dbe-1bf7-4924-bc17-987dee0da70f" />


2. Cấu hình Trunking, VTP Domain và Khởi tạo VLAN

Cấu hình đường Trunk kết nối giữa các Switch:

SW_Core:

<img width="943" height="976" alt="image" src="https://github.com/user-attachments/assets/7be91cfb-94cb-4f16-9cbd-e99141f21e96" />

SW_01:

<img width="933" height="958" alt="image" src="https://github.com/user-attachments/assets/3452288a-61a2-4acb-a6c8-646f13062f6f" />


SW_02:

<img width="925" height="992" alt="image" src="https://github.com/user-attachments/assets/039837ea-e547-4f14-a90d-6c2f175bb9ce" />


Cấu hình VTP Domain ccna.com và Mật khẩu admin:

Sw_Core (VTP Server):



SW_01 (VTP Client):

<img width="557" height="143" alt="image" src="https://github.com/user-attachments/assets/054437b6-afb9-4d86-a2b3-5532fea8ce7f" />

SW_02 (VTP Client):

<img width="873" height="123" alt="image" src="https://github.com/user-attachments/assets/6361a8b1-11cd-4012-b188-625c506dfa37" />


3. Cấu hình Interface VLAN & Gán cổng Access

Trên Sw_Core (Tạo Gateway cho các VLAN):











