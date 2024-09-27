import numpy as np

def getTargets(vel_range, n_targets):

    vel_targets = []

    for i in range(n_targets):
        vel_span = vel_range[1] - vel_range[0]
        vel_step = vel_span/(n_targets - 1)
        vel_targets.append(vel_range[0] + i*vel_step)

    return vel_targets


if __name__ == '__main__':
    test_range = np.array([-50, 50])
    increment = 25 # RPM
    increments = int(abs(test_range[0])/increment + abs(test_range[1])/increment + 1)
    targets = getTargets(test_range,increments)
    print(targets)
    sort_indexes = np.argsort(np.abs(targets))
    # print(sort_indexes[::-1])
    final_targets = np.zeros(np.size(sort_indexes))
    i = 0
    for s in sort_indexes:
        final_targets[i] = targets[s]
        i += 1

    print(final_targets[1:])



