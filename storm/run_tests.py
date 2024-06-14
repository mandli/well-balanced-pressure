#!/usr/bin/env python

import os
import numpy
import datetime

import batch.batch

import clawpack.geoclaw.topotools as topotools

days2seconds = lambda days: days * 60.0**2 * 24.0

class SplitSourceJob(batch.batch.Job):
    r""""""

    def __init__(self, split=False, ratio=1, depth=1000, base_path='./'):

        super(SplitSourceJob, self).__init__()

        self.split_forcing = split
        self.ratio = ratio
        self.depth = depth

        self.type = "well-balanced-pressure"
        self.name = "storm"
        self.prefix = f"{str(self.split_forcing)[0]}_n{ratio}_d{int(abs(depth))}"
        self.executable = "xgeoclaw"


        # Create base data object
        import setrun
        self.rundata = setrun.setrun()

        self.rundata.splitting_data.split_forcing = self.split_forcing
        self.rundata.clawdata.num_cells[0] = 300 * self.ratio
        self.rundata.clawdata.num_cells[1] = 200 * self.ratio
        self.rundata.topo_data.basin_depth = float(-self.depth)

    def __str__(self):
        output = super(SplitSourceJob, self).__str__()
        output += f"  Split: {self.split_forcing}\n"
        output += f"  Resolution: {self.ratio}\n"
        output += f"  Depth: {int(self.depth)}"
        return output


    def write_data_objects(self):
        r""""""

        # Write out all data files
        super(SplitSourceJob, self).write_data_objects()


if __name__ == '__main__':

    jobs = []
    for split in [True, False]:
        for depth in [50, 100, 200]:
            jobs.append(SplitSourceJob(split=split, depth=depth))

    controller = batch.batch.BatchController(jobs)
    controller.wait = True
    controller.plot = True
    print(controller)
    controller.run()
