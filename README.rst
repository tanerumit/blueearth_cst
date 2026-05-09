BlueEarth Climate Stress Test toolbox
#####################################

.. note::

   **Fork status (v0.2.0-alpha).** This is a personal fork of
   `Deltares/blueearth_cst <https://github.com/Deltares/blueearth_cst>`_
   under active refactoring. Foundation work — replication baseline,
   pixi-based env, library upgrades (hydromt 1.x, Wflow.jl 1.0.x),
   Python 3.14, and unit-test coverage — is sealed at ``v0.2.0-alpha``.
   Workflow refactoring (R1–R6) starts after this release. See
   ``dev/roadmap.md`` and ``CHANGELOG.md`` for the full picture.

The BlueEarth Climate Stress Test toolbox (blueearth_cst) is a free, open-source, and online toolbox for interactive climate risk assessment based on bottom-up analysis principles.
The toolbox will enable end-users to: 

 - Explore the range of hydro-climatic uncertainty in a selected geographic area of choice, including natural variability and climate change signals.  

 - Design and execute a climate stress test for the response and vulnerabilities of user-defined thresholds and metrics.  

 - Make a judgment on the plausibility of vulnerabilities identified using climate model projections. As such, users should be able to estimate up to what extent the chosen metric or parameter may be sensitive to climate change. 

 - Provide a user-friendly tool with visualization elements that satisfy the needs and expectations of non-specialized audiences 

The Climate Stress Tester is part of the BlueEarth_ initiative and uses weathergenr_ as weather generator and Wflow_ for hydrological modelling.

.. image:: docs/_images/CST_scheme.png


.. _BlueEarth: https://blueearth.deltares.org/

.. _weathergenr: https://github.com/Deltares/weathergenr

.. _Wflow: https://github.com/Deltares/Wflow.jl


Installation
============
BlueEarth CST is a Python + R + Julia toolbox. Python and R dependencies
are managed with pixi_; Julia and Wflow.jl are managed via the standard
``Project.toml`` / ``Manifest.toml``. A single ``pixi run install`` task
wires both layers together.

For a step-by-step walkthrough of a fresh install, also see ``dev/install.md``.

Prerequisites
-------------
1. **pixi** (manages Python 3.14 + R 4.5 via conda-forge).

   Windows (PowerShell):

   .. code-block:: powershell

       iwr -useb https://pixi.sh/install.ps1 | iex

   Or via winget: ``winget install prefix-dev.pixi``. Restart your shell after install.

2. **Julia 1.11.x** via juliaup_. conda-forge has no win-64 Julia build, and
   Wflow.jl 1.0.x deadlocks under Julia 1.12. After installing juliaup:

   .. code-block:: console

       juliaup add 1.11
       juliaup default 1.11

   Verify with ``julia --version`` (expect 1.11.x).

3. Clone the repo:

   .. code-block:: console

       git clone https://github.com/tanerumit/blueearth_cst.git
       cd blueearth_cst

Install
-------

.. code-block:: console

    pixi install         # Python + R toolchain (conda-forge)
    pixi run install     # weathergenr (R) + Wflow.jl (Julia)

The first command installs everything declared in ``pixi.toml`` into a
local ``.pixi/`` env. The second runs ``dev/scripts/install_weathergenr.R``
(installs ``tanerumit/weathergenr@v1.2.0``) and
``julia --project=. -e 'Pkg.instantiate()'`` (locks Wflow.jl and 130
transitive Julia deps from ``Manifest.toml``).

To enter the pixi shell with the env activated:

.. code-block:: console

    pixi shell

Docker
------
A pixi-based ``Dockerfile`` is included but Docker / Linux end-to-end
validation is currently **deferred** in this fork — see
"Deferred: Linux replication" in ``dev/roadmap.md``. The file builds
against the pixi env but is not exercised in CI.

A pre-built image of an earlier (conda-based) Deltares release remains
available at ``containers.deltares.nl/CST/cst_workflows:0.1.0`` and
corresponds to the upstream conda-based stack, not this fork's
pixi-based v0.2.x line.

.. _pixi: https://pixi.sh/
.. _juliaup: https://github.com/JuliaLang/juliaup

