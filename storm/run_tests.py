#!/usr/bin/env python

import os
import numpy
import datetime

import batch.batch

import clawpack.geoclaw.topotools as topotools

days2seconds = lambda days: days * 60.0**2 * 24.0

# def eta(x, y, A=1.0, sigma=50e3, x0=0.0):
#     return A * numpy.exp(-(x - x0)**2 / sigma**2)


class SplitSourceJob(batch.batch.Job):
    r""""""

    def __init__(self, split=False, test_type='pressure', base_path='./'):

        super(SplitSourceJob, self).__init__()

        self.split_forcing = split
        self.test_type = test_type

        self.type = "split_source"
        self.name = ""
        self.prefix = f"{str(self.split_forcing)[0]}_{self.test_type}"
        self.executable = "xgeoclaw"


        # Create base data object
        import setrun
        self.rundata = setrun.setrun()

        self.rundata.splitting_data.split_forcing = self.split_forcing
        self.rundata.splitting_data.test_type = self.test_type

        # Dimensional stuff
        self.rundata.geo_data.gravity = 9.81
        self.rundata.geo_data.rho = 1025.0
        # self.rundata.geo_data.gravity = 1.0
        # self.rundata.geo_data.rho = 1.0

    def __str__(self):
        output = super(SplitSourceJob, self).__str__()
        output += f"\n  Split: {self.split_forcing}"
        output += f"\n  Test: {self.test_type}"
        return output


    def write_data_objects(self):
        r""""""

        # Write out all data files
        super(SplitSourceJob, self).write_data_objects()


if __name__ == '__main__':

    jobs = []
    for test_type in ['pressure', 'bathymetry']:
        for split in [True, False]:
                jobs.append(SplitSourceJob(split=split, test_type=test_type))

    controller = batch.batch.BatchController(jobs)
    controller.wait = True
    controller.plot = False
    print(controller)
    controller.run()
