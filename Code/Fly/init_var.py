

F = open("init.txt",'r') 
test =  F.readlines()
print test
content = [x.strip().split(' ') for x in test]

TIME_INTERVAL = float(content[0][1])
MAX_SPEED = float(content[1][1])
MAX_ROTATION_SPEED = float(content[2][1])
TURN_THRESHOLD = float(content[3][1])
POSITION_THRESHOLD = float(content[4][1])
EIGEN_ANGLE = float(content[5][1])
ANGLE_CORRECTION_THRESHOLD = float(content[6][1])

print content, TIME_INTERVAL, MAX_SPEED, MAX_ROTATION_SPEED, TURN_THRESHOLD, POSITION_THRESHOLD, EIGEN_ANGLE, ANGLE_CORRECTION_THRESHOLD