from batch import batchManager

bm = batchManager(num_batches=2, num_steps=100, do_animation=True, animation_moving_average_coefficient=0.9)

bm.start()


