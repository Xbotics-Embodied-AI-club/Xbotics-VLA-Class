#!/usr/bin/env bash
# SO101 leader -> follower teleoperation + dataset recording.
# Task: put the cuboid into the basket.

set -euo pipefail

lerobot-record \
    --robot.type=so101_follower \
    --robot.port=/dev/ttyFollower \
    --robot.id=my_awesome_follower_arm \
    --robot.cameras='{ front: {type: opencv, index_or_path: 0, width: 640, height: 480, fps: 30, fourcc: "MJPG"}, side: {type: opencv, index_or_path: 2, width: 640, height: 480, fps: 30, fourcc: "MJPG"} }' \
    --teleop.type=so101_leader \
    --teleop.port=/dev/ttyLeader \
    --teleop.id=my_awesome_leader_arm \
    --display_data=true \
    --dataset.repo_id=local/put_cuboid_into_basket \
    --dataset.num_episodes=5 \
    --dataset.single_task="Put the cuboid into the basket" \
    --dataset.push_to_hub=false \
    --dataset.episode_time_s=30 \
    --dataset.reset_time_s=30

# --resume=true
