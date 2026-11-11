# Gwsus

[![Documentation](https://img.shields.io/badge/docs-blue?style=flat&logo=gitbook)](https://naibafomsare.github.io/gwsus/)
[![Documentation](https://img.shields.io/badge/github-repo-blue?logo=github)](https://naibafomsare.github.io/gwsus/)


<img align="right" src="SR2_gwsus.png" alt="Long Vertical Figure" width="150" hspace="15">

### Numerical rigid-body simulation of the mirror suspensions of the gravitational-wave detector [KAGRA](https://gwcenter.icrr.u-tokyo.ac.jp/en/)


Predicting the behaviour of mirror suspensions is a mandatory task for the successful construction and operation
of gravitational-wave detectors. Before construction, it is necessary to ensure that the mechanical design of the
vibration isolation systems and payloads meet the seismic attenuation requirements, and that it is possible to
actively damp their mechanical resonances without injecting too much control noise. And later, once the mechanical
systems have been implemented in hardware, knowledge of their resonance frequencies and mode
shapes is necessary to identify stray resonant motion during commissioning and astronomical observations.

Gwsus aims to replace SUMCOM, the software package used in KAGRA for the tasks described above.
Despite the fact that SUMCOM produces scientifically sound predictions, througout the years it has become 
clear that a easy-to-use replacement written in a more accesible language is needed. 
SUMCOM has the disadvantages of requiring a license to run on Mathematica, and of not being 
maintained since 2015.



<br clear="right"/>

## Features

- **[Feature 1]:** [Brief description of a key capability.]
- **[Feature 2]:** [Brief description of another capability.]
- **[Feature 3]:** [Describe an important scientific or computational advantage.]
- This software works in the frequency domain. It calculates frequencies and shapes of resonant modes, and transfer functions.
- It creates interactive 3D animations of the resonance modes for ease of examination.
- It can export the specification of a suspension to Pendulum Toolkit format to allow comparison and validation.

## Project status

In development

## Requirements

- Python [minimum supported version]
- [Important dependency 1]
- [Important dependency 2]

See the project configuration for the complete list of dependencies.

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
    
## Tutorial

**[Link to the tutorials]**

## Documentation

**[Link to the full documentation]**


## License

This is text

## Acknowledgments

This is text.

