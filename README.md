# Binance Auto Algorithm
## Making Auto trade Binance Future by api and websocket api


# *///---------------------------------------------///*

# Needs

api.txt (from Binance api hompage)

in api.txt file (just need two lines)

1. api_key (txt)
2. secret key

Python Modules

TA-Lib Module 

Pandas Module

CCXT Module


put every python files into same folders directory with api.txt

ex)
folders)

 |
 
 ㄴapi.txt
 
 |
 
 ㄴexchange_utils.py
 
 |
 
 ㄴmain.py
 
 |
 
 ㄴrecord_utils.py
 
 |
 
 ㄴRsiNew.py
 
 |
 
 ㄴtrading_utils.py
 
 |
 
 ㄴvolume_utils.py

# *///---------------------------------------------///*

# 필요항목

api.txt (바이낸스 홈페이지에서 api 신청후 받아서 메모장에 저장)

api.txt 파일안에 문자열 단 두줄만 필요

1. api_key (txt)
2. secret key

Python Modules

TA-Lib Module 

Pandas Module

CCXT Module

모든 파이선(.py)파일을 같은 경로에 있는 폴더에 api.txt파일과 함께 넣기

ex)
folders)

 |
 
 ㄴapi.txt
 
 |
 
 ㄴexchange_utils.py
 
 |
 
 ㄴmain.py
 
 |
 
 ㄴrecord_utils.py
 
 |
 
 ㄴRsiNew.py
 
 |
 
 ㄴtrading_utils.py
 
 |
 
 ㄴvolume_utils.py

 # *///---------------------------------------------///*

 # Result | 결과
 
Start Seed	Entry Price	Exit Price	Profit/Loss	Fee	Net Profit	Finish Seed	Entry Time	Exit Time	Result	Leverage	승률
50.89671569	67672.8	67651.4	-1.284			49.61271569	06-01-24 16:18	06-01-24 16:25	패	75	0.6
49.61271569	67656	67786.4	7.4328			57.04551569	06-01-24 16:27	06-01-24 16:48	승	75	
55.4476091	68966.7	68876.7	-5.13			46.3890722	06-04-24 8:15	06-04-24 8:37	패	75	
28	70772.2	71176.4	11.3176			37.205	06-06-24 8:28	06-06-24 9:17	승	75	
23	70225	70702.7	10.98			33.5186	06-07-24 5:01	06-07-24 5:39	승	75	
61	67065.9	66.982.90	-5.32			51	06-13-24 12:38	06-13-24 12:39	패	75	
53.60022322	67684.1	68024.8	14.9908			51.70187082	06-13-24 21:58	06-13-24 22:29	승	75	
35.02043923	67573.2	67554.1	-0.76399999			33.80140723	06-13-24 22:57	06-13-24 22:58	패	75	
17.78317129	65530.1	65499.6	-0.671			17.1565019	06-15-24 2:21	06-15-24 2:22	패	75	
14.48	6612187	66279.9	2.37			15.8619	06-15-24 18:32	06-15-24 19:38	승	75	
14.74137525	66315.4	66315.8	0.0068			14.43360598	06-15-24 21:00	06-15-24 21:00	승	75	
11.2106832	66004.2	65873.3	-0.9163			10.80564546	06-16-24 5:19	06-16-24 5:19	패	75	
10.80564546	65913.1	66044.8	1.58			11.9993	06-16-24 5:19	06-16-24 5:31	승	75	
11.9993358	65913.1	66044.8	1.5804			12.7895	06-16-24 5:19	06-16-24 5:31	승	75	
10.0928011	65612.1	65467.7	-1.8772			10.14949462	06-17-24 21:28	06-17-24 22:06	패	75	
10.1	64,310.30	64,567.40	2.82			12.212	06-21-24 12:58	06-21-24 13:20	승	75	
9.64382495	64424.2	64291	-1.7316			9.3266284	06-21-24 16:48	06-21-24 16:51	패	75	
7.67627818	64334.7	64203.7	-1.31			7.42883242	06-23-24 14:27	06-23-24 23:17	패	75	
7.42883242	60721.1	61394.7	4.7152			10.18703876	06-24-24 18:33	06-24-24 18:54	승	75	
10.18703876	61259.7	61502.2	2.91			12.65429732	06-27-24 0:12	06-27-24 1:09	승	75	
12.65429732	60723.7	60859.2	1.897			13.70021702	06-29-24 14:20	06-29-24 16:01	승	75	
13.70021702	61464.1	61341	-1.8465			10.93267877	06-30-24 21:37	06-30-24 21:39	패	75	
10.93267877	61335.1	61523.1	2.256			12.45152957	06-30-24 21:39	06-30-24 21:51	승	75	
12.45152957	61912.6	62199.9	4.3			16.39	07-03-24 10:07	07-03-24 10:23	승	75	
16.39	59977.5	60225	4.95			20.1366	07-04-24 10:16	07-04-24 10:25	승	75	
20.1366	54226.9	54118.2	-2.8262			15.90198079	07-05-24 4:18	07-05-24 4:19	패	75	
