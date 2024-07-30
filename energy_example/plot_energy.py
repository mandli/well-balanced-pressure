#!/usr/bin/env python

import os

import numpy as np
import scipy.integrate as integrate
import matplotlib.pyplot as plt

import clawpack.geoclaw.surge.plot as surgeplot

def E0(t, rho, g, dp, R_m, U):
    f = lambda x, y: (1 - np.exp(-R_m / np.sqrt((x - U * t)**2 + y**2)))**2
    return 0.5 / (rho * g) * dp**2 * integrate.dblquad(f, -R_m, R_m, -R_m, R_m)[0]

def parse_amr_log(path=None):

    if path is None:
        path = os.path.join(os.getcwd(), "_output", "fort.amr")
    else:
        path = os.path.join(path, "fort.amr")

    t = []
    mass = []
    KE = []
    PE = []
    mass_diff = []
    KE_diff = []
    PE_diff = []
    with open(path, 'r') as amr_file:
        for line in amr_file:
            if "time t =" in line:
                if line.split()[5] == "mass":
                    t.append(float(line.split()[3].strip(',')))
                    mass.append(float(line.split()[7]))
                    mass_diff.append(float(line.split()[10]))
                elif line.split()[5] == 'KE':
                    KE.append(float(line.split()[7]))
                    KE_diff.append(float(line.split()[10]))
                elif line.split()[5] == 'PE':
                    PE.append(float(line.split()[7]))
                    PE_diff.append(float(line.split()[10]))
                else:
                    raise ValueError("Invalid type of conservation found.")

    t = np.array(t)
    mass = np.array(mass)
    KE = np.array(KE)
    PE = np.array(PE)
    mass_diff = np.array(mass_diff)
    KE_diff = np.array(KE_diff)
    PE_diff = np.array(PE_diff)

    return [t, mass, KE, PE, mass_diff, KE_diff, PE_diff]


def plot_energy(base_path=None):

    if base_path is None:
        base_path = os.getcwd()

    R_m = 10e3
    g = 9.81
    rho = 1025.0
    d = 40
    eta_0 = 0.04
    U = 0
    T0 = R_m / np.sqrt(g * d)
    dp = eta_0 * rho * g
    t, mass, KE, PE, mass_diff, KE_diff, PE_diff = parse_amr_log(os.path.join(base_path, "_output"))
    
    t /= T0
    E = KE + PE
    E_norm = E0(0.0, rho, g, dp, R_m, U)

    fig, ax = plt.subplots()
    ax.plot(t, E / E_norm, 'k-', label='Total Energy')
    ax.plot(t, KE / E_norm, 'b--', label="KE")
    ax.plot(t, PE / E_norm, 'r--', label="PE")
    ax.set_title("Energy")
    ax.set_ylabel(r"$KE, PE, E / E_0$")
    ax.set_xlabel(r"$t / T_0$")
    # ax.set_xlim((0.0, 50.0))
    # ax.set_ylim((-0.05, 1.1))
    ax.legend()

    return fig


if __name__ == '__main__':
    plot_energy()
    plt.show()