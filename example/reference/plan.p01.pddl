(calibrate rover0 camera0 objective1 waypoint3)
(take_image rover0 waypoint3 objective1 camera0 high_res)
(communicate_image_data rover0 general objective1 high_res waypoint3 waypoint0)
(sample_rock rover0 rover0store waypoint3)
(navigate rover0 waypoint3 waypoint1)
(navigate rover0 waypoint1 waypoint2)
(communicate_rock_data rover0 general waypoint3 waypoint2 waypoint0)
(drop rover0 rover0store)
(sample_soil rover0 rover0store waypoint2)
(communicate_soil_data rover0 general waypoint2 waypoint2 waypoint0)
; cost = 10 (unit cost)
