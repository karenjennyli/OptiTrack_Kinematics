from DeltaArray import DeltaArray
from OptiTrackStreaming.DataStreamer import OptiTrackDataStreamer
import numpy as np
from time import sleep
import time

da = DeltaArray('COM3')

# for this to work enter the "Data Streaming Pane" in Motive:
#   "Broadcast Frame Data" is turned on
#   Command Port = 1510
#   Data Port = 1511
#   Multicast Interface = 239.255.42.99

# https://v22.wiki.optitrack.com/index.php?title=Data_Streaming
op = OptiTrackDataStreamer()

def sample_actuator(max_height, max_actuator_dif, spacing=.005):
    pts = np.arange(.005, max_height, spacing)
    pts = pts.reshape((pts.shape[0], 1))
    return pts

def save_training_data(data, filename="actuator_data"):
    np.save(filename,data)

def retract():
    da.reset()
    time.sleep(2)

sample = sample_actuator(.1 + .005, .005, .005)

# PRESET POSITIONS
p = np.ones((sample.shape[0], 12)) * 0.0012
p[:,0] = sample # sets actuator 0 to sample

retract()

pos_0,rot_0,t = op.get_closest_datapoint(time.time())
print(pos_0)

Data = []
for i in range(0, p.shape[0]): # LOOP THROUGH ALL PRESET POSITIONS
    duration = [1.0]
    da.move_joint_position(p[i, :].reshape(1,12), duration)
    print(100*i/p.shape[0],"%","i","=",i)
    da.wait_until_done_moving()
    pos,rot,t = op.get_closest_datapoint(time.time())
    encoder = da.get_joint_positions()[0]
    print("Actuator Position = ",pos-pos_0)
    print("Endcoder = ",encoder)
    Data.append((sample[i,:],encoder,pos-pos_0)) # (desired position, encoder value, optitrack recorded position)
    save_training_data(np.array(Data),"actuator1_data")

save_training_data(np.array(Data),"actuator1_data")

# RESET TO FULLY RETRACTED ACTUATORS
retract()

da.close()
op.close()