Running
=======
BlueEarth CST toolbox is based on several workflows developed using Snakemake_ . Three workflows are available:

 - **Snakefile_model_creation**: creates a Wflow model based on global data for the selected region and run and analyse the model results for a historical period.
 - **Snakefile_climate_projections**: derives future climate statistics (expected temperature and precipitation change) for different RCPs and GCMs (from CMIP dataset).
 - **Snakefile_climate_experiment**: prepares future weather realizations and climate stress tests and run the realizations with the hydrological model.

To prepare these workflows, you can select the different options for your model region and climate scenario using a config file. An example is available in the folder 
config/snake_config_model_test.yml.

You can run each workflow using the ``snakemake`` command line, from within the pixi shell.

Running from pixi shell
-----------------------
Activate the pixi env and ``cd`` into the repo:

.. code-block:: console

    $ pixi shell
    $ cd blueearth_cst

Then run the workflows using the snakemake commands detailed below.

Running from docker image
-------------------------
A script is available to run via docker: `run_snake_docker.sh`

Snakefile_model_creation
------------------------
This workflow creates a hydrological wflow model, based on global data for the selected region, and runs and analyses the model results for a historical period.

.. code-block:: console

    $ snakemake -s Snakefile_model_creation --configfile config/snake_config_model_test.yml  --dag | dot -Tpng > dag_all.png
    $ snakemake --unlock -s Snakefile_model_creation --configfile config/snake_config_model_test.yml
    $ snakemake all -c 1 -s Snakefile_model_creation --configfile config/snake_config_model_test.yml

The first line will activate your environment, the second creates a picture file recapitulating the different steps of the workflow, the third will if needed unlock your directory 
in order to save the future results of the workflow, and the fourth line runs the workflow (here for model creation).

With snakemake command line, you can use different options:

- **-s**: selection of the snakefile (workflow) to run (see list above).
- **--config-file**: name of the config file with the model and climate options.
- **-c**: number of cores to use to run the workflows (if more than 1, the workflow will be parallelized).
- **--dry-run**: returns the list of steps (rules) in the workflow that will be run, without actually running it.

There are many other options available, you can learn more in the `Snakemake CLI documentation <https://snakemake.readthedocs.io/en/stable/executing/cli.html>`_

More examples of how to run the workflows are available in the file run_snake_test.cmd .

.. _Snakemake: https://snakemake.github.io/

Snakefile_climate_projections
-----------------------------
This workflow derives future climate statistics (expected temperature and precipitation change) for different RCPs and GCMs (from CMIP dataset).

.. code-block:: console

    $ snakemake --unlock -s Snakefile_climate_projections --configfile config/snake_config_model_test.yml
    $ snakemake -s Snakefile_climate_projections --configfile config/snake_config_model_test.yml --dag | dot -Tpng > dag_projections.png
    $ snakemake all -c 1 -s Snakefile_climate_projections --configfile config/snake_config_model_test.yml --keep-going 

Snakefile_climate_experiment
----------------------------
This workflow prepares future weather realizations and climate stress tests and run the realizations with the hydrological model.
Finally it derives the results of the stress test and the model run.

.. code-block:: console

    $ snakemake -s Snakefile_climate_experiment --configfile config/snake_config_model_test.yml  --dag | dot -Tpng > dag_climate.png
    $ snakemake --unlock -s Snakefile_climate_experiment --configfile config/snake_config_model_test.yml
    $ snakemake all -c 1 -s Snakefile_climate_experiment --configfile config/snake_config_model_test.yml

Documentation
=============

User-facing documentation:

- Jupyter notebooks explaining each workflow are in ``docs/notebooks/``
  (inherited from `upstream <https://github.com/Deltares/blueearth_cst/tree/main/docs/notebooks>`_).
- ``docs/`` also contains hydromt architecture and user guide content.

Fork-specific development docs:

- ``dev/roadmap.md`` — milestone roadmap, branching/tagging conventions, commit strategy.
- ``dev/install.md`` — step-by-step install walkthrough.
- ``dev/phase-1/`` — sealed foundation milestone artifacts (audits, plans, baseline diffs).
- ``dev/r01/``, ``dev/r02/`` — active Phase 2 milestone designs (modularity contracts, naming conventions).
- ``CHANGELOG.md`` — release history.

License
=======

Copyright (c) 2021, Deltares

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
