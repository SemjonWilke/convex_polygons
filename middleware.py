
import time

def snapshoot_t(start_t, _msg):
    elp_t = time.process_time() - start_t

    # print("seconds: ", elp_t)
    # print("minutes:", elp_t/60)
    # print("hours:", elp_t/3600)


    print("{0}: \n \tseconds: {1} \n \tminutes: {2} \n \thours: {3} \n".format(_msg, elp_t, \
                elp_t/60, elp_t/3600))
