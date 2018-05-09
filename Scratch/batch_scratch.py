from ABM.batch import batchManager

bm = batchManager(num_batches=100, num_steps=10000, do_animation=True, animation_moving_average_coefficient=0.95)

bm.start()


