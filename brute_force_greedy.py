from __future__ import print_function

import neal

from dwave.system.composites import EmbeddingComposite
from dwave.system.samplers import DWaveSampler
from dwavebinarycsp.exceptions import ImpossibleBQM

from job_shop_scheduler import get_jss_bqm

from instance_parser import *

from pprint import pprint

from copy import deepcopy


def brute_force_greedy(jobs, solution, qpu=False, num_reads=2000, max_time=None, window_size=5, chain_strength=2, times=10):
    if max_time is None:
        max_time = get_result(jobs, solution) + 3
    for iteration_number in range(times):
        print(iteration_number)
        try:
            if qpu:
                sampler = EmbeddingComposite(
                    DWaveSampler(solver={'qpu': True}))
            else:
                sampler = neal.SimulatedAnnealingSampler()

            for i in range(max_time - window_size):
                info = find_time_window(jobs, solution, i, i + window_size)
                new_jobs, indexes, disable_till, disable_since, disabled_variables = info

                if not bool(new_jobs):  # if new_jobs dict is empty
                    continue

                task_times = solve_greedily(new_jobs)

                # improving original solution
                sol_found = deepcopy(solution)
                for job, times in task_times.items():
                    for j in range(len(times)):
                        if sol_found[job][indexes[job][j]] != task_times[job][j] + i:
                            sol_found[job][indexes[job][j]
                                           ] = task_times[job][j] + i
                if True:  # FIXME: checkValidity(jobs, sol_found):
                    solution = sol_found
                    yield solution, i  # rozwiązanie i miejsce ramki
        except Exception as e:
            print(e)
            continue
