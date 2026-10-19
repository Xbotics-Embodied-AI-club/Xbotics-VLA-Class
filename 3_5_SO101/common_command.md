lerobot-find-port

lerobot-find-cameras opencv

lerobot-calibrate \
    --robot.type=so101_follower \
    --robot.port=/dev/ttyFollower \
    --robot.id=my_awesome_follower_arm

lerobot-calibrate \
    --teleop.type=so101_leader \ 
    --teleop.port=/dev/ttyLeader \ 
    --teleop.id=my_awesome_leader_arm