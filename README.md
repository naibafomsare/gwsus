# Gwsus

[![Documentation](https://img.shields.io/badge/docs-blue?style=flat&logo=gitbook)](https://naibafomsare.github.io/gwsus/)
![Astrophysics](https://img.shields.io/badge/domain-astrophysics-orange.svg)
![Instrumentation](https://img.shields.io/badge/domain-instrumentation-yellowgreen.svg)
[![Github](https://img.shields.io/badge/github-repo-blue?logo=github)](https://naibafomsare.github.io/gwsus/)
[![License](https://img.shields.io/badge/license-MIT-green)](https://naibafomsare.github.io/gwsus/)




<img align="right" src="SR2_gwsus.png" alt="Long Vertical Figure" width="150" hspace="15">

### Numerical rigid-body simulation of the mirror suspensions of the gravitational-wave detector [KAGRA](https://gwcenter.icrr.u-tokyo.ac.jp/en/)


Predicting the behaviour of mirror suspensions is a mandatory task for the successful construction and operation
of gravitational-wave detectors. Before construction, it is necessary to ensure that the 
vibration isolation systems and payloads meet the seismic attenuation requirements, and that it is possible to
actively damp their resonant motion without injecting too much control noise. And after construction, when the suspensions are already in operation, knowledge of their resonance frequencies and mode
shapes is necessary to identify the origin of stray motion during commissioning and astronomical observations.

Gwsus aims to replace SUMCOM, the software used in KAGRA for the tasks described above.
Such a package has the disadvantage of requiring a license to run on Mathematica, has
bugs and has not been maintained since 2015. Despite the fact that it produces scientifically
sound predictions, througout the years it has become clear that an easy-to-use alternative
written in a more accesible language is needed.


<br clear="right"/>

## Features

- Works in the frequency domain.
- Calculates resonance frequencies, mode shapes, and creates interactive
  3D animations of the modes for ease of examination.
- Computes transfer functions.
- Provides templates for the components of the signal
  recycling suspensions of KAGRA.

For future releases, the aim is to add the capability to calculate displacement
thermal noise, and to provide templates for the components of Type-Bp and Type-A suspensions.

## Project status

This software is in constant development, and there are a few features
that still need to be assessed, improved or added before it is ready
for scientific work in a GW observatory. 

- Implemention of inverted pendulums.
- Implementation of wire bending potential.
- Validation of results by comparison with
  independent calculations.
- Assessment of numerical round-off error in eigenvector
  calculation with Mpmath and, depending on results, write a
  completely symbolic calculation in Symengine.

## Tutorial

The current tutorial describes how to implement KAGRA's SR2 suspension.
It covers the specification of its components, their assembly into a suspension,
calculation of resonance
frequencies and modes, how to display interactive 3D animations and the calculation of
transfer functions:

[SR2 Tutorial](https://naibafomsare.github.io/gwsus/auto_examples/)


## Documentation

It covers installation instructions, tutorials, theoretical background, application programing interface (API) and bibliography.

[Gwsus documentation](https://naibafomsare.github.io/gwsus/)


## Requirements

- Python 3.10 or later
- Numpy
- Mpmath
- Sympy
- Symengine
- VPython
- Bigtree
- Matplotlib
- Tabulate
- Termcolor

## Installation

Clone the repository:

```bash
git clone https://github.com/[USERNAME]/Gwsus.git
cd Gwsus
```

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows, activate the environment with:

```powershell
.venv\Scripts\activate
```

Install the project and its dependencies:

```bash
python -m pip install -e .
```

This command assumes that the repository contains a correctly configured `pyproject.toml`.
    

## Acknowledgments

As SUMCOM before, Gwsus is based on Mark Barton's software *Pendulum Toolkit*,
which is written in Mathematica and was developed specifically to analyze LIGO's suspensions. Whereas
Gwsus aims to be accesible, easy to use and to maintain, and tailored for KAGRA-style suspensions,
Pendulum Toolkit remains an authoritative reference.